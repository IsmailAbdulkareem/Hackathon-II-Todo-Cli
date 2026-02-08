# Implementation Plan: Phase V - Advanced Features with Dapr-First Architecture

**Branch**: `001-dapr-advanced-features` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-dapr-advanced-features/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance the existing Todo application with advanced task management features (due dates, priorities, tags, recurring tasks, reminders, search/filter) and implement an event-driven architecture using Dapr as the first-class integration layer. All integrations must go through Dapr APIs (Pub/Sub, State Store, Jobs, Service Invocation) with graceful degradation when Dapr is unavailable. The system will support multi-user task ownership with Server-Sent Events (SSE) for real-time reminder notifications. Implementation follows a phased approach: Phase III (local development with Dapr sidecar) then Phase IV (Kubernetes deployment) with zero code changes between phases.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Node.js 20+ (frontend)
**Primary Dependencies**: FastAPI (backend), Dapr 1.12+, Redis 6.0+, Next.js 16+, React 19, Tailwind CSS
**Storage**: Redis (via Dapr State Store API) for task persistence, Redis Streams (via Dapr Pub/Sub API) for event messaging
**Testing**: pytest (Python backend), Jest/Vitest (TypeScript frontend)
**Target Platform**: Local development (Phase III with Dapr self-hosted), Kubernetes/Minikube 1.30+ (Phase IV)
**Project Type**: Web application (backend API + frontend SPA)
**Performance Goals**: 1000 concurrent task operations, <2s filter results, <1s search (10k tasks), <500ms event latency, <1min reminder delivery, <5min recurring task generation
**Constraints**: Dapr-first mandate (no direct Kafka/cron/message brokers), HTTP API only (no gRPC/SDKs), graceful degradation when Dapr unavailable, Phase III→IV code reuse without modification, user_id derived from auth session (never from client input)
**Scale/Scope**: 10,000 tasks per user, multi-user system with existing authentication, 4 event topics (task-events, task-reminders, task-recurring, task-audit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development First
✅ **PASS** - Complete specification exists at `specs/001-dapr-advanced-features/spec.md` with 48 functional requirements, 6 prioritized user stories, and measurable success criteria.

### Principle II: AI as Implementer, Human as Architect
✅ **PASS** - Specification created by human architect with AI assistance. Implementation will be performed by AI agents following explicit specifications. All clarifications documented in spec.

### Principle III: Deterministic Behavior Across Non-LLM Components
✅ **PASS** - All business logic (task management, recurring task generation, reminder scheduling) will be deterministic. Side effects (Dapr API calls, Redis operations, SSE notifications) will be isolated from domain logic through adapter pattern.

### Principle IV: Evolvability Across Phases Without Breaking Domain Contracts
✅ **PASS** - Domain model (Enhanced Task, Task Event, Reminder, Recurring Task Instance) is infrastructure-agnostic. Dapr integration is abstracted through repository and event publisher interfaces. Phase III→IV migration requires zero code changes (only configuration).

### Principle V: Clear Separation of Domain Logic, Interfaces, and Infrastructure
✅ **PASS** - Architecture follows three-layer separation:
- **Domain**: Task entities, business rules (recurrence logic, reminder calculation, priority sorting)
- **Interfaces**: REST API endpoints, SSE notification endpoint
- **Infrastructure**: Dapr adapters (state store, pub/sub, jobs), Redis configuration

### Principle VI: Reusable Intelligence Over One-Off Solutions
⚠️ **N/A** - No AI-powered features in this phase. Event-driven architecture enables future AI integration (e.g., smart task prioritization, deadline prediction).

### Principle VII: Infrastructure as Declarative and Reproducible
✅ **PASS** - All infrastructure defined declaratively:
- Dapr components (YAML manifests for state store, pub/sub)
- Kubernetes deployment specs with Dapr annotations
- Helm charts for Phase IV deployment
- Redis configuration files

**Constitution Check Result**: ✅ **PASS** - All applicable principles satisfied. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-dapr-advanced-features/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 research outputs
├── data-model.md        # Phase 1 entity definitions
├── quickstart.md        # Phase 1 local development guide
├── contracts/           # Phase 1 API contracts
│   ├── openapi.yaml     # REST API specification
│   ├── events.yaml      # Event schema definitions
│   └── sse.md           # SSE notification protocol
└── tasks.md             # Phase 2 task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── task.py              # Enhanced Task entity
│   │   │   ├── task_event.py        # Task Event entity
│   │   │   ├── reminder.py          # Reminder entity
│   │   │   └── recurring_instance.py # Recurring Task Instance entity
│   │   ├── services/
│   │   │   ├── task_service.py      # Task business logic
│   │   │   ├── recurrence_service.py # Recurring task generation
│   │   │   ├── reminder_service.py   # Reminder scheduling
│   │   │   └── search_service.py     # Search/filter/sort logic
│   │   └── repositories/
│   │       ├── task_repository.py    # Task persistence interface
│   │       └── event_publisher.py    # Event publishing interface
│   ├── infrastructure/
│   │   ├── dapr/
│   │   │   ├── state_store_adapter.py  # Dapr State Store implementation
│   │   │   ├── pubsub_adapter.py       # Dapr Pub/Sub implementation
│   │   │   ├── jobs_adapter.py         # Dapr Jobs implementation
│   │   │   └── service_invocation.py   # Dapr Service Invocation
│   │   ├── redis/
│   │   │   └── fallback_store.py       # Local fallback when Dapr unavailable
│   │   └── sse/
│   │       └── notification_manager.py # SSE connection management
│   ├── api/
│   │   ├── routes/
│   │   │   ├── tasks.py              # Task CRUD endpoints
│   │   │   ├── search.py             # Search/filter/sort endpoints
│   │   │   └── notifications.py      # SSE notification endpoint
│   │   ├── middleware/
│   │   │   ├── auth.py               # Authentication validation
│   │   │   └── error_handler.py      # Error handling middleware
│   │   └── schemas/
│   │       ├── task_schemas.py       # Pydantic models for API
│   │       └── event_schemas.py      # Event payload schemas
│   └── config/
│       ├── settings.py               # Application configuration
│       └── dapr_config.py            # Dapr connection settings
├── tests/
│   ├── unit/
│   │   ├── domain/                   # Domain logic tests
│   │   └── services/                 # Service tests
│   ├── integration/
│   │   ├── dapr/                     # Dapr integration tests
│   │   └── api/                      # API endpoint tests
│   └── e2e/
│       └── scenarios/                # End-to-end user scenarios
├── dapr/
│   ├── components/
│   │   ├── statestore.yaml           # Redis state store component
│   │   ├── pubsub.yaml               # Redis Streams pub/sub component
│   │   └── jobs.yaml                 # Jobs component configuration
│   └── config.yaml                   # Dapr runtime configuration
└── requirements.txt                  # Python dependencies

frontend/
├── src/
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx          # Task list with filters
│   │   │   ├── TaskForm.tsx          # Task creation/edit form
│   │   │   ├── TaskItem.tsx          # Individual task display
│   │   │   ├── PriorityBadge.tsx     # Priority indicator
│   │   │   ├── TagList.tsx           # Tag display/management
│   │   │   └── RecurrencePicker.tsx  # Recurrence configuration
│   │   ├── filters/
│   │   │   ├── FilterBar.tsx         # Filter controls
│   │   │   ├── SearchBox.tsx         # Text search input
│   │   │   └── SortSelector.tsx      # Sort options
│   │   └── notifications/
│   │       ├── NotificationBell.tsx  # Notification indicator
│   │       └── NotificationList.tsx  # Reminder notifications
│   ├── services/
│   │   ├── api/
│   │   │   ├── taskApi.ts            # Task API client
│   │   │   └── searchApi.ts          # Search/filter API client
│   │   ├── sse/
│   │   │   └── notificationClient.ts # SSE connection manager
│   │   └── auth/
│   │       └── authContext.ts        # Authentication context
│   ├── hooks/
│   │   ├── useTasks.ts               # Task data management
│   │   ├── useFilters.ts             # Filter state management
│   │   └── useNotifications.ts       # SSE notification hook
│   ├── types/
│   │   ├── task.ts                   # Task type definitions
│   │   └── event.ts                  # Event type definitions
│   └── pages/
│       ├── tasks/
│       │   ├── index.tsx             # Task list page
│       │   └── [id].tsx              # Task detail page
│       └── api/                      # Next.js API routes (if needed)
├── tests/
│   ├── unit/
│   │   └── components/               # Component tests
│   └── integration/
│       └── api/                      # API integration tests
└── package.json                      # Node.js dependencies

infrastructure/
├── kubernetes/
│   ├── backend-deployment.yaml       # Backend deployment with Dapr annotations
│   ├── frontend-deployment.yaml      # Frontend deployment
│   ├── redis-deployment.yaml         # Redis deployment
│   ├── dapr-components/
│   │   ├─ statestore.yaml           # K8s Dapr state store component
│   │   └── pubsub.yaml               # K8s Dapr pub/sub component
│   └── helm/
│       └── todo-app/
│           ├── Chart.yaml            # Helm chart metadata
│           ├── values.yaml           # Configuration values
│           └── templates/            # Kubernetes templates
└── docs/
    ├── dapr-setup.md                 # Dapr installation guide
    ├── redis-setup.md                # Redis configuration guide
    └── deployment.md                 # Deployment procedures
```

**Structure Decision**: Web application structure (Option 2) selected because the feature requires both backend API (FastAPI) and frontend SPA (Next.js). Backend handles business logic, Dapr integration, and SSE notifications. Frontend provides user interface for task management and real-time notifications. Clear separation enables independent development and testing of each layer.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional principles are satisfied.

---

## Phase 0: Research & Technical Decisions

**Status**: To be completed during `/sp.plan` execution

### Research Areas

The following areas require research to resolve technical unknowns before design:

1. **Dapr Jobs API Patterns** (FR-031)
   - Research: How to schedule and manage jobs using Dapr Jobs API 1.12+
   - Questions: Job scheduling syntax, recurring job patterns, job cancellation, failure handling
   - Output: Best practices for reminder scheduling and recurring task generation

2. **Server-Sent Events in FastAPI** (FR-046, FR-047)
   - Research: SSE implementation patterns in FastAPI for real-time notifications
   - Questions: Connection management, per-user streams, reconnection handling, authentication
   - Output: SSE endpoint design and connection lifecycle management

3. **Redis Streams for Dapr Pub/Sub** (FR-029)
   - Research: Redis Streams configuration as Dapr pub/sub component
   - Questions: Topic configuration, consumer groups, message retention, delivery guarantees
   - Output: Dapr component YAML configuration and event publishing patterns

4. **Graceful Degradation Strategies** (FR-036, FR-040)
   - Research: Patterns for handling Dapr unavailability
   - Questions: Local queuing mechanisms, retry strategies, feature degradation matrix
   - Output: Fallback architecture and degradation decision tree

5. **Recurring Task Scheduling Patterns** (FR-006, FR-009, FR-010, FR-011)
   - Research: Algorithms for calculating next recurrence dates
   - Questions: Day-of-week calculation, month-end handling, DST considerations
   - Output: Recurrence calculation functions and edge case handling

6. **Multi-User Task Isolation** (FR-043, FR-044, FR-048)
   - Research: Patterns for user_id filtering in Dapr state store queries
   - Questions: Query performance, index strategies, authorization enforcement
   - Output: Repository query patterns and security best practices

### Research Output Location

All research findings will be documented in `specs/001-dapr-advanced-features/research.md` with the following structure:

```markdown
# Research: Phase V Advanced Features

## 1. Dapr Jobs API Patterns
- Decision: [chosen approach]
- Rationale: [why chosen]
- Alternatives considered: [other options]
- Implementation notes: [key details]

## 2. Server-Sent Events in FastAPI
[same structure]

## 3. Redis Streams for Dapr Pub/Sub
[same structure]

## 4. Graceful Degradation Strategies
[same structure]

## 5. Recurring Task Scheduling Patterns
[same structure]

## 6. Multi-User Task Isolation
[same structure]
```

---

## Phase 1: Design & Contracts

**Status**: To be completed after Phase 0 research

### Data Model

Entity definitions will be documented in `specs/001-dapr-advanced-features/data-model.md` covering:

1. **Enhanced Task Entity**
   - Fields: id, user_id, title, description, completed, created_at, updated_at, due_date, priority, tags, recurrence, reminder_offset_minutes
   - Validation rules: ISO 8601 timestamps, priority enum, tag normalization
   - State transitions: creation → active → completed/overdue
   - Relationships: user ownership, recurring parent-child

2. **Task Event Entity**
   - Fields: task_id, event_type, timestamp, payload
   - Event types: TASK_CREATED, TASK_UPDATED, TASK_COMPLETED, REMINDER_DUE
   - Schema validation: standard event structure

3. **Reminder Entity**
   - Fields: task_id, reminder_time, notification_sent
   - Lifecycle: scheduled → triggered → sent
   - Cancellation rules: task completion, task deletion

4. **Recurring Task Instance Entity**
   - Fields: parent_task_id, instance_date, instance_task_id
   - Generation rules: daily/weekly/monthly patterns
   - Edge cases: month-end handling, DST transitions

### API Contracts

API specifications will be documented in `specs/001-dapr-advanced-features/contracts/`:

#### REST API Endpoints (`openapi.yaml`)

**Task Management**
- `POST /api/tasks` - Create task with due date, priority, tags, recurrence
- `GET /api/tasks` - List user's tasks with pagination
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task attributes
- `DELETE /api/tasks/{id}` - Delete task (cancels reminders)

**Search & Filter**
- `GET /api/tasks/search` - Search tasks by text, filter by priority/tags/due date/status, sort by priority/due date
- Query parameters: `q` (text), `priority`, `tags[]`, `due_from`, `due_to`, `completed`, `sort_by`, `sort_order`

**Notifications**
- `GET /api/notifications/stream` - SSE endpoint for real-time reminders
- Authentication: Bearer token in query param or header
- Event format: `data: {"task_id": "...", "message": "...", "timestamp": "..."}`

#### Event Schemas (`events.yaml`)

**Standard Event Structure**
```yaml
TaskEvent:
  type: object
  required: [task_id, event_type, timestamp, payload]
  properties:
    task_id:
      type: string
      format: uuid
    event_type:
      type: string
      enum: [TASK_CREATED, TASK_UPDATED, TASK_COMPLETED, REMINDER_DUE]
    timestamp:
      type: string
      format: date-time
    payload:
      type: object
```

**Event Topics**
- `task-events`: Task lifecycle events (CREATED, UPDATED, COMPLETED)
- `task-reminders`: Reminder notifications (REMINDER_DUE)
- `task-recurring`: Recurring task generation events
- `task-audit`: Audit log stream (all events)

#### SSE Protocol (`sse.md`)

**Connection Lifecycle**
1. Client connects to `/api/notifications/stream` with auth token
2. Server validates authentication and creates user-specific stream
3. Server sends heartbeat every 30 seconds to keep connection alive
4. Server pushes reminder events as they occur
5. Client reconnects on disconnect with Last-Event-ID for resume

**Event Format**
```
event: reminder
id: <event-id>
data: {"task_id": "...", "title": "...", "due_date": "...", "message": "..."}

event: heartbeat
data: {"timestamp": "..."}
```

### Quickstart Guide

Local development setup will be documented in `specs/001-dapr-advanced-features/quickstart.md`:

1. **Prerequisites**
   - Python 3.13+, Node.js 20+
   - Dapr CLI installation (`winget install Dapr.CLI`)
   - Redis installation (Docker or local)

2. **Dapr Initialization**
   ```bash
   dapr init
   dapr --version  # Verify 1.12+
   ```

3. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 -- uvicorn src.main:app --reload
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Verification**
   - Backend: http://localhost:8000/docs (OpenAPI docs)
   - Frontend: http://localhost:3000
   - Dapr dashboard: http://localhost:8080

### Agent Context Update

After Phase 1 design completion, run:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will update `.specify/memory/claude-context.md` with:
- Dapr 1.12+ (Jobs API, State Store, Pub/Sub, Service Invocation)
- Redis 6.0+ (state store and pub/sub backend)
- FastAPI SSE patterns
- Next.js 16+ with React 19

---

## Phase 2: Task Breakdown

**Status**: Not started (requires `/sp.tasks` command)

Task breakdown will be generated in `specs/001-dapr-advanced-features/tasks.md` after Phase 1 design is complete. Tasks will be organized by:

1. **Infrastructure Setup** (Dapr, Redis, configuration)
2. **Domain Model Implementation** (entities, business logic)
3. **Dapr Integration** (state store, pub/sub, jobs adapters)
4. **API Implementation** (REST endpoints, SSE notifications)
5. **Frontend Implementation** (components, hooks, SSE client)
6. **Testing** (unit, integration, e2e)
7. **Documentation** (API docs, deployment guides)

Each task will include:
- Clear acceptance criteria
- Dependencies on other tasks
- Estimated complexity
- Test requirements

---

## Implementation Notes

### Critical Path

1. **Phase 0 Research** → Resolve all technical unknowns
2. **Phase 1 Design** → Define data model and API contracts
3. **Infrastructure Setup** → Install Dapr, Redis, configure components
4. **Domain Model** → Implement entities and business logic (infrastructure-agnostic)
5. **Dapr Adapters** → Implement state store, pub/sub, jobs integration
6. **API Layer** → Implement REST endpoints and SSE notifications
7. **Frontend** → Implement UI components and SSE client
8. **Testing** → Unit, integration, e2e tests
9. **Phase III Validation** → Test locally with Dapr sidecar
10. **Phase IV Migration** → Deploy to Kubernetes without code changes

### Key Design Decisions

1. **Repository Pattern**: Abstract Dapr state store behind repository interface to enable graceful degradation and testing
2. **Event Publisher Interface**: Abstract Dapr pub/sub behind publisher interface for testability
3. **Adapter Pattern**: Wrap all Dapr APIs in adapters to isolate infrastructure concerns
4. **SSE Manager**: Centralized connection management for per-user notification streams
5. **Fallback Store**: Local in-memory store for graceful degradation when Dapr unavailable

### Risk Mitigation

1. **Dapr Installation Failure**: Document installation process, provide Docker Compose alternative
2. **Dapr Unavailability**: Implement fallback store and event queue for local operation
3. **SSE Connection Loss**: Implement automatic reconnection with Last-Event-ID resume
4. **Recurring Task Accumulation**: Implement batch generation with rate limiting
5. **Event Delivery Failure**: Implement retry with exponential backoff and dead letter queue

### Success Metrics

Implementation will be considered successful when:
- All 48 functional requirements are met
- All 10 success criteria are achieved
- Constitution check passes (all principles satisfied)
- Phase III code runs in Phase IV without modification
- All tests pass (unit, integration, e2e)
- Documentation is complete and accurate

---

**Next Steps**:
1. Execute Phase 0 research to resolve technical unknowns
2. Create `research.md` with findings and decisions
3. Execute Phase 1 design to create data model and contracts
4. Create `data-model.md`, `contracts/`, and `quickstart.md`
5. Update agent context with new technologies
6. Run `/sp.tasks` to generate task breakdown
