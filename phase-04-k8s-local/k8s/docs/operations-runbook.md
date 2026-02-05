# Kubernetes Operations Runbook

**Purpose**: Standard operating procedures for managing the Todo Chatbot Kubernetes deployment

**Last Updated**: 2026-02-01

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Deployment Procedures](#deployment-procedures)
3. [Scaling Operations](#scaling-operations)
4. [Configuration Management](#configuration-management)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance Tasks](#maintenance-tasks)
7. [Emergency Procedures](#emergency-procedures)
8. [Monitoring and Alerts](#monitoring-and-alerts)

---

## Daily Operations

### Morning Health Check

**Frequency**: Daily at start of business day

**Procedure**:
```bash
# 1. Check cluster status
kubectl cluster-info
kubectl get nodes

# 2. Check all pods
kubectl get pods --all-namespaces

# 3. Check services and endpoints
kubectl get svc
kubectl get endpoints

# 4. Check recent events
kubectl get events --sort-by='.lastTimestamp' | tail -20

# 5. Check resource usage (if metrics-server available)
kubectl top nodes
kubectl top pods
```

**Expected Results**:
- Cluster: Running and accessible
- Nodes: Ready status
- Frontend pods: 2/2 or 3/3 Running and Ready
- Backend pods: 1/1 Running and Ready (with valid credentials)
- Services: All endpoints populated
- No critical error events in last 24 hours

**Action if Failed**:
- See [Troubleshooting](#troubleshooting) section
- Escalate if issue persists >15 minutes

---

## Deployment Procedures

### Initial Deployment

**Prerequisites**:
- Minikube cluster running
- Docker images built and loaded
- Kubernetes Secret created with valid credentials

**Procedure**:
```bash
# 1. Verify prerequisites
minikube status
minikube image ls | grep todo
kubectl get secret todo-backend-secrets

# 2. Deploy backend first
helm install todo-backend ./phase-04-k8s-local/k8s/helm/todo-backend

# 3. Wait for backend to be ready
kubectl wait --for=condition=ready pod -l app=todo-backend --timeout=120s

# 4. Deploy frontend
helm install todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend

# 5. Wait for frontend to be ready
kubectl wait --for=condition=ready pod -l app=todo-frontend --timeout=120s

# 6. Verify deployment
kubectl get pods
kubectl get svc
kubectl get endpoints

# 7. Test access
kubectl port-forward svc/todo-frontend 8080:3000
# Open browser to http://localhost:8080
```

**Rollback on Failure**:
```bash
helm uninstall todo-frontend
helm uninstall todo-backend
# Fix issue and retry
```

### Application Update

**Use Case**: Deploy new version of frontend or backend

**Procedure**:
```bash
# 1. Build new Docker image
docker build -t todo-frontend:v2 -f phase-04-k8s-local/frontend/Dockerfile phase-02-fullstack-web/frontend

# 2. Load into Minikube
minikube image load todo-frontend:v2

# 3. Update Helm values
# Edit phase-04-k8s-local/k8s/helm/todo-frontend/values.yaml
# Change: image.tag: v2

# 4. Upgrade Helm release
helm upgrade todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend

# 5. Monitor rollout
kubectl rollout status deployment/todo-frontend

# 6. Verify new version
kubectl get pods -l app=todo-frontend
kubectl describe pod <pod-name> | grep Image:

# 7. Test functionality
# Access application and verify changes
```

**Rollback if Issues**:
```bash
# Rollback to previous version
helm rollback todo-frontend

# Verify rollback
kubectl rollout status deployment/todo-frontend
kubectl get pods -l app=todo-frontend
```

---

## Scaling Operations

### Scale Up (Increase Replicas)

**Use Case**: Handle increased traffic or improve availability

**Procedure**:
```bash
# 1. Check current replica count
kubectl get deployment todo-frontend

# 2. Scale deployment
kubectl scale deployment todo-frontend --replicas=3

# 3. Monitor scaling
kubectl get pods -l app=todo-frontend -w

# 4. Wait for all replicas to be ready
kubectl wait --for=condition=ready pod -l app=todo-frontend --timeout=120s

# 5. Verify endpoints updated
kubectl get endpoints todo-frontend

# 6. Check resource usage
kubectl top pods -l app=todo-frontend
```

**Expected Time**: <1 minute (SC-004)

**Rollback if Issues**:
```bash
# Scale back to original count
kubectl scale deployment todo-frontend --replicas=2
```

### Scale Down (Decrease Replicas)

**Use Case**: Reduce resource usage during low traffic

**Procedure**:
```bash
# 1. Check current replica count
kubectl get deployment todo-frontend

# 2. Scale deployment
kubectl scale deployment todo-frontend --replicas=1

# 3. Monitor scaling
kubectl get pods -l app=todo-frontend -w

# 4. Verify endpoints updated
kubectl get endpoints todo-frontend
```

**Caution**: Never scale below 1 replica for production services

---

## Configuration Management

### Update ConfigMap

**Use Case**: Change non-sensitive configuration (API URLs, log levels, etc.)

**Procedure**:
```bash
# 1. Backup current ConfigMap
kubectl get configmap todo-frontend-config -o yaml > configmap-backup.yaml

# 2. Edit ConfigMap
kubectl edit configmap todo-frontend-config
# Make changes and save

# 3. Restart pods to pick up changes
kubectl rollout restart deployment/todo-frontend

# 4. Monitor restart
kubectl rollout status deployment/todo-frontend

# 5. Verify changes applied
kubectl exec <pod-name> -- env | grep <CONFIG_KEY>

# 6. Test functionality
# Access application and verify configuration change
```

**Expected Time**: <2 minutes (SC-005)

**Rollback if Issues**:
```bash
# Restore from backup
kubectl apply -f configmap-backup.yaml
kubectl rollout restart deployment/todo-frontend
```

### Update Secret

**Use Case**: Rotate credentials, update API keys

**Procedure**:
```bash
# 1. Backup current Secret (base64 encoded)
kubectl get secret todo-backend-secrets -o yaml > secret-backup.yaml

# 2. Delete and recreate Secret
kubectl delete secret todo-backend-secrets
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="<new-value>" \
  --from-literal=ANTHROPIC_API_KEY="<new-value>" \
  --from-literal=BETTER_AUTH_SECRET="<new-value>" \
  --from-literal=OPENAI_API_KEY="<new-value>"

# 3. Restart pods to pick up changes
kubectl rollout restart deployment/todo-backend

# 4. Monitor restart
kubectl rollout status deployment/todo-backend

# 5. Verify pods are healthy
kubectl get pods -l app=todo-backend
kubectl logs -l app=todo-backend --tail=20

# 6. Test functionality
# Verify application can connect to database and APIs
```

**Security Note**: Never commit secrets to version control

**Rollback if Issues**:
```bash
# Restore from backup
kubectl apply -f secret-backup.yaml
kubectl rollout restart deployment/todo-backend
```

---

## Troubleshooting

### Pod Not Starting

**Symptoms**: Pod stuck in Pending, ContainerCreating, or CrashLoopBackOff

**Diagnosis**:
```bash
# 1. Check pod status
kubectl get pod <pod-name>

# 2. Describe pod for events
kubectl describe pod <pod-name>

# 3. Check logs
kubectl logs <pod-name> --tail=50

# 4. Check previous logs if restarted
kubectl logs <pod-name> --previous
```

**Common Causes and Solutions**:

**ImagePullBackOff**:
```bash
# Cause: Image not found in Minikube
# Solution: Load image
minikube image load todo-frontend:latest
kubectl delete pod <pod-name>  # Force recreation
```

**CrashLoopBackOff**:
```bash
# Cause: Application failing to start
# Solution: Check logs for error, fix configuration
kubectl logs <pod-name> --tail=100
# Common issues: database connection, missing env vars
```

**Pending**:
```bash
# Cause: Insufficient resources
# Solution: Check node resources
kubectl describe nodes
kubectl top nodes
# Scale down other pods or increase cluster resources
```

### Service Not Accessible

**Symptoms**: Cannot access application via service URL

**Diagnosis**:
```bash
# 1. Check service exists
kubectl get svc <service-name>

# 2. Check endpoints
kubectl get endpoints <service-name>

# 3. Check pod labels match service selector
kubectl get pods --show-labels
kubectl describe svc <service-name> | grep Selector

# 4. Test from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  wget -O- http://<service-name>:<port>
```

**Common Solutions**:
- No endpoints: Pods not ready, check pod health
- Wrong selector: Update service selector to match pod labels
- Port mismatch: Verify service port matches container port

### High Resource Usage

**Symptoms**: Pods using excessive CPU or memory

**Diagnosis**:
```bash
# 1. Check resource usage
kubectl top pods
kubectl top nodes

# 2. Check resource limits
kubectl describe pod <pod-name> | grep -A 10 "Limits:"

# 3. Check for memory leaks
kubectl logs <pod-name> --tail=100 | grep -i "memory\|oom"
```

**Solutions**:
- Increase resource limits if legitimate usage
- Investigate memory leaks in application code
- Scale horizontally instead of vertically

---

## Maintenance Tasks

### Weekly Tasks

**Cluster Health Review**:
```bash
# Review events from past week
kubectl get events --sort-by='.lastTimestamp' | grep -i "error\|warning"

# Check pod restart counts
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}'

# Review resource usage trends
kubectl top pods --all-namespaces
```

**Image Updates**:
```bash
# Check for security updates
# Rebuild images with latest base images
docker build -t todo-frontend:latest -f phase-04-k8s-local/frontend/Dockerfile phase-02-fullstack-web/frontend
docker build -t todo-backend:latest -f phase-04-k8s-local/backend/Dockerfile phase-03-ai-chatbot/backend

# Load into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Rolling update
kubectl rollout restart deployment/todo-frontend
kubectl rollout restart deployment/todo-backend
```

### Monthly Tasks

**Credential Rotation**:
```bash
# Rotate database credentials
# Rotate API keys
# Update Kubernetes Secret (see Configuration Management)
```

**Backup Verification**:
```bash
# Verify Helm chart backups
helm list
helm get values todo-frontend > backup/frontend-values.yaml
helm get values todo-backend > backup/backend-values.yaml

# Backup ConfigMaps and Secrets
kubectl get configmap -o yaml > backup/configmaps.yaml
kubectl get secret -o yaml > backup/secrets.yaml  # Store securely!
```

---

## Emergency Procedures

### Complete Service Outage

**Symptoms**: All pods down, cluster unresponsive

**Procedure**:
```bash
# 1. Check cluster status
minikube status

# 2. If cluster stopped, restart
minikube start

# 3. Verify cluster health
kubectl cluster-info
kubectl get nodes

# 4. Check pod status
kubectl get pods --all-namespaces

# 5. If pods not running, check Helm releases
helm list

# 6. Reinstall if needed
helm uninstall todo-frontend
helm uninstall todo-backend
# Follow Initial Deployment procedure
```

### Data Loss Prevention

**Before Destructive Operations**:
```bash
# Always backup before:
# - Deleting secrets
# - Uninstalling Helm releases
# - Deleting cluster

# Backup commands
kubectl get all -o yaml > backup/all-resources.yaml
kubectl get configmap -o yaml > backup/configmaps.yaml
kubectl get secret -o yaml > backup/secrets.yaml
helm get values todo-frontend > backup/frontend-values.yaml
helm get values todo-backend > backup/backend-values.yaml
```

### Rollback Procedure

**When to Rollback**:
- New deployment causing errors
- Performance degradation after update
- Functionality broken after configuration change

**Procedure**:
```bash
# Helm rollback
helm rollback <release-name>

# Or kubectl rollback
kubectl rollout undo deployment/<deployment-name>

# Verify rollback
kubectl rollout status deployment/<deployment-name>
kubectl get pods
kubectl logs <pod-name> --tail=20
```

---

## Monitoring and Alerts

### Key Metrics to Monitor

**Pod Health**:
- Pod status (Running, Ready)
- Restart count (should be low)
- Resource usage (CPU, memory)

**Service Health**:
- Endpoint count (should match replica count)
- Response time (should be <3 seconds per SC-003)

**Cluster Health**:
- Node status (Ready)
- Resource availability (CPU, memory)

### Manual Monitoring Commands

```bash
# Quick health check
kubectl get pods
kubectl get svc
kubectl get endpoints

# Detailed health check
kubectl describe pods
kubectl top pods
kubectl top nodes

# Log monitoring
kubectl logs -l app=todo-frontend --tail=50
kubectl logs -l app=todo-backend --tail=50

# Event monitoring
kubectl get events --sort-by='.lastTimestamp' | tail -20
```

### Alert Thresholds

**Critical**:
- All pods down for a service
- Cluster node not ready
- Persistent CrashLoopBackOff (>5 restarts)

**Warning**:
- Pod restart count >3 in 1 hour
- Resource usage >80% of limits
- Response time >5 seconds

**Info**:
- Pod restart (single occurrence)
- Configuration change applied
- Scaling operation completed

---

## Contact Information

**On-Call Engineer**: [Contact details]
**Escalation Path**: [Escalation procedure]
**Documentation**: `phase-04-k8s-local/k8s/docs/`

---

**Last Updated**: 2026-02-01
**Version**: 1.0
**Maintained By**: DevOps Team
