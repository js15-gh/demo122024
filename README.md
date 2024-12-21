# Demo Project

This project demonstrates a modern web service setup with full Google Cloud Platform integration.

## Architecture Overview
- **Backend**: FastAPI Python service
- **Database**: Cloud SQL (PostgreSQL)
- **Container Registry**: Google Container Registry (GCR)
- **Deployment**: Google Cloud Run
- **CI/CD**: GitHub Actions with GCP integration
- **Infrastructure**: Terraform for Infrastructure as Code

## Prerequisites
1. Google Cloud SDK (`gcloud`)
2. Terraform
3. Docker
4. Python 3.9+

## Local Development Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```
3. Run locally:
   ```bash
   uvicorn src.main:app --reload
   ```

## Google Cloud Setup Guide

### 1. Initial GCP Setup
```bash
# Install Google Cloud SDK
brew install google-cloud-sdk

# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Required APIs
```bash
# Enable required GCP services
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  containerregistry.googleapis.com
```

### 3. Database Setup
1. Create Cloud SQL instance:
   ```bash
   gcloud sql instances create demo-db \
     --database-version=POSTGRES_13 \
     --tier=db-f1-micro \
     --region=us-west1
   ```
2. Create database:
   ```bash
   gcloud sql databases create demo-db \
     --instance=demo-db
   ```

### 4. Container Registry
```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Build and push
docker build -t gcr.io/YOUR_PROJECT_ID/demo-app .
docker push gcr.io/YOUR_PROJECT_ID/demo-app
```

### 5. Cloud Run Deployment
```bash
gcloud run deploy demo-service \
  --image gcr.io/YOUR_PROJECT_ID/demo-app \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated
```

## Infrastructure as Code
Our Terraform configurations in `/infrastructure` manage:
- Cloud SQL instance
- Cloud Run service
- IAM permissions
- Network settings

To apply:
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

## CI/CD Pipeline
The GitHub Actions workflow in `.github/workflows/`:
1. Runs tests
2. Builds Docker image
3. Pushes to GCR
4. Deploys to Cloud Run

## Security
- Secrets are managed via GitHub Secrets and GCP Secret Manager
- Database credentials are rotated automatically
- All services use least-privilege IAM roles

## Monitoring
- Cloud Run metrics in GCP Console
- Cloud SQL insights
- Custom application metrics via Cloud Monitoring

## Estimated Costs
- Cloud Run: Pay per use (~$0.00002400/100ms)
- Cloud SQL: ~$7/month for db-f1-micro
- Container Registry: ~$0.026/GB/month
