# Real-Time News Sentiment Intelligence Dashboard

An end-to-end containerized sentiment analysis web application built with Streamlit and deployed to AWS ECS Fargate via Amazon Elastic Container Registry (ECR).

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Step1 ["1. Local Environment"]
        A[Python Code: app.py] --> B[Docker Engine: Port 8501]
    end

    subgraph Step2 ["2. AWS Container Registry (ECR)"]
        C[(Amazon ECR: streamlit-docker-demo)]
    end

    subgraph Step3 ["3. AWS Serverless Compute (ECS Fargate)"]
        D[ECS Cluster: news-sentiment-cluster]
        E[Task Definition: streamlit-sentiment-task]
        F[Security Group: Port 8501 Inbound]
        D --> E --> F
    end

    subgraph Step4 ["4. Live User Access"]
        G[Browser Access: http://PUBLIC_IP:8501]
    end

    Step1 -->|docker push via AWS CLI| Step2
    Step2 -->|pulls image| Step3
    Step3 -->|provisions public IP| Step4

    style Step1 fill:#f9f9f9,stroke:#333,stroke-width:1px
    style Step2 fill:#e1f5fe,stroke:#0288d1,stroke-width:1px
    style Step3 fill:#fff3e0,stroke:#f57c00,stroke-width:1px
    style Step4 fill:#e8f5e9,stroke:#388e3c,stroke-width:1px

⚙️ How It Works

1. **Application Layer (`app.py`)**: 
   The dashboard runs on Streamlit and displays real-time sentiment distribution (positive, neutral, negative metrics), sentiment polarity doughnut charts, publisher polarity breakdowns, and a live article ingestion table.

2. **Containerization (`Dockerfile`)**: 
   Packages Python 3.11, project dependencies (`requirements.txt`), and dashboard scripts into an isolated container. It exposes internal port `8501` and configures Streamlit to accept external connections with headless browser mode enabled.

3. **Image Distribution (Amazon ECR)**: 
   The local Docker image is tagged and pushed to Amazon Elastic Container Registry (`streamlit-docker-demo`) in the Mumbai region (`ap-south-1`). ECR serves as the secure, private cloud registry for deployment.

4. **Serverless Orchestration (Amazon ECS on AWS Fargate)**:
   - **Task Definition (`streamlit-sentiment-task`)**: Defines resource allocation (0.5 vCPU, 1 GB RAM), port mappings (`8501`), and points to the ECR image URI.
   - **Service & Scheduler**: Runs the task in replica mode, maintaining the desired number of tasks.
   - **Serverless Compute (AWS Fargate)**: AWS handles EC2 provisioning, instance patching, and underlying operating systems automatically.
   - **Networking & Security Group (`streamlit-ecs-sg`)**: Placed within the default VPC public subnets with a public IP assigned, allowing inbound web traffic over Custom TCP port `8501`.

---

## 📂 Project Structure

```text
streamlit-docker-demo/
│
├── app.py                # Main Streamlit dashboard application
├── Dockerfile            # Container build and execution recipe
├── requirements.txt      # Python runtime dependencies
├── .dockerignore         # Files ignored during Docker build
└── README.md             # Project documentation and architecture guide

🚀 Setup & Deployment Guide
Prerequisites
--> Docker Desktop installed and running

--> AWS CLI installed and configured (aws configure)

--> Git

1. Local Testing
Clone the project and verify locally:

git clone [https://github.com/AntonyJoji/news-sentiment-dashboard.git](https://github.com/AntonyJoji/news-sentiment-dashboard.git)
cd news-sentiment-dashboard

Build and run via Docker:

docker build -t streamlit-sentiment-app .
docker run -p 8501:8501 streamlit-sentiment-app

Access at http://localhost:8501

2. Push Image to Amazon ECR
Log in to your AWS ECR registry:

aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com

Create repository and push:

aws ecr create-repository --repository-name streamlit-docker-demo --region ap-south-1
docker tag streamlit-sentiment-app:latest <AWS_ACCOUNT_ID>[.dkr.ecr.ap-south-1.amazonaws.com/streamlit-docker-demo:latest](https://.dkr.ecr.ap-south-1.amazonaws.com/streamlit-docker-demo:latest)
docker push <AWS_ACCOUNT_ID>[.dkr.ecr.ap-south-1.amazonaws.com/streamlit-docker-demo:latest](https://.dkr.ecr.ap-south-1.amazonaws.com/streamlit-docker-demo:latest)


3. Deploy to AWS ECS Fargate
Create a cluster named news-sentiment-cluster on ECS.

Register a task definition streamlit-sentiment-task pointing to your ECR image URI with port 8501 mapped.

Create a service on Fargate:

Desired tasks: 1

Public IP: Turned on

Security Group: Allow TCP inbound on port 8501 (0.0.0.0/0).

Grab the public IP from the running task:
http://<TASK_PUBLIC_IP>:8501

4. Stopping / Cost Management
To avoid Fargate runtime charges when not presenting:

Open ECS --> Clusters --> news-sentiment-cluster --> Services.Click Update service --> change Desired tasks to 0.

---
