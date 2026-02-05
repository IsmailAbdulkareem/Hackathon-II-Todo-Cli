# Kubernetes Resource Specifications

**Date**: 2026-01-31
**Purpose**: Define exact specifications for all Kubernetes resources (Deployments, Services, ConfigMaps, Secrets)

---

## Frontend Deployment Specification

### Metadata
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
    component: frontend
    tier: presentation
```

### Spec
```yaml
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: frontend
        image: todo-frontend:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3000
          name: http
          protocol: TCP

        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 250m
            memory: 512Mi

        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3

        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: todo-frontend-config
              key: API_URL
        - name: NODE_ENV
          value: "production"
```

---

## Backend Deployment Specification

### Metadata
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
    component: backend
    tier: application
```

### Spec
```yaml
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
          protocol: TCP

        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 500m
            memory: 1Gi

        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3

        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-backend-secrets
              key: DATABASE_URL
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-backend-secrets
              key: ANTHROPIC_API_KEY
        - name: CORS_ORIGINS
          valueFrom:
            configMapKeyRef:
              name: todo-backend-config
              key: CORS_ORIGINS
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: todo-backend-config
              key: LOG_LEVEL
```

---

## Frontend Service Specification

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
spec:
  type: NodePort
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
    nodePort: 30080
    name: http
  selector:
    app: todo-frontend
```

**Service Type**: NodePort
**Rationale**: Minikube doesn't support LoadBalancer natively. NodePort provides external access via `minikube service` command.
**Access**: `minikube service todo-frontend --url` returns accessible URL

---

## Backend Service Specification

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: todo-backend
```

**Service Type**: ClusterIP
**Rationale**: Backend is internal-only, accessed by frontend via Kubernetes DNS (`http://todo-backend:8000`)
**Access**: Only accessible within cluster

---

## Frontend ConfigMap Specification

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-frontend-config
  labels:
    app: todo-frontend
data:
  API_URL: "http://todo-backend:8000"
```

**Purpose**: Provide backend service URL to frontend
**Key**: `API_URL` (mapped to `NEXT_PUBLIC_API_URL` in deployment)
**Value**: Kubernetes DNS name for backend service

---

## Backend ConfigMap Specification

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-backend-config
  labels:
    app: todo-backend
data:
  CORS_ORIGINS: "*"
  LOG_LEVEL: "INFO"
```

**Purpose**: Non-sensitive backend configuration
**Keys**:
- `CORS_ORIGINS`: Allowed CORS origins (use `*` for development, specific origins for production)
- `LOG_LEVEL`: Python logging level (DEBUG, INFO, WARNING, ERROR)

---

## Backend Secret Specification

### Creation Command
```bash
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@host:port/database?sslmode=require" \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-..."
```

### Secret Structure
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-backend-secrets
  labels:
    app: todo-backend
type: Opaque
data:
  DATABASE_URL: <base64-encoded-value>
  ANTHROPIC_API_KEY: <base64-encoded-value>
```

**Important**:
- Secrets are created manually, NOT via Helm templates
- Helm charts reference existing secrets
- Never commit secrets to version control
- Use `.env` files locally, Kubernetes Secrets in cluster

---

## Resource Limits Rationale

### Frontend (250m CPU / 512Mi Memory)
- **CPU**: Next.js server-side rendering requires moderate CPU
- **Memory**: React hydration and caching require reasonable memory
- **Replicas**: 2 for redundancy and load distribution
- **Total Cluster Usage**: 500m CPU, 1Gi memory for frontend

### Backend (500m CPU / 1Gi Memory)
- **CPU**: FastAPI + AI processing requires more CPU
- **Memory**: SQLModel ORM, connection pooling, AI model inference
- **Replicas**: 1 initially (can scale to 3 per SC-004)
- **Total Cluster Usage**: 500m CPU, 1Gi memory for backend (1 replica)

### Cluster Capacity
- **Minikube Allocation**: 4 CPUs, 6GB memory
- **Application Usage**: ~1 CPU, ~2Gi memory (with 2 frontend + 1 backend)
- **Remaining**: ~3 CPUs, ~4Gi memory for Kubernetes system components and scaling

---

## Health Probe Configuration

### Liveness Probe
- **Purpose**: Detect if container is alive (restart if failing)
- **Path**: `/` for both applications
- **Initial Delay**: 30 seconds (allow application startup)
- **Period**: 10 seconds (check every 10s)
- **Timeout**: 3 seconds (wait up to 3s for response)
- **Failure Threshold**: 3 (restart after 3 consecutive failures)

### Readiness Probe
- **Purpose**: Detect if container is ready to serve traffic
- **Path**: `/` for both applications
- **Initial Delay**: 5 seconds (check readiness quickly)
- **Period**: 5 seconds (check every 5s)
- **Timeout**: 3 seconds (wait up to 3s for response)
- **Failure Threshold**: 3 (remove from service after 3 consecutive failures)

### Probe Timing Rationale
- **30s liveness initial delay**: Allows Next.js and FastAPI to fully initialize
- **5s readiness initial delay**: Applications should be ready quickly after startup
- **10s liveness period**: Balance between quick detection and avoiding false positives
- **5s readiness period**: Faster detection for traffic routing decisions

---

## Label Strategy

### Standard Labels
All resources include:
- `app`: Application name (todo-frontend, todo-backend)
- `component`: Component type (frontend, backend)
- `tier`: Architecture tier (presentation, application)
- `app.kubernetes.io/name`: Chart name
- `app.kubernetes.io/instance`: Release name
- `app.kubernetes.io/version`: App version
- `app.kubernetes.io/managed-by`: Helm

### Selector Labels
Used for pod selection (must be stable):
- `app.kubernetes.io/name`: Chart name
- `app.kubernetes.io/instance`: Release name

**Important**: Selector labels cannot be changed after deployment creation

---

## Service Discovery

### Frontend → Backend Communication
- **Method**: Kubernetes DNS
- **Service Name**: `todo-backend`
- **Full DNS**: `todo-backend.default.svc.cluster.local` (can use short name within same namespace)
- **URL**: `http://todo-backend:8000`
- **Environment Variable**: `NEXT_PUBLIC_API_URL=http://todo-backend:8000`

### DNS Resolution
- Kubernetes DNS automatically resolves service names to ClusterIP
- Frontend pods can reach backend via service name
- No need for IP addresses or external DNS

---

## Deployment Strategy

### Order of Deployment
1. **Secrets**: Create secrets first (required by backend)
2. **Backend**: Deploy backend (provides API service)
3. **Frontend**: Deploy frontend (consumes backend service)

### Verification Steps
1. Check pod status: `kubectl get pods`
2. Check service endpoints: `kubectl get endpoints`
3. Check service status: `kubectl get svc`
4. Check pod logs: `kubectl logs -l app=<app-name>`
5. Test health checks: `kubectl describe pod <pod-name>`

---

## Scaling Considerations

### Horizontal Scaling
- **Frontend**: Can scale to 3+ replicas (stateless)
- **Backend**: Can scale to 3+ replicas (stateless, database handles concurrency)
- **Command**: `kubectl scale deployment <name> --replicas=<count>`

### Resource Constraints
- Monitor cluster resources: `kubectl top nodes`
- Monitor pod resources: `kubectl top pods`
- Adjust limits if needed based on actual usage

---

## Configuration Update Workflow

### ConfigMap Changes
1. Edit ConfigMap: `kubectl edit configmap <name>`
2. Restart pods: `kubectl rollout restart deployment <name>`
3. Verify changes: `kubectl exec <pod> -- env | grep <KEY>`

### Secret Changes
1. Update secret: `kubectl create secret generic <name> --from-literal=<key>=<value> --dry-run=client -o yaml | kubectl apply -f -`
2. Restart pods: `kubectl rollout restart deployment <name>`
3. Verify changes: `kubectl describe pod <pod> | grep secretKeyRef`

**Important**: Pods do NOT automatically restart when ConfigMaps or Secrets change. Manual restart required.

---

## Implementation Notes

1. **Namespace**: Using `default` namespace for simplicity (can be parameterized later)
2. **Image Pull**: Images loaded into Minikube via `minikube image load`
3. **Service Mesh**: Not used (out of scope)
4. **Ingress**: Not used (NodePort sufficient for local development)
5. **Persistent Volumes**: Not needed (external database)
