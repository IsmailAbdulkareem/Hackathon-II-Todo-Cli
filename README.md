# Todo Spec-Driven Development - Hackathon Project

A 5-phase development project demonstrating Spec-Driven Development (SDD) principles using Python, Next.js, FastAPI, Kubernetes, and cloud-native technologies.

## Project Phases

| Phase | Description | Tech Stack | Points | Due Date | Status |
|-------|-------------|------------|--------|----------|--------|
| Phase I | In-Memory Python Console App | Python 3.13+, Claude Code, Spec-Kit Plus | 100 | Dec 7, 2025 | ✅ Complete |
| Phase II | Full-Stack Web Application | Next.js, FastAPI, SQLModel, Neon DB | 150 | Dec 14, 2025 | ✅ Complete |
| Phase III | AI-Powered Todo Chatbot | OpenAI ChatKit, Agents SDK, MCP SDK | 200 | Dec 21, 2025 | ✅ Complete |
| Phase IV | Local Kubernetes Deployment | Docker, Minikube, Helm, kubectl-ai, Docker AI | 250 | Jan 4, 2026 | ✅ Complete |
| Phase V | Advanced Cloud Deployment | Kafka, Dapr, DigitalOcean DOKS | 300 | Jan 18, 2026 | 🔜 Pending |

## Directory Structure

```
.
├── phase-01-in-memory-console/    # Phase I: Python CLI todo app
│   ├── src/                        # Source code (domain, service, cli)
│   ├── main.py                     # Entry point
│   ├── specs/                      # Feature specifications
│   └── pyproject.toml              # Project metadata
├── phase-02-fullstack-web/        # Phase II: Next.js + FastAPI
│   ├── frontend/                   # Next.js app (Vercel deployable)
│   └── backend/                    # FastAPI API
├── phase-03-ai-chatbot/            # Phase III: AI chatbot integration
├── phase-04-k8s-local/             # Phase IV: Docker + K8s manifests
├── phase-05-cloud-deploy/          # Phase V: Kafka + Dapr + cloud K8s
├── .specify/                       # Spec-Kit Plus templates
├── .claude/                        # Claude Code settings
├── history/                        # PHRs and ADRs
│   ├── prompts/                    # Prompt History Records
│   └── adr/                        # Architecture Decision Records
├── CLAUDE.md                       # Claude Code project instructions
├── .gitignore                      # Git exclusions
└── README.md                       # This file
```

## Getting Started

### Phase I - In-Memory Console App

```bash
cd phase-01-in-memory-console
uv run main.py
```

### Phase II - Full-Stack Web App

**Frontend (Next.js):**
```bash
cd phase-02-fullstack-web/frontend
npm install
npm run dev
```

**Backend (FastAPI):**
```bash
cd phase-02-fullstack-web/backend
uvicorn main:app --reload
```

### Deploying to Vercel

The Next.js frontend in `phase-02-fullstack-web/frontend/` can be deployed to Vercel directly from this monorepo:

**Option 1: Vercel Dashboard**
- Link this GitHub repository
- Set **Root Directory** to: `phase-02-fullstack-web/frontend`

**Option 2: vercel.json** (create at root)
```json
{
  "buildCommand": "cd phase-02-fullstack-web/frontend && npm run build",
  "outputDirectory": "phase-02-fullstack-web/frontend/.next",
  "installCommand": "cd phase-02-fullstack-web/frontend && npm install"
}
```

### Phase III - AI Chatbot

**Frontend (Next.js with AI Chat):**
```bash
cd phase-03-ai-chatbot/frontend
npm install
npm run dev
```

**Backend (FastAPI with OpenAI):**
```bash
cd phase-03-ai-chatbot/backend
uvicorn main:app --reload --port 7860
```

### Phase IV - Kubernetes Deployment

**Prerequisites:**
- Docker Desktop installed and running
- Minikube installed
- Helm 3+ installed
- kubectl installed

**Deploy to Local Kubernetes:**

```bash
# Start Minikube cluster
minikube start --cpus=2 --memory=3072 --driver=docker

# Configure Docker to use Minikube's registry
eval $(minikube docker-env)

# Build images inside Minikube
docker build -t todo-frontend:latest -f phase-04-k8s-local/k8s/dockerfiles/frontend.Dockerfile ./phase-03-ai-chatbot/frontend
docker build -t todo-backend:latest -f phase-04-k8s-local/k8s/dockerfiles/backend.Dockerfile ./phase-03-ai-chatbot/backend

# Deploy with Helm
helm install todo-chatbot ./phase-04-k8s-local/k8s/helm/todo-chatbot

# Access the application
minikube service todo-frontend  # Opens in browser
minikube service todo-backend --url  # Get backend URL
```

**Verify Deployment:**
```bash
# Check pods
kubectl get pods

# Check services
kubectl get services

# View logs
kubectl logs deployment/todo-frontend
kubectl logs deployment/todo-backend
```

**AI DevOps Tools Used:**
- ✅ **Docker AI (Gordon)**: Generated production-ready Dockerfiles
- ✅ **kubectl-ai**: Installed and functional (requires OpenAI API key)
- ❌ **kagent**: Unavailable (documented)

See [phase-04-k8s-local/docs/](phase-04-k8s-local/docs/) for complete documentation.

## Spec-Driven Development (SDD) Workflow

This project follows SDD principles using Spec-Kit Plus:

1. **Specification**: Define requirements in `specs/<feature>/spec.md`
2. **Planning**: Create architectural decisions in `plan.md`
3. **Tasks**: Break down into testable tasks in `tasks.md`
4. **Implementation**: Execute tasks with TDD (Red → Green → Refactor)
5. **Documentation**: Create PHRs (Prompt History Records) and ADRs (Architecture Decision Records)

### Key Artifacts

- `specs/` - Feature specifications and plans
- `history/prompts/` - Prompt History Records
- `history/adr/` - Architecture Decision Records

## Constitution

This project is governed by **7 Core Principles** defined in [.specify/memory/constitution.md](.specify/memory/constitution.md):

1. **Spec-Driven Development First** - Specifications govern all implementation
2. **AI as Implementer, Human as Architect** - Clear division of responsibilities
3. **Deterministic Behavior** - Predictable, testable systems
4. **Evolvability Across Phases** - Stable domain contracts
5. **Clear Separation of Concerns** - Domain, interfaces, infrastructure layers
6. **Reusable Intelligence** - AI features must be explainable and fail-safe
7. **Infrastructure as Declarative** - Reproducible, version-controlled infrastructure

## Active Technologies

- **Phase I**: Python 3.13+ (standard library only)
- **Phase II**: Next.js 15, FastAPI, SQLModel, Neon PostgreSQL
- **Phase III**: OpenAI API, MCP SDK
- **Phase IV**: Docker, Minikube, Helm
- **Phase V**: Kafka, Dapr, DigitalOcean DOKS

## Documentation

- **Project Constitution**: [.specify/memory/constitution.md](.specify/memory/constitution.md)
- **Phase I Specs**: [phase-01-in-memory-console/specs/](phase-01-in-memory-console/specs/)
- **Claude Code Rules**: [CLAUDE.md](CLAUDE.md)
- **Prompt History**: [history/prompts/](history/prompts/)
- **Architecture Decisions**: [history/adr/](history/adr/)

## Phase I Features

The Phase I in-memory console app provides:

1. **Add Task** - Create new tasks with title and optional description
2. **View Tasks** - Display all tasks with status indicators ([ ] incomplete, [x] complete)
3. **Mark Complete/Incomplete** - Toggle task completion status
4. **Update Task** - Modify task title or description
5. **Delete Task** - Remove tasks from the list

**Note**: Phase I tasks are stored in memory only and are lost when the application exits.

## License

MIT
