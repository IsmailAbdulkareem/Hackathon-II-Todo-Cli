# Troubleshooting Guide

**Purpose**: Common issues and solutions for Kubernetes deployment

**Last Updated**: 2026-02-01

---

## Quick Diagnosis

### Is the cluster running?

```bash
minikube status
kubectl cluster-info
```

**If not**: `minikube start --cpus=4 --memory=3500`

### Are pods running?

```bash
kubectl get pods
```

**Expected**: All pods showing `Running` and `Ready`

### Are services accessible?

```bash
kubectl get svc
kubectl get endpoints
```

**Expected**: Services have endpoints matching pod count

---

## Common Issues

### 1. Backend Pod in CrashLoopBackOff

**Symptoms**:
```
NAME                            READY   STATUS             RESTARTS
todo-backend-xxx                0/1     CrashLoopBackOff   5
```

**Diagnosis**:
```bash
kubectl logs todo-backend-xxx --tail=50
kubectl describe pod todo-backend-xxx
```

**Common Causes**:

**A. Database Connection Failure**
```
Error: could not connect to server
FATAL: password authentication failed
```

**Solution**:
```bash
# Update secret with valid credentials
kubectl delete secret todo-backend-secrets
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host:port/db?sslmode=require" \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-..." \
  --from-literal=BETTER_AUTH_SECRET="min-32-chars" \
  --from-literal=OPENAI_API_KEY="sk-..."

# Restart deployment
kubectl rollout restart deployment/todo-backend

# Monitor recovery
kubectl get pods -l app=todo-backend -w
```

**B. Missing Environment Variables**
```
ValidationError: Field required
```

**Solution**:
```bash
# Check which variables are missing
kubectl logs todo-backend-xxx | grep -i "field required\|missing"

# Update Helm chart to include missing variables
# Edit: phase-04-k8s-local/k8s/helm/todo-backend/templates/deployment.yaml
# Add missing env vars

# Upgrade Helm release
helm upgrade todo-backend ./phase-04-k8s-local/k8s/helm/todo-backend
```

**C. Application Code Error**
```
ImportError: No module named 'xyz'
SyntaxError: invalid syntax
```

**Solution**:
```bash
# Rebuild Docker image with fixes
docker build -t todo-backend:latest -f phase-04-k8s-local/backend/Dockerfile phase-03-ai-chatbot/backend

# Load into Minikube
minikube image load todo-backend:latest

# Restart deployment
kubectl rollout restart deployment/todo-backend
```

---

### 2. Frontend Pod Not Ready

**Symptoms**:
```
NAME                             READY   STATUS    RESTARTS
todo-frontend-xxx                0/1     Running   0
```

**Diagnosis**:
```bash
kubectl logs todo-frontend-xxx --tail=50
kubectl describe pod todo-frontend-xxx
```

**Common Causes**:

**A. Health Check Failing**
```
Readiness probe failed: Get "http://10.244.0.7:3000/": dial tcp: connection refused
```

**Solution**:
```bash
# Check if application is listening on correct port
kubectl exec todo-frontend-xxx -- netstat -tlnp

# If port mismatch, update Helm values
# Edit: phase-04-k8s-local/k8s/helm/todo-frontend/values.yaml
# Ensure service.targetPort matches container port

# Upgrade Helm release
helm upgrade todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend
```

**B. Application Startup Slow**
```
Readiness probe failed: Get "http://10.244.0.7:3000/": context deadline exceeded
```

**Solution**:
```bash
# Increase initialDelaySeconds in readiness probe
# Edit: phase-04-k8s-local/k8s/helm/todo-frontend/values.yaml
# Change: readinessProbe.initialDelaySeconds: 10 (from 5)

# Upgrade Helm release
helm upgrade todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend
```

---

### 3. ImagePullBackOff

**Symptoms**:
```
NAME                             READY   STATUS             RESTARTS
todo-frontend-xxx                0/1     ImagePullBackOff   0
```

**Diagnosis**:
```bash
kubectl describe pod todo-frontend-xxx | grep -A 5 "Events:"
```

**Error Message**:
```
Failed to pull image "todo-frontend:latest": rpc error: code = Unknown desc = Error response from daemon: pull access denied
```

**Cause**: Image not loaded into Minikube

**Solution**:
```bash
# Verify image exists locally
docker images | grep todo-frontend

# If not, build it
docker build -t todo-frontend:latest -f phase-04-k8s-local/frontend/Dockerfile phase-02-fullstack-web/frontend

# Load into Minikube
minikube image load todo-frontend:latest

# Verify image in Minikube
minikube image ls | grep todo-frontend

# Delete pod to force recreation
kubectl delete pod todo-frontend-xxx
```

---

### 4. Service Not Accessible

**Symptoms**: Cannot access frontend via browser or curl

**Diagnosis**:
```bash
# Check service exists
kubectl get svc todo-frontend

# Check endpoints
kubectl get endpoints todo-frontend

# Check pod status
kubectl get pods -l app=todo-frontend
```

**Common Causes**:

**A. No Endpoints**
```
NAME            ENDPOINTS   AGE
todo-frontend   <none>      5m
```

**Cause**: Pods not ready (failing health checks)

**Solution**: Fix pod health issues (see sections 1 & 2)

**B. Port Forward Not Working**
```
error: unable to forward port because pod is not running
```

**Solution**:
```bash
# Kill existing port-forward processes
# Windows:
taskkill /F /IM kubectl.exe

# Linux/Mac:
pkill -f "kubectl port-forward"

# Start new port-forward
kubectl port-forward svc/todo-frontend 8080:3000
```

**C. NodePort Not Accessible**
```
curl: (7) Failed to connect to 192.168.49.2 port 30080: Connection refused
```

**Solution**:
```bash
# Verify Minikube IP
minikube ip

# Verify NodePort
kubectl get svc todo-frontend -o jsonpath='{.spec.ports[0].nodePort}'

# Use minikube service command
minikube service todo-frontend --url

# Or use port-forward instead
kubectl port-forward svc/todo-frontend 8080:3000
```

---

### 5. Helm Install/Upgrade Fails

**Symptoms**:
```
Error: INSTALLATION FAILED: unable to build kubernetes objects from release manifest
```

**Diagnosis**:
```bash
# Lint Helm chart
helm lint ./phase-04-k8s-local/k8s/helm/todo-frontend

# Dry run to see what would be created
helm install todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend --dry-run --debug
```

**Common Causes**:

**A. Invalid YAML Syntax**
```
Error: YAML parse error
```

**Solution**:
```bash
# Check YAML syntax
helm lint ./phase-04-k8s-local/k8s/helm/todo-frontend

# Fix syntax errors in templates
# Common issues: incorrect indentation, missing quotes
```

**B. Missing Values**
```
Error: template: todo-frontend/templates/deployment.yaml:10:20: executing "todo-frontend/templates/deployment.yaml" at <.Values.image.tag>: nil pointer evaluating interface {}.tag
```

**Solution**:
```bash
# Check values.yaml has all required values
cat phase-04-k8s-local/k8s/helm/todo-frontend/values.yaml

# Add missing values
# Edit: phase-04-k8s-local/k8s/helm/todo-frontend/values.yaml
```

**C. Release Already Exists**
```
Error: INSTALLATION FAILED: cannot re-use a name that is still in use
```

**Solution**:
```bash
# Use upgrade instead of install
helm upgrade todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend

# Or uninstall first
helm uninstall todo-frontend
helm install todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend
```

---

### 6. Minikube Won't Start

**Symptoms**:
```
X Exiting due to MK_USAGE: Docker Desktop has only 3861MB memory but you specified 6144MB
```

**Solution**:
```bash
# Reduce memory allocation
minikube start --cpus=4 --memory=3500

# Or increase Docker Desktop memory
# Docker Desktop → Settings → Resources → Memory
```

**Symptoms**:
```
X Exiting due to GUEST_DRIVER_MISMATCH: The existing "minikube" cluster was created using the "docker" driver, which is incompatible with requested "hyperv" driver.
```

**Solution**:
```bash
# Delete existing cluster
minikube delete

# Start with correct driver
minikube start --cpus=4 --memory=3500 --driver=docker
```

---

### 7. Configuration Not Applied

**Symptoms**: Changed ConfigMap but pods still using old values

**Cause**: Pods don't automatically restart when ConfigMap changes

**Solution**:
```bash
# Restart deployment to pick up changes
kubectl rollout restart deployment/todo-frontend

# Monitor restart
kubectl rollout status deployment/todo-frontend

# Verify new values
kubectl exec <pod-name> -- env | grep <CONFIG_KEY>
```

---

### 8. Secret Not Found

**Symptoms**:
```
Error: secret "todo-backend-secrets" not found
```

**Solution**:
```bash
# Create secret
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-..." \
  --from-literal=BETTER_AUTH_SECRET="..." \
  --from-literal=OPENAI_API_KEY="sk-..."

# Verify secret created
kubectl get secret todo-backend-secrets

# Restart deployment
kubectl rollout restart deployment/todo-backend
```

---

### 9. High Resource Usage

**Symptoms**: Pods using excessive CPU or memory

**Diagnosis**:
```bash
# Check resource usage
kubectl top pods

# Check resource limits
kubectl describe pod <pod-name> | grep -A 10 "Limits:"

# Check for OOM kills
kubectl get events | grep -i "oom\|killed"
```

**Solution**:
```bash
# Increase resource limits
# Edit: phase-04-k8s-local/k8s/helm/todo-frontend/values.yaml
# Increase: resources.limits.memory

# Upgrade Helm release
helm upgrade todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend

# Or scale horizontally
kubectl scale deployment todo-frontend --replicas=3
```

---

### 10. Logs Not Showing

**Symptoms**: `kubectl logs` returns empty or no output

**Diagnosis**:
```bash
# Check pod status
kubectl get pod <pod-name>

# Check if container started
kubectl describe pod <pod-name> | grep -A 5 "State:"
```

**Common Causes**:

**A. Pod Not Started Yet**
```
State: Waiting
Reason: ContainerCreating
```

**Solution**: Wait for pod to start, then check logs

**B. Application Not Logging to stdout**

**Solution**: Configure application to log to stdout/stderr

**C. Pod Restarted**

**Solution**: Check previous logs
```bash
kubectl logs <pod-name> --previous
```

---

## Systematic Troubleshooting Process

### Step 1: Identify the Problem

```bash
# Check overall status
kubectl get all

# Check events
kubectl get events --sort-by='.lastTimestamp' | tail -20

# Identify failing component
kubectl get pods | grep -v "Running\|Completed"
```

### Step 2: Gather Information

```bash
# Describe the failing resource
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name> --tail=100

# Check previous logs if restarted
kubectl logs <pod-name> --previous

# Check resource usage
kubectl top pod <pod-name>
```

### Step 3: Analyze Root Cause

Common patterns:
- **ImagePullBackOff**: Image not available
- **CrashLoopBackOff**: Application failing to start
- **Pending**: Insufficient resources
- **Error**: Configuration issue

### Step 4: Apply Fix

Based on root cause:
- Update configuration
- Fix application code
- Adjust resource limits
- Load missing images

### Step 5: Verify Fix

```bash
# Check pod status
kubectl get pods

# Check logs
kubectl logs <pod-name> --tail=20

# Test functionality
# Access application and verify it works
```

---

## Emergency Recovery

### Complete Cluster Reset

**When**: Cluster in unrecoverable state

**Procedure**:
```bash
# 1. Backup current state
kubectl get all -o yaml > backup/all-resources.yaml
helm get values todo-frontend > backup/frontend-values.yaml
helm get values todo-backend > backup/backend-values.yaml

# 2. Delete cluster
minikube delete

# 3. Start fresh cluster
minikube start --cpus=4 --memory=3500

# 4. Load images
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# 5. Recreate secret
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="..." \
  --from-literal=ANTHROPIC_API_KEY="..." \
  --from-literal=BETTER_AUTH_SECRET="..." \
  --from-literal=OPENAI_API_KEY="..."

# 6. Redeploy applications
helm install todo-backend ./phase-04-k8s-local/k8s/helm/todo-backend
helm install todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend

# 7. Verify deployment
kubectl get pods
kubectl get svc
```

---

## Getting Help

### Documentation

- **README**: `phase-04-k8s-local/README.md`
- **Operations Runbook**: `phase-04-k8s-local/k8s/docs/operations-runbook.md`
- **Manual Fallbacks**: `phase-04-k8s-local/k8s/docs/manual-fallbacks.md`
- **Specifications**: `specs/001-k8s-local-deployment/`

### Useful Commands

```bash
# Quick health check
kubectl get pods && kubectl get svc && kubectl get endpoints

# Detailed diagnostics
kubectl describe pod <pod-name>
kubectl logs <pod-name> --tail=100
kubectl get events --sort-by='.lastTimestamp'

# Resource usage
kubectl top pods
kubectl top nodes
```

### Escalation

If issue persists after troubleshooting:
1. Document the issue (symptoms, steps taken, error messages)
2. Collect diagnostic information (logs, events, pod descriptions)
3. Contact DevOps team or escalate to on-call engineer

---

**Last Updated**: 2026-02-01
**Maintained By**: DevOps Team
