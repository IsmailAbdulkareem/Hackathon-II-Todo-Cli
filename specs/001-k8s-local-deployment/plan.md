# Implementation Plan: Local Kubernetes Deployment

**Branch**: `001-k8s-local-deployment` | **Date**: 2026-01-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-k8s-local-deployment/spec.md`

## Summary

Deploy the existing Phase III Todo Chatbot (frontend + backend) to a local Kubernetes cluster using Minikube, with all infrastructure artifacts (Dockerfiles, Helm charts, Kubernetes manifests) generated via AI-assisted tools (Docker AI, kubectl-ai, kagent). The deployment must support:

- Multi-stage Docker builds for optimized container images
- Helm-based declarative deployment with configurable parameters
- Health monitoring with liveness and readiness probes
- Service discovery using Kubernetes DNS
- Resource management with defined CPU/memory limits
- AI-assisted operations with manual kubectl fallbacks

**Technical Approach**: Use Claude Code to orchestrate AI tools for generating infrastructure-as-code artifacts, build and test containers locally, deploy to Minikube with Helm, and validate end-to-end functionality through the Kubernetes service mesh.

## Technical Context

**Containerization**: Docker Desktop 4.53+ or Docker Engine
**Container Orchestration**: Kubernetes via Minikube (local cluster)
**Package Manager**: Helm v3
**AI DevOps Tools**: Docker AI (Gordon), kubectl-ai, kagent
**Frontend Stack**: Next.js 16+, React 19 (from Phase III)
**Backend Stack**: Python 3.13+, FastAPI, MCP Server (from Phase III)
**Database**: External Neon PostgreSQL (existing from Phase III)
**Testing**: Container smoke tests, Kubernetes health checks, end-to-end flow validation
**Target Platform**: Local development (Minikube on Docker Desktop)
**Project Type**: Infrastructure/Deployment (containerization and orchestration)

**Performance Goals**:
- Container build time: < 5 minutes for both images
- Pod startup time: < 2 minutes to Running status
- End-to-end response time: < 3 seconds
- Scaling time: < 1 minute for replica changes

**Constraints**:
- Minikube cluster: 4 CPUs, 6GB memory
- Frontend pods: 250m CPU, 512Mi memory per replica
- Backend pods: 500m CPU, 1Gi memory per replica
- Initial replicas: Frontend 2, Backend 1
- No manual YAML/Dockerfile writing (AI-generated only)

**Scale/Scope**:
- 2 containerized applications (frontend, backend)
- 2 Helm charts with 4-5 Kubernetes resources each
- 1 local Kubernetes cluster
- 3-4 AI-assisted operational workflows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Applicable Constitution Principles** (from `.specify/memory/constitution.md`):

1. **Simplicity First**: ✅ Using standard Kubernetes patterns (Deployment, Service, ConfigMap, Secret) without unnecessary abstractions. Helm charts provide declarative configuration without custom operators or CRDs.

2. **AI-Assisted Workflow**: ✅ All infrastructure artifacts generated via AI tools (Docker AI, kubectl-ai, kagent) with manual fallbacks documented. Aligns with project's AI-first development approach.

3. **Testability**: ✅ Each user story independently testable. Containers can be tested locally before Kubernetes deployment. Health probes enable automated validation.

4. **Documentation**: ✅ FR-015 requires reproducible commands. SC-006 mandates complete deployment documentation. All AI operations have manual kubectl equivalents.

5. **Security**: ✅ FR-004 prohibits baked-in secrets. FR-010 requires Kubernetes Secrets for sensitive data. External database connection uses secure configuration.

**Constitution Compliance**: ✅ PASS - No violations detected. Deployment approach follows established patterns and project principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-k8s-local-deployment/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Application analysis and tool validation
├── quickstart.md        # Phase 1: Deployment quickstart guide
├── contracts/           # Phase 1: API contracts and configuration schemas
│   ├── dockerfile-requirements.md
│   ├── helm-chart-structure.md
│   └── kubernetes-resources.md
└── tasks.md             # Phase 2: Detailed implementation tasks (created by /sp.tasks)
```

### Infrastructure Artifacts (repository root)

```text
phase-04-k8s-local/
├── frontend/                    # Existing Phase III frontend code
│   ├── src/                     # Next.js application source
│   ├── package.json
│   └── Dockerfile               # [TO BE GENERATED] Multi-stage build
│
├── backend/                     # Existing Phase III backend code
│   ├── src/                     # FastAPI + MCP Server source
│   ├── requirements.txt
│   └── Dockerfile               # [TO BE GENERATED] Multi-stage build
│
├── k8s/                         # [TO BE CREATED] Kubernetes manifests
│   ├── helm/
│   │   ├── todo-frontend/       # [TO BE GENERATED] Frontend Helm chart
│   │   │   ├── Chart.yaml
│   │   │   ├── values.yaml
│   │   │   └── templates/
│   │   │       ├── deployment.yaml
│   │   │       ├── service.yaml
│   │   │       ├── configmap.yaml
│   │   │       └── _helpers.tpl
│   │   │
│   │   └── todo-backend/        # [TO BE GENERATED] Backend Helm chart
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       └── templates/
│   │           ├── deployment.yaml
│   │           ├── service.yaml
│   │           ├── configmap.yaml
│   │           ├── secret.yaml
│   │           └── _helpers.tpl
│   │
│   └── docs/                    # [TO BE CREATED] Deployment documentation
│       ├── docker-ai-usage.md
│       ├── kubectl-ai-usage.md
│       ├── kagent-usage.md
│       └── manual-fallbacks.md
│
└── README.md                    # [TO BE UPDATED] Phase IV overview
```

**Structure Decision**: Infrastructure-focused layout with Dockerfiles co-located with application code and Helm charts centralized in `k8s/helm/`. This follows Kubernetes community conventions and enables independent versioning of infrastructure artifacts. The `k8s/docs/` directory will contain AI tool usage guides and manual fallback procedures per FR-018.

## Complexity Tracking

> **No constitution violations requiring justification.**

This deployment follows standard Kubernetes patterns without introducing unnecessary complexity. The AI-assisted workflow is a project requirement, not a complexity addition.

---

## Phase 0: Research & Discovery

**Objective**: Understand existing Phase III applications, validate AI tool availability, and identify containerization requirements.

### Research Tasks

#### R1: Analyze Frontend Application Structure
- **Goal**: Understand Next.js build process, dependencies, and runtime requirements
- **Method**: Inspect `phase-04-k8s-local/frontend/` directory structure, package.json, and build scripts
- **Deliverable**: Document in `research.md`:
  - Node.js version requirement
  - Build command and output directory
  - Runtime dependencies vs dev dependencies
  - Environment variables needed
  - Static assets and public files
  - Port configuration (default 3000)

#### R2: Analyze Backend Application Structure
- **Goal**: Understand FastAPI application, MCP Server integration, and Python dependencies
- **Method**: Inspect `phase-04-k8s-local/backend/` directory structure, requirements.txt, and entry points
- **Deliverable**: Document in `research.md`:
  - Python version requirement (3.13+)
  - Application entry point (main.py or similar)
  - Runtime dependencies from requirements.txt
  - Environment variables needed (DATABASE_URL, API keys)
  - Port configuration (default 8000)
  - Health check endpoint implementation

#### R3: Validate AI Tool Availability
- **Goal**: Confirm Docker AI, kubectl-ai, and kagent are installed and functional
- **Method**: Execute test commands for each tool
- **Commands**:
  ```bash
  docker ai --version
  kubectl-ai --version
  kagent --version
  ```
- **Deliverable**: Document in `research.md`:
  - Tool versions and installation status
  - Authentication/configuration requirements
  - Known limitations or constraints
  - Fallback strategy if tools unavailable

#### R4: Identify External Dependencies
- **Goal**: Document external services and their connection requirements
- **Method**: Review Phase III configuration for database and API integrations
- **Deliverable**: Document in `research.md`:
  - Neon PostgreSQL connection string format
  - Required environment variables for database connection
  - API keys or tokens needed (Anthropic API, etc.)
  - Network connectivity requirements

#### R5: Define Health Check Endpoints
- **Goal**: Verify or implement /health endpoints in both applications
- **Method**: Check existing code for health check routes, implement if missing
- **Deliverable**: Document in `research.md`:
  - Frontend /health endpoint (returns 200 OK when ready)
  - Backend /health endpoint (returns 200 OK, optionally checks DB connection)
  - Response format and status codes
  - Dependencies checked by health endpoint

### Research Deliverable: `research.md`

Create `specs/001-k8s-local-deployment/research.md` with sections:
1. Frontend Application Analysis
2. Backend Application Analysis
3. AI Tool Validation Results
4. External Dependencies Inventory
5. Health Check Endpoint Specification
6. Containerization Readiness Assessment

**Exit Criteria**: All research tasks completed, no blocking issues identified, AI tools validated or fallback strategy documented.

---

## Phase 1: Design & Architecture

**Objective**: Design Dockerfile structure, Helm chart architecture, and configuration management strategy.

### Design Tasks

#### D1: Design Frontend Dockerfile
- **Goal**: Define multi-stage build strategy for Next.js application
- **Method**: Use Docker AI to generate initial Dockerfile, review and document structure
- **Deliverable**: Document in `contracts/dockerfile-requirements.md`:
  - Stage 1: Dependencies (install Node.js, copy package files, npm install)
  - Stage 2: Build (copy source, run build command, generate static output)
  - Stage 3: Runtime (minimal Node.js image, copy build artifacts, expose port 3000)
  - Health check command: `curl -f http://localhost:3000/health || exit 1`
  - Environment variables: NEXT_PUBLIC_API_URL
  - Image size target: < 500MB

#### D2: Design Backend Dockerfile
- **Goal**: Define multi-stage build strategy for FastAPI application
- **Method**: Use Docker AI to generate initial Dockerfile, review and document structure
- **Deliverable**: Document in `contracts/dockerfile-requirements.md`:
  - Stage 1: Dependencies (Python 3.13, copy requirements.txt, pip install)
  - Stage 2: Runtime (copy application code, expose port 8000)
  - Health check command: `curl -f http://localhost:8000/health || exit 1`
  - Environment variables: DATABASE_URL, ANTHROPIC_API_KEY
  - Image size target: < 300MB
  - Non-root user for security

#### D3: Design Helm Chart Structure
- **Goal**: Define Helm chart organization and template hierarchy
- **Method**: Use kubectl-ai to generate chart scaffolding, document structure
- **Deliverable**: Document in `contracts/helm-chart-structure.md`:
  - Chart.yaml metadata (name, version, appVersion)
  - values.yaml schema (replicas, image, resources, probes, config)
  - Template files (Deployment, Service, ConfigMap, Secret)
  - Helper functions in _helpers.tpl (labels, selectors, names)
  - Parameterization strategy (what's configurable vs hardcoded)

#### D4: Design Kubernetes Resource Specifications
- **Goal**: Define exact specifications for each Kubernetes resource
- **Method**: Document resource requirements based on clarified spec values
- **Deliverable**: Document in `contracts/kubernetes-resources.md`:

  **Frontend Deployment**:
  - Replicas: 2 (configurable via values.yaml)
  - Image: todo-frontend:latest
  - Resources: requests/limits 250m CPU, 512Mi memory
  - Liveness probe: /health, 30s initial, 10s period, 3 failures
  - Readiness probe: /health, 5s initial, 5s period, 3 failures
  - Environment: NEXT_PUBLIC_API_URL from ConfigMap

  **Backend Deployment**:
  - Replicas: 1 (configurable via values.yaml)
  - Image: todo-backend:latest
  - Resources: requests/limits 500m CPU, 1Gi memory
  - Liveness probe: /health, 30s initial, 10s period, 3 failures
  - Readiness probe: /health, 5s initial, 5s period, 3 failures
  - Environment: DATABASE_URL from Secret, other config from ConfigMap

  **Frontend Service**:
  - Type: NodePort
  - Port: 3000
  - Selector: app=todo-frontend

  **Backend Service**:
  - Type: ClusterIP
  - Port: 8000
  - Selector: app=todo-backend

  **ConfigMaps**:
  - Frontend: NEXT_PUBLIC_API_URL=http://todo-backend:8000
  - Backend: Non-sensitive application configuration

  **Secrets**:
  - Backend: DATABASE_URL, ANTHROPIC_API_KEY (base64 encoded)

#### D5: Design Configuration Management Strategy
- **Goal**: Define how configuration flows from values.yaml to pods
- **Method**: Document configuration hierarchy and override mechanisms
- **Deliverable**: Document in `contracts/helm-chart-structure.md`:
  - Default values in values.yaml
  - Environment-specific overrides (dev, staging, prod - though only dev for Phase IV)
  - Secret management approach (manual creation, not in Git)
  - ConfigMap vs Secret decision criteria
  - Configuration validation strategy

#### D6: Create Deployment Quickstart Guide
- **Goal**: Provide step-by-step deployment instructions
- **Method**: Document complete workflow from prerequisites to validation
- **Deliverable**: Create `quickstart.md` with sections:
  1. Prerequisites (Docker, Minikube, kubectl, Helm, AI tools)
  2. Minikube Setup (start with 4 CPUs, 6GB memory)
  3. Build Docker Images (using Docker AI)
  4. Load Images to Minikube (minikube image load)
  5. Create Secrets (kubectl create secret)
  6. Deploy with Helm (helm install commands)
  7. Verify Deployment (kubectl get pods, services)
  8. Access Application (minikube service URL)
  9. Test End-to-End Flow (send chat message)
  10. AI-Assisted Operations Examples (kubectl-ai, kagent)
  11. Troubleshooting Common Issues
  12. Cleanup (helm uninstall, minikube stop)

### Design Deliverables

1. `contracts/dockerfile-requirements.md` - Dockerfile specifications
2. `contracts/helm-chart-structure.md` - Helm chart architecture
3. `contracts/kubernetes-resources.md` - K8s resource specifications
4. `quickstart.md` - Deployment guide

**Exit Criteria**: All design documents completed, architecture reviewed, no ambiguities in resource specifications.

---

## Phase 2: Implementation Approach

**Objective**: Outline the implementation workflow (detailed tasks will be in `tasks.md` via `/sp.tasks`).

### Implementation Workflow

The implementation will follow the prioritized user stories (P1 → P2 → P3 → P4):

#### Phase 2.1: Containerization (User Story 1 - P1)
1. Generate Frontend Dockerfile using Docker AI
2. Generate Backend Dockerfile using Docker AI
3. Build frontend Docker image
4. Build backend Docker image
5. Test containers locally with docker run
6. Verify health check endpoints
7. Validate database connectivity from backend container

#### Phase 2.2: Cluster Setup (User Story 2 - P2)
1. Start Minikube with specified resources (4 CPUs, 6GB memory)
2. Verify cluster health (kubectl get nodes)
3. Load Docker images into Minikube
4. Test cluster with simple pod deployment

#### Phase 2.3: Helm Deployment (User Story 3 - P3)
1. Generate frontend Helm chart using kubectl-ai
2. Generate backend Helm chart using kubectl-ai
3. Create Kubernetes Secrets for sensitive configuration
4. Deploy frontend with Helm
5. Deploy backend with Helm
6. Verify pod status and health checks
7. Test service discovery (frontend → backend)
8. Validate end-to-end user flow

#### Phase 2.4: AI Operations (User Story 4 - P4)
1. Document kubectl-ai usage for common operations
2. Document kagent usage for cluster analysis
3. Test scaling operations with kubectl-ai
4. Test health checks with kubectl-ai
5. Test troubleshooting with kubectl-ai
6. Document manual kubectl fallbacks
7. Create operational runbook

### Testing Strategy

**Container Testing**:
- Build success (exit code 0, no errors)
- Image size validation (< targets)
- Container startup (docker run succeeds)
- Health check response (curl /health returns 200)
- Database connectivity (backend connects to Neon)

**Kubernetes Testing**:
- Pod status (all pods Running)
- Health probe success (liveness and readiness pass)
- Service endpoints (kubectl get endpoints shows IPs)
- Resource limits (kubectl describe pod shows correct limits)
- Configuration injection (env vars present in pods)

**Integration Testing**:
- Frontend accessible via Minikube service URL
- Backend accessible from frontend (service discovery works)
- End-to-end flow (send chat message, receive AI response)
- Response time < 3 seconds (SC-003)

**Operational Testing**:
- Scaling (kubectl scale or kubectl-ai)
- Configuration updates (edit ConfigMap, restart pods)
- Health monitoring (kubectl-ai health checks)
- Troubleshooting (kubectl-ai diagnostics)

### Risk Mitigation

**Risk 1: Docker AI unavailable or generates invalid Dockerfiles**
- Mitigation: Document manual Dockerfile creation as fallback
- Validation: Test Docker AI early in Phase 2.1

**Risk 2: Image pull errors in Minikube**
- Mitigation: Use `minikube image load` to load local images
- Validation: Test image loading before Helm deployment

**Risk 3: Resource constraints in Minikube**
- Mitigation: Monitor resource usage, adjust pod limits if needed
- Validation: Use `kubectl top nodes` and `kubectl top pods`

**Risk 4: Service discovery failures**
- Mitigation: Verify Kubernetes DNS, use fully qualified service names if needed
- Validation: Test DNS resolution from within pods

**Risk 5: Health check failures**
- Mitigation: Implement robust /health endpoints, adjust probe timing if needed
- Validation: Test health endpoints locally before Kubernetes deployment

---

## Architectural Decisions

### AD-1: Multi-Stage Docker Builds
**Decision**: Use multi-stage builds for both frontend and backend
**Rationale**: Minimizes final image size by separating build dependencies from runtime dependencies. Aligns with FR-003 requirement.
**Alternatives Considered**: Single-stage builds (rejected: larger images, slower deployments)

### AD-2: Helm for Deployment Management
**Decision**: Use Helm charts for Kubernetes resource management
**Rationale**: Provides parameterization, versioning, and lifecycle management (install, upgrade, rollback). Industry standard for Kubernetes deployments.
**Alternatives Considered**: Raw kubectl apply (rejected: no parameterization or versioning), Kustomize (rejected: less mature ecosystem)

### AD-3: Separate Helm Charts per Service
**Decision**: Create independent Helm charts for frontend and backend
**Rationale**: Enables independent deployment, scaling, and versioning of each service. Follows microservices best practices.
**Alternatives Considered**: Single umbrella chart (rejected: tight coupling, harder to manage independently)

### AD-4: ConfigMap for Service Discovery
**Decision**: Use ConfigMap to inject NEXT_PUBLIC_API_URL into frontend
**Rationale**: Non-sensitive configuration, needs to be accessible at build time for Next.js. Kubernetes DNS provides runtime resolution.
**Alternatives Considered**: Hardcoded URL (rejected: not configurable), Service environment variables (rejected: Next.js needs compile-time value)

### AD-5: External Database (No StatefulSet)
**Decision**: Connect to existing external Neon PostgreSQL database
**Rationale**: Reuses Phase III infrastructure, avoids complexity of StatefulSet management. Aligns with FR-014 and out-of-scope constraints.
**Alternatives Considered**: Deploy PostgreSQL in Kubernetes (rejected: out of scope, adds operational complexity)

### AD-6: NodePort for Frontend Service
**Decision**: Use NodePort service type for frontend (not LoadBalancer)
**Rationale**: Minikube doesn't support LoadBalancer natively. NodePort provides external access via `minikube service` command.
**Alternatives Considered**: LoadBalancer (rejected: requires cloud provider), Ingress (rejected: out of scope per spec)

### AD-7: AI-First with Manual Fallbacks
**Decision**: Generate all infrastructure artifacts with AI tools, document manual alternatives
**Rationale**: Aligns with project's AI-assisted development approach (FR-016, FR-017, FR-018). Ensures resilience if AI tools fail.
**Alternatives Considered**: Manual-first approach (rejected: doesn't meet spec requirement for AI-generated artifacts)

---

## Success Validation

The implementation will be considered successful when all success criteria (SC-001 through SC-007) are met:

✅ **SC-001**: Container builds complete in < 5 minutes
✅ **SC-002**: Pods reach Running status in < 2 minutes
✅ **SC-003**: End-to-end flow works with < 3 second response time
✅ **SC-004**: Scaling completes in < 1 minute
✅ **SC-005**: Configuration changes work without image rebuild
✅ **SC-006**: Complete deployment documentation exists
✅ **SC-007**: AI operations work with documented fallbacks

**Validation Method**: Execute complete deployment from scratch following `quickstart.md`, measure all timing criteria, verify all functional requirements.

---

## Next Steps

1. **Execute Phase 0**: Run research tasks, create `research.md`
2. **Execute Phase 1**: Complete design tasks, create contract documents and `quickstart.md`
3. **Run `/sp.tasks`**: Generate detailed implementation tasks in `tasks.md`
4. **Execute Phase 2**: Implement containerization, deployment, and operations per task list
5. **Validate Success**: Execute validation checklist, measure success criteria
6. **Document Completion**: Update README, create operational runbook

**Estimated Effort**:
- Phase 0 (Research): 2-3 hours
- Phase 1 (Design): 3-4 hours
- Phase 2 (Implementation): 6-8 hours
- Total: 11-15 hours

**Dependencies**:
- Phase III applications must be functional
- Docker Desktop, Minikube, kubectl, Helm must be installed
- AI tools (Docker AI, kubectl-ai, kagent) should be available (fallbacks documented if not)
