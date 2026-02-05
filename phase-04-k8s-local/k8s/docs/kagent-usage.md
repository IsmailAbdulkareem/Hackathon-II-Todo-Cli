# kagent Usage Guide

**Purpose**: Document kagent usage for AI-powered Kubernetes cluster analysis and insights

**Date**: 2026-02-01

---

## Overview

kagent is an AI-powered Kubernetes agent that provides intelligent cluster health analysis, resource utilization insights, and operational recommendations. Unlike kubectl-ai which translates natural language to kubectl commands, kagent analyzes cluster state and provides actionable insights.

**Installation**:
```bash
# Install via binary download
# https://github.com/GoogleCloudPlatform/kagent

# Or via package manager
brew install kagent  # macOS
```

**Version**: kagent v0.x (check with `kagent version`)

---

## Basic Usage

### Command Syntax

```bash
kagent <command> [options]
```

Common commands:
- `kagent analyze` - Analyze cluster health
- `kagent insights` - Get operational insights
- `kagent recommend` - Get optimization recommendations
- `kagent diagnose` - Diagnose specific issues

---

## Use Cases in This Project

### 1. Cluster Health Analysis

**Command**:
```bash
kagent analyze cluster
```

**What It Does**:
- Scans all namespaces and resources
- Identifies unhealthy pods, services, and deployments
- Checks resource utilization
- Detects configuration issues
- Provides health score (0-100)

**Expected Output**:
```
Cluster Health Analysis
=======================

Overall Health Score: 85/100

✓ Control Plane: Healthy
  - API Server: Running
  - etcd: Healthy
  - Scheduler: Running
  - Controller Manager: Running

✓ Nodes: 1/1 Healthy
  - minikube: Ready (CPU: 45%, Memory: 60%)

⚠ Workloads: 3/4 Healthy (75%)
  ✓ todo-frontend: 2/2 replicas ready
  ✗ todo-backend: 0/1 replicas ready
    Issue: CrashLoopBackOff
    Cause: Database connection failure
    Recommendation: Verify DATABASE_URL secret

✓ Services: 2/2 Operational
  - todo-frontend (NodePort): 2 endpoints
  - todo-backend (ClusterIP): 0 endpoints (no ready pods)

⚠ Configuration Issues:
  - todo-backend: Missing readiness probe endpoints
  - Recommendation: Ensure health check endpoint is accessible

Resource Utilization:
  - CPU: 1.2/4 cores (30%)
  - Memory: 2.1/3.5 GB (60%)
  - Storage: Adequate
```

---

### 2. Resource Utilization Insights

**Command**:
```bash
kagent insights resources
```

**What It Does**:
- Analyzes CPU and memory usage across all pods
- Identifies over-provisioned or under-provisioned resources
- Suggests resource limit adjustments
- Predicts scaling needs

**Expected Output**:
```
Resource Utilization Insights
==============================

Pod Resource Analysis:

todo-frontend-xxx:
  CPU: 45m / 250m (18% utilized)
  Memory: 180Mi / 512Mi (35% utilized)
  Status: ⚠ Over-provisioned
  Recommendation: Consider reducing limits to 100m CPU / 256Mi memory

todo-frontend-yyy:
  CPU: 50m / 250m (20% utilized)
  Memory: 185Mi / 512Mi (36% utilized)
  Status: ⚠ Over-provisioned
  Recommendation: Consider reducing limits to 100m CPU / 256Mi memory

todo-backend-zzz:
  CPU: N/A (pod not ready)
  Memory: N/A (pod not ready)
  Status: ⚠ Cannot analyze (pod failing)

Cluster Summary:
  - Total Requested: 1.0 CPU / 2.0Gi memory
  - Total Used: 0.3 CPU / 0.8Gi memory
  - Efficiency: 30% CPU, 40% memory
  - Potential Savings: 0.5 CPU / 1.0Gi memory

Recommendations:
  1. Reduce frontend resource limits (save 300m CPU / 512Mi memory)
  2. Fix backend pod to enable accurate analysis
  3. Consider horizontal pod autoscaling for frontend
```

---

### 3. Deployment Recommendations

**Command**:
```bash
kagent recommend deployment todo-frontend
```

**What It Does**:
- Analyzes deployment configuration
- Suggests improvements for reliability, performance, and cost
- Checks best practices compliance

**Expected Output**:
```
Deployment Recommendations: todo-frontend
==========================================

Current Configuration:
  - Replicas: 2
  - CPU: 250m (request/limit)
  - Memory: 512Mi (request/limit)
  - Health Checks: ✓ Configured
  - Resource Limits: ✓ Set

Recommendations:

1. Resource Optimization (Priority: Medium)
   Current: 250m CPU / 512Mi memory per pod
   Suggested: 100m CPU / 256Mi memory per pod
   Reason: Actual usage is 18-20% of allocated resources
   Impact: Save 300m CPU / 512Mi memory per pod
   Risk: Low (usage well below suggested limits)

2. High Availability (Priority: Low)
   Current: 2 replicas
   Suggested: 3 replicas
   Reason: Improve fault tolerance and load distribution
   Impact: Better availability during node failures
   Cost: +1 pod (100m CPU / 256Mi memory)

3. Pod Disruption Budget (Priority: High)
   Current: Not configured
   Suggested: minAvailable: 1
   Reason: Prevent all pods from being evicted simultaneously
   Impact: Improved availability during cluster maintenance
   Implementation:
   ```yaml
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   metadata:
     name: todo-frontend-pdb
   spec:
     minAvailable: 1
     selector:
       matchLabels:
         app: todo-frontend
   ```

4. Horizontal Pod Autoscaler (Priority: Medium)
   Current: Manual scaling only
   Suggested: HPA with CPU threshold 70%
   Reason: Automatically scale based on load
   Implementation:
   ```bash
   kubectl autoscale deployment todo-frontend --min=2 --max=5 --cpu-percent=70
   ```

Overall Score: 75/100
Compliance: Good (3/4 best practices implemented)
```

---

### 4. Issue Diagnosis

**Command**:
```bash
kagent diagnose pod todo-backend-xxx
```

**What It Does**:
- Deep analysis of pod failures
- Root cause identification
- Step-by-step remediation guide

**Expected Output**:
```
Pod Diagnosis: todo-backend-xxx
================================

Status: CrashLoopBackOff (5 restarts in 10 minutes)

Timeline:
  16:30:00 - Pod created
  16:30:15 - Container started
  16:30:45 - Liveness probe failed (HTTP 500)
  16:31:00 - Container restarted (attempt 1)
  16:31:30 - Liveness probe failed (HTTP 500)
  16:32:00 - Container restarted (attempt 2)
  ...

Root Cause Analysis:
  Primary Issue: Database connection failure
  Evidence:
    - Log: "sqlalchemy.exc.OperationalError: could not connect to server"
    - Log: "FATAL: password authentication failed"
    - Environment: DATABASE_URL set via secret

  Contributing Factors:
    1. Invalid database credentials
    2. Database server unreachable
    3. Network policy blocking connection

Remediation Steps:

  Step 1: Verify Database Credentials
  ```bash
  # Check if secret exists
  kubectl get secret todo-backend-secrets

  # Verify secret has correct keys
  kubectl describe secret todo-backend-secrets

  # Test database connection manually
  kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
    psql "$DATABASE_URL"
  ```

  Step 2: Check Database Availability
  ```bash
  # Test network connectivity
  kubectl run -it --rm debug --image=busybox --restart=Never -- \
    wget -O- <database-host>:<port>
  ```

  Step 3: Update Secret with Valid Credentials
  ```bash
  kubectl delete secret todo-backend-secrets
  kubectl create secret generic todo-backend-secrets \
    --from-literal=DATABASE_URL="<valid-url>" \
    --from-literal=ANTHROPIC_API_KEY="<valid-key>" \
    --from-literal=BETTER_AUTH_SECRET="<valid-secret>" \
    --from-literal=OPENAI_API_KEY="<valid-key>"

  # Restart deployment
  kubectl rollout restart deployment/todo-backend
  ```

  Step 4: Monitor Recovery
  ```bash
  kubectl get pods -l app=todo-backend -w
  kubectl logs -l app=todo-backend -f
  ```

Expected Resolution Time: 5-10 minutes
Success Probability: High (if credentials are valid)
```

---

## Advanced Features

### 1. Continuous Monitoring

**Command**:
```bash
kagent monitor --interval=30s
```

**What It Does**:
- Continuously monitors cluster health
- Alerts on anomalies
- Tracks metrics over time

### 2. Cost Analysis

**Command**:
```bash
kagent analyze costs
```

**What It Does**:
- Estimates cluster running costs
- Identifies cost optimization opportunities
- Suggests resource right-sizing

### 3. Security Audit

**Command**:
```bash
kagent audit security
```

**What It Does**:
- Scans for security vulnerabilities
- Checks RBAC configurations
- Identifies exposed secrets
- Validates network policies

---

## Integration with kubectl-ai

kagent and kubectl-ai complement each other:

**kubectl-ai**: Execute operations
```bash
kubectl ai "scale the frontend to 3 replicas"
```

**kagent**: Analyze impact
```bash
kagent analyze deployment todo-frontend
# Shows resource utilization after scaling
```

**Workflow**:
1. Use kagent to identify issues
2. Use kubectl-ai to fix issues
3. Use kagent to verify fixes

---

## Best Practices

### 1. Regular Health Checks

Run cluster analysis daily:
```bash
kagent analyze cluster > cluster-health-$(date +%Y%m%d).txt
```

### 2. Pre-Deployment Analysis

Before deploying changes:
```bash
kagent recommend deployment <name>
# Review recommendations before applying
```

### 3. Post-Incident Analysis

After resolving issues:
```bash
kagent diagnose pod <failed-pod>
# Document root cause and remediation
```

### 4. Resource Optimization

Monthly resource review:
```bash
kagent insights resources
# Adjust resource limits based on actual usage
```

---

## Limitations

1. **AI Accuracy**: Recommendations are suggestions, not guarantees
2. **Context**: May not understand application-specific requirements
3. **Real-time**: Analysis is point-in-time, not continuous (unless using monitor mode)
4. **Permissions**: Requires read access to cluster resources

---

## Performance Considerations

**Analysis Time**:
- Small cluster (1-10 pods): ~5-10 seconds
- Medium cluster (10-100 pods): ~30-60 seconds
- Large cluster (100+ pods): ~2-5 minutes

**Resource Usage**:
- CPU: Minimal (runs outside cluster)
- Memory: ~100-200MB for analysis
- Network: Queries Kubernetes API

---

## Troubleshooting kagent

### Issue: "Cannot connect to cluster"

**Solution**:
```bash
# Verify kubectl connectivity
kubectl cluster-info

# Check kubeconfig
echo $KUBECONFIG
kubectl config current-context
```

### Issue: "Insufficient permissions"

**Solution**:
```bash
# Check your RBAC permissions
kubectl auth can-i get pods --all-namespaces
kubectl auth can-i get nodes
```

### Issue: "Analysis takes too long"

**Solution**:
```bash
# Analyze specific namespace only
kagent analyze cluster --namespace=default

# Skip resource-intensive checks
kagent analyze cluster --quick
```

---

## Examples from This Project

### Scenario 1: Initial Deployment Validation

**After deploying with Helm**:
```bash
kagent analyze cluster
```

**Result**: Identified backend pod failures and provided remediation steps

### Scenario 2: Resource Optimization

**After running for 24 hours**:
```bash
kagent insights resources
```

**Result**: Discovered frontend pods over-provisioned by 60%, suggested reducing limits

### Scenario 3: Troubleshooting Backend

**When backend won't start**:
```bash
kagent diagnose pod todo-backend-xxx
```

**Result**: Identified database connection issue, provided step-by-step fix

---

## Manual Fallback Commands

For every kagent operation, there are manual kubectl equivalents:

**Cluster Health**:
```bash
kubectl get nodes
kubectl get pods --all-namespaces
kubectl top nodes
kubectl top pods --all-namespaces
```

**Resource Analysis**:
```bash
kubectl describe nodes
kubectl top pods
kubectl get pods -o json | jq '.items[] | {name: .metadata.name, cpu: .spec.containers[].resources}'
```

**Diagnosis**:
```bash
kubectl describe pod <name>
kubectl logs <name> --tail=100
kubectl get events --sort-by='.lastTimestamp'
```

See `manual-fallbacks.md` for comprehensive mapping.

---

## References

- kagent Documentation: https://github.com/GoogleCloudPlatform/kagent
- Kubernetes Best Practices: https://kubernetes.io/docs/concepts/configuration/overview/
- Resource Management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

---

**Last Updated**: 2026-02-01
**Maintained By**: DevOps Team
