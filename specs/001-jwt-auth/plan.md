# Implementation Plan: JWT-Based Authentication for Task Management

**Branch**: `001-jwt-auth` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-jwt-auth/spec.md`

## Summary

Implement stateless JWT-based authentication using Better Auth (frontend) for user registration, login, and token issuance, and python-jose (backend) for JWT verification. The system enforces user isolation by comparing JWT user_id claims with URL user_id parameters, returning HTTP 401 for authentication failures and HTTP 403 for authorization failures.

**Key Technical Approach**:
- Frontend: Better Auth handles all authentication (registration, login, JWT issuance) with separate user database
- Backend: python-jose verifies JWT signatures and extracts user_id from `sub` claim
- Stateless: No server-side sessions, token blacklists, or invalidation mechanisms
- User Isolation: Backend compares JWT user_id with URL user_id before allowing access

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5+ with Next.js 16+ (App Router)
- Backend: Python 3.13+ with FastAPI

**Primary Dependencies**:
- Frontend: `better-auth`, `@better-auth/react`, Next.js 16+, React 19
- Backend: `python-jose[cryptography]`, FastAPI, SQLModel

**Storage**:
- User credentials: PostgreSQL (separate database managed by Better Auth)
- Task data: PostgreSQL (Neon) - existing database
- JWT tokens: Client-side (httpOnly cookies or memory) - not stored server-side

**Testing**:
- Frontend: Jest/React Testing Library (optional per constitution)
- Backend: pytest (optional per constitution)

**Target Platform**:
- Frontend: Vercel (Next.js deployment)
- Backend: Hugging Face Spaces (FastAPI deployment)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- JWT verification: <50ms latency per request
- Authentication flow: <5 seconds for login/registration
- Support 1000+ concurrent authenticated users

**Constraints**:
- Stateless architecture (no server-side sessions)
- JWT verification on every protected request
- user_id must come exclusively from JWT claims
- HTTP 401 for authentication failures, 403 for authorization failures
- Backend must NOT handle user registration or credential storage

**Scale/Scope**:
- Multi-user task management system
- Each user isolated to their own tasks
- Production-grade security for hackathon evaluation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Review

✅ **Spec-Driven Development First**: Complete specification exists at `specs/001-jwt-auth/spec.md` with clear scope and acceptance criteria

✅ **AI as Implementer, Human as Architect**: Specification defines requirements; implementation will be done by Claude Code following explicit constraints

✅ **Deterministic Behavior**: JWT verification is deterministic (signature validation, expiration checks); no LLM components in auth flow

✅ **Evolvability**: Authentication layer is independent of task domain logic; can evolve without breaking task management contracts

✅ **Clear Separation**:
- Domain Logic: Task management (unchanged)
- Interfaces: JWT middleware (new), Better Auth API routes (new)
- Infrastructure: PostgreSQL for users (new), PostgreSQL for tasks (existing)

✅ **Reusable Intelligence**: N/A - no AI-powered features in authentication

✅ **Infrastructure as Declarative**: Environment variables for configuration; no infrastructure changes needed

### Gates Status

- [x] Specification complete and approved
- [x] No implementation details in specification
- [x] Architecture aligns with constitution principles
- [x] Domain logic remains independent of authentication layer
- [x] No violations requiring justification

## Project Structure

### Documentation (this feature)

```text
specs/001-jwt-auth/
├── spec.md                          # Feature specification (273 lines)
├── plan.md                          # This file (implementation plan)
├── research.md                      # Phase 0 research (Q&A format, 8 questions resolved)
├── data-model.md                    # Entity definitions (User, JWT, Task)
├── quickstart.md                    # Step-by-step implementation guide
├── contracts/
│   ├── better-auth-integration.md   # Frontend authentication contract
│   └── jwt-middleware.md            # Backend JWT verification contract
├── checklists/
│   └── requirements.md              # Validation checklist (passed)
└── tasks.md                         # NOT created yet - run /sp.tasks
```

### Source Code (repository root)

```text
phase-02-fullstack-web/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── tasks.py             # MODIFY: Add JWT dependency to all routes
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── auth.py              # CREATE: JWT verification middleware
│   │   │   ├── config.py            # MODIFY: Add BETTER_AUTH_SECRET setting
│   │   │   ├── database.py
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── task.py              # NO CHANGES: Task model already has user_id
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── main.py                      # NO CHANGES: Main FastAPI app
│   ├── requirements.txt             # MODIFY: Add python-jose[cryptography]
│   └── .env                         # MODIFY: Add BETTER_AUTH_SECRET
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── auth/
│   │   │   │       └── [...all]/
│   │   │   │           └── route.ts # CREATE: Better Auth API handler
│   │   │   ├── login/
│   │   │   │   └── page.tsx         # CREATE: Login page
│   │   │   ├── register/
│   │   │   │   └── page.tsx         # CREATE: Registration page
│   │   │   ├── layout.tsx           # NO CHANGES
│   │   │   └── page.tsx             # MODIFY: Add session check and redirect
│   │   ├── components/
│   │   │   └── todo/                # NO CHANGES: Existing components
│   │   ├── lib/
│      │   ├── auth.ts              # CREATE: Better Auth configuration
│   │   │   ├── auth-client.ts       # CREATE: Better Auth client hooks
│   │   │   ├── api-service.ts       # MODIFY: Add JWT token to requests
│   │   │   └── api-config.ts        # NO CHANGES
│   │   └── types/
│   │       └── todo.ts              # NO CHANGES
│   ├── package.json                 # MODIFY: Add better-auth dependencies
│   └── .env.local                   # MODIFY: Add Better Auth config
│
└── README.md                        # MODIFY: Document authentication setup
```

**Structure Decision**: Web application structure (Option 2) is used because the project has separate frontend (Next.js) and backend (FastAPI) directories. Authentication is added as a cross-cutting concern that protects existing task API routes.

## Complexity Tracking

> **No violations** - All constitutional principles are satisfied without exceptions.

## Phase 0: Research (Completed)

**Output**: `research.md` (8 technical questions resolved)

**Key Findings**:
1. Better Auth integrates with Next.js 16+ App Router via API route handlers
2. python-jose verifies JWT tokens using `jwt.decode()` with HS256 algorithm
3. JWT `sub` claim maps to `user_id` for backend authorization
4. Shared secret (BETTER_AUTH_SECRET) required in both environments
5. HTTP 401 for authentication failures, 403 for authorization failures
6. Backend does NOT need user table (JWT signature is proof of user existence)
7. Frontend attaches JWT via Authorization header using Better Auth session
8. Token expiration handled by redirecting to login (no automatic refresh)

**Technical Decisions**:
- Better Auth handles all user registration and login (frontend only)
- python-jose verifies JWT tokens (backend only)
- No user table in backend (stateless architecture)
- Two-stage validation: authentication (401) then authorization (403)
- No automatic token refresh (users re-authenticate on expiration)

## Phase 1: Design (Completed)

### Data Model (`data-model.md`)

**Entities**:

1. **User** (Frontend Only - Better Auth Database):
   - `id`: UUID (primary key)
   - `email`: Unique email address
   - `password`: Hashed with bcrypt
   - Managed by Better Auth library
   - Backend never queries this table

2. **JWT Token** (Stateless - Not Stored):
   - `sub`: User ID (UUID)
   - `email`: User email
   - `iat`: Issued at timestamp
   - `exp`: Expiration timestamp
   - Signed with BETTER_AUTH_SECRET using HS256
   - Stored client-side (httpOnly cookie or memory)

3. **Task** (Backend Database - Existing):
   - `id`: UUID (primary key)
   - `user_id`: User identifier from JWT (indexed)
   - `title`, `description`, `completed`, `created_at`, `updated_at`
   - No schema changes needed

**Data Flow**:
```
Registration → Better Auth → User DB (frontend)
Login → Better Auth → JWT issued → Client storage
API Request → JWT in header → Backend verification → Query by JWT user_id
```

### API Contracts

**Frontend Contract** (`contracts/better-auth-integration.md`):
- Better Auth configuration with PostgreSQL database
- API route handler at `/api/auth/[...all]`
- Client hooks: `useSession`, `signIn`, `signUp`, `signOut`
- Registration/login flows with error handling
- API service integration with JWT token attachment
- Route protection with session checks

**Backend Contract** (`contracts/jwt-middleware.md`):
- `get_current_user_id()` dependency for JWT verification
- `validate_user_ownership()` for authorization checks
- Protected route pattern with two-stage validation
- Error responses: 401 (auth failure), 403 (authz failure)
- Integration with existing task routes

### Quickstart Guide (`quickstart.md`)

**Phase 1: Backend JWT Verification (2-3 hours)**:
1. Install python-jose
2. Generate shared secret
3. Update environment variables
4. Create JWT middleware
5. Update task routes with JWT dependency
6. Test JWT verification

**Phase 2: Frontend Better Auth Integration (2-3 hours)**:
1. Install Better Auth dependencies
2. Set up Better Auth database
3. Create Better Auth configuration
4. Create login/registration pages
5. Update API service with JWT tokens
6. Protect main page with session check

**Phase 3: Testing (1 hour)**:
1. Test user registration
2. Test user login
3. Test authenticated API requests
4. Test token expiration
5. Test unauthorized access

## Implementation Phases

### Phase 2: Tasks Generation (Next Step)

**Command**: `/sp.tasks`

**Expected Output**: `tasks.md` with testable implementation tasks

**Task Categories**:
1. Backend JWT verification middleware
2. Backend route protection
3. Frontend Better Auth setup
4. Frontend authentication UI
5. Frontend API service updates
6. Integration testing
7. Security testing

### Phase 3: Implementation (After Tasks)

**Workflow**: Red-Green-Refactor cycle for each task

**Order**:
1. Backend first (JWT verification infrastructure)
2. Frontend second (Better Auth integration)
3. Integration testing last (end-to-end flows)

### Phase 4: Validation

**Acceptance Criteria** (from spec.md):
- All task routes require valid JWT (FR-B001 to FR-B014)
- Users can register and login in <5 seconds (SC-001)
- 100% user isolation enforcement (SC-002)
- Unauthorized requests rejected in <100ms (SC-003)
- Stateless architecture maintained (SC-004)
- JWT verification adds <50ms latency (SC-005)

## Risk Analysis

### Risk 1: BETTER_AUTH_SECRET Mismatch

**Impact**: JWT tokens issued by frontend cannot be verified by backend

**Mitigation**:
- Document secret generation in quickstart
- Validate secret format (minimum 32 characters)
- Test JWT verification immediately after setup

**Likelihood**: Medium | **Severity**: High

---

### Risk 2: Better Auth Database Connection Failure

**Impact**: Users cannot register or login

**Mitigation**:
- Use separate database for Better Auth (not task database)
- Test database connection during setup
- Provide clear error messages for connection failures

**Likelihood**: Low | **Severity**: High

---

### Risk 3: Token Expiration During Active Session

**Impact**: User interrupted mid-task when token expires

**Mitigation**:
- Set reasonable expiration time (24 hours)
- Frontend detects 401 and redirects to login with clear message
- Document expected behavior in user guide

**Likelihood**: High | **Severity**: Low

---

## Dependencies and Prerequisites

### External Dependencies

**Frontend**:
- `better-auth` - Authentication library for Next.js
- `@better-auth/react` - React hooks for Better Auth
- PostgreSQL database for user credentials (separate from task database)

**Backend**:
- `python-jose[cryptography]` - JWT verification library
- Shared secret (BETTER_AUTH_SECRET) configured in both environments

### Internal Dependencies

**Existing Code**:
- Task API routes at `phase-02-fullstack-web/backend/src/api/tasks.py`
- Task model at `phase-02-fullstack-web/backend/src/models/task.py`
- API service at `phase-02-fullstack-web/frontend/src/lib/api-service.ts`

**No Breaking Changes**: Authentication is added as middleware; existing task logic unchanged

### Environment Setup

**Required Environment Variables**:

Frontend (`.env.local`):
```bash
BETTER_AUTH_SECRET=<shared-secret>
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_DATABASE_URL=postgresql://...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Backend (`.env`):
```bash
BETTER_AUTH_SECRET=<same-shared-secret>
DATABASE_URL=postgresql://...
CORS_ORIGINS=http://localhost:3000,...
```

## Architectural Decisions

### ADR 1: Better Auth for Frontend Authentication

**Context**: Need user registration, login, and JWT issuance in frontend

**Decision**: Use Better Auth library instead of custom authentication

**Rationale**:
- Production-grade security out of the box
- Built-in JWT signing with configurable secrets
- Next.js 16+ App Router support
- Reduces implementation time and security risks

**Alternatives Considered**:
- NextAuth.js: More complex, heavier weight
- Custom JWT implementation: Higher security risk, more development time

**Consequences**:
- Requires separate PostgreSQL database for user credentials
- Adds dependency on Better Auth library
- Simplifies frontend authentication logic

---

### ADR 2: python-jose for Backend JWT Verification

**Context**: Need to verify JWT tokens in FastAPI backend

**Decision**: Use python-jose library for JWT verification

**Rationale**:
- Lightweight and focused on JWT operations
- Standard library for JWT in Python ecosystem
- Compatible with Better Auth's HS256 algorithm
- Well-documented and actively maintained

**Alternatives Considered**:
- PyJWT: Similar functionality, slightly different API
- Custom JWT verification: Security risk, reinventing the wheel

**Consequences**:
- Adds python-jose dependency to backend
- Requires shared secret management between frontend and backend
- Provides standard JWT verification with minimal overhead

---

### ADR 3: Stateless JWT Architecture (No Token Blacklist)

**Context**: Need to decide whether to implement server-side token invalidation

**Decision**: Use stateless JWT architecture without token blacklists or server-side sessions

**Rationale**:
- Aligns with specification constraints (FR-B012)
- Enables horizontal scalability (no shared session state)
- Simplifies backend implementation (no token storage)
- Standard practice for stateless authentication

**Alternatives Considered**:
- Token blacklist: Adds complexity, requires database/cache, breaks stateless architecture
- Server-side sessions: Contradicts specification, adds state management overhead

**Consequences**:
- Tokens remain valid until expiration (cannot be revoked early)
- Short expiration time (24 hours) mitigates security risk
- Users must re-authenticate after token expiration
- No database queries for authentication (only signature verification)

---

### ADR 4: Two-Stage Validation (401 vs 403)

**Context**: Need to distinguish authentication failures from authorization failures

**Decision**: Implement two-stage validation with distinct HTTP status codes

**Rationale**:
- HTTP 401: Authentication failure (missing, invalid, expired token)
- HTTP 403: Authorization failure (valid token, wrong user)
- Follows REST best practices and RFC 7235
- Provides clear error semantics for frontend

**Alternatives Considered**:
- Single 401 for all failures: Less precise error reporting
- Custom status codes: Non-standard, confusing for clients

**Consequences**:
- Frontend can distinguish between "need to login" (401) and "access denied" (403)
- Backend implements two separate validation steps
- Clear separation of authentication vs authorization logic

---

## Success Metrics

**From Specification** (SC-001 to SC-010):

1. ✅ Login/registration completes in <5 seconds
2. ✅ 100% user isolation (no cross-user access)
3. ✅ Unauthorized requests rejected in <100ms
4. ✅ Stateless architecture (no server-side sessions)
5. ✅ JWT verification adds <50ms latency
6. ✅ 100% of protected endpoints require JWT
7. ✅ Production-grade security visible to judges
8. ✅ 100% of tampered tokens rejected
9. ✅ Clear error messages for auth failures
10. ✅ Supports 1000+ concurrent users

**Validation Method**:
- Performance testing with load testing tools
- Security testing with invalid/tampered tokens
- Integration testing with multiple user accounts
- Code review for architecture compliance

## Next Steps

1. **Run `/sp.tasks`** to generate implementation tasks
2. **Review tasks** for completeness and order
3. **Begin implementation** following Red-Green-Refactor cycle
4. **Test incrementally** after each task completion
5. **Deploy to production** with proper secrets management

## Notes

- This plan follows the spec-driven development workflow
- All design artifacts are complete and ready for implementation
- No clarifications needed - all technical unknowns resolved
- Architecture aligns with constitution principles
- Ready to proceed to task generation phase
