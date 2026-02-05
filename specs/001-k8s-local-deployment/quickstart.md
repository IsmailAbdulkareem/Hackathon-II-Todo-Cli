# Quickstart: Local Kubernetes Deployment

**Date**: 2026-01-31
**Purpose**: 12-step deployment workflow for Todo Chatbot on local Kubernetes (Minikube)
**Target Time**: < 15 minutes from prerequisites to running application

---

## Prerequisites

Before starting, ensure you have:

- ✅ Docker Desktop 4.53+ or Docker Engine installed and running
- ✅ Minikube v1.37+ installed
- ✅ kubectl v1.35+ installed
- ✅ Helm v4+ installed
- ✅ Phase III applications (frontend + backend) available in `phase-04-k8s-local/`
- ✅ Neon PostgreSQL database connection string
- ✅ Anthropic API key for AI chat functionality

**Verify Prerequisites**:
```bash
docker --version
minikube version
kubectl version --client
helm version
```

---

## Deployment Workflow

### Step 1: Build Docker Images

Build both frontend and backend Docker images locally.

```bash
# Navigate to project root
cd "D:\Projects\spec-driven-development-hacathon\Hackathon II - Todo Spec-Driven Development"

# Build frontend image
docker build -t todo-frontend:latest -f phase-04-k8s-local/frontend/Dockerfile phase-04-k8s-local/frontend

# Build backend image
docker build -t todo-backend:latest -f phase-04-k8s-local/backend/Dockerfile phase-04-k8s-local/backend

# Verify images
docker images | grep todo
```

**Expected Output**: Two images (todo-frontend:latest, todo-backend:latest) with sizes < 500MB and < 300MB respectively.

**Time**: ~3-5 minutes

---

### Step 2: Test Containers Locally

Verify containers run correctly before Kubernetes deployment.

```bash
# Test backend (requires DATABASE_URL and ANTHROPIC_API_KEY)
docker run -d --name test-backend \
  -p 8000:8000 \
  -e DATABASE_URL="your-neon-connection-string" \
  -e ANTHROPIC_API_KEY="your-api-key" \
  todo-backend:latest

# Check backend health
curl http://localhost:8000/

# Test frontend
docker run -d --name test-frontend \
  -p 3000:80 \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  todo-frontend:latest

# Check frontend health
curl http://localhost:3000/

# Cleanup test containers
docker stop test-backend test-frontend
docker rm test-backend test-frontend
```

**Expected Output**: Both health checks return 200 OK.

**Time**: ~1 minute

---

### Step 3: Start Minikube Cluster

Initialize local Kubernetes cluster with required resources.

```bash
# Start Minikube with 4 CPUs and 6GB memory
minikube start --cpus=4 --memory=6144

# Verify cluster is running
kubectl get nodes

# Check cluster info
kubectl cluster-info
```

**Expected Output**: Minikube node shows "Ready" status.

**Time**: ~2-3 minutes

---

### Step 4: Load Images into Minikube

Transfer Docker images to Minikube's internal registry.

```bash
# Load frontend image
minikube image load todo-frontend:latest

# Load backend image
minikube image load todo-backend:latest

# Verify images are available
minikube image ls | grep todo
```

**Expected Output**: Both images listed in Minikube's image registry.

**Time**: ~1 minute

---

### Step 5: Create Kubernetes Secrets

Store sensitive credentials in Kubernetes Secrets.

```bash
# Create backend secrets (replace with actual values)
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@host:port/database?sslmode=require" \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-..."

# Verify secret creation
kubectl get secrets
kubectl describe secret todo-backend-secrets
```

**Expected Output**: Secret created with 2 data keys (DATABASE_URL, ANTHROPIC_API_KEY).

**Security Note**: Secret values should NOT be visible in `kubectl describe` output.

**Time**: ~30 seconds

---

### Step 6: Deploy Backend with Helm

Deploy backend application using Helm chart.

```bash
# Navigate to Helm charts directory
cd phase-04-k8s-local/k8s/helm

# Install backend chart
helm install todo-backend ./todo-backend

# Verify deployment
kubectl get pods -l app=todo-backend
kubectl get svc todo-backend
```

**Expected Output**: Backend pod reaches "Running" status within 2 minutes.

**Time**: ~2 minutes

---

### Step 7: Deploy Frontend with Helm

Deploy frontend application using Helm chart.

```bash
# Install frontend chart
helm install todo-frontend ./todo-frontend

# Verify deployment
kubectl get pods -l app=todo-frontend
kubectl get svc todo-frontend
```

**Expected Output**: Frontend pods (2 replicas) reach "Running" status within 2 minutes.

**Time**: ~2 minutes

---

### Step 8: Verify Pod Health

Ensure all pods are healthy and passing health checks.

```bash
# Check all pods
kubectl get pods

# Check pod details
kubectl describe pod -l app=todo-backend
kubectl describe pod -l app=todo-frontend

# Check pod logs
kubectl logs -l app=todo-backend --tail=50
kubectl logs -l app=todo-frontend --tail=50
```

**Expected Output**: All pods show "Ready" status with passing liveness/readiness probes.

**Time**: ~1 minute

---

### Step 9: Verify Service Endpoints

Confirm Kubernetes services are properly configured.

```bash
# Check services
kubectl get svc

# Check service endpoints
kubectl get endpoints

# Verify backend service (ClusterIP)
kubectl describe svc todo-backend

# Verify frontend service (NodePort)
kubectl describe svc todo-frontend
```

**Expected Output**:
- Backend service has ClusterIP with port 8000
- Frontend service has NodePort with port 3000
- Endpoints show pod IPs

**Time**: ~30 seconds

---

### Step 10: Access Application

Get frontend URL and access the application.

```bash
# Get frontend service URL
minikube service todo-frontend --url

# Open in browser (or use curl)
# Example: http://192.168.49.2:30080
```

**Expected Output**: Frontend URL displayed. Opening in browser shows Todo Chatbot interface.

**Time**: ~30 seconds

---

### Step 11: Test End-to-End Flow

Validate complete user workflow through Kubernetes.

**Manual Test**:
1. Open frontend URL in browser
2. Navigate to chat interface
3. Send a test message (e.g., "Create a todo: Buy groceries")
4. Verify AI response is received within 3 seconds
5. Check that todo is created and visible

**CLI Verification**:
```bash
# Check backend logs for request processing
kubectl logs -l app=todo-backend --tail=20

# Verify database connection
kubectl logs -l app=todo-backend | grep -i database

# Check frontend logs
kubectl logs -l app=todo-frontend --tail=20
```

**Expected Output**:
- AI response received within 3 seconds
- Backend logs show successful request processing
- Database connection confirmed

**Time**: ~2 minutes

---

### Step 12: Verify Configuration

Confirm ConfigMaps and Secrets are properly mounted.

```bash
# Get frontend pod name
FRONTEND_POD=$(kubectl get pods -l app=todo-frontend -o jsonpath='{.items[0].metadata.name}')

# Verify frontend ConfigMap
kubectl exec $FRONTEND_POD -- env | grep NEXT_PUBLIC_API_URL

# Get backend pod name
BACKEND_POD=$(kubectl get pods -l app=todo-backend -o jsonpath='{.items[0].metadata.name}')

# Verify backend Secret is mounted (should show secretKeyRef, not values)
kubectl describe pod $BACKEND_POD | grep -A 5 "Environment:"
```

**Expected Output**:
- Frontend shows `NEXT_PUBLIC_API_URL=http://todo-backend:8000`
- Backend shows environment variables from secretKeyRef (not plaintext values)

**Time**: ~1 minute

---

## Deployment Complete! 🎉

**Total Time**: ~12-15 minutes

Your Todo Chatbot is now running on local Kubernetes with:
- ✅ Frontend: 2 replicas, accessible via NodePort
- ✅ Backend: 1 replica, internal ClusterIP service
- ✅ Health monitoring with liveness/readiness probes
- ✅ Secure secret management
- ✅ Service discovery via Kubernetes DNS

---

## Common Operations

### Scale Replicas

```bash
# Scale frontend to 3 replicas
kubectl scale deployment todo-frontend --replicas=3

# Scale backend to 2 replicas
kubectl scale deployment todo-backend --replicas=2

# Verify scaling
kubectl get pods
```

### Update Configuration

```bash
# Edit frontend ConfigMap
kubectl edit configmap todo-frontend

# Restart frontend pods to pick up changes
kubectl rollout restart deployment todo-frontend

# Verify rollout
kubectl rollout status deployment todo-frontend
```

### View Logs

```bash
# Stream backend logs
kubectl logs -f -l app=todo-backend

# Stream frontend logs
kubectl logs -f -l app=todo-frontend

# View logs from all replicas
kubectl logs -l app=todo-frontend --all-containers=true
```

### Check Resource Usage

```bash
# View pod resource usage
kubectl top pods

# View node resource usage
kubectl top nodes
```

---

## Cleanup

When you're done testing, clean up all resources.

```bash
# Uninstall Helm releases
helm uninstall todo-frontend
helm uninstall todo-backend

# Delete secrets
kubectl delete secret todo-backend-secrets

# Verify cleanup
kubectl get all

# Stop Minikube
minikube stop

# (Optional) Delete Minikube cluster
minikube delete
```

**Time**: ~1 minute

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# Check image pull status
kubectl get events --sort-by='.lastTimestamp'
```

### Service Not Accessible

```bash
# Verify service endpoints
kubectl get endpoints

# Check service configuration
kubectl describe svc <service-name>

# Test service from within cluster
kubectl run test-pod --image=curlimages/curl --rm -it -- curl http://todo-backend:8000/
```

### Configuration Issues

```bash
# Verify ConfigMap
kubectl get configmap todo-frontend -o yaml

# Verify Secret exists (values should be base64 encoded)
kubectl get secret todo-backend-secrets -o yaml

# Check environment variables in pod
kubectl exec <pod-name> -- env
```

### Image Not Found

```bash
# Verify images in Minikube
minikube image ls | grep todo

# Reload images if needed
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

---

## Next Steps

- **AI Operations**: Explore kubectl-ai and kagent for natural language cluster management
- **Monitoring**: Set up Prometheus and Grafana for metrics
- **Logging**: Configure centralized logging with EFK stack
- **Production**: Migrate to cloud Kubernetes (EKS, GKE, AKS) for production deployment

---

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- Project Spec: [spec.md](./spec.md)
- Implementation Plan: [plan.md](./plan.md)
- Helm Chart Structure: [contracts/helm-chart-structure.md](./contracts/helm-chart-structure.md)
