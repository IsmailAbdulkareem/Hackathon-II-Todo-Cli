# Quickstart: Local Kubernetes Deployment for Todo Chatbot

**Feature**: 001-k8s-local-deployment
**Date**: 2026-01-28
**Purpose**: Step-by-step guide for deploying Todo Chatbot to local Kubernetes cluster

## Prerequisites

### Required Tools

1. **Docker Desktop 4.53+**
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version`

2. **Minikube**
   - Install: https://minikube.sigs.k8s.io/docs/start/
   - Verify: `minikube version`

3. **kubectl**
   - Usually included with Docker Desktop or Minikube
   - Verify: `kubectl version --client`

4. **Helm 3+**
   - Install: https://helm.sh/docs/intro/install/
   - Verify: `helm version`

### AI DevOps Tools (Attempt Installation)

5. **Docker AI (Gordon)** - Optional but recommended
   - Included in Docker Desktop with subscription
   - Verify: `docker ai --help`
   - If unavailable: Document error and use Claude Code fallback

6. **kubectl-ai** - Optional but recommended
   - Install krew: https://krew.sigs.k8s.io/docs/user-guide/setup/install/
   - Install plugin: `kubectl krew install ai`
   - Verify: `kubectl ai --help`
   - If unavailable: Document error and use standard kubectl

7. **kagent** - Optional, minimal demonstration
   - Research installation method (may require API keys)
   - Document setup process and any blockers
   - If unavailable: Document attempt and use kubectl-ai or standard tools

### System Requirements

- **RAM**: Minimum 4GB available (8GB recommended)
- **CPU**: Minimum 2 cores available
- **Disk**: 20GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux

## Step 1: Start Minikube Cluster

### 1.1 Start Cluster with Resource Allocation

```bash
# Start Minikube with appropriate resources
minikube start --cpus=2 --memory=3072 --driver=docker

# Expected output:
# 😄  minikube v1.x.x on [Your OS]
# ✨  Using the docker driver based on user configuration
# 🎉  minikube 1.x.x is available! Download it: https://github.com/kubernetes/minikube/releases/tag/v1.x.x
# 💿  Downloading Kubernetes v1.x.x preload ...
# 🔥  Creating docker container (CPUs=2, Memory=3072MB) ...
# 🐳  Preparing Kubernetes v1.x.x on Docker 24.x.x ...
# 🔎  Verifying Kubernetes components...
# 🌟  Enabled addons: storage-provisioner, default-storageclass
# 🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

### 1.2 Verify Cluster Health

**Using kubectl-ai (if available):**
```bash
kubectl ai "show me cluster information and verify all nodes are ready"
```

**Using standard kubectl (fallback):**
```bash
# Check cluster info
kubectl cluster-info

# Check node status
kubectl get nodes

# Expected output:
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   1m    v1.x.x

# Check system pods
kubectl get pods -n kube-system
```

### 1.3 Configure Docker Environment

```bash
# Point your shell to Minikube's Docker daemon
# This allows images built locally to be used directly by Minikube
eval $(minikube docker-env)

# Verify Docker is pointing to Minikube
docker ps
# You should see Minikube's Kubernetes containers
```

**Note**: Run `eval $(minikube docker-env)` in each new terminal session where you build images.

## Step 2: Build Container Images

### 2.1 Create Dockerfiles with AI Assistance

**Using Docker AI (Gordon) - Attempt First:**

```bash
# Navigate to frontend directory
cd phase-02-fullstack-web/frontend  # Adjust path as needed

# Use Docker AI to generate Dockerfile
docker ai "Create an optimized production Dockerfile for a Next.js application"

# Review and save the generated Dockerfile
# Document the AI-generated content and any modifications made
```

**Using Claude Code (Fallback):**

If Docker AI is unavailable, use Claude Code to generate Dockerfiles with explanations:

**Frontend Dockerfile** (k8s/dockerfiles/frontend.Dockerfile):
```dockerfile
# Multi-stage build for Next.js application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Build Next.js application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Set environment to production
ENV NODE_ENV=production

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
```

**Backend Dockerfile** (k8s/dockerfiles/backend.Dockerfile):
```dockerfile
# Python backend Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "main.py"]  # Adjust based on actual backend entry point
```

**Documentation**: Create `docs/ai-devops-tools.md` documenting:
- Which AI tool was used (Docker AI or Claude Code)
- The prompts/instructions provided
- The generated output
- Any modifications made and why

### 2.2 Build Images

```bash
# Ensure Docker is pointing to Minikube
eval $(minikube docker-env)

# Build frontend image
docker build -t todo-frontend:latest -f k8s/dockerfiles/frontend.Dockerfile ./phase-02-fullstack-web/frontend

# Build backend image
docker build -t todo-backend:latest -f k8s/dockerfiles/backend.Dockerfile ./phase-02-fullstack-web/backend

# Verify images are available
docker images | grep todo
```

**Expected output:**
```
todo-frontend   latest   abc123def456   1 minute ago   150MB
todo-backend    latest   def456ghi789   1 minute ago   200MB
```

## Step 3: Deploy with Helm

### 3.1 Create Helm Chart Structure

```bash
# Create Helm chart directory
mkdir -p k8s/helm/todo-chatbot/templates

# Chart.yaml will be created in implementation phase
# values.yaml will be created in implementation phase
# Template files will be created in implementation phase
```

### 3.2 Install Helm Release

**Using kubectl-ai for verification (if available):**
```bash
# Install the Helm chart
helm install todo-chatbot ./k8s/helm/todo-chatbot

# Use kubectl-ai to verify deployment
kubectl ai "show me all resources created by the todo-chatbot release"
```

**Using standard commands (fallback):**
```bash
# Install the Helm chart
helm install todo-chatbot ./k8s/helm/todo-chatbot

# Expected output:
# NAME: todo-chatbot
# LAST DEPLOYED: [timestamp]
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1

# Verify deployment
kubectl get all
```

### 3.3 Wait for Pods to be Ready

```bash
# Watch pod status
kubectl get pods -w

# Expected output (after ~1-2 minutes):
# NAME                                READY   STATUS    RESTARTS   AGE
# todo-frontend-xxxxxxxxxx-xxxxx      1/1     Running   0          1m
# todo-backend-xxxxxxxxxx-xxxxx       1/1     Running   0          1m

# Press Ctrl+C to stop watching
```

## Step 4: Access the Application

### 4.1 Get Frontend URL

```bash
# Get the frontend service URL
minikube service todo-frontend --url

# Expected output:
# http://192.168.49.2:30080
```

### 4.2 Open in Browser

```bash
# Open the URL in your default browser
minikube service todo-frontend

# Or manually open the URL from step 4.1 in your browser
```

### 4.3 Verify Frontend-Backend Communication

1. Open the application in your browser
2. Try creating a todo item
3. Verify the todo appears in the list
4. Check backend logs to confirm API requests:

```bash
# Get backend pod name
kubectl get pods | grep backend

# View backend logs
kubectl logs <backend-pod-name>
```

## Step 5: Test Scaling (Optional)

### 5.1 Scale Frontend

**Using kubectl-ai (if available):**
```bash
kubectl ai "scale the frontend deployment to 3 replicas"
```

**Using standard kubectl (fallback):**
```bash
# Scale frontend to 3 replicas
kubectl scale deployment todo-frontend --replicas=3

# Verify scaling
kubectl get pods | grep frontend

# Expected output:
# todo-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          5m
# todo-frontend-xxxxxxxxxx-yyyyy   1/1     Running   0          10s
# todo-frontend-xxxxxxxxxx-zzzzz   1/1     Running   0          10s
```

### 5.2 Verify Load Distribution

```bash
# Watch pod logs to see which pods handle requests
kubectl logs -f deployment/todo-frontend
```

## Step 6: Demonstrate kagent (Minimal)

### 6.1 Attempt kagent Setup

```bash
# Research and document kagent installation
# This may require:
# - API keys or cloud service setup
# - Specific Kubernetes versions
# - Additional dependencies

# Document the setup process in docs/ai-devops-tools.md
```

### 6.2 Minimal Demonstration

If kagent is available, demonstrate one operation:
```bash
# Example: Use kagent for deployment health check
kagent check deployment todo-frontend

# Or: Use kagent for resource optimization
kagent optimize resources
```

If kagent is unavailable:
```bash
# Document the attempt in docs/ai-devops-tools.md:
# - Installation steps attempted
# - Error messages encountered
# - Reason for unavailability (region, tier, platform)
# - Fallback approach used
```

## Step 7: Cleanup

### 7.1 Uninstall Helm Release

```bash
# Uninstall the Helm release
helm uninstall todo-chatbot

# Verify resources are removed
kubectl get all
```

### 7.2 Stop Minikube

```bash
# Stop the Minikube cluster
minikube stop

# Optional: Delete the cluster entirely
minikube delete
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# Common issues:
# - Image pull errors: Verify imagePullPolicy is set to Never
# - Resource constraints: Check if cluster has sufficient resources
# - Application errors: Check logs for startup issues
```

### Service Not Accessible

```bash
# Verify service exists
kubectl get services

# Check service endpoints
kubectl get endpoints

# Verify Minikube tunnel (if using LoadBalancer)
minikube tunnel

# Check NodePort assignment
kubectl describe service todo-frontend
```

### Docker Environment Issues

```bash
# Reset Docker environment
eval $(minikube docker-env -u)

# Re-configure for Minikube
eval $(minikube docker-env)

# Rebuild images if needed
```

### Resource Constraints

```bash
# Check cluster resource usage
kubectl top nodes
kubectl top pods

# Increase Minikube resources (requires restart)
minikube stop
minikube start --cpus=4 --memory=4096
```

## Success Criteria Verification

- [ ] SC-001: Cluster setup completed in under 10 minutes
- [ ] SC-002: Container images built successfully with AI assistance (or documented fallback)
- [ ] SC-003: Helm deployment completed and all services running within 5 minutes
- [ ] SC-004: Application accessible via local URL and responds to requests
- [ ] SC-005: Services scaled successfully within 2 minutes
- [ ] SC-006: Deployment steps repeatable with identical results
- [ ] SC-007: Logs and diagnostics accessible for troubleshooting
- [ ] SC-008: Zero-cost deployment (no cloud resources used)
- [ ] SC-009: AI DevOps tool usage demonstrated with documented attempts and outcomes

## Next Steps

After successful deployment:
1. Document AI DevOps tool usage in `docs/ai-devops-tools.md`
2. Create deployment automation scripts (optional)
3. Prepare for Phase V: Production cloud deployment
4. Review and refine Helm chart configurations
5. Consider adding monitoring and observability tools

## References

- Minikube Documentation: https://minikube.sigs.k8s.io/docs/
- Kubernetes Documentation: https://kubernetes.io/docs/
- Helm Documentation: https://helm.sh/docs/
- Docker Documentation: https://docs.docker.com/
- kubectl-ai: https://github.com/sozercan/kubectl-ai
