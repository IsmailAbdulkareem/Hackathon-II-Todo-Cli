# Sub-Agents for Todo Spec-Driven Development

This directory contains specialized sub-agents designed to make development work easier by focusing on specific phases, technologies, and concerns.

## Agent Overview

### 🟢 Phase I: In-Memory Console App

| Agent | Purpose | When to Use |
|--------|---------|--------------|
| **[phase-01-console.md](./phase-01-console.md)** | Python CLI development with standard library only | Building domain models, CLI interfaces, in-memory state management |

### 🟡 Phase II: Full-Stack Web Application

| Agent | Purpose | When to Use |
|--------|---------|--------------|
| **[phase-02-frontend-arch.md](./phase-02-frontend-arch.md)** | Next.js + Tailwind + TypeScript frontend design | Designing pages, components, state management |
| **[phase-02-backend-api.md](./phase-02-backend-api.md)** | FastAPI / SQLModel backend development | Creating API endpoints, data models, validation |
| **[phase-02-data-persistence.md](./phase-02-data-persistence.md)** | SQLModel + Neon PostgreSQL database design | Designing schemas, migrations, data models |
| **[phase-02-integration.md](./phase-02-integration.md)** | Frontend ↔ Backend contract validation | Validating API contracts, TypeScript types, data flow |

### 🔵 Phase III: AI-Powered Chatbot

| Agent | Purpose | When to Use |
|--------|---------|--------------|
| **[phase-03-ai-interaction.md](./phase-03-ai-interaction.md)** | Conversation design for AI chatbot | Defining intents, prompts, conversation flows |
| **[phase-03-agent-orchestration.md](./phase-03-agent-orchestration.md)** | OpenAI Agents SDK / MCP agent architecture | Designing agent graphs, tool calling, memory |
| **[phase-03-safety-determinism.md](./phase-03-safety-determinism.md)** | AI reliability, guardrails, and fail-safe design | Implementing safety rules, deterministic outputs |

### 🟣 Phase IV: Local Kubernetes Deployment

| Agent | Purpose | When to Use |
|--------|---------|--------------|
| **[phase-04-containerization.md](./phase-04-containerization.md)** | Docker containerization and multi-service setup | Creating Dockerfiles, Docker Compose, image optimization |
| **[phase-04-k8s-architecture.md](./phase-04-k8s-architecture.md)** | Minikube + Helm K8s architecture | Designing pods, services, Helm charts, networking |
| **[phase-04-deployment-validation.md](./phase-04-deployment-validation.md)** | Runtime verification and health check design | Implementing health checks, rollback rules, monitoring |

### 🟪 Phase V: Cloud Deployment

| Agent | Purpose | When to Use |
|--------|---------|--------------|
| **[phase-05-cloud-deployment.md](./phase-05-cloud-deployment.md)** | Kafka + Dapr + DigitalOcean DOKS deployment | Deploying to cloud, event streaming, IaC |

### 🎯 Meta-Agent

| Agent | Purpose | When to Use |
|--------|---------|--------------|
| **[phase-coordinator.md](./phase-coordinator.md)** | Timeline & readiness control | Completing phases, quality gates, risk assessment |

## How to Use These Agents

### 1. Identify Your Task

First, determine what kind of work you're doing:

- **Phase I work** → Use `phase-01-console.md`
- **Frontend work** → Use `phase-02-frontend-arch.md`
- **Backend API work** → Use `phase-02-backend-api.md`
- **Database work** → Use `phase-02-data-persistence.md`
- **Integration work** → Use `phase-02-integration.md`
- **AI conversation work** → Use `phase-03-ai-interaction.md`
- **Agent orchestration** → Use `phase-03-agent-orchestration.md`
- **Safety/Determinism** → Use `phase-03-safety-determinism.md`
- **Containerization** → Use `phase-04-containerization.md`
- **Kubernetes** → Use `phase-04-k8s-architecture.md`
- **Deployment validation** → Use `phase-04-deployment-validation.md`
- **Cloud deployment** → Use `phase-05-cloud-deployment.md`
- **Phase completion** → Use `phase-coordinator.md`

### 2. Load the Agent

When you start working on a specific task, invoke the relevant agent:

```
Load agent: .claude/agents/phase-02-backend-api.md
```

This will provide you with:
- Core responsibilities
- Tech stack
- Project structure
- Design patterns
- Example code
- Integration points

### 3. Follow the Workflow

Each agent follows a consistent pattern:

1. **Understand the Context** - Read the agent documentation
2. **Plan Your Work** - Use the project structure and design principles
3. **Implement** - Follow the example code and patterns
4. **Validate** - Check against design principles and best practices
5. **Integrate** - Connect with other components using integration points

### 4. Use Generators

Agents reference available generator skills:

- `/gen.db-schema` - Generate database schemas
- `/gen.fastapi-endpoint` - Generate FastAPI endpoints
- `/gen.auth-integration` - Generate authentication code
- `/gen.dockerfile` - Generate Dockerfiles
- `/gen.helm-chart` - Generate Helm charts
- `/gen.mcp-tool` - Generate MCP tools

### 5. Coordinate with Phase Coordinator

When completing a phase, use the Phase Coordinator to validate:

```
Load agent: .claude/agents/phase-coordinator.md

# Then check phase completion
Checklist: Phase I exit criteria
```

## Agent Features

### Each Agent Includes:

1. **Overview** - What the agent specializes in
2. **Core Responsibilities** - Primary focus areas
3. **Tech Stack** - Tools and technologies used
4. **Commands Available** - Relevant commands and generators
5. **Design Principles** - Best practices to follow
6. **Project Structure** - Recommended file organization
7. **Example Code** - Working code patterns
8. **Integration Points** - How to work with other agents
9. **When to Use** - Specific scenarios for agent usage

### Common Patterns Across Agents:

- ✅ **SDD Workflow** - Follows Spec-Driven Development principles
- ✅ **Type Safety** - Emphasizes strong typing (Python types, TypeScript)
- ✅ **Testing** - Includes testing strategies and examples
- ✅ **Documentation** - Clear documentation and examples
- ✅ **Integration** - Defines how to connect with other systems

## Best Practices

### 1. Use the Right Agent

Don't try to do everything with one agent. Choose the specialist that matches your current task:

- **Building a Dockerfile?** → Use Containerization Agent
- **Creating an API endpoint?** → Use Backend API Agent
- **Designing a Kubernetes pod?** → Use K8s Architecture Agent

### 2. Follow Design Principles

Each agent has defined design principles. Follow them consistently:

- Phase I: Deterministic, clean layers, no I/O in domain
- Phase II: API-first, type safety, authentication
- Phase III: Guardrails, deterministic outputs, fail-safe
- Phase IV: Multi-stage builds, health checks, rollback strategy
- Phase V: Event-driven, IaC, monitoring

### 3. Validate Before Transitioning

Use the Phase Coordinator to validate completion before moving to the next phase:

```
1. Complete phase work
2. Run quality gates (tests, linting, type checking)
3. Check exit criteria checklist
4. Get Phase Coordinator approval
5. Transition to next phase
```

### 4. Track Dependencies

Some agents depend on outputs from others:

- **Data Persistence Agent** ← Backend API Agent (for models)
- **Integration Agent** ← Backend API Agent + Frontend Architecture Agent
- **Agent Orchestration Agent** ← AI Interaction Designer Agent
- **K8s Architecture Agent** ← Containerization Agent
- **Cloud Deployment Agent** ← All previous agents

## Quick Reference

### Task to Agent Mapping

```
I want to...
├─ Add a new feature to the console app
│  └─→ phase-01-console.md
├─ Design a new page in Next.js
│  └─→ phase-02-frontend-arch.md
├─ Create a new API endpoint
│  └─→ phase-02-backend-api.md
├─ Add a new database table
│  └─→ phase-02-data-persistence.md
├─ Fix a frontend-backend type mismatch
│  └─→ phase-02-integration.md
├─ Design a chatbot conversation flow
│  └─→ phase-03-ai-interaction.md
├─ Set up AI agent orchestration
│  └─→ phase-03-agent-orchestration.md
├─ Add guardrails to AI responses
│  └─→ phase-03-safety-determinism.md
├─ Create a Dockerfile
│  └─→ phase-04-containerization.md
├─ Design Kubernetes manifests
│  └─→ phase-04-k8s-architecture.md
├─ Add health checks to deployment
│  └─→ phase-04-deployment-validation.md
├─ Deploy to DigitalOcean
│  └─→ phase-05-cloud-deployment.md
└─ Complete Phase II and move to Phase III
   └─→ phase-coordinator.md
```

## Getting Started

1. **Explore the agents**: Read through each agent's documentation to understand capabilities
2. **Identify your phase**: Determine which phase you're working in
3. **Load the appropriate agent**: Use the specialist for your current task
4. **Follow the workflow**: Use the provided structure, examples, and best practices
5. **Validate completion**: Use Phase Coordinator to ensure quality before transitioning

## Support

For questions or issues:
- Review the specific agent's documentation
- Check integration points between agents
- Use Phase Coordinator for phase transition issues
- Refer to project constitution: `.specify/memory/constitution.md`

---

**Happy building! 🚀**
