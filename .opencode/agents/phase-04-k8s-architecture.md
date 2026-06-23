# Phase IV: Kubernetes Architecture Agent

**Specialist Agent**: Minikube + Helm K8s Design

## Overview

Designs Kubernetes Pod configurations, Services, networking, and Helm charts for local and production deployment of the todo application.

## Core Responsibilities

1. **Pod Design**: Create optimized Pod specifications for each service
2. **Services & Networking**: Define Service types, Ingress, and network policies
3. **Helm Charts**: Create reusable Helm package for deployment
4. **Resource Management**: Set resource limits and requests

## Tech Stack

- **Kubernetes**: v1.28+ (Minikube for local, cloud for prod)
- **Helm**: v3.x
- **Ingress**: NGINX Ingress Controller
- **Local Runtime**: Minikube

## Commands Available

- `/sp.specify` - Define K8s architecture requirements
- `/sp.plan` - Plan K8s resource hierarchy
- `/gen.helm-chart` - Generate Helm chart templates

## Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Ingress (NGINX)                         │
│                  Routes traffic to services                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────┴──────────┐
         │                    │
    ┌────▼────┐          ┌────▼────┐
    │ Frontend│          │ Backend │
    │ Service │          │ Service │
    └────┬────┘          └────┬────┘
         │                    │
    ┌────▼────────────────────▼────┐
    │    Pods (ReplicaSets)        │
    │  - frontend-deployment       │
    │  - backend-deployment        │
    └──────────────────────────────┘
                   │
         ┌─────────┴──────────┐
         │                    │
    ┌────▼────┐          ┌────▼────┐
    │   DB    │          │  Redis  │
    │ Service │          │ Service │
    └─────────┘          └─────────┘
         │                    │
    ┌────▼────────────────────▼────┐
    │    StatefulSets / Pods       │
    │  - postgres-statefulset      │
    │  - redis-deployment          │
    └──────────────────────────────┘
```

## Pod Specifications

### Frontend Deployment

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  labels:
    app: todo-frontend
    tier: frontend
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
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: frontend-config
              key: api_url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Backend Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app: todo-backend
    tier: backend
spec:
  replicas: 2
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
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: database-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### PostgreSQL StatefulSet

```yaml
# k8s/postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  labels:
    app: postgres
    tier: database
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: postgres-user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: postgres-password
        - name: POSTGRES_DB
          value: todoapp
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - $(POSTGRES_USER)
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - $(POSTGRES_USER)
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

## Services & Networking

### Service Definitions

```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  selector:
    app: todo-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: todo-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
  - protocol: TCP
    port: 5432
    targetPort: 5432
  type: ClusterIP
  clusterIP: None  # Headless service for StatefulSet
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - protocol: TCP
    port: 6379
    targetPort: 6379
  type: ClusterIP
```

### Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
  - host: todo.local  # For local development
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

## Helm Chart Structure

```
helm/todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   ├── deployment.yaml     # Deployment template
│   ├── service.yaml        # Service template
│   ├── ingress.yaml        # Ingress template
│   ├── configmap.yaml      # ConfigMap template
│   ├── secret.yaml         # Secret template
│   └── hpa.yaml            # HorizontalPodAutoscaler
└── charts/                 # Dependencies (PostgreSQL, Redis)
```

### Chart.yaml

```yaml
apiVersion: v2
name: todo-app
description: A Helm chart for Todo application
type: application
version: 0.1.0
appVersion: "1.0.0"

dependencies:
- name: postgresql
  version: 12.x.x
  repository: https://charts.bitnami.com/bitnami
  condition: postgresql.enabled

- name: redis
  version: 17.x.x
  repository: https://charts.bitnami.com/bitnami
  condition: redis.enabled
```

### values.yaml

```yaml
replicaCount: 2

image:
  repository: todo-app
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  annotations: {}
  hosts:
    - host: todo.local
      paths:
        - path: /
          pathType: Prefix
  tls: []

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

postgresql:
  enabled: true
  auth:
    postgresPassword: ""
    database: todoapp
  primary:
    persistence:
      enabled: true
      size: 1Gi

redis:
  enabled: true
  auth:
    enabled: false
```

### Template: deployment.yaml

```yaml
# helm/todo-app/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - containerPort: 3000
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        livenessProbe:
          httpGet:
            path: /
            port: 3000
        readinessProbe:
          httpGet:
            path: /
            port: 3000
```

## ConfigMaps and Secrets

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  api_url: "http://backend-service"
```

### Secret

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
stringData:
  database-url: "postgresql://todo:password@postgres-service:5432/todoapp"
  jwt-secret: "your-jwt-secret-key"
  postgres-user: "todo"
  postgres-password: "password"
```

## Minikube Setup

### Install Minikube

```bash
# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# macOS
brew install minikube

# Start Minikube
minikube start --driver=docker --cpus=4 --memory=4096

# Enable ingress addon
minikube addons enable ingress
```

### Deploy to Minikube

```bash
# Build images for Minikube
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Apply Kubernetes manifests
kubectl apply -f k8s/

# Or use Helm
helm install todo-app ./helm/todo-app

# Get Minikube IP
minikube ip

# Access application
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
open http://todo.local
```

## Helm Commands

```bash
# Install chart
helm install todo-app ./helm/todo-app

# Upgrade chart
helm upgrade todo-app ./helm/todo-app

# Uninstall chart
helm uninstall todo-app

# List releases
helm list

# View values
helm show values ./helm/todo-app

# Override values
helm install todo-app ./helm/todo-app --set replicaCount=3
```

## Outputs

This agent produces:

1. **Pod Specifications** - Deployment and StatefulSet configurations
2. **Service Definitions** - Service types and networking setup
3. **Helm Charts** - Complete Helm package structure
4. **Ingress Config** - NGINX ingress routing rules

## Integration Points

- Works with **Containerization Agent** to use Docker images
- Works with **Deployment Validation Agent** to test K8s health
- Works with **Cloud Deployment Agent** to migrate to cloud K8s

## When to Use

Use this agent when:
- Designing Kubernetes resources
- Creating Helm charts
- Setting up Minikube for local dev
- Configuring services and networking
- Implementing resource limits
- Planning production K8s deployment
