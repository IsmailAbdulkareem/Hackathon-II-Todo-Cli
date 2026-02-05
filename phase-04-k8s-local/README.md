# Phase IV: Local Kubernetes Deployment

**Status:** Complete ✅
**Points:** 250
**Tech Stack:** Docker, Minikube, Helm, kubectl
**Completed:** Feb 1, 2026

## Overview

Phase IV containerizes the Todo Chatbot application and deploys it locally using Kubernetes with Helm charts, demonstrating cloud-native practices and operational readiness.

## What Was Implemented

### Containerization
- ✅ **Multi-stage Docker builds** for frontend (Next.js) and backend (FastAPI)
- ✅ **Health checks** configured for both applications
- ✅ **Non-root users** for security
- ✅ **Secret management** with Kubernetes Secrets
- ✅ **Image optimization** (frontend: 1.01GB, backend: 390MB)

### Kubernetes Deployment
- ✅ **Minikube** local cluster (4 CPUs, 3.5GB memory)
- ✅ **Helm charts** for declarative deployment (separate charts for frontend and backend)
- ✅ **ConfigMaps** for non-sensitive configuration
- ✅ **Secrets** for sensitive data (database credentials, API keys)
- ✅ **Services** (NodePort for frontend, ClusterIP for backend)
- ✅ **Health probes** (liveness and readiness)

### AI Operations Documentation
- ✅ **Docker AI** usage guide for Dockerfile generation
- ✅ **kubectl-ai** documentation for natural language Kubernetes operations
- ✅ **kagent** documentation for cluster health analysis
- ✅ **Manual kubectl fallbacks** for all AI operations (FR-018 compliance)

## Prerequisites

### Required Tools

```bash
# Docker Desktop 4.53+ (includes Docker Engine)
# Download from: https://docs.docker.com/get-docker/

# Minikube v1.37.0+
# Windows: choco install minikube
# macOS: brew install minikube
# Linux: curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# kubectl v1.35.0+
# Windows: choco install kubernetes-cli
# macOS: brew install kubectl
# Linux: curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Helm 3+
# Windows: choco install kubernetes-helm
# macOS: brew install helm
# Linux: curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Verify Installation

```bash
docker --version          # Docker version 20.10+
minikube version         # minikube version: v1.37.0
kubectl version --client # Client Version: v1.35.0
helm version            # version.BuildInfo{Version:"v3.x.x"}
```

## Quick Start

### 1. Build Docker Images

```bash
# Navigate to project root
cd "D:\Projects\spec-driven-development-hacathon\Hackathon II - Todo Spec-Driven Development"

# Build frontend image
docker build -t todo-frontend:latest -f phase-04-k8s-local/frontend/Dockerfile phase-03-ai-chatbot/frontend

# Build backend image
docker build -t todo-backend:latest -f phase-04-k8s-local/backend/Dockerfile phase-03-ai-chatbot/backend

# Verify images
docker images | grep todo
```

### 2. Start Minikube Cluster

```bash
# Start Minikube with appropriate resources
minikube start --cpus=4 --memory=3500

# Verify cluster is running
minikube status
kubectl cluster-info
kubectl get nodes
```

### 3. Load Images into Minikube

```bash
# Load images into Minikube's internal registry
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Verify images are loaded
minikube image ls | grep todo
```

### 4. Create Kubernetes Secrets

```bash
# Create secret with your actual credentials
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@host:port/database?sslmode=require" \
  --from-literal=BETTER_AUTH_SECRET="your-auth-secret-min-32-chars" \
  --from-literal=OPENAI_API_KEY="sk-your-openai-key-here"\
  --from-literal=OPENAI_API_KEY="sk-your-openai-key-here"\
  --from-literal=CORS_ORIGINS="http://localhost:3000,https://ismail233290-todo-app.hf.space,https://todohackathonphase3.vercel.ap"

# Verify secret created
kubectl get secrets
```

### 5. Deploy with Helm

```bash
# Deploy backend first (provides API service)
helm install todo-backend ./phase-04-k8s-local/k8s/helm/todo-backend

# Deploy frontend
helm install todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend

# Check deployment status
kubectl get pods
kubectl get services
```

### 6. Access Application

```bash
# Get frontend URL
minikube service todo-frontend --url

# Or use port-forward
kubectl port-forward svc/todo-frontend 8080:3000

# Access at: http://localhost:8080
```

## Project Structure

```
phase-04-k8s-local/
├── frontend/
│   ├── Dockerfile              # Frontend container (Next.js)
│   └── .dockerignore          # Files to exclude from image
├── backend/
│   ├── Dockerfile              # Backend container (FastAPI)
│   └── .dockerignore          # Files to exclude from image
├── k8s/
│   ├── helm/
│   │   ├── todo-frontend/      # Frontend Helm chart
│   │   │   ├── Chart.yaml      # Chart metadata
│   │   │   ├── values.yaml     # Default configuration
│   │   │   ├── .helmignore     # Files to exclude
│   │   │   └── templates/
│   │   │       ├── deployment.yaml    # Frontend deployment
│   │   │       ├── service.yaml       # Frontend service (NodePort)
│   │   │       ├── configmap.yaml     # Frontend config
│   │   │       └── _helpers.tpl       # Template helpers
│   │   └── todo-backend/       # Backend Helm chart
│   │       ├── Chart.yaml      # Chart metadata
│   │       ├── values.yaml     # Default configuration
│   │       ├── .helmignore     # Files to exclude
│   │       └── templates/
│   │           ├── deployment.yaml    # Backend deployment
│   │           ├── service.yaml       # Backend service (ClusterIP)
│   │           ├── configmap.yaml     # Backend config
│   │           ├── secret.yaml        # Secret documentation
│   │           └── _helpers.tpl       # Template helpers
│   └── docs/
│       ├── docker-ai-usage.md         # Docker AI guide
│       ├── kubectl-ai-usage.md        # kubectl-ai guide
│       ├── kagent-usage.md            # kagent guide
│       └── manual-fallbacks.md        # Manual kubectl commands
└── README.md                   # This file
```

## Kubernetes Resources

### Deployments

**Frontend (todo-frontend)**:
- Replicas: 2
- Image: todo-frontend:latest
- Resources: 250m CPU / 512Mi memory per pod
- Health Probes: Liveness and readiness on port 3000
- Environment: NEXT_PUBLIC_API_URL (from ConfigMap)

**Backend (todo-backend)**:
- Replicas: 1
- Image: todo-backend:latest
- Resources: 500m CPU / 1Gi memory per pod
- Health Probes: Liveness and readiness on port 8000
- Environment: DATABASE_URL, ANTHROPIC_API_KEY, BETTER_AUTH_SECRET, OPENAI_API_KEY (from Secret)

### Services

**Frontend Service (todo-frontend)**:
- Type: NodePort
- Port: 3000
- NodePort: 30080
- Access: External via Minikube IP or port-forward

**Backend Service (todo-backend)**:
- Type: ClusterIP
- Port: 8000
- Access: Internal only (via Kubernetes DNS: http://todo-backend:8000)

### Configuration

**Frontend ConfigMap (todo-frontend-config)**:
- API_URL: http://todo-backend:8000

**Backend ConfigMap (todo-backend-config)**:
- CORS_ORIGINS: *
- LOG_LEVEL: INFO

**Backend Secret (todo-backend-secrets)**:
- DATABASE_URL: PostgreSQL connection string
- ANTHROPIC_API_KEY: Claude API key
- BETTER_AUTH_SECRET: Authentication secret
- OPENAI_API_KEY: OpenAI API key

## Common Operations

### Scaling

```bash
# Scale frontend to 3 replicas
kubectl scale deployment todo-frontend --replicas=3

# Verify scaling
kubectl get deployment todo-frontend
kubectl get pods -l app=todo-frontend
```

### Updating Configuration

```bash
# Update ConfigMap
kubectl edit configmap todo-frontend-config

# Restart pods to pick up changes
kubectl rollout restart deployment/todo-frontend

# Verify changes
kubectl exec <pod-name> -- env | grep API_URL
```

### Updating Secrets

```bash
# Delete and recreate secret
kubectl delete secret todo-backend-secrets
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="new-value" \
  --from-literal=ANTHROPIC_API_KEY="new-value" \
  --from-literal=BETTER_AUTH_SECRET="new-value" \
  --from-literal=OPENAI_API_KEY="new-value"

# Restart pods
kubectl rollout restart deployment/todo-backend
```

### Viewing Logs

```bash
# Frontend logs
kubectl logs -l app=todo-frontend --tail=50

# Backend logs
kubectl logs -l app=todo-backend --tail=50

# Follow logs in real-time
kubectl logs -l app=todo-backend -f
```

### Health Checks

```bash
# Check pod status
kubectl get pods

# Detailed pod information
kubectl describe pod <pod-name>

# Check service endpoints
kubectl get endpoints

# Resource usage (requires metrics-server)
kubectl top pods
kubectl top nodes
```

## Helm Operations

### List Releases

```bash
helm list
```

### Upgrade Release

```bash
# After modifying Helm chart
helm upgrade todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend
helm upgrade todo-backend ./phase-04-k8s-local/k8s/helm/todo-backend
```

### Rollback Release

```bash
# View history
helm history todo-frontend

# Rollback to previous version
helm rollback todo-frontend

# Rollback to specific revision
helm rollback todo-frontend 1
```

### Uninstall Release

```bash
helm uninstall todo-frontend
helm uninstall todo-backend
```

## AI-Assisted Operations

### Documentation Available

We've documented three AI tools for Kubernetes operations:

1. **Docker AI** (`k8s/docs/docker-ai-usage.md`): Dockerfile generation and optimization
2. **kubectl-ai** (`k8s/docs/kubectl-ai-usage.md`): Natural language Kubernetes operations
3. **kagent** (`k8s/docs/kagent-usage.md`): Cluster health analysis and insights

### Manual Fallbacks

All AI operations have manual kubectl equivalents documented in `k8s/docs/manual-fallbacks.md` (FR-018 compliance).

**Example Operations**:

```bash
# Scaling (kubectl-ai: "scale the frontend to 3 replicas")
kubectl scale deployment todo-frontend --replicas=3

# Health Check (kubectl-ai: "check the health of all pods")
kubectl get pods --all-namespaces

# Troubleshooting (kubectl-ai: "explain why the backend pod is failing")
kubectl describe pod <pod-name>
kubectl logs <pod-name> --tail=50
```

## Troubleshooting

### Common Issues

**Backend Pod Not Ready**:
```bash
# Check pod status
kubectl get pods -l app=todo-backend

# Check logs
kubectl logs -l app=todo-backend --tail=50

# Check events
kubectl describe pod <backend-pod-name>

# Common cause: Invalid database credentials
# Solution: Update secret with valid credentials
```

**Frontend Cannot Connect to Backend**:
```bash
# Verify backend service exists
kubectl get svc todo-backend

# Check backend endpoints
kubectl get endpoints todo-backend

# Verify ConfigMap has correct API URL
kubectl get configmap todo-frontend-config -o yaml
```

**Images Not Found**:
```bash
# Verify images are loaded in Minikube
minikube image ls | grep todo

# Reload if needed
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

**Port Forward Not Working**:
```bash
# Kill existing port-forward processes
# Windows: taskkill /F /IM kubectl.exe
# Linux/Mac: pkill -f "kubectl port-forward"

# Start new port-forward
kubectl port-forward svc/todo-frontend 8080:3000
```

### Systematic Troubleshooting

```bash
# 1. Check cluster health
kubectl cluster-info
kubectl get nodes

# 2. Check pod status
kubectl get pods

# 3. Check services
kubectl get svc
kubectl get endpoints

# 4. Check logs
kubectl logs <pod-name> --tail=100

# 5. Check events
kubectl get events --sort-by='.lastTimestamp'

# 6. Check resource usage
kubectl top pods  # Requires metrics-server
```

## Security Best Practices

### Implemented

- ✅ Non-root users in containers
- ✅ Secrets stored in Kubernetes Secrets (not in code)
- ✅ Resource limits set for all pods
- ✅ Health probes configured
- ✅ Secrets not exposed in pod descriptions (secretKeyRef only)

### Recommendations

- Use external secret management (e.g., HashiCorp Vault) for production
- Implement network policies to restrict pod-to-pod communication
- Enable Pod Security Standards
- Regular image scanning with Trivy or similar tools
- Implement RBAC for fine-grained access control

## Performance Tuning

### Current Configuration

**Frontend**:
- CPU: 250m (request/limit)
- Memory: 512Mi (request/limit)
- Actual Usage: ~18-20% of allocated resources
- Recommendation: Can reduce to 100m CPU / 256Mi memory

**Backend**:
- CPU: 500m (request/limit)
- Memory: 1Gi (request/limit)
- Actual Usage: Cannot measure (pod not ready with placeholder credentials)

### Optimization Opportunities

1. Reduce frontend resource limits (over-provisioned by 60%)
2. Implement Horizontal Pod Autoscaler (HPA) for automatic scaling
3. Add Pod Disruption Budget (PDB) for high availability
4. Optimize Docker images (currently exceed size targets)

## Cleanup

### Uninstall Applications

```bash
# Uninstall Helm releases
helm uninstall todo-frontend
helm uninstall todo-backend

# Delete secrets
kubectl delete secret todo-backend-secrets

# Verify cleanup
kubectl get all
```

### Stop Minikube

```bash
# Stop cluster (preserves state)
minikube stop

# Delete cluster (removes all data)
minikube delete
```

## Success Metrics

### Achieved

- ✅ **SC-001**: Docker images build in <5 minutes
- ✅ **SC-002**: Minikube cluster starts in <3 minutes
- ✅ **SC-004**: Scaling operations complete in <1 minute
- ✅ **SC-006**: Deployment documentation enables deployment in <15 minutes
- ✅ **FR-018**: All AI operations have manual kubectl fallbacks

### Partially Achieved

- ⚠️ **SC-003**: End-to-end response time <3 seconds (cannot test without valid credentials)
- ⚠️ **SC-005**: Configuration updates apply in <2 minutes (tested, functional)
- ⚠️ **SC-007**: AI tools provide insights in <10 seconds (documented, not installed)

## Next Steps

### To Complete Full Functionality

1. Update Kubernetes Secret with valid credentials
2. Verify backend becomes healthy
3. Test end-to-end user flow
4. Optimize Docker image sizes
5. Implement Horizontal Pod Autoscaler

### Future Enhancements (Phase V)

- Cloud deployment (DigitalOcean DOKS)
- Production-grade monitoring (Prometheus + Grafana)
- Distributed tracing (Jaeger)
- GitOps with ArgoCD
- High availability setup

## Documentation

- **Specifications**: `specs/001-k8s-local-deployment/`
- **Docker AI Guide**: `k8s/docs/docker-ai-usage.md`
- **kubectl-ai Guide**: `k8s/docs/kubectl-ai-usage.md`
- **kagent Guide**: `k8s/docs/kagent-usage.md`
- **Manual Fallbacks**: `k8s/docs/manual-fallbacks.md`
- **Tasks**: `specs/001-k8s-local-deployment/tasks.md`

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review documentation in `k8s/docs/`
3. Check task completion status in `specs/001-k8s-local-deployment/tasks.md`
4. Review Prompt History Records in `history/prompts/001-k8s-local-deployment/`

---

**Last Updated**: 2026-02-01
**Status**: MVP Complete - Infrastructure functional, awaiting valid credentials for full end-to-end testing
