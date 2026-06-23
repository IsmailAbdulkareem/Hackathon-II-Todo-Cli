# Helm Chart Generator

**Critical for Phases:** IV, V

Generates complete Kubernetes Helm charts for deployment to Minikube and DigitalOcean DOKS.

## Usage

```
/gen.helm-chart "<service-spec>"

# Examples:
/gen.helm-chart "backend FastAPI service with PostgreSQL database"
/gen.helm-chart "frontend Next.js app with API URL config"
/gen.helm-chart "fullstack app with backend, frontend, and database"
```

## What It Generates

- Complete Helm chart structure
- Kubernetes manifests (Deployment, Service, Ingress, PVC)
- Values.yaml for configuration
- ConfigMaps for environment variables
- Secrets for sensitive data
- Horizontal Pod Autoscaler config
- Health checks and probes
- Ingress rules for routing

## Output Structure

```
phase-XX/charts/
  ├── todo-app/
  │   ├── Chart.yaml              # Helm chart metadata
  │   ├── values.yaml             # Default configuration
  │   ├── templates/
  │   │   ├── deployment.yaml     # Pod deployments
  │   │   ├── service.yaml        # Service definitions
  │   │   ├── ingress.yaml        # Ingress routing
  │   │   ├── configmap.yaml      # Configuration
  │   │   ├── secret.yaml         # Secrets
  │   │   ├── hpa.yaml            # Horizontal Pod Autoscaler
  │   │   └── pvc.yaml           # Persistent Volume Claims
  │   └── charts/                 # Chart dependencies
  │       └── postgresql/         # PostgreSQL sub-chart
```

## Features

- Multi-environment support (dev, staging, prod)
- Configurable replicas and resources
- Automatic scaling with HPA
- Health check probes (liveness, readiness, startup)
- Secret management
- Configurable database connection
- Ingress with TLS support
- PVC for database persistence
- Node selectors and affinity rules
- Pod disruption budgets

## Phase Usage

- **Phase IV:** Local Minikube deployment
- **Phase V:** DigitalOcean DOKS deployment
- **Phase V:** Multi-region deployment

## Example Output

### Chart.yaml
```yaml
apiVersion: v2
name: todo-app
description: Full-stack Todo application
type: application
version: 0.1.0
appVersion: "1.0.0"

dependencies:
  - name: postgresql
    version: 12.x.x
    repository: https://charts.bitnami.com/bitnami
```

### values.yaml
```yaml
# Global configuration
global:
  imageRegistry: ""
  imagePullSecrets: []

# Frontend configuration
frontend:
  replicaCount: 2
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Always

  service:
    type: NodePort
    port: 3000

  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

# Backend configuration
backend:
  replicaCount: 3
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Always

  service:
    type: ClusterIP
    port: 8000

  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi

  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10

  env:
    DATABASE_HOST: todo-postgresql
    DATABASE_PORT: 5432
    DATABASE_NAME: todo
    JWT_SECRET: {{ .Values.secrets.jwtSecret }}

  probes:
    liveness:
      path: /health
      initialDelaySeconds: 30
      periodSeconds: 10
    readiness:
      path: /ready
      initialDelaySeconds: 5
      periodSeconds: 5

# PostgreSQL configuration
postgresql:
  auth:
    username: todo
    database: todo
    password: {{ .Values.secrets.postgresPassword }}

  primary:
    persistence:
      enabled: true
      size: 10Gi

  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 1Gi

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: todo.example.com
      paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: todo-frontend
  tls:
    - hosts:
        - todo.example.com
      secretName: todo-tls
```

### templates/deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.backend.replicaCount }}
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
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - containerPort: 8000
          env:
            {{- range $key, $value := .Values.backend.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: {{ .Values.backend.probes.liveness.path }}
              port: 8000
            initialDelaySeconds: {{ .Values.backend.probes.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.backend.probes.liveness.periodSeconds }}
          readinessProbe:
            httpGet:
              path: {{ .Values.backend.probes.readiness.path }}
              port: 8000
            initialDelaySeconds: {{ .Values.backend.probes.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.backend.probes.readiness.periodSeconds }}
```

### templates/hpa.yaml
```yaml
{{- if .Values.backend.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "todo-app.fullname" . }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "todo-app.fullname" . }}
  minReplicas: {{ .Values.backend.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.backend.autoscaling.maxReplicas }}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.backend.autoscaling.targetCPUUtilizationPercentage }}
{{- end }}
```

## Deployment Commands

```bash
# Local (Minikube)
helm install todo-app ./charts/todo-app --values values-dev.yaml

# Production (DigitalOcean)
helm install todo-app ./charts/todo-app --values values-prod.yaml

# Upgrade
helm upgrade todo-app ./charts/todo-app

# Uninstall
helm uninstall todo-app

# Get status
helm status todo-app
```

## Configuration Files

```
charts/todo-app/
  ├── values.yaml          # Default configuration
  ├── values-dev.yaml       # Development overrides
  ├── values-staging.yaml  # Staging overrides
  └── values-prod.yaml    # Production overrides
```

## Best Practices

- Always use values.yaml for configuration
- Never commit secrets to git
- Use Kubernetes secrets for passwords
- Configure health checks for all services
- Set resource limits to prevent runaway pods
- Enable HPA for production
- Use persistent volumes for databases
- Implement rolling updates
- Configure pod disruption budgets
