# Manual kubectl Fallbacks Guide

**Purpose**: Provide manual kubectl command equivalents for all AI-assisted operations

**Date**: 2026-02-01

**Requirement**: FR-018 - All AI operations must have documented manual kubectl equivalents

---

## Overview

This guide provides manual kubectl commands that replicate the functionality of AI-assisted tools (Docker AI, kubectl-ai, kagent). Use these commands when:
- AI tools are unavailable
- Automation/scripting is required
- Deterministic behavior is needed
- Learning kubectl fundamentals

---

## Quick Reference Table

| AI Operation | Manual kubectl Command |
|--------------|------------------------|
| Scale deployment | `kubectl scale deployment <name> --replicas=<count>` |
| Check pod health | `kubectl get pods` + `kubectl describe pod <name>` |
| View logs | `kubectl logs <pod-name> --tail=<lines>` |
| Resource usage | `kubectl top pods` |
| Service endpoints | `kubectl get endpoints` |
| Restart deployment | `kubectl rollout restart deployment/<name>` |
| Rollback deployment | `kubectl rollout undo deployment/<name>` |
| Update ConfigMap | `kubectl edit configmap <name>` |
| Create Secret | `kubectl create secret generic <name> --from-literal=<key>=<value>` |

---

## 1. Scaling Operations

### kubectl-ai: "scale the frontend to 3 replicas"

**Manual Equivalent**:
```bash
# Scale deployment
kubectl scale deployment todo-frontend --replicas=3

# Verify scaling
kubectl get deployment todo-frontend

# Wait for rollout to complete
kubectl rollout status deployment/todo-frontend

# Check pod status
kubectl get pods -l app=todo-frontend
```

**Expected Output**:
```
deployment.apps/todo-frontend scaled
NAME            READY   UP-TO-DATE   AVAILABLE   AGE
todo-frontend   3/3     3            3           1h

Waiting for deployment "todo-frontend" rollout to finish: 2 of 3 updated replicas are available...
deployment "todo-frontend" successfully rolled out

NAME                             READY   STATUS    RESTARTS   AGE
todo-frontend-55dccf5586-7xk7j   1/1     Running   0          1h
todo-frontend-55dccf5586-dfrp5   1/1     Running   0          1h
todo-frontend-55dccf5586-xyz12   1/1     Running   0          30s
```

**Success Criteria**: All 3 replicas Running and Ready within 1 minute (SC-004)

---

## 2. Health Checks

### kubectl-ai: "check the health of all pods"

**Manual Equivalent**:
```bash
# List all pods with status
kubectl get pods --all-namespaces

# Check specific namespace
kubectl get pods -n default

# Detailed pod information
kubectl get pods -o wide

# Check pod conditions
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'

# Describe pods for events
kubectl describe pods | grep -A 5 "Events:"
```

**Health Check Checklist**:
```bash
# 1. Pod Status
kubectl get pods
# Look for: Running, Ready (1/1)

# 2. Pod Events
kubectl describe pod <pod-name> | grep -A 10 "Events:"
# Look for: No error events

# 3. Container Status
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].ready}{"\n"}{end}'
# Look for: true

# 4. Restart Count
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}'
# Look for: 0 or low number
```

---

## 3. Troubleshooting

### kubectl-ai: "explain why the backend pod is failing"

**Manual Equivalent**:
```bash
# Step 1: Check pod status
kubectl get pods -l app=todo-backend

# Step 2: Describe pod for events
kubectl describe pod <backend-pod-name>

# Step 3: Check recent logs
kubectl logs <backend-pod-name> --tail=50

# Step 4: Check previous container logs (if restarted)
kubectl logs <backend-pod-name> --previous

# Step 5: Check resource constraints
kubectl top pod <backend-pod-name>

# Step 6: Check service endpoints
kubectl get endpoints todo-backend

# Step 7: Check events in namespace
kubectl get events --sort-by='.lastTimestamp' | grep <pod-name>
```

**Systematic Troubleshooting Flow**:
```bash
#!/bin/bash
# troubleshoot-pod.sh <pod-name>

POD_NAME=$1

echo "=== Pod Status ==="
kubectl get pod $POD_NAME

echo -e "\n=== Pod Description ==="
kubectl describe pod $POD_NAME

echo -e "\n=== Recent Logs ==="
kubectl logs $POD_NAME --tail=50

echo -e "\n=== Previous Logs (if restarted) ==="
kubectl logs $POD_NAME --previous 2>/dev/null || echo "No previous logs"

echo -e "\n=== Resource Usage ==="
kubectl top pod $POD_NAME 2>/dev/null || echo "Metrics not available"

echo -e "\n=== Recent Events ==="
kubectl get events --field-selector involvedObject.name=$POD_NAME --sort-by='.lastTimestamp'
```

---

## 4. Resource Monitoring

### kagent: "analyze cluster health"

**Manual Equivalent**:
```bash
# Cluster-level health
kubectl cluster-info
kubectl get nodes
kubectl top nodes

# Namespace-level health
kubectl get all -n default
kubectl get pods --all-namespaces

# Resource utilization
kubectl top pods --all-namespaces --sort-by=memory
kubectl top pods --all-namespaces --sort-by=cpu

# Deployment status
kubectl get deployments
kubectl rollout status deployment/todo-frontend
kubectl rollout status deployment/todo-backend

# Service status
kubectl get services
kubectl get endpoints

# ConfigMap and Secret status
kubectl get configmaps
kubectl get secrets
```

**Comprehensive Health Check Script**:
```bash
#!/bin/bash
# cluster-health.sh

echo "=== Cluster Info ==="
kubectl cluster-info

echo -e "\n=== Node Status ==="
kubectl get nodes
kubectl top nodes

echo -e "\n=== Pod Status ==="
kubectl get pods --all-namespaces
kubectl get pods -o wide

echo -e "\n=== Deployment Status ==="
kubectl get deployments

echo -e "\n=== Service Status ==="
kubectl get services
kubectl get endpoints

echo -e "\n=== Resource Usage ==="
kubectl top pods --all-namespaces

echo -e "\n=== Recent Events ==="
kubectl get events --sort-by='.lastTimestamp' | tail -20

echo -e "\n=== Failed Pods ==="
kubectl get pods --all-namespaces --field-selector=status.phase!=Running,status.phase!=Succeeded
```

---

## 5. Log Analysis

### kubectl-ai: "show me recent errors in the backend logs"

**Manual Equivalent**:
```bash
# Recent logs with errors
kubectl logs -l app=todo-backend --tail=100 | grep -i error

# All error types
kubectl logs -l app=todo-backend --tail=100 | grep -iE "error|exception|fatal|fail"

# Follow logs in real-time
kubectl logs -l app=todo-backend -f

# Logs from all containers in pod
kubectl logs <pod-name> --all-containers=true

# Logs with timestamps
kubectl logs <pod-name> --timestamps=true

# Logs from specific time range
kubectl logs <pod-name> --since=1h
kubectl logs <pod-name> --since-time=2026-02-01T10:00:00Z
```

**Log Analysis Patterns**:
```bash
# Database connection errors
kubectl logs -l app=todo-backend | grep -i "database\|connection\|sqlalchemy"

# Authentication errors
kubectl logs -l app=todo-backend | grep -i "auth\|token\|unauthorized"

# HTTP errors
kubectl logs -l app=todo-backend | grep -E "HTTP [45][0-9]{2}"

# Performance issues
kubectl logs -l app=todo-backend | grep -i "timeout\|slow\|latency"
```

---

## 6. Configuration Management

### kubectl-ai: "update the frontend configmap"

**Manual Equivalent**:
```bash
# Method 1: Edit interactively
kubectl edit configmap todo-frontend-config

# Method 2: Patch specific value
kubectl patch configmap todo-frontend-config \
  -p '{"data":{"API_URL":"http://new-backend:8000"}}'

# Method 3: Replace from file
kubectl create configmap todo-frontend-config \
  --from-literal=API_URL="http://new-backend:8000" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up changes
kubectl rollout restart deployment/todo-frontend

# Verify changes
kubectl get configmap todo-frontend-config -o yaml
kubectl exec <frontend-pod> -- env | grep API_URL
```

**Secret Management**:
```bash
# Create secret
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-..."

# Update secret
kubectl delete secret todo-backend-secrets
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-..."

# Restart pods to pick up changes
kubectl rollout restart deployment/todo-backend

# Verify secret exists (values are base64 encoded)
kubectl get secret todo-backend-secrets -o yaml
kubectl describe secret todo-backend-secrets
```

---

## 7. Deployment Management

### kubectl-ai: "rollback the frontend deployment"

**Manual Equivalent**:
```bash
# View rollout history
kubectl rollout history deployment/todo-frontend

# Rollback to previous version
kubectl rollout undo deployment/todo-frontend

# Rollback to specific revision
kubectl rollout undo deployment/todo-frontend --to-revision=2

# Check rollout status
kubectl rollout status deployment/todo-frontend

# Pause rollout
kubectl rollout pause deployment/todo-frontend

# Resume rollout
kubectl rollout resume deployment/todo-frontend

# Restart deployment (rolling restart)
kubectl rollout restart deployment/todo-frontend
```

---

## 8. Service and Networking

### kubectl-ai: "show me all services and their endpoints"

**Manual Equivalent**:
```bash
# List services
kubectl get services

# Detailed service information
kubectl describe service todo-frontend
kubectl describe service todo-backend

# Service endpoints
kubectl get endpoints

# Detailed endpoint information
kubectl describe endpoints todo-frontend

# Test service connectivity (from within cluster)
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  wget -O- http://todo-backend:8000

# Port forward for local testing
kubectl port-forward svc/todo-frontend 8080:3000

# Get service URL (Minikube)
minikube service todo-frontend --url
```

---

## 9. Resource Inspection

### kagent: "what resources is the backend pod using?"

**Manual Equivalent**:
```bash
# Current resource usage
kubectl top pod -l app=todo-backend

# Resource requests and limits
kubectl describe pod <backend-pod> | grep -A 10 "Limits:"
kubectl describe pod <backend-pod> | grep -A 10 "Requests:"

# Detailed resource information
kubectl get pod <backend-pod> -o jsonpath='{.spec.containers[0].resources}'

# All pods resource usage
kubectl top pods --sort-by=memory
kubectl top pods --sort-by=cpu

# Node resource usage
kubectl top nodes
kubectl describe nodes | grep -A 5 "Allocated resources:"
```

---

## 10. Debugging

### kubectl-ai: "debug the backend pod"

**Manual Equivalent**:
```bash
# Execute command in pod
kubectl exec <backend-pod> -- env
kubectl exec <backend-pod> -- ps aux
kubectl exec <backend-pod> -- df -h

# Interactive shell
kubectl exec -it <backend-pod> -- /bin/sh
kubectl exec -it <backend-pod> -- /bin/bash

# Debug with ephemeral container (Kubernetes 1.23+)
kubectl debug <backend-pod> -it --image=busybox

# Copy files from pod
kubectl cp <backend-pod>:/app/logs/error.log ./error.log

# Copy files to pod
kubectl cp ./config.yaml <backend-pod>:/app/config.yaml

# Run debug pod in same network namespace
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
```

---

## 11. Helm Operations

### Manual Helm Commands

```bash
# List releases
helm list

# Get release status
helm status todo-frontend
helm status todo-backend

# Get release values
helm get values todo-frontend
helm get values todo-backend

# Upgrade release
helm upgrade todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend

# Rollback release
helm rollback todo-frontend
helm rollback todo-frontend 1  # to specific revision

# Uninstall release
helm uninstall todo-frontend
helm uninstall todo-backend

# Dry run (preview changes)
helm upgrade todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend --dry-run

# Lint chart
helm lint ./phase-04-k8s-local/k8s/helm/todo-frontend
```

---

## 12. Minikube Operations

### Manual Minikube Commands

```bash
# Start cluster
minikube start --cpus=4 --memory=3500

# Stop cluster
minikube stop

# Delete cluster
minikube delete

# Cluster status
minikube status

# Get cluster IP
minikube ip

# Access service
minikube service todo-frontend --url

# SSH into node
minikube ssh

# Load Docker image
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# List images in Minikube
minikube image ls

# Dashboard
minikube dashboard
```

---

## Common Workflows

### Workflow 1: Deploy New Version

```bash
# 1. Build new image
docker build -t todo-frontend:v2 ./phase-04-k8s-local/frontend

# 2. Load into Minikube
minikube image load todo-frontend:v2

# 3. Update Helm values
# Edit values.yaml: image.tag: v2

# 4. Upgrade release
helm upgrade todo-frontend ./phase-04-k8s-local/k8s/helm/todo-frontend

# 5. Monitor rollout
kubectl rollout status deployment/todo-frontend

# 6. Verify deployment
kubectl get pods -l app=todo-frontend
kubectl logs -l app=todo-frontend --tail=20
```

### Workflow 2: Troubleshoot Failing Pod

```bash
# 1. Identify failing pod
kubectl get pods

# 2. Check pod details
kubectl describe pod <pod-name>

# 3. Check logs
kubectl logs <pod-name> --tail=100
kubectl logs <pod-name> --previous  # if restarted

# 4. Check events
kubectl get events --field-selector involvedObject.name=<pod-name>

# 5. Check resource usage
kubectl top pod <pod-name>

# 6. Debug interactively
kubectl exec -it <pod-name> -- /bin/sh

# 7. Fix issue (update config, secret, etc.)
kubectl edit configmap <name>
kubectl rollout restart deployment/<name>

# 8. Verify fix
kubectl get pods
kubectl logs <pod-name> --tail=20
```

### Workflow 3: Scale Application

```bash
# 1. Check current state
kubectl get deployment todo-frontend

# 2. Scale deployment
kubectl scale deployment todo-frontend --replicas=3

# 3. Monitor scaling
kubectl get pods -l app=todo-frontend -w

# 4. Verify all pods ready
kubectl get deployment todo-frontend

# 5. Check resource usage
kubectl top pods -l app=todo-frontend

# 6. Verify load distribution
kubectl logs -l app=todo-frontend --tail=10
```

---

## Performance Comparison

| Operation | AI Tool Time | Manual kubectl Time | Notes |
|-----------|--------------|---------------------|-------|
| Scale deployment | 5-10s | 2-3s | Manual is faster |
| Health check | 10-15s | 5-10s | Manual requires multiple commands |
| Troubleshooting | 15-30s | 10-20s | AI provides analysis, manual requires interpretation |
| Log analysis | 10-20s | 5-10s | Manual is faster but less insightful |

**Recommendation**: Use manual kubectl for:
- Time-critical operations
- Automation/scripting
- CI/CD pipelines
- When AI tools are unavailable

Use AI tools for:
- Learning and exploration
- Complex analysis
- Interactive troubleshooting
- Getting recommendations

---

## References

- kubectl Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- kubectl Commands: https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands
- Helm Commands: https://helm.sh/docs/helm/
- Minikube Commands: https://minikube.sigs.k8s.io/docs/commands/

---

**Last Updated**: 2026-02-01
**Maintained By**: DevOps Team
