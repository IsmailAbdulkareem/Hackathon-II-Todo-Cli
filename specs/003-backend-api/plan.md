# Implementation Plan: Backend REST API with Persistent Storage

**Branch**: `003-backend-api` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-backend-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a production-quality FastAPI backend that provides persistent task management via RESTful APIs. The API implements 6 endpoints for full CRUD operations on tasks, with user isolation enforced via user_id path parameters. All data persists in a PostgreSQL database using SQLModel ORM. The architecture is designed to support future JWT authentication integration without requiring refactoring.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI, SQLModel, psycopg2 (PostgreSQL driver), uvicorn (ASGI server)
**Storage**: Neon Serverless PostgreSQL (PostgreSQL-compatible)
**Testing**: pytest (with pytest-asyncio for async tests)
**Target Platform**: Linux/Windows server (development), cloud-hosted (production)
**Project Type**: Web (backend only)
**Performance Goals**: <500ms response time for single-task operations, 100 concurrent requests without degradation
**Constraints**: User isolation mandatory, no authentication in this phase, CORS enabled for frontend integration
**Scale/Scope**: <10,000 tasks per user, 6 REST endpoints, single Task entity

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development First
✅ **PASS** - Complete specification exists at `specs/003-backend-api/spec.md` with:
- 6 prioritized user stories with acceptance scenarios
- 18 functional requirements
- 8 measurable success criteria
- Clear scope boundaries (Out of Scope section)

### Principle II: AI as Implementer, Human as Architect
✅ **PASS** - Human architect provided detailed specification with:
- Explicit API endpoint definitions
- Data model requirements
- Behavior rules and constraints
- No ambiguity requiring AI assumptions

### Principle III: Deterministic Behavior Across Non-LLM Components
✅ **PASS** - REST API design ensures deterministic behavior:
- Standard HTTP methods with predictable semantics
- Explicit validation rules (title required, length constraints)
- Database persistence with ACID guarantees
- No AI/LLM components in this phase

### Principle IV: Evolvability Across Phases
✅ **PASS** - Architecture prepared for evolution:
- user_id path parameter enables future JWT integration
- Domain model (Task entity) independent of transport layer
- No authentication logic to refactor later
- Clean separation between API routes and business logic

### Principle V: Clear Separation of Domain Logic, Interfaces, and Infrastructure
✅ **PASS** - Planned structure maintains separation:
- **Domain**: Task entity with validation rules
- **Interfaces**: FastAPI routes (6 REST endpoints)
- **Infrastructure**: SQLModel database layer, PostgreSQL connection

### Principle VI: Reusable Intelligence Over One-Off Solutions
✅ **N/A** - No AI-powered features in this phase

### Principle VII: Infrastructure as Declarative and Reproducible
✅ **PASS** - Infrastructure will be declarative:
- Database schema defined via SQLModel models
- Database migrations (Alembic) for reproducible schema changes
- Environment variables for configuration (DATABASE_URL)
- Requirements file for dependency management

## Project Structure

### Documentation (this feature)

```text
specs/003-backend-api/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── openapi.yaml     # OpenAPI 3.0 specification
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phase-02-fullstack-web/
├── backend/
│   ├── src/
│   │   ├── models/          # SQLModel database models
│   │   │   ├── __init__.py
│   │   │   ├── base.py      # Database session and engine
│   │   │   └── task.py      # Task entity model
│   │   ├── api/             # FastAPI route handlers
│   │   │   ├── __init__.py
│   │   │   └── tasks.py     # Task CRUD endpoints
│   │   └── core/            # Configuration and utilities
│   │       ├── __init__.py
│   │       ├── config.py    # Environment configuration
│   │       └── database.py  # Database connection management
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py      # Pytest fixtures
│   │   ├── test_api.py      # API endpoint tests
│   │   └── test_models.py   # Model validation tests
│   ├── main.py              # FastAPI application entry point
│   ├── pyproject.toml       # Project metadata and dependencies
│   ├── .env.example         # Environment variable template
│   └── README.md            # Backend setup instructions
└── frontend/                # Existing Next.js frontend
    └── [existing structure]
```

**Structure Decision**: Web application structure (Option 2) selected because this is a backend API that complements the existing frontend in `phase-02-fullstack-web/frontend`. The backend follows FastAPI best practices with clear separation between models (data layer), api (interface layer), and core (infrastructure/configuration).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional principles are satisfied.

## Phase 0: Research (Complete)

**Status**: ✅ Complete
**Output**: `research.md`

All technical decisions finalized:
- FastAPI 0.109+ as web framework
- SQLModel 0.0.14+ for ORM
- UUID for task IDs
- UTC timestamps with automatic management
- Connection pooling for database
- CORSMiddleware for frontend integration
- HTTPException for error handling
- Pydantic Settings for configuration

No NEEDS CLARIFICATION items remain. Ready for implementation.

## Phase 1: Design & Contracts (Complete)

**Status**: ✅ Complete
**Outputs**: `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`

### Data Model
- Task entity with 7 fields (id, user_id, title, description, completed, created_at, updated_at)
- Validation rules for title (required, max 500 chars) and description (optional, max 2000 chars)
- Indexes on id (primary) and user_id (secondary)
- Request/response models (TaskCreate, TaskUpdate, Task)

### API Contracts
- OpenAPI 3.0 specification with 6 endpoints
- Complete request/response schemas
- Error response formats (404, 422, 500)
- Example requests and responses

### Quickstart Guide
- Setup instructions (Python 3.13+, virtual environment, dependencies)
- Environment configuration (.env file)
- Database initialization
- Running development server
- Testing endpoints (cURL, Swagger UI, Python requests)
- Troubleshooting common issues

### Agent Context Update
- Updated CLAUDE.md with Python 3.13+, FastAPI, SQLModel, Neon PostgreSQL
- Technologies added to Active Technologies section

## Phase 2: Tasks (Not Started)

**Status**: ⏳ Pending
**Command**: `/sp.tasks`

Tasks will be generated in the next phase to break down implementation into testable units following TDD (Red-Green-Refactor) cycle.

## Architecture Decisions

### Decision 1: FastAPI + SQLModel Stack

**Context**: Need to choose web framework and ORM for REST API backend.

**Options Considered**:
1. FastAPI + SQLModel (chosen)
2. Flask + SQLAlchemy + Pydantic
3. Django REST Framework

**Decision**: FastAPI + SQLModel

**Rationale**:
- Native async/await support for high performance
- Automatic OpenAPI documentation generation
- SQLModel unifies database models and API schemas (reduces duplication)
- Type-safe with full IDE support
- Same author (Sebastián Ramírez) ensures tight integration
- Large ecosystem and active community

**Trade-offs**:
- SQLModel is less mature than SQLAlchemy alone (acceptable for this use case)
- FastAPI requires understanding of async patterns (team has Python 3.13+ experience)

### Decision 2: UUID for Task IDs

**Context**: Need to choose ID format for tasks.

**Options Considered**:
1. UUID (chosen)
2. Auto-incrementing integers
3. ULID (Universally Unique Lexicographically Sortable Identifier)

**Decision**: UUID (string format)

**Rationale**:
- Globally unique across all users and systems
- No sequential ID leakage (security consideration)
- Easier to merge data from multiple sources
- Aligns with specification requirement (FR-009)
- Standard Python uuid.uuid4() generation

**Trade-offs**:
- Larger storage size (36 chars vs 8 bytes for int)
- Not sortable by creation time (acceptable - we have created_at)
- Slightly slower indexing (acceptable for <10k tasks per user)

### Decision 3: Path Parameter for user_id

**Context**: Need to decide how to scope API operations to users.

**Options Considered**:
1. Path parameter `/api/{user_id}/tasks` (chosen)
2. Query parameter `/api/tasks?user_id=...`
3. Header-based (X-User-ID)

**Decision**: Path parameter

**Rationale**:
- RESTful convention: path parameters for resource identification
- Clear ownership hierarchy in URL structure
- Prepares for future JWT authentication (user_id extracted from token)
- Aligns with specification requirements
- Better API discoverability

**Trade-offs**:
- Slightly longer URLs (acceptable)
- Cannot easily query across users (not needed per spec)

## Implementation Readiness

### Prerequisites Met
- ✅ Specification complete and validated
- ✅ Constitution check passed
- ✅ Research complete (no unknowns)
- ✅ Data model defined
- ✅ API contracts specified (OpenAPI)
- ✅ Quickstart guide written
- ✅ Agent context updated

### Next Steps
1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks following TDD cycle (Red-Green-Refactor)
3. Implement FastAPI application structure
4. Create SQLModel models
5. Implement API endpoints
6. Write tests
7. Deploy to development environment

### Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Database connection issues with Neon | High | Low | Use connection pooling, implement retry logic, provide clear error messages |
| CORS configuration errors | Medium | Medium | Test with frontend early, document CORS setup in quickstart |
| Validation edge cases | Low | Medium | Comprehensive test coverage, follow Pydantic best practices |
| Performance under load | Medium | Low | Use async/await, implement connection pooling, monitor with logging |

## Success Metrics

Implementation will be considered successful when:
- ✅ All 6 API endpoints functional and tested
- ✅ User isolation enforced (100% - no cross-user access)
- ✅ Response times <500ms for single-task operations
- ✅ All validation rules enforced (title required, length constraints)
- ✅ Database persistence verified (data survives server restart)
- ✅ OpenAPI documentation accessible at /docs
- ✅ Frontend can integrate without modifications

## Appendix

### Technology Versions
- Python: 3.13+
- FastAPI: 0.109+
- SQLModel: 0.0.14+
- Uvicorn: 0.27+
- PostgreSQL: 14+ (Neon Serverless)

### Related Documents
- Specification: [spec.md](./spec.md)
- Research: [research.md](./research.md)
- Data Model: [data-model.md](./data-model.md)
- API Contract: [contracts/openapi.yaml](./contracts/openapi.yaml)
- Quickstart: [quickstart.md](./quickstart.md)

### Architectural Decision Records
No ADRs created yet. Significant decisions documented in this plan should be formalized as ADRs if they meet the three-part test (impact, alternatives, scope).

**Potential ADR Candidates**:
1. "FastAPI + SQLModel Stack Selection" - Framework and ORM choice
2. "User Isolation via Path Parameters" - API design pattern for multi-tenancy
3. "UUID-based Task Identifiers" - ID generation strategy

📋 **Architectural decision detected**: FastAPI + SQLModel stack selection, UUID-based identifiers, and path parameter user isolation pattern.
   Document reasoning and tradeoffs? Run `/sp.adr "Backend API Architecture Decisions"`
