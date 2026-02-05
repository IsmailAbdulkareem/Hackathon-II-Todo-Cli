# kubectl-ai Usage Guide

**Purpose**: Document kubectl-ai usage for natural language Kubernetes operations

**Date**: 2026-02-01

---

## Overview

kubectl-ai is a kubectl plugin that enables natural language interaction with Kubernetes clusters. It translates human-readable commands into kubectl operations, making cluster management more intuitive.

**Installation**:
```bash
# Install via krew (kubectl plugin manager)
kubectl krew install ai

# Or download binary directly
# https://github.com/sozercan/kubectl-ai
```

**Version**: kubectl-ai v0.0.x (check with `kubectl ai version`)

---

## Basic Usage

### Command Syntax

```bash
kubectl ai "<natural language query>"
```

The AI interprets your request and executes the appropriate kubectl commands.

---

## Use Cases in This Project

### 1. Scaling Operations

**Natural Language**:
```bash
kubectl ai "scale the frontend to 3 replicas"
```

**Equivalent kubectl**:
```bash
kubectl scale deployment todo-frontend --replicas=3
```

**Expected Behavior**:
- Interprets "frontend" as the todo-frontend deployment
- Scales from 2 to 3 replicas
- Completes within 1 minute (per SC-004)

**Verification**:
```bash
kubectl get deployment todo-frontend
# Should show READY: 3/3
```

---

### 2. Health Checks

**Natural Language**:
```bash
kubectl ai "check the health of all pods"
```

**Equivalent kubectl**:
```bash
kubectl get pods --all-namespaces
kubectl describe pods | grep -A 5 "Conditions:"
```

**Expected Output**:
- Summary of pod status across all namespaces
- Health check results (Ready, Running, etc.)
- Any failing pods highlighted

**Example Response**:
```
Checking pod health across all namespaces...

✓ kube-system: 8/8 pods healthy
✓ default: 2/3 pods healthy
  - todo-frontend-xxx: Running (Ready)
  - todo-frontend-yyy: Running (Ready)
  - todo-backend-zzz: Running (Not Ready - failing health checks)

Summary: 10/11 pods healthy (90.9%)
```

---

### 3. Troubleshooting

**Natural Language**:
```bash
kubectl ai "explain why the backend pod is failing"
```

**Equivalent kubectl**:
```bash
kubectl get pods -l app=todo-backend
kubectl describe pod <backend-pod-name>
kubectl logs <backend-pod-name> --tail=50
```

**Expected Analysis**:
- Pod status and events
- Recent log entries
- Potential root causes
- Suggested remediation steps

**Example Response**:
```
Analyzing todo-backend-xxx...

Status: CrashLoopBackOff (3 restarts)

Recent Events:
- Liveness probe failed: HTTP probe failed with statuscode: 500
- Back-off restarting failed container

Log Analysis:
- Database connection error: could not connect to server
- Error: FATAL: password authentication failed

Root Cause: Database connection failure
Suggestion: Check DATABASE_URL secret and database availability
```

---

### 4. Resource Inspection

**Natural Language**:
```bash
kubectl ai "show me all services and their endpoints"
```

**Equivalent kubectl**:
```bash
kubectl get services
kubectl get endpoints
```

**Natural Language**:
```bash
kubectl ai "what resources is the backend pod using?"
```

**Equivalent kubectl**:
```bash
kubectl top pod -l app=todo-backend
kubectl describe pod <backend-pod> | grep -A 10 "Limits:"
```

---

### 5. Configuration Management

**Natural Language**:
```bash
kubectl ai "show me the environment variables for the backend"
```

**Equivalent kubectl**:
```bash
kubectl exec <backend-pod> -- env
# Or
kubectl describe pod <backend-pod> | grep -A 20 "Environment:"
```

**Natural Language**:
```bash
kubectl ai "update the frontend configmap to use a different API URL"
```

**Equivalent kubectl**:
```bash
kubectl edit configmap todo-frontend-config
# Then manually edit the API_URL value
kubectl rollout restart deployment todo-frontend
```

---

## Advanced Operations

### Deployment Management

**Rollback**:
```bash
kubectl ai "rollback the frontend deployment to the previous version"
```

**Equivalent**:
```bash
kubectl rollout undo deployment/todo-frontend
```

**Check Rollout Status**:
```bash
kubectl ai "is the frontend deployment finished rolling out?"
```

**Equivalent**:
```bash
kubectl rollout status deployment/todo-frontend
```

---

### Resource Monitoring

**CPU and Memory Usage**:
```bash
kubectl ai "which pods are using the most memory?"
```

**Equivalent**:
```bash
kubectl top pods --sort-by=memory
```

**Node Resources**:
```bash
kubectl ai "how much CPU and memory is available on the cluster?"
```

**Equivalent**:
```bash
kubectl top nodes
kubectl describe nodes | grep -A 5 "Allocated resources:"
```

---

### Log Analysis

**Recent Errors**:
```bash
kubectl ai "show me recent errors in the backend logs"
```

**Equivalent**:
```bash
kubectl logs -l app=todo-backend --tail=100 | grep -i error
```

**Follow Logs**:
```bash
kubectl ai "stream logs from all frontend pods"
```

**Equivalent**:
```bash
kubectl logs -l app=todo-frontend -f --all-containers=true
```

---

## Best Practices

### 1. Be Specific

**Good**:
```bash
kubectl ai "scale the todo-frontend deployment to 3 replicas"
```

**Less Good**:
```bash
kubectl ai "scale frontend"
```

### 2. Use Context

kubectl-ai understands context from previous commands:
```bash
kubectl ai "show me the backend pods"
kubectl ai "describe the first one"  # References previous result
kubectl ai "show me its logs"        # References the described pod
```

### 3. Verify Actions

Always verify destructive operations:
```bash
kubectl ai "delete the test pod"
# Check: kubectl get pods | grep test
```

### 4. Combine with Manual Commands

Use kubectl-ai for exploration, manual kubectl for automation:
```bash
# Exploration
kubectl ai "what's wrong with the backend?"

# Automation (in scripts)
kubectl logs -l app=todo-backend --tail=50
```

---

## Limitations

1. **Ambiguity**: May misinterpret vague requests
2. **Complex Operations**: Multi-step operations may require manual intervention
3. **Security**: Always review suggested commands before execution
4. **Context Limits**: May not understand very complex cluster states
5. **API Rate Limits**: Frequent queries may hit rate limits

---

## Performance Considerations

**Success Criteria (from spec.md)**:
- **SC-004**: Scaling operations complete within 1 minute
- kubectl-ai adds ~2-5 seconds overhead for interpretation
- Total time: ~5-65 seconds for scaling operations

**Optimization Tips**:
- Use specific resource names to reduce interpretation time
- Cache common queries
- Fall back to manual kubectl for time-critical operations

---

## Security Considerations

1. **Command Review**: Always review suggested commands before execution
2. **Secrets**: kubectl-ai should not expose secret values
3. **RBAC**: Respects your kubectl RBAC permissions
4. **Audit Logs**: All operations are logged like normal kubectl commands

---

## Troubleshooting kubectl-ai

### Issue: "kubectl ai command not found"

**Solution**:
```bash
# Check if plugin is installed
kubectl plugin list | grep ai

# Reinstall if needed
kubectl krew install ai
```

### Issue: "AI interpretation is incorrect"

**Solution**:
- Be more specific in your query
- Use exact resource names
- Fall back to manual kubectl commands

### Issue: "Operation times out"

**Solution**:
- Check cluster connectivity: `kubectl cluster-info`
- Verify API server is responsive
- Use manual kubectl for time-critical operations

---

## Integration with CI/CD

kubectl-ai is best for:
- **Interactive debugging**: Manual troubleshooting sessions
- **Learning**: Understanding kubectl commands
- **Exploration**: Discovering cluster state

**Not recommended for**:
- **Automated pipelines**: Use standard kubectl commands
- **Production deployments**: Use Helm or GitOps tools
- **Critical operations**: Use tested, deterministic commands

---

## Examples from This Project

### Scenario 1: Deployment Verification

**Task**: Verify both applications are deployed correctly

```bash
kubectl ai "show me all deployments and their status"
```

**Expected Output**:
```
NAME            READY   UP-TO-DATE   AVAILABLE   AGE
todo-backend    0/1     1            0           22h
todo-frontend   2/2     2            2           22h

Analysis:
✓ todo-frontend: Healthy (2/2 replicas ready)
⚠ todo-backend: Unhealthy (0/1 replicas ready)
  Suggestion: Check pod logs and events
```

### Scenario 2: Scaling for Load

**Task**: Scale frontend to handle increased traffic

```bash
kubectl ai "scale the frontend to 3 replicas to handle more traffic"
```

**Expected Actions**:
1. Identifies todo-frontend deployment
2. Scales from 2 to 3 replicas
3. Waits for new pod to be Ready
4. Confirms successful scaling

### Scenario 3: Debugging Backend Issues

**Task**: Investigate why backend is not ready

```bash
kubectl ai "why is the backend pod not ready?"
```

**Expected Analysis**:
1. Checks pod status and events
2. Reviews recent logs
3. Examines health check failures
4. Suggests potential fixes

---

## Manual Fallback Commands

For every kubectl-ai operation, there's a manual kubectl equivalent. See `manual-fallbacks.md` for comprehensive mapping.

**Quick Reference**:
- Scaling: `kubectl scale deployment <name> --replicas=<count>`
- Health: `kubectl get pods` + `kubectl describe pod <name>`
- Logs: `kubectl logs <pod-name> --tail=<lines>`
- Resources: `kubectl top pods`

---

## References

- kubectl-ai GitHub: https://github.com/sozercan/kubectl-ai
- kubectl Documentation: https://kubernetes.io/docs/reference/kubectl/
- Kubernetes API: https://kubernetes.io/docs/reference/kubernetes-api/

---

**Last Updated**: 2026-02-01
**Maintained By**: DevOps Team
