# Flask DevOps Project — End to End Cloud Deployment on AWS EKS

![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

A production-style DevOps project showcasing containerization, infrastructure as code, Kubernetes orchestration, and automated CI/CD — built from scratch on AWS.

---

## Architecture

```
Developer pushes code to GitHub
        ↓
GitHub Actions triggers CI/CD pipeline
        ↓
Docker image built → pushed to AWS ECR
        ↓
EKS deployment updated with new image
        ↓
Internet → AWS ALB → K8s Ingress → Service → Pod (Flask app)
```

![Architecture](architecture.png)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application | Python, Flask |
| Containerization | Docker |
| Container Registry | AWS ECR |
| Orchestration | AWS EKS (Kubernetes) |
| Infrastructure as Code | Terraform |
| CI/CD | GitHub Actions |
| Ingress | AWS Load Balancer Controller (ALB) |
| Networking | AWS VPC, Subnets, Internet Gateway |
| Auth | OIDC (no hardcoded credentials) |

---

## Project Structure

```
flask-devops-project1/
├── app.py                          # Flask application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage Docker build
├── docker-compose.yml              # Local development
├── terraform/
│   ├── main.tf                     # AWS provider config
│   ├── variables.tf                # Input variables
│   ├── outputs.tf                  # Output values
│   ├── vpc.tf                      # VPC, subnets, IGW, route tables
│   ├── ecr.tf                      # ECR repository + lifecycle policy
│   ├── iam.tf                      # IAM roles and policies for EKS
│   ├── eks.tf                      # EKS cluster + node group
│   └── backend.tf                  # S3 remote state + DynamoDB locking
├── k8s/
│   ├── namespace.yaml              # K8s namespace
│   ├── deployment.yaml             # K8s deployment with probes
│   ├── service.yaml                # ClusterIP service
│   └── ingress.yaml                # ALB ingress
└── .github/
    └── workflows/
        └── cd.yml                  # CI/CD pipeline
```

---

## Application

A lightweight Flask REST API with 3 endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Returns app info (message, version, environment) |
| `/health` | GET | Health check — used by K8s liveness and readiness probes |
| `/info` | GET | Returns app metadata and available endpoints |

Config is injected via environment variables — same image runs in any environment:

```bash
APP_VERSION=1.0
APP_ENV=production
```

---

## Infrastructure (Terraform)

All AWS infrastructure is provisioned as code:

- **VPC** — isolated network with 2 public subnets across 2 availability zones
- **Internet Gateway + Route Tables** — public internet access
- **ECR Repository** — private Docker registry with vulnerability scanning and lifecycle policy (keeps last 10 images)
- **EKS Cluster** — managed Kubernetes control plane (v1.31)
- **EKS Node Group** — EC2 worker nodes with auto-scaling (min 1, max 3)
- **IAM Roles** — least privilege roles for EKS control plane and worker nodes
- **S3 Backend** — remote Terraform state with DynamoDB locking

### Provision Infrastructure

```bash
cd terraform

# Create S3 backend resources first
aws s3api create-bucket \
  --bucket flask-devops-terraform-state \
  --region ap-south-1

aws dynamodb create-table \
  --table-name flask-devops-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-south-1

# Deploy infrastructure
terraform init
terraform plan
terraform apply
```

---

## Kubernetes

The app runs on EKS with the following K8s resources:

- **Namespace** — `flask-app` isolates all resources
- **Deployment** — manages pod lifecycle with rolling updates
- **Liveness Probe** — K8s restarts pod if `/health` stops responding
- **Readiness Probe** — K8s only sends traffic when `/health` returns 200
- **Service** — ClusterIP routes internal traffic to pods on port 5000
- **Ingress** — AWS ALB exposes app to internet on port 80

### Deploy to EKS

```bash
# Connect kubectl to cluster
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name flask-devops-cluster

# Apply manifests
kubectl apply -f k8s/

# Verify
kubectl get pods -n flask-app
kubectl get ingress -n flask-app
```

---

## CI/CD Pipeline (GitHub Actions)

Every push to `main` triggers an automated pipeline with two jobs:

```
Job 1: build-and-test
  → Install Python dependencies
  → Run smoke test
  → Build Docker image

Job 2: push-and-deploy (runs only if Job 1 passes)
  → Authenticate with AWS via OIDC (no hardcoded credentials)
  → Push image to ECR tagged with git commit SHA
  → Update EKS deployment with new image
  → Verify rollout completes successfully
```

### OIDC Authentication

GitHub Actions authenticates with AWS using **OpenID Connect** — no AWS access keys stored anywhere. A short-lived token is generated per run and expires automatically.

### Image Tagging Strategy

Every image is tagged with the git commit SHA:

```
flask-devops:a1b2c3d4   ← traceable to exact commit
flask-devops:b2c3d4e5
flask-devops:latest
```

This enables instant rollback to any previous version:

```bash
kubectl set image deployment/flask-app \
  flask-app=YOUR_ECR_URL:PREVIOUS_SHA \
  -n flask-app
```

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `AWS_ROLE_ARN` | ARN of the GitHub Actions IAM role |
| `AWS_REGION` | AWS region (ap-south-1) |
| `ECR_REPOSITORY` | Full ECR repository URL |
| `EKS_CLUSTER_NAME` | EKS cluster name |

---

## Local Development

```bash
# Clone the repo
git clone https://github.com/Vismaya582/flask-devops-project1.git
cd flask-devops-project1

# Run with Docker Compose (app + local postgres if needed)
docker compose up --build

# Test endpoints
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/info
```

---

## Key DevOps Concepts Demonstrated

**Infrastructure as Code** — every AWS resource defined in Terraform. No manual console clicks. Entire infrastructure can be created or destroyed in one command.

**Immutable Infrastructure** — never SSH into servers to make changes. Every change goes through a new Docker image and a new deployment.

**GitOps Principles** — git is the single source of truth. Every deployment is tied to a specific commit SHA.

**Zero Credential Storage** — OIDC means no AWS access keys are stored anywhere. GitHub Actions gets temporary credentials per run.

**Self-Healing** — Kubernetes liveness probes automatically restart unhealthy pods without human intervention.

**Zero Downtime Deployments** — Kubernetes rolling updates ensure new pods are healthy before old pods are terminated.

**Layer Caching** — Dockerfile copies `requirements.txt` before app code so pip install is cached between builds — only reruns when dependencies change.

---

## Cost Management

| Resource | Cost |
|---|---|
| EKS Control Plane | $0.10/hr (~$72/month) |
| t3.small node (1x) | ~$15/month |
| ALB | ~$18/month |

> Always destroy when not in use: `terraform destroy`
> Scale nodes to zero for short breaks:
> ```bash
> aws eks update-nodegroup-config \
>   --cluster-name flask-devops-cluster \
>   --nodegroup-name flask-devops-nodes \
>   --scaling-config minSize=0,maxSize=3,desiredSize=0 \
>   --region ap-south-1
> ```

---

## Author

**Vismaya** — [GitHub](https://github.com/Vismaya582)