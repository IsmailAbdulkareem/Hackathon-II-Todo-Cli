# Implementation Plan: Phase 5 Part A - Advanced Task Management Features

**Branch**: `001-phase-05-advanced-features` | **Date**: 2026-02-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-05-advanced-features/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Transform the existing monolithic Todo application into TaskAI - a next-generation task management system with dual interface design (Chat Mode + Tasks Mode), advanced task features (priorities, tags, search, filters, due dates, reminders, recurring tasks), and event-driven microservices architecture. The system will be restructured into 4 independent microservices communicating via Kafka events and coordinated through Dapr, supporting 10,000+ concurrent users with real-time synchronization between interfaces.

## Technical Context

**Language/Version**: Python 3.13+ (backend services), TypeScript/Node.js 20+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, Dapr Python SDK, asyncpg (PostgreSQL), aiokafka, Resend (email), OpenAI SDK (chat)
- Frontend: Next.js 16+, React 19, Tailwind CSS, Dapr JavaScript SDK
**Storage**: PostgreSQL 15+ (shared database with service-specific schemas: public, tasks, notifications, audit)
**Testing**: pytest (Python backend), Jest/Vitest (TypeScript frontend)
**Target Platform**: Kubernetes (Minikube for local development, AKS/GKE/OKE for cloud deployment)
**Project Type**: Microservices web application (4 services: Backend API, Recurring Service, Notification Service, Frontend)
**Performance Goals**:
- Real-time sync: <100ms between interfaces
- Search/filter: <300ms for 1000+ tasks
- Autocomplete: <200ms for tag suggestions
- Concurrent users: 10,000+ without degradation
**Constraints**:
- Reminder delivery: <5 seconds from scheduled time
- Recurring task creation: <5 seconds after completion
- API response time: <200ms p95 latency
**Scale/Scope**:
- Users: 10,000 concurrent, unlimited total
- Tasks: 10,000 per user
- Tags: 100 unique per user, 10 per task
- Reminders: 5 per task

## Constitution Check (Post-Design Re-evaluation)

*GATE: Re-checked after Phase 1 design completion.*

### Principle I: Spec-Driven Development First
✅ **PASS** - Complete specification exists with all requirements defined. Planning artifacts (research.md, data-model.md, contracts/, quickstart.md) created before implementation.

### Principle II: AI as Implementer, Human as Architect
✅ **PASS** - Human architect approved microservices architecture and technology choices. AI (Claude Code) generated planning artifacts based on approved specifications.

### Principle III: Deterministic Behavior Across Non-LLM Components
✅ **PASS** - Data model defines deterministic state transitions. Event schemas ensure predictable behavior. Only chat interface uses LLM with explicit tool constraints.

### Principle IV: Evolvability Across Phases Without Breaking Domain Contracts
✅ **PASS** - Domain model (Task, Tag, Reminder, RecurrenceRule) remains stable across services. Service boundaries defined with clear API contracts. Database schema supports evolution with service-specific schemas.

### Principle V: Clear Separation of Domain Logic, Interfaces, and Infrastructure
✅ **PASS** - Architecture enforces separation:
- **Domain Logic**: Task entities, recurrence calculation, reminder scheduling (in services/)
- **Interfaces**: REST API (OpenAPI), Events (Kafka schemas), Chat (MCP tools)
- **Infrastructure**: PostgreSQL schemas, Kafka topics, Dapr components, Kubernetes manifests

### Principle VI: Reusable Intelligence Over One-Off Solutions
✅ **PASS** - Chat interface uses 18 reusable MCP tools. Event-driven patterns enable reusable async processing. Dapr provides reusable resilience patterns.

### Principle VII: Infrastructure as Declarative and Reproducible
✅ **PASS** - All infrastructure is declarative:
- Kubernetes manifests (YAML)
- Helm charts (templated YAML)
- Dapr components (YAML)
- Docker Compose (YAML)
- Database schemas (SQL migrations)

**Post-Design Evaluation**: All constitutional principles satisfied. Complexity justified in Complexity Tracking section. Ready for implementation phase.

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-05-advanced-features/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── backend-api.openapi.yaml
│   ├── recurring-service.yaml
│   ├── notification-service.yaml
│   └── events.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Legend**: ✅ EXISTS (already implemented) | 🆕 NEW (needs creation) | 📝 (needs extension)

```text
phase-05-cloud-deploy/
├── services/                           # Microservices (separate deployable units)
│   │
│   ├── backend-api/                    # ✅ EXISTS - Core API service (Port 8000)
│   │   ├── src/
│   │   │   ├── api/                    # ✅ EXISTS - FastAPI routes
│   │   │   │   ├── __init__.py         # ✅ EXISTS
│   │   │   │   ├── auth.py             # 📝 EXISTS (needs JWT + user registration)
│   │   │   │   ├── tasks.py            # 📝 EXISTS (needs tags, priorities, reminders, recurrence)
│   │   │   │   ├── chat.py             # 🆕 NEW - Chat/MCP endpoints
│   │   │   │   ├── tags.py             # 🆕 NEW - Tag management
│   │   │   │   └── search.py           # 🆕 NEW - Search & filter endpoints
│   │   │   │
│   │   │   ├── core/                   # ✅ EXISTS - Core utilities
│   │   │   │   ├── __init__.py         # ✅ EXISTS
│   │   │   │   ├── config.py           # ✅ EXISTS (needs Kafka/Dapr config)
│   │   │   │   ├── database.py         # ✅ EXISTS (needs schema support)
│   │   │   │   ├── auth.py             # ✅ EXISTS (needs JWT utilities)
│   │   │   │   └── dapr.py             # 🆕 NEW - Dapr client wrapper
│   │   │   │
│   │   │   ├── models/                 # ✅ EXISTS - Domain models
│   │   │   │   ├── __init__.py         # ✅ EXISTS
│   │   │   │   ├── task.py             # 📝 EXISTS (needs priority, tags, recurrence fields)
│   │   │   │   ├── tag.py              # 🆕 NEW - Tag entity
│   │   │   │   ├── reminder.py         # 🆕 NEW - Reminder entity
│   │   │   │   └── recurrence.py       # 🆕 NEW - Recurrence rule entity
│   │   │   │
│   │   │   ├── services/               # ✅ EXISTS - Business logic
│   │   │   │   ├── __init__.py         # ✅ EXISTS
│   │   │   │   ├── task_service.py     # 📝 EXISTS (needs advanced features)
│   │   │   │   ├── tag_service.py      # 🆕 NEW - Tag operations
│   │   │   │   ├── search_service.py   # 🆕 NEW - Search & filter logic
│   │   │   │   ├── event_publisher.py  # 🆕 NEW - Kafka event publishing
│   │   │   │   └── mcp_server.py       # 🆕 NEW - MCP server with 18 tools
│   │   │   │
│   │   │   └── schemas/                # ✅ EXISTS - Pydantic schemas
│   │   │       ├── __init__.py         # ✅ EXISTS
│   │   │       ├── task.py             # 📝 EXISTS (needs new fields)
│   │   │       ├── tag.py              # 🆕 NEW
│   │   │       └── reminder.py         # 🆕 NEW
│   │   │
│   │   ├── tests/                      # ✅ EXISTS
│   │   │   ├── unit/                   # ✅ EXISTS
│   │   │   ├── integration/            # ✅ EXISTS
│   │   │   └── contract/               # 🆕 NEW
│   │   │
│   │   ├── migrations/                 # ✅ EXISTS - Database migrations
│   │   ├── main.py                     # ✅ EXISTS (needs Dapr integration)
│   │   ├── Dockerfile                  # ✅ EXISTS
│   │   ├── requirements.txt            # ✅ EXISTS (needs Dapr, Kafka, OpenAI SDKs)
│   │   ├── .env.example                # ✅ EXISTS (needs new env vars)
│   │   └── README.md                   # ✅ EXISTS
│   │
│   ├── recurring-service/              # 🆕 NEW - Recurring task automation (Port 8002)
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── subscriber.py           # Dapr subscriber for task-events
│   │   │   ├── recurrence_engine.py    # Calculate next occurrence
│   │   │   └── dapr_client.py          # Dapr pub/sub client
│   │   ├── tests/
│   │   │   └── test_recurrence.py
│   │   ├── main.py                     # FastAPI app with Dapr subscriber
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── README.md
│   │
│   ├── notification-service/           # 🆕 NEW - Reminder notifications (Port 8001)
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── subscriber.py           # Dapr subscriber for reminders
│   │   │   ├── email_sender.py         # Resend API integration
│   │   │   ├── retry_handler.py        # Exponential backoff retry logic
│   │   │   └── dapr_client.py
│   │   ├── tests/
│   │   │   └── test_notifications.py
│   │   ├── main.py                     # FastAPI app with Dapr subscriber
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── README.md
│   │
│   └── frontend/                       # ✅ EXISTS - Next.js frontend (Port 3000)
│       ├── src/
│       │   ├── app/                    # ✅ EXISTS - Next.js 16 App Router
│       │   │   ├── layout.tsx          # ✅ EXISTS
│       │   │   ├── page.tsx            # ✅ EXISTS (landing page)
│       │   │   ├── tasks/              # 📝 EXISTS (needs filters, search, tags UI)
│       │   │   │   └── page.tsx        # ✅ EXISTS
│       │   │   └── chat/               # 🆕 NEW - Chat Mode (conversational UI)
│       │   │       └── page.tsx
│       │   │
│       │   ├── components/             # ✅ EXISTS - React components
│       │   │   ├── tasks/              # 📝 EXISTS (needs new components)
│       │   │   │   ├── TaskList.tsx    # 📝 EXISTS (needs priority, tags display)
│       │   │   │   ├── TaskForm.tsx    # 📝 EXISTS (needs new fields)
│       │   │   │   ├── FilterPanel.tsx # 🆕 NEW
│       │   │   │   ├── SearchBar.tsx   # 🆕 NEW
│       │   │   │   └── TagPill.tsx     # 🆕 NEW
│       │   │   └── chat/               # 🆕 NEW
│       │   │       ├── ChatInterface.tsx
│       │   │       ├── MessageList.tsx
│       │   │       └── InputBox.tsx
│       │   │
│       │   ├── services/               # 📝 EXISTS (needs new API clients)
│       │   │   ├── api.ts              # 📝 EXISTS (needs new endpoints)
│       │   │   ├── dapr.ts             # 🆕 NEW - Dapr service invocation
│       │   │   └── realtime.ts         # 🆕 NEW - Real-time sync logic
│       │   │
│       │   ├── hooks/                  # ✅ EXISTS
│       │   ├── lib/                    # ✅ EXISTS
│       │   │   ├── types.ts            # 📝 EXISTS (needs new types)
│       │   │   └── utils.ts            # ✅ EXISTS
│       │   └── types/                  # ✅ EXISTS
│       │
│       ├── tests/                      # ✅ EXISTS
│       ├── public/                     # ✅ EXISTS
│       ├── Dockerfile                  # ✅ EXISTS
│       ├── package.json                # ✅ EXISTS (needs new dependencies)
│       ├── next.config.ts              # ✅ EXISTS
│       ├── tailwind.config.ts          # ✅ EXISTS
│       ├── .env.example                # ✅ EXISTS (needs new env vars)
│       └── README.md                   # ✅ EXISTS
│
├── infrastructure/                     # 🆕 NEW - Deployment configurations
│   ├── dapr/                          # 🆕 NEW - Dapr components
│   │   ├── components/
│   │   │   ├── kafka-pubsub.yaml      # Pub/Sub component
│   │   │   ├── statestore.yaml        # State management (PostgreSQL)
│   │   │   ├── secrets.yaml           # Kubernetes secrets store
│   │   │   └── jobs.yaml              # Jobs API configuration
│   │   └── subscriptions/
│   │       ├── recurring-service-sub.yaml
│   │       └── notification-service-sub.yaml
│   │
│   ├── kafka/                         # 🆕 NEW - Kafka/Redpanda setup
│   │   ├── local/                     # Redpanda for local dev
│   │   │   └── docker-compose.yml
│   │   └── k8s/                       # Strimzi operator for K8s
│   │       └── kafka-cluster.yaml
│   │
│   ├── kubernetes/                    # 🆕 NEW - Raw K8s manifests (Minikube)
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── deployments/
│   │   │   ├── backend-api.yaml
│   │   │   ├── recurring-service.yaml
│   │   │   ├── notification-service.yaml
│   │   │   └── frontend.yaml
│   │   ├── services/
│   │   │   ├── backend-api-service.yaml
│   │   │   ├── recurring-service.yaml
│   │   │   ├── notification-service.yaml
│   │   │   └── frontend-service.yaml
│   │   └── ingress/
│   │       └── ingress.yaml
│   │
│   ├── helm/                          # 🆕 NEW - Helm charts (cloud deployment)
│   │   └── taskai/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── values-dev.yaml        # Minikube overrides
│   │       ├── values-prod.yaml       # Cloud overrides
│   │       └── templates/
│   │           ├── _helpers.tpl
│   │           ├── namespace.yaml
│   │           ├── configmap.yaml
│   │           ├── secrets.yaml
│   │           ├── backend-api/
│   │           ├── recurring-service/
│   │           ├── notification-service/
│   │           ├── frontend/
│   │           ├── dapr/
│   │           └── kafka/
│   │
│   ├── docker-compose/                # 🆕 NEW - Local development
│   │   ├── docker-compose.yml         # All services + Kafka + PostgreSQL
│   │   └── docker-compose.dev.yml     # Development overrides
│   │
│   └── scripts/                       # 🆕 NEW - Deployment automation
│       ├── setup-minikube.sh          # Initialize Minikube cluster
│       ├── install-dapr.sh            # Install Dapr on K8s
│       ├── install-kafka.sh           # Install Strimzi operator
│       ├── deploy-local.sh            # Deploy to Minikube
│       ├── deploy-cloud.sh            # Deploy to AKS/GKE
│       └── teardown.sh                # Cleanup resources
│
├── docs/                              # 🆕 NEW - Documentation
│   ├── architecture.md
│   ├── api-reference.md
│   ├── deployment-guide.md
│   ├── local-development.md
│   └── mcp-tools.md
│
├── AGENTS.md                          # ✅ EXISTS - Agent behavior rules
├── CLAUDE.md                          # ✅ EXISTS - Claude Code instructions
├── README.md                          # ✅ EXISTS - Project overview
├── .gitignore                         # ✅ EXISTS
└── LICENSE                            # ✅ EXISTS
```

**Structure Decision**: Microservices architecture with 4 independent services in `services/` directory. Two services (backend-api, frontend) already exist with partial implementation and need extensions for Phase 5 features. Two new services (recurring-service, notification-service) need to be created from scratch. Infrastructure configurations will be centralized in a new `infrastructure/` directory for reusability across all services. This structure supports independent deployment, scaling, and development of each service while maintaining clear separation of concerns.

**Migration Strategy**:
1. Extend existing backend-api with new models (Tag, Reminder, RecurrenceRule), endpoints (tags, search, chat), and Dapr integration
2. Extend existing frontend with new components (FilterPanel, SearchBar, TagPill, chat interface) and API clients
3. Create new recurring-service for automated recurring task generation
4. Create new notification-service for reminder email delivery
5. Create infrastructure/ directory with Dapr components, Kafka setup, Kubernetes manifests, Helm charts, and deployment scripts

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Microservices architecture (4 services vs monolith) | Event-driven architecture required for recurring tasks and reminders. Recurring Service must react to task completion events. Notification Service must handle scheduled reminders independently. Separation enables independent scaling and deployment. | Monolithic architecture cannot support exact-time reminder scheduling (requires Dapr Jobs API) or automatic recurring task creation (requires event consumption). Single service would create tight coupling between task management, scheduling, and notifications. |
| Kafka message broker | Reliable event delivery required for recurring tasks and reminders. Task completion events must trigger recurring task creation. Reminder events must be delivered exactly once at scheduled times. | Direct HTTP calls between services would create tight coupling and single points of failure. Database polling would not meet <5 second latency requirements for recurring task creation and reminder delivery. |
| Dapr integration (5 building blocks) | Jobs API required for exact-time reminder scheduling (not achievable with cron). Pub/Sub abstraction simplifies Kafka integration. Service Invocation provides built-in retries and circuit breakers. State Management needed for chat conversation history. Secrets Management for secure credential handling. | Native Kafka clients would require custom retry logic, circuit breakers, and connection management. Custom job scheduling would require complex timer management and persistence. Direct service calls would lack resilience patterns. |
| Dual interface (Chat + Tasks) | Specification explicitly requires conversational interface alongside graphical UI. Different user preferences and accessibility needs. Chat mode enables natural language task management for users who prefer conversational interfaces. | Single graphical interface would not meet accessibility requirements or support natural language interaction patterns defined in FR-045 to FR-053. |
