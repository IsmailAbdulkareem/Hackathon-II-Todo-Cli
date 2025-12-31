# Phase IV: Local Kubernetes Deployment

**Status:** 🔜 Pending
**Points:** 250
**Tech Stack:** Docker, Minikube, Helm, kubectl-ai, kagent
**Due Date:** Jan 4, 2026

## Overview

Phase IV containerizes the application and deploys it locally using Kubernetes, demonstrating cloud-native practices and operational readiness.

## What's New

### Containerization
- **Multi-stage Docker builds** for optimized image sizes
- **Docker Compose** for local development
- **Health checks** and graceful shutdowns
- **Secret management** with Kubernetes Secrets

### Kubernetes
- **Minikube** local K8s cluster
- **Helm charts** for declarative deployment
- **Auto-scaling** with Horizontal Pod Autoscaler
- **Ingress** configuration for routing
- **Persistent volumes** for database storage

### AI Operations
- **kubectl-ai**: AI-enhanced kubectl commands
- **kagent**: AI-powered cluster management
- **Intelligent monitoring** and alerting

## Prerequisites

```bash
# Install required tools
# Docker
# https://docs.docker.com/get-docker/

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# kubectl-ai (AI-enhanced kubectl)
npm install -g @kubernetes/kubectl-ai

# kagent (AI cluster agent)
npm install -g @kubernetes/kagent
```

## Quick Start

### 1. Start Minikube

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Build Docker Images

```bash
# Build backend image
cd ../phase-02-fullstack-web/backend
docker build -t todo-backend:local .

# Build frontend image
cd ../frontend
docker build -t todo-frontend:local .
```

### 3. Deploy with Helm

```bash
cd phase-04-k8s-local

# Install dependencies
helm dependency update

# Deploy application
helm install todo-app ./chart

# Check deployment status
kubectl get pods
kubectl get services
```

### 4. Access Application

```bash
# Get Minikube IP
minikube ip

# Access frontend at
http://$(minikube ip):30000
```

## Project Structure

```
phase-04-k8s-local/
├── chart/
│   ├── Chart.yaml              # Helm chart metadata
│   ├── values.yaml             # Default configuration
│   ├── templates/
│   │   ├── deployment.yaml     # Pod deployments
│   │   ├── service.yaml        # Service definitions
│   │   ├── ingress.yaml        # Ingress routing
│   │   ├── configmap.yaml      # Configuration
│   │   ├── secret.yaml         # Secrets
│   │   ├── hpa.yaml            # Horizontal Pod Autoscaler
│   │   └── pvc.yaml           # Persistent Volume Claims
│   └── charts/                 # Chart dependencies
│       └── postgresql/         # PostgreSQL sub-chart
├── docker/
│   ├── backend/
│   │   └── Dockerfile          # Backend container
│   ├── frontend/
│   │   └── Dockerfile          # Frontend container
│   └── docker-compose.yml      # Local development
├── k8s/
│   ├── namespace.yaml          # Namespace definition
│   ├── base/                   # Kustomize base
│   └── overlays/               # Environment overlays
│       ├── dev/
│       └── staging/
└── scripts/
    ├── build-and-push.sh       # Build & push images
    ├── deploy.sh               # Deploy to K8s
    └── rollback.sh             # Rollback deployment
```

## Kubernetes Resources

### Deployments
- **todo-backend**: FastAPI backend (replicas: 3)
- **todo-frontend**: Next.js frontend (replicas: 2)
- **postgres**: PostgreSQL database (replicas: 1)

### Services
- **todo-backend-svc**: ClusterIP for backend
- **todo-frontend-svc**: NodePort for frontend
- **postgres-svc**: ClusterIP for database

### Auto-scaling
- **HPA**: Scale based on CPU > 70%
- **Min replicas**: 2
- **Max replicas**: 10

## kubectl-ai Usage

```bash
# Ask natural language questions to your cluster
kubectl-ai "show me all failing pods"

# Get explanations for issues
kubectl-ai "explain why the backend is crashing"

# Generate commands
kubectl-ai "scale up the backend to 5 replicas"

# Get configuration help
kubectl-ai "configure an ingress for /api to route to backend"
```

## kagent Features

```bash
# Start kagent
kagent init

# AI-powered monitoring
kagent monitor --alert-on-errors

# Intelligent troubleshooting
kagent troubleshoot --deployment todo-backend

# Optimization suggestions
kagent optimize --resource usage
```

## Monitoring & Observability

### Metrics
- **CPU/Memory**: kube-state-metrics + Prometheus
- **Application Metrics**: Custom metrics endpoint
- **Database Metrics**: PostgreSQL exporter

### Logging
- **Pod Logs**: Standard output captured
- **Structured Logs**: JSON format for parsing
- **Log Aggregation**: Centralized logging setup

### Tracing
- **Distributed Tracing**: Jaeger integration
- **Request Tracing**: End-to-end request tracking

## Security

### Best Practices
- **Secrets Management**: Kubernetes Secrets, never in plain text
- **Network Policies**: Restrict pod-to-pod communication
- **Pod Security**: Run as non-root, read-only root filesystem
- **Image Scanning**: Trivy for vulnerability scanning

### RBAC
- **Service Accounts**: Least privilege access
- **RoleBindings**: Scoped permissions
- **Audit Logging**: Track all API actions

## Disaster Recovery

### Backups
- **Database Backups**: Automated daily backups
- **Volume Snapshots**: Persistent volume backups
- **Configuration Backup**: GitOps with ArgoCD (future)

### Rollback
```bash
# Helm rollback
helm rollback todo-app

# Kubectl rollback
kubectl rollout undo deployment/todo-backend
```

## Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**Connection refused:**
```bash
kubectl get endpoints
kubectl get svc
```

**CPU/Memory pressure:**
```bash
kubectl top nodes
kubectl top pods
```

### kubectl-ai Diagnosis

```bash
kubectl-ai "diagnose why todo-backend pods are pending"
kubectl-ai "check if database connection is working"
kubectl-ai "verify all services are communicating"
```

## Performance Tuning

### Resource Limits
```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

### Probes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Next Steps

Phase V will add:
- Kafka for event streaming
- Dapr for distributed application runtime
- DigitalOcean DOKS for cloud deployment
- Production-grade configuration
- High availability setup

## Cleanup

```bash
# Delete Helm release
helm uninstall todo-app

# Stop Minikube
minikube stop

# Full cleanup
minikube delete
```
