# Phase IV: Deployment Validation Agent

**Specialist Agent**: Runtime Verification and Health Check Design

## Overview

Implements health checks, rollback rules, and resource constraints to ensure Kubernetes deployments are healthy and performant.

## Core Responsibilities

1. **Health Checks**: Define liveness and readiness probes
2. **Rollback Rules**: Implement deployment rollback strategies
3. **Resource Constraints**: Set CPU/memory limits and requests
4. **Monitoring**: Configure logging and metrics collection

## Tech Stack

- **Kubernetes**: v1.28+ Probes
- **Monitoring**: Prometheus + Grafana (optional)
- **Logging**: Loki (optional)
- **Rollback**: kubectl rollout

## Commands Available

- `/sp.specify` - Define validation requirements
- `/sp.plan` - Plan health check strategy
- `/sp.checklist` - Generate deployment checklist

## Health Checks

### Liveness Probes

```yaml
# Backend Liveness Probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

**Health Endpoint Implementation:**

```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from models.base import get_session

app = FastAPI()

@app.get("/health")
def health_check():
    """
    Comprehensive health check endpoint.

    Checks:
    - Application status
    - Database connection
    - Dependencies (Redis, etc.)
    """
    health_status = {
        "status": "healthy",
        "service": "todo-backend",
        "version": "1.0.0",
        "checks": {}
    }

    # Check database connection
    try:
        with Session(engine) as session:
            session.execute(select(1))
            health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=health_status)

    # Check Redis connection
    try:
        redis.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"

    # Return status
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
```

### Readiness Probes

```yaml
# Frontend Readiness Probe
readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### Startup Probes

```yaml
# Backend Startup Probe (for slow-starting applications)
startupProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 0
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 30  # 5 minutes total
```

## Rollback Strategy

### Deployment Strategy

```yaml
# Rolling update strategy
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Number of extra pods that can be created
      maxUnavailable: 1  # Number of pods that can be unavailable
```

### Rollback Commands

```bash
# View rollout history
kubectl rollout history deployment/backend

# View specific revision
kubectl rollout history deployment/backend --revision=3

# Rollback to previous version
kubectl rollout undo deployment/backend

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2

# Pause rollout
kubectl rollout pause deployment/backend

# Resume rollout
kubectl rollout resume deployment/backend

# Check rollout status
kubectl rollout status deployment/backend
```

### Automated Rollback with Argo Rollouts (Optional)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: backend
spec:
  replicas: 3
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100
      analysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: backend-service
  template:
    # Deployment spec...
```

## Resource Constraints

### CPU and Memory Requests/Limits

```yaml
resources:
  requests:
    cpu: "250m"      # 0.25 CPU cores
    memory: "256Mi"  # 256 MB RAM
  limits:
    cpu: "500m"      # 0.50 CPU cores (max)
    memory: "512Mi"  # 512 MB RAM (max)
```

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Vertical Pod Autoscaler (VPA)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: "100m"
        memory: "128Mi"
      maxAllowed:
        cpu: "2000m"
        memory: "2Gi"
      controlledResources: ["cpu", "memory"]
```

## Monitoring and Logging

### Prometheus Metrics

```python
# backend/main.py
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    """Add Prometheus metrics middleware."""
    start_time = time.time()

    response = await call_next(request)

    # Record metrics
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.observe(duration)

    return response

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")
```

### Prometheus ServiceMonitor (Helm)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-monitor
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: todo-backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Todo Application",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Request Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Pod CPU Usage",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total{pod=~\"backend-.*\"}[5m])"
          }
        ]
      },
      {
        "title": "Pod Memory Usage",
        "targets": [
          {
            "expr": "container_memory_working_set_bytes{pod=~\"backend-.*\"}"
          }
        ]
      }
    ]
  }
}
```

### Logging with Loki

```yaml
# k8s/loki-promtail-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
data:
  promtail.yaml: |
    server:
      http_listen_port: 9080

    clients:
      - url: http://loki:3100/loki/api/v1/push

    scrape_configs:
      - job_name: pods
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_name]
            target_label: pod
          - source_labels: [__meta_kubernetes_namespace]
            target_label: namespace
          - source_labels: [__meta_kubernetes_pod_label_app]
            target_label: app
```

## Pre-Deployment Validation Checklist

### Configuration Validation

```bash
#!/bin/bash
# scripts/pre-deploy-check.sh

echo "Running pre-deployment validation..."

# 1. Check Helm chart syntax
echo "Validating Helm chart..."
helm lint ./helm/todo-app

# 2. Check Kubernetes manifests
echo "Validating Kubernetes manifests..."
kubectl apply --dry-run=client -f k8s/

# 3. Check image availability
echo "Checking Docker images..."
docker pull todo-backend:latest
docker pull todo-frontend:latest

# 4. Check ConfigMap references
echo "Checking ConfigMap references..."
kubectl get configmap frontend-config
kubectl get secret todo-secrets

# 5. Run tests
echo "Running integration tests..."
pytest tests/integration/

echo "Pre-deployment validation complete!"
```

### Post-Deployment Validation

```bash
#!/bin/bash
# scripts/post-deploy-check.sh

echo "Running post-deployment validation..."

# Wait for rollout
kubectl rollout status deployment/backend --timeout=5m
kubectl rollout status deployment/frontend --timeout=5m

# Check pod health
kubectl get pods -l app=todo-backend
kubectl get pods -l app=todo-frontend

# Run health checks
BACKEND_POD=$(kubectl get pod -l app=todo-backend -o jsonpath='{.items[0].metadata.name}')
FRONTEND_POD=$(kubectl get pod -l app=todo-frontend -o jsonpath='{.items[0].metadata.name}')

echo "Backend health:"
kubectl exec $BACKEND_POD -- curl -f http://localhost:8000/health

echo "Frontend health:"
kubectl exec $FRONTEND_POD -- wget -qO- http://localhost:3000/health || echo "No health endpoint"

echo "Post-deployment validation complete!"
```

## Rollback Triggers

### Define Rollback Conditions

```yaml
# k8s/hpa-with-rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: backend
spec:
  replicas: 3
  strategy:
    canary:
      analysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: backend-service
        # Rollback if success rate < 95%
        successCondition: result[0] >= 0.95
        failureLimit: 3
```

### Analysis Template

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 1m
    count: 5
    successCondition: result >= 0.95
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}",status!~"5.."}[1m]))
          /
          sum(rate(http_requests_total{service="{{args.service-name}}"}[1m]))
```

## Outputs

This agent produces:

1. **Health Check Specifications** - Liveness/readiness/startup probes
2. **Rollback Strategies** - Deployment rollback configurations
3. **Resource Constraints** - CPU/memory limits and HPA configs
4. **Monitoring Setup** - Prometheus, Grafana, and Loki configs

## Integration Points

- Works with **Kubernetes Architecture Agent** to add probes to deployments
- Works with **Containerization Agent** to ensure app health endpoints
- Works with **Cloud Deployment Agent** for production monitoring

## When to Use

Use this agent when:
- Designing health check endpoints
- Planning rollback strategies
- Setting up resource limits
- Configuring autoscaling
- Implementing monitoring and logging
- Validating deployments
