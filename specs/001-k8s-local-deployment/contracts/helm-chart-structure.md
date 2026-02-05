# Helm Chart Structure

**Date**: 2026-01-31
**Purpose**: Define Helm chart organization and template hierarchy for frontend and backend deployments

---

## Chart Organization

### Directory Structure

```
phase-04-k8s-local/k8s/helm/
├── todo-frontend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── .helmignore
│   └── templates/
│       ├── _helpers.tpl
│       ├── deployment.yaml
│       ├── service.yaml
│       └── configmap.yaml
│
└── todo-backend/
    ├── Chart.yaml
    ├── values.yaml
    ├── .helmignore
    └── templates/
        ├── _helpers.tpl
        ├── deployment.yaml
        ├── service.yaml
        ├── configmap.yaml
        └── secret.yaml
```

---

## Frontend Helm Chart

### Chart.yaml
```yaml
apiVersion: v2
name: todo-frontend
description: Helm chart for Todo Chatbot Frontend (Next.js)
type: application
version: 0.1.0
appVersion: "0.1.0"
keywords:
  - todo
  - frontend
  - nextjs
maintainers:
  - name: Todo Chatbot Team
```

### values.yaml Schema
```yaml
replicaCount: 2

image:
  repository: todo-frontend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 3000
  targetPort: 3000
  nodePort: 30080

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
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3

config:
  apiUrl: "http://todo-backend:8000"

labels:
  app: todo-frontend
  component: frontend
  tier: presentation
```

---

## Backend Helm Chart

### Chart.yaml
```yaml
apiVersion: v2
name: todo-backend
description: Helm chart for Todo Chatbot Backend (FastAPI)
type: application
version: 0.1.0
appVersion: "0.1.0"
keywords:
  - todo
  - backend
  - fastapi
maintainers:
  - name: Todo Chatbot Team
```

### values.yaml Schema
```yaml
replicaCount: 1

image:
  repository: todo-backend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000
  targetPort: 8000

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
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3

config:
  corsOrigins: "*"
  logLevel: "INFO"

secrets:
  existingSecret: "todo-backend-secrets"
  databaseUrlKey: "DATABASE_URL"
  apiKeyKey: "ANTHROPIC_API_KEY"

labels:
  app: todo-backend
  component: backend
  tier: application
```

---

## Template Helpers (_helpers.tpl)

### Common Helper Functions

Both charts should include these helper templates:

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "chart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "chart.labels" -}}
helm.sh/chart: {{ include "chart.chart" . }}
{{ include "chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

## Configuration Management Strategy

### Values Hierarchy

1. **Default values**: Defined in `values.yaml`
2. **Environment overrides**: Can be provided via `--values` or `--set` flags
3. **Secret references**: Secrets created separately, referenced in values

### Parameterization Strategy

**What's Configurable**:
- Replica counts
- Image tags
- Resource limits
- Probe timing
- Service types and ports
- ConfigMap values
- Secret references

**What's Hardcoded**:
- Container ports (3000, 8000)
- Health check paths
- Label keys
- Template structure

### Secret Management

**Approach**: External Secret Creation
- Secrets are NOT created by Helm charts
- Secrets are created manually via `kubectl create secret`
- Helm charts reference existing secrets by name
- Secret names are configurable via values.yaml

**Rationale**:
- Prevents secrets from being stored in Helm releases
- Allows secret rotation without Helm upgrade
- Follows Kubernetes security best practices

### ConfigMap vs Secret Decision Criteria

**Use ConfigMap for**:
- API URLs
- Feature flags
- Log levels
- CORS origins
- Non-sensitive application settings

**Use Secret for**:
- Database credentials
- API keys
- Authentication tokens
- Encryption keys
- TLS certificates

---

## Template Structure

### Deployment Template Pattern

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "chart.fullname" . }}
  labels:
    {{- include "chart.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "chart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "chart.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - containerPort: {{ .Values.service.targetPort }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
        livenessProbe:
          {{- toYaml .Values.livenessProbe | nindent 10 }}
        readinessProbe:
          {{- toYaml .Values.readinessProbe | nindent 10 }}
        env:
        # Environment variables from ConfigMap/Secret
```

### Service Template Pattern

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "chart.fullname" . }}
  labels:
    {{- include "chart.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
    targetPort: {{ .Values.service.targetPort }}
    protocol: TCP
    {{- if and (eq .Values.service.type "NodePort") .Values.service.nodePort }}
    nodePort: {{ .Values.service.nodePort }}
    {{- end }}
  selector:
    {{- include "chart.selectorLabels" . | nindent 4 }}
```

---

## Validation Strategy

### Helm Lint
All charts must pass `helm lint`:
```bash
helm lint helm/todo-frontend
helm lint helm/todo-backend
```

### Template Rendering
Verify templates render correctly:
```bash
helm template todo-frontend helm/todo-frontend
helm template todo-backend helm/todo-backend
```

### Dry Run
Test installation without applying:
```bash
helm install todo-frontend helm/todo-frontend --dry-run --debug
helm install todo-backend helm/todo-backend --dry-run --debug
```

---

## Upgrade Strategy

### Rolling Updates
- Deployments use `RollingUpdate` strategy (default)
- MaxUnavailable: 1
- MaxSurge: 1

### Helm Upgrade
```bash
helm upgrade todo-frontend helm/todo-frontend
helm upgrade todo-backend helm/todo-backend
```

### Rollback
```bash
helm rollback todo-frontend
helm rollback todo-backend
```

---

## .helmignore

Both charts should include:
```
# Patterns to ignore when building packages
.git/
.gitignore
.DS_Store
*.swp
*.bak
*.tmp
*.orig
*~
.vscode/
.idea/
```

---

## Implementation Notes

1. **Chart Generation**: Use kubectl-ai or manual creation (kubectl-ai not available)
2. **Naming Convention**: Use `todo-frontend` and `todo-backend` for consistency
3. **Service Discovery**: Backend service name `todo-backend` used by frontend
4. **Image Pull Policy**: `IfNotPresent` for local Minikube (images loaded manually)
5. **Resource Limits**: Set to match clarified values (frontend 250m/512Mi, backend 500m/1Gi)
