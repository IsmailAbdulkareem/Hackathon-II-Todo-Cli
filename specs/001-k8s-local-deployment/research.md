# Research: Local Kubernetes Deployment for Todo Chatbot

**Feature**: 001-k8s-local-deployment
**Date**: 2026-01-28
**Purpose**: Resolve technical unknowns identified in plan.md Technical Context

## Research Areas

### 1. AI DevOps Tools Integration

#### Docker AI (Gordon)

**Decision**: Use Docker AI (Gordon) for Dockerfile generation with documented fallback to Claude Code

**Rationale**:
- Docker AI (Gordon) is Docker's official AI assistant integrated into Docker Desktop
- Provides natural language interface for Dockerfile creation and optimization
- Can analyze application structure and suggest appropriate base images, dependencies, and build steps
- Available in Docker Desktop 4.53+ with Docker subscription (may have regional/tier restrictions)

**Integration Approach**:
1. Attempt to use `docker ai` command for Dockerfile generation
2. Document the prompts used and AI-generated outputs
3. If unavailable, use Claude Code to generate Dockerfiles following best practices
4. Document the attempt, error message, and fallback approach used

**Example Usage**:
```bash
# Attempt Docker AI
docker ai "Create a Dockerfile for a Next.js frontend application"

# Fallback: Claude Code generates Dockerfile with explanation
```

**Alternatives Considered**:
- Manual Dockerfile creation: Rejected because it doesn't demonstrate AI-assisted DevOps
- Only Claude Code: Rejected because hackathon requires attempting Docker AI first

---

#### kubectl-ai

**Decision**: Use kubectl-ai for natural language Kubernetes operations with fallback to standard kubectl

**Rationale**:
- kubectl-ai is a kubectl plugin that translates natural language to kubectl commands
- Helps with command discovery and complex operations
- Open source and installable via krew (kubectl plugin manager)
- May not be available on all platforms or may require specific setup

**Installation Method**:
```bash
# Install krew (kubectl plugin manager)
# Then install kubectl-ai
kubectl krew install ai

# Verify installation
kubectl ai --help
```

**Usage Patterns**:
```bash
# Natural language queries
kubectl ai "show me all pods in the default namespace"
kubectl ai "scale the frontend deployment to 3 replicas"
kubectl ai "get logs from the backend pod"
```

**Fallback Strategy**:
- If kubectl-ai unavailable: Document attempt and use standard kubectl commands
- Provide Claude Code-generated kubectl command explanations
- Document the natural language intent and corresponding kubectl command

**Alternatives Considered**:
- Only standard kubectl: Rejected because it doesn't demonstrate AI assistance
- Custom AI wrapper: Rejected as over-engineering for this phase

---

#### kagent

**Decision**: Demonstrate kagent for at least one Kubernetes operation with documented fallback

**Rationale**:
- kagent is an AI-powered Kubernetes agent for autonomous cluster operations
- Provides higher-level automation than kubectl-ai
- May have more complex setup requirements or availability limitations
- Minimal demonstration sufficient for hackathon requirements

**Setup Requirements**:
- Research specific installation method (likely requires API keys or cloud service)
- May be a commercial tool or require specific Kubernetes versions
- Document setup process and any blockers encountered

**Minimal Demonstration Approach**:
1. Attempt to install and configure kagent
2. Use for one operation (e.g., deployment health check, resource optimization)
3. Document the interaction and outcome
4. If unavailable: Document attempt, provide fallback using kubectl-ai or standard tools

**Alternatives Considered**:
- Skip kagent entirely: Rejected because spec requires demonstration
- Extensive kagent usage: Rejected as out of scope for minimal demonstration

---

### 2. Helm Chart Structure for Multi-Service Deployment

**Decision**: Use standard Helm chart structure with separate templates for frontend and backend

**Rationale**:
- Helm is the de facto package manager for Kubernetes
- Supports parameterization through values.yaml for environment-specific configs
- Enables versioning and rollback capabilities
- Standard structure is well-documented and widely adopted

**Chart Structure**:
```
helm/todo-chatbot/
├── Chart.yaml              # Chart metadata (name, version, description)
├── values.yaml             # Default configuration values
├── templates/
│   ├── _helpers.tpl        # Template helpers and named templates
│   ├── namespace.yaml      # Namespace definition
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   └── NOTES.txt           # Post-install instructions
└── .helmignore             # Files to ignore during packaging
```

**Key Configuration Parameters** (values.yaml):
```yaml
frontend:
  image:
    repository: todo-frontend
    tag: latest
  replicas: 1
  service:
    type: NodePort
    port: 3000

backend:
  image:
    repository: todo-backend
    tag: latest
  replicas: 1
  service:
    type: ClusterIP
    port: 8000
```

**Alternatives Considered**:
- Raw Kubernetes manifests: Rejected because Helm provides better parameterization and management
- Kustomize: Rejected because Helm is more feature-rich for this use case
- Separate charts per service: Rejected as over-engineering for tightly coupled services

---

### 3. Container Registry Strategy

**Decision**: Use Minikube's built-in Docker daemon for local image storage

**Rationale**:
- Minikube can use the local Docker daemon, eliminating need for registry push/pull
- Simplifies local development workflow (no registry authentication)
- Zero-cost solution (no external registry required)
- Images built locally are immediately available to Minikube

**Implementation Approach**:
```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images (they go directly to Minikube's registry)
docker build -t todo-frontend:latest -f k8s/dockerfiles/frontend.Dockerfile ./frontend
docker build -t todo-backend:latest -f k8s/dockerfiles/backend.Dockerfile ./backend

# Set imagePullPolicy to Never in K8s manifests
# This prevents Kubernetes from trying to pull from external registry
```

**Configuration in Helm**:
```yaml
frontend:
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never  # Use local images only
```

**Alternatives Considered**:
- Docker Hub: Rejected due to push/pull overhead and potential rate limits
- Minikube registry addon: Rejected as more complex than using Docker daemon directly
- Local registry container: Rejected as unnecessary complexity for single-node cluster

---

### 4. Service Exposure Method

**Decision**: Use NodePort for frontend, ClusterIP for backend

**Rationale**:
- **Frontend (NodePort)**: Needs external access for browser testing
  - NodePort exposes service on each node's IP at a static port
  - Accessible via `minikube service frontend` or `http://<minikube-ip>:<nodeport>`
  - Simple and suitable for local development

- **Backend (ClusterIP)**: Internal service, accessed only by frontend
  - ClusterIP provides internal cluster networking
  - Frontend communicates with backend via service DNS (e.g., `http://backend:8000`)
  - More secure as backend is not externally exposed

**Access Pattern**:
```bash
# Get frontend URL
minikube service frontend --url

# Backend is accessed internally by frontend
# Frontend makes requests to: http://backend-service:8000/api/...
```

**Alternatives Considered**:
- LoadBalancer for both: Rejected because Minikube LoadBalancer requires additional setup (minikube tunnel)
- Ingress: Rejected as over-engineering for simple local deployment
- NodePort for both: Rejected because backend doesn't need external access

---

### 5. Resource Allocation Best Practices

**Decision**: Set conservative resource requests/limits suitable for local development

**Rationale**:
- Local machines have limited resources (4GB RAM, 2 CPU minimum)
- Must leave resources for OS and other applications
- Kubernetes needs resources for system pods (kube-system namespace)
- Conservative limits prevent cluster instability

**Recommended Allocations**:
```yaml
frontend:
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

backend:
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

**Minikube Cluster Configuration**:
```bash
# Start Minikube with appropriate resources
minikube start --cpus=2 --memory=3072 --driver=docker
```

**Resource Budget**:
- Total available: 3GB RAM, 2 CPUs
- Kubernetes system: ~500MB RAM, ~200m CPU
- Frontend: 256-512MB RAM, 250-500m CPU
- Backend: 256-512MB RAM, 250-500m CPU
- Remaining: ~1.5GB RAM for overhead and scaling

**Alternatives Considered**:
- No resource limits: Rejected because pods could consume all resources
- Higher limits: Rejected because local machines may not have sufficient resources
- Lower limits: Rejected because applications may not function properly

---

### 6. Network Configuration for Frontend-Backend Communication

**Decision**: Use Kubernetes DNS for service discovery with environment-based configuration

**Rationale**:
- Kubernetes provides built-in DNS for service discovery
- Services are accessible via DNS name: `<service-name>.<namespace>.svc.cluster.local`
- Short form works within same namespace: `<service-name>`
- Frontend needs to know backend URL at build time or runtime

**Implementation Approach**:

**Option 1: Environment Variable (Recommended)**
```yaml
# Frontend deployment
env:
  - name: NEXT_PUBLIC_API_URL
    value: "http://backend-service:8000"
```

**Option 2: ConfigMap**
```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  API_URL: "http://backend-service:8000"

# Frontend deployment references ConfigMap
envFrom:
  - configMapRef:
      name: frontend-config
```

**DNS Resolution**:
- Backend service name: `backend-service`
- Full DNS: `backend-service.default.svc.cluster.local`
- Frontend makes requests: `http://backend-service:8000/api/todos`

**Network Policy** (Optional for this phase):
- Not implementing network policies in Phase IV (out of scope)
- All pods can communicate freely within cluster
- Security hardening deferred to Phase V (production deployment)

**Alternatives Considered**:
- Hardcoded IPs: Rejected because IPs change and are not portable
- External DNS: Rejected as unnecessary for local cluster
- Service mesh (Istio): Rejected as over-engineering for local development

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Docker AI | Use with Claude fallback | Demonstrates AI-first approach with practical fallback |
| kubectl-ai | Install via krew, fallback to kubectl | Natural language interface for K8s operations |
| kagent | Minimal demonstration with fallback | Meets spec requirement with realistic constraints |
| Helm Structure | Standard multi-service chart | Industry best practice, parameterized configuration |
| Container Registry | Minikube Docker daemon | Zero-cost, simplified local workflow |
| Service Exposure | NodePort (frontend), ClusterIP (backend) | Appropriate access patterns for each service |
| Resource Allocation | Conservative requests/limits | Ensures stability on resource-constrained local machines |
| Network Config | Kubernetes DNS + env vars | Standard service discovery pattern |

## Next Steps

Phase 1 will generate:
1. **quickstart.md**: Step-by-step deployment guide incorporating AI DevOps tools
2. Detailed Dockerfile specifications for frontend and backend
3. Kubernetes manifest templates
4. Helm chart structure with values.yaml configuration

All decisions above will be implemented in Phase 2 tasks.
