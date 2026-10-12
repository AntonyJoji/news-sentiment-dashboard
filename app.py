import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Global News Sentiment Intelligence",
    page_icon="📡",
    layout="wide"
)

# Dark styling for matplotlib charts
plt.style.use("dark_background")

# --- Expanded Realistic Mock Data ---
sample_data = {
    "title": [
        "Tech stocks surge as quarterly chip earnings surpass Wall Street forecasts",
        "Inflation fears spike following volatile energy price adjustments",
        "Pioneering renewable solid-state battery tech achieves commercial scale",
        "Major enterprise software firm confirms restructuring and layoffs",
        "Global trade summit concludes with bilateral tariff reduction agreement",
        "Cybersecurity researchers disclose zero-day vulnerability in cloud router firmware",
        "Central bank signals pause on interest rate hikes amid cooling market data",
        "Biotech firm receives expedited FDA clearance for novel autoimmune therapy",
        "Commercial real estate debt defaults reach five-year high in major metros",
        "Autonomous logistics fleet logs first accident-free million kilometers",
        "Oil output steady as shipping route security measures implemented",
        "Retail consumer confidence index stabilizes in latest economic bulletin"
    ],
    "source_name": [
        "Bloomberg", "Reuters", "TechCrunch", "WSJ", "Financial Times",
        "Ars Technica", "CNBC", "Endpoints News", "Bloomberg", "TechCrunch",
        "Reuters", "BBC News"
    ],
    "category": [
        "Markets", "Economy", "Technology", "Business", "Trade",
        "Cybersecurity", "Finance", "Healthcare", "Real Estate", "AI/Robotics",
        "Energy", "Economy"
    ],
    "published_at": [
        "2026-10-12 09:45", "2026-10-12 09:30", "2026-10-12 09:12", "2026-10-12 08:50",
        "2026-10-12 08:35", "2026-10-12 08:15", "2026-10-12 07:55", "2026-10-12 07:30",
        "2026-10-12 07:10", "2026-10-12 06:45", "2026-10-12 06:20", "2026-10-12 06:00"
    ],
    "sentiment_label": [
        "POSITIVE", "NEGATIVE", "POSITIVE", "NEGATIVE", "POSITIVE",
        "NEGATIVE", "NEUTRAL", "POSITIVE", "NEGATIVE", "POSITIVE",
        "NEUTRAL", "NEUTRAL"
    ],
    "sentiment_score": [
        0.78, -0.65, 0.82, -0.71, 0.54,
        -0.80, 0.02, 0.74, -0.68, 0.85,
        -0.03, 0.05
    ]
}

df_raw = pd.DataFrame(sample_data)

# --- Sidebar Filters ---
st.sidebar.header("🕹️ Pipeline Filters")
st.sidebar.caption("Filter news ingested from EventBridge / Lambda")

selected_sentiment = st.sidebar.multiselect(
    "Sentiment Filter",
    options=["POSITIVE", "NEGATIVE", "NEUTRAL"],
    default=["POSITIVE", "NEGATIVE", "NEUTRAL"]
)

selected_sources = st.sidebar.multiselect(
    "Publisher Filter",
    options=sorted(df_raw["source_name"].unique()),
    default=sorted(df_raw["source_name"].unique())
)

df = df_raw[
    (df_raw["sentiment_label"].isin(selected_sentiment)) &
    (df_raw["source_name"].isin(selected_sources))
]

# --- Main Dashboard Header ---
st.title("📡 Real-Time News Sentiment Intelligence Dashboard")
st.caption(f"AWS ECS Fargate Container • Automated Ingestion Every 5 Mins • Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")

# --- Top Level Metrics ---
col1, col2, col3, col4, col5 = st.columns(5)
total_count = len(df)
pos_count = len(df[df["sentiment_label"] == "POSITIVE"])
neg_count = len(df[df["sentiment_label"] == "NEGATIVE"])
neu_count = len(df[df["sentiment_label"] == "NEUTRAL"])
avg_score = df["sentiment_score"].mean() if total_count > 0 else 0.0

col1.metric("Articles Processed", total_count)
col2.metric("Positive Sentiment", pos_count, delta=f"{pos_count} articles")
col3.metric("Negative Sentiment", neg_count, delta=f"-{neg_count} articles", delta_color="inverse")
col4.metric("Neutral Sentiment", neu_count)
col5.metric("Avg Sentiment Score", f"{avg_score:+.2f}")

st.markdown("---")

# --- Charts Section ---
chart_col1, chart_col2 = st.columns([1, 1])

with chart_col1:
    st.subheader("📊 Sentiment Polarity Distribution")
    if not df.empty:
        counts = df["sentiment_label"].value_counts()
        labels = counts.index
        palette = {"POSITIVE": "#00C853", "NEGATIVE": "#D50000", "NEUTRAL": "#757575"}
        colors = [palette.get(l, "#9E9E9E") for l in labels]

        fig, ax = plt.subplots(figsize=(6, 4.5), facecolor="#0E1117")
        ax.set_facecolor("#0E1117")

        wedges, texts, autotexts = ax.pie(
            counts,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            wedgeprops=dict(width=0.45, edgecolor="#0E1117", linewidth=2),
            textprops=dict(color="white", fontsize=10, weight="bold")
        )
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(10)

        st.pyplot(fig, use_container_width=True)
    else:
        st.warning("No data matches current filters.")

with chart_col2:
    st.subheader("📰 Sentiment Score by Source")
    if not df.empty:
        source_avg = df.groupby("source_name")["sentiment_score"].mean().sort_values()
        
        fig2, ax2 = plt.subplots(figsize=(6, 4.5), facecolor="#0E1117")
        ax2.set_facecolor("#0E1117")

        bar_colors = ["#00C853" if val >= 0 else "#D50000" for val in source_avg.values]
        bars = ax2.barh(source_avg.index, source_avg.values, color=bar_colors, height=0.55)

        ax2.axvline(0, color="#757575", linewidth=1, linestyle="--")
        ax2.set_xlim(-1.0, 1.0)
        ax2.tick_params(colors="white", labelsize=9)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.spines["bottom"].set_color("#424242")
        ax2.spines["left"].set_color("#424242")
        ax2.set_xlabel("Compound Polarity (-1.0 to +1.0)", color="white", fontsize=9)

        st.pyplot(fig2, use_container_width=True)
    else:
        st.warning("No data matches current filters.")

st.markdown("---")

# --- Data Table Feed ---
st.subheader("⚡ Live Article Ingestion Stream")

display_cols = ["published_at", "source_name", "category", "sentiment_label", "sentiment_score", "title"]
st.dataframe(
    df[display_cols].rename(columns={
        "published_at": "Timestamp (UTC)",
        "source_name": "Publisher",
        "category": "Topic",
        "sentiment_label": "Label",
        "sentiment_score": "Score",
        "title": "Headline"
    }),
    use_container_width=True,
    height=320,
    hide_index=True
)