# Phase IV: Local Kubernetes Deployment

**Feature**: Local Kubernetes deployment for Todo Chatbot (Phase III application)
**Date**: 2026-01-28
**Status**: Implementation in Progress

## Overview

This directory contains all Kubernetes deployment artifacts for deploying the Phase III Todo Chatbot application to a local Minikube cluster using AI-assisted DevOps practices.

## Directory Structure

```
k8s/
├── dockerfiles/          # Container definitions for frontend and backend
│   ├── frontend.Dockerfile
│   └── backend.Dockerfile
├── helm/                 # Helm chart for deployment
│   └── todo-chatbot/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── backend-deployment.yaml
│           └── backend-service.yaml
└── manifests/           # Raw Kubernetes YAML (optional reference)
```

## Deployment Flow

### 1. **Containerization** (Phase 3)
- Build Docker images for frontend (Next.js) and backend (FastAPI)
- Use AI assistance (Docker AI/Gordon) for Dockerfile generation
- Store images in Minikube's local Docker registry

### 2. **Kubernetes Deployment** (Phase 4)
- Deploy using Helm charts for parameterized configuration
- Frontend: NodePort service (port 3000) for external access
- Backend: ClusterIP service (port 7860) for internal communication
- Use AI tools (kubectl-ai, kagent) for deployment verification

### 3. **Verification**
- Verify pods are running
- Verify services are accessible
- Test frontend-backend communication

## AI DevOps Tools Strategy

### Docker AI (Gordon)
**Purpose**: AI-assisted Dockerfile generation and optimization

**Usage**:
```bash
# Check capabilities
docker ai "What can you do?"

# Generate Dockerfiles
docker ai "Create a Dockerfile for a Next.js frontend application"
docker ai "Create a Dockerfile for a Python FastAPI backend"
```

**Fallback**: If Docker AI is unavailable, use Claude Code to generate Dockerfiles following best practices.

### kubectl-ai
**Purpose**: Natural language interface for Kubernetes operations

**Usage**:
```bash
# Verify deployment
kubectl ai "show me all pods and their status"
kubectl ai "list all services and their endpoints"

# Scaling operations
kubectl ai "scale the frontend deployment to 3 replicas"
```

**Fallback**: Use standard kubectl commands with AI-generated explanations.

### kagent
**Purpose**: AI-powered Kubernetes agent for autonomous operations

**Usage**:
```bash
# Deployment analysis
kagent analyze deployment todo-frontend

# Health checks
kagent check deployment todo-backend
```

**Fallback**: If unavailable, document the attempt and use standard kubectl diagnostics.

## Application Configuration

### Frontend (Next.js)
- **Source**: `../../phase-03-ai-chatbot/frontend`
- **Port**: 3000
- **Service Type**: NodePort (external access)
- **Environment Variables**:
  - `NEXT_PUBLIC_API_URL`: http://backend-service:7860

### Backend (FastAPI)
- **Source**: `../../phase-03-ai-chatbot/backend`
- **Port**: 7860 (not 8000!)
- **Service Type**: ClusterIP (internal only)
- **Existing Dockerfile**: Available at `../../phase-03-ai-chatbot/backend/Dockerfile`

## Quick Start

### Prerequisites
- Docker Desktop running
- Minikube installed and started
- kubectl configured
- Helm 3+ installed

### Deploy

```bash
# 1. Configure Docker to use Minikube registry
eval $(minikube docker-env)

# 2. Build images
docker build -t todo-frontend:latest -f dockerfiles/frontend.Dockerfile ../../phase-03-ai-chatbot/frontend
docker build -t todo-backend:latest -f dockerfiles/backend.Dockerfile ../../phase-03-ai-chatbot/backend

# 3. Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot

# 4. Verify deployment
kubectl get pods
kubectl get services

# 5. Access application
minikube service todo-frontend --url
```

## Documentation

All AI tool attempts and outcomes are documented in:
- `../docs/ai-devops-tools.md` - AI tool usage log
- `../docs/k8s-setup.md` - Cluster setup proof
- `../docs/deployment-guide.md` - Detailed deployment instructions

## Success Criteria

- ✅ Cluster running and healthy
- ✅ Docker images built with AI assistance documented
- ✅ Helm deployment successful
- ✅ All pods running
- ✅ Services accessible
- ✅ AI tool usage documented (even failures)

## Important Notes

1. **Backend Port**: Uses port 7860 (not 8000) - matches Phase III configuration
2. **Image Pull Policy**: Set to `Never` to use local Minikube images
3. **AI Tool Documentation**: Document ALL attempts, even if tools are unavailable
4. **Zero Cost**: Everything runs locally, no cloud resources required

## Troubleshooting

### Images not found
```bash
# Ensure Docker is using Minikube registry
eval $(minikube docker-env)

# Rebuild images
docker build -t todo-frontend:latest -f dockerfiles/frontend.Dockerfile ../../phase-03-ai-chatbot/frontend
```

### Pods not starting
```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Service not accessible
```bash
# Get service URL
minikube service todo-frontend --url

# Check service endpoints
kubectl get endpoints
```

## For Hackathon Judges

This deployment demonstrates:
1. **AI-Assisted Containerization**: Docker AI attempts documented
2. **AI-Powered Kubernetes Operations**: kubectl-ai and kagent usage
3. **Cloud-Native Architecture**: Microservices deployed on Kubernetes
4. **Zero-Cost Local Development**: Minikube-based deployment
5. **Reproducible Infrastructure**: Helm charts for declarative deployment

All AI tool attempts are documented in `../docs/ai-devops-tools.md`, including:
- Commands executed
- Outputs received
- Fallback strategies used
- Reasons for unavailability (if applicable)
