# Tasks: JWT-Based Authentication for Task Management

**Input**: Design documents from `/specs/001-jwt-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL per constitution. This feature specification does not explicitly request TDD, so test tasks are NOT included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase-02-fullstack-web/backend/`
- **Frontend**: `phase-02-fullstack-web/frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Generate shared JWT secret using Python secrets module and document in quickstart
- [ ] T002 Install python-jose[cryptography] in backend requirements.txt
- [ ] T003 [P] Install better-auth and @better-auth/react in frontend package.json
- [ ] T004 [P] Create separate PostgreSQL database for Better Auth user credentials
- [ ] T005 Update backend .env with BETTER_AUTH_SECRET environment variable
- [ ] T006 [P] Update frontend .env.local with Better Auth configuration (BETTER_AUTH_SECRET, BETTER_AUTH_URL, BETTER_AUTH_DATABASE_URL)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Add better_auth_secret field to Settings class in phase-02-fullstack-web/backend/src/core/config.py
- [ ] T008 Create JWT verification middleware with get_current_user_id() function in phase-02-fullstack-web/backend/src/core/auth.py
- [ ] T009 Create validate_user_ownership() authorization function in phase-02-fullstack-web/backend/src/core/auth.py
- [ ] T010 [P] Create Better Auth configuration in phase-02-fullstack-web/frontend/src/lib/auth.ts
- [ ] T011 [P] Create Better Auth API route handler in phase-02-fullstack-web/frontend/src/app/api/auth/[...all]/route.ts
- [ ] T012 [P] Create Better Auth client hooks in phase-02-fullstack-web/frontend/src/lib/auth-client.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and log in through the frontend, receiving a JWT token for subsequent API requests

**Independent Test**:
1. Navigate to /register and create a new account with email/password
2. Verify redirect to home page after successful registration
3. Navigate to /login and log in with registered credentials
4. Verify JWT token is stored in browser (check cookies or session storage)
5. Verify redirect to home page after successful login

### Implementation for User Story 1

- [ ] T013 [P] [US1] Create registration page UI in phase-02-fullstack-web/frontend/src/app/register/page.tsx
- [ ] T014 [P] [US1] Create login page UI in phase-02-fullstack-web/frontend/src/app/login/page.tsx
- [ ] T015 [US1] Implement registration form submission with signUp.email() in register page
- [ ] T016 [US1] Implement login form submission with signIn.email() in login page
- [ ] T017 [US1] Add error handling for registration failures (duplicate email, weak password) in register page
- [ ] T018 [US1] Add error handling for login failures (invalid credentials) in login page
- [ ] T019 [US1] Add redirect logic after successful registration/login to home page

**Checkpoint**: At this point, users can register and log in. JWT tokens are issued by Better Auth and stored client-side.

---

## Phase 4: User Story 2 - Authenticated Task Operations (Priority: P2)

**Goal**: Enable authenticated users to create, view, update, and delete their personal tasks through API requests with JWT tokens

**Independent Test**:
1. Log in as a user to obtain JWT token
2. Create a new task via API and verify it appears in task list
3. Update the task and verify changes are saved
4. Delete the task and verify it's removed
5. Attempt to access another user's tasks by changing user_id in URL - verify 403 Forbidden response

### Implementation for User Story 2

- [ ] T020 [US2] Add get_current_user_id dependency to get_all_tasks route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T021 [US2] Add validate_user_ownership call to get_all_tasks route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T022 [US2] Update get_all_tasks database query to filter by jwt_user_id in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T023 [P] [US2] Add get_current_user_id dependency to create_task route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T024 [P] [US2] Add validate_user_ownership call to create_task route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T025 [P] [US2] Update create_task to use jwt_user_id for task ownership in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T026 [P] [US2] Add get_current_user_id dependency to get_task_by_id route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T027 [P] [US2] Add validate_user_ownership call to get_task_by_id route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T028 [P] [US2] Update get_task_by_id database query to filter by jwt_user_id in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T029 [P] [US2] Add get_current_user_id dependency to update_task route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T030 [P] [US2] Add validate_user_ownership call to update_task route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T031 [P] [US2] Update update_task database query to filter by jwt_user_id in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T032 [P] [US2] Add get_current_user_id dependency to delete_task route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T033 [P] [US2] Add validate_user_ownership call to delete_task route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T034 [P] [US2] Update delete_task database query to filter by jwt_user_id in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T035 [P] [US2] Add get_current_user_id dependency to toggle_task_completion route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T036 [P] [US2] Add validate_user_ownership call to toggle_task_completion route in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T037 [P] [US2] Update toggle_task_completion database query to filter by jwt_user_id in phase-02-fullstack-web/backend/src/api/tasks.py
- [ ] T038 [US2] Create getAuthHeaders() method in phase-02-fullstack-web/frontend/src/lib/api-service.ts
- [ ] T039 [US2] Update getTasks() method to use getAuthHeaders() in phase-02-fullstack-web/frontend/src/lib/api-service.ts
- [ ] T040 [US2] Update createTask() method to use getAuthHeaders() in phase-02-fullstack-web/frontend/src/lib/api-service.ts
- [ ] T041 [US2] Update updateTask() method to use getAuthHeaders() in phase-02-fullstack-web/frontend/src/lib/api-service.ts
- [ ] T042 [US2] Update deleteTask() method to use getAuthHeaders() in phase-02-fullstack-web/frontend/src/lib/api-service.ts
- [ ] T043 [US2] Update toggleComplete() method to use getAuthHeaders() in phase-02-fullstack-web/frontend/src/lib/api-service.ts
- [ ] T044 [US2] Add 401 error handling (redirect to login) in all API service methods in phase-02-fullstack-web/frontend/src/lib/api-service.ts
- [ ] T045 [US2] Add 403 error handling (access denied message) in all API service methods in phase-02-fullstack-web/frontend/src/lib/api-service.ts

**Checkpoint**: At this point, authenticated users can perform all task operations with JWT tokens. Backend enforces user isolation.

---

## Phase 5: User Story 3 - Client-Side Logout (Priority: P3)

**Goal**: Enable users to securely log out by deleting their JWT token from client-side storage

**Independent Test**:
1. Log in as a user
2. Perform authenticated operations (create task)
3. Click logout button
4. Verify JWT token is deleted from browser storage
5. Attempt to access protected resources - verify redirect to login page

### Implementation for User Story 3

- [ ] T046 [US3] Add useSession hook to main page in phase-02-fullstack-web/frontend/src/app/page.tsx
- [ ] T047 [US3] Add session check and redirect logic to login page in phase-02-fullstack-web/frontend/src/app/page.tsx
- [ ] T048 [US3] Create logout button component with signOut() handler in phase-02-fullstack-web/frontend/src/components/logout-button.tsx
- [ ] T049 [US3] Add logout button to main page layout in phase-02-fullstack-web/frontend/src/app/page.tsx
- [ ] T050 [US3] Implement redirect to login page after logout in logout button component

**Checkpoint**: At this point, users can log out and their JWT tokens are deleted. Subsequent API requests without tokens receive 401 responses.

---

## Phase 6: User Story 4 - Authentication and Authorization Enforcement (Priority: P4)

**Goal**: Ensure backend automatically rejects API requests based on JWT token validity and user ownership with appropriate HTTP status codes

**Independent Test**:
1. Attempt API request without Authorization header - verify 401 Unauthorized
2. Attempt API request with invalid JWT signature - verify 401 Unauthorized
3. Attempt API request with expired JWT token - verify 401 Unauthorized
4. Attempt API request with valid JWT for User A to access User B's tasks - verify 403 Forbidden
5. Verify all protected endpoints require JWT tokens

### Implementation for User Story 4

- [ ] T051 [P] [US4] Add WWW-Authenticate header to 401 responses in phase-02-fullstack-web/backend/src/core/auth.py
- [ ] T052 [P] [US4] Verify JWT expiration validation in get_current_user_id() in phase-02-fullstack-web/backend/src/core/auth.py
- [ ] T053 [P] [US4] Verify JWT signature validation in get_current_user_id() in phase-02-fullstack-web/backend/src/core/auth.py
- [ ] T054 [P] [US4] Verify malformed token handling in get_current_user_id() in phase-02-fullstack-web/backend/src/core/auth.py
- [ ] T055 [US4] Test missing Authorization header scenario and verify 401 response
- [ ] T056 [US4] Test invalid JWT signature scenario and verify 401 response
- [ ] T057 [US4] Test expired JWT token scenario and verify 401 response
- [ ] T058 [US4] Test cross-user access attempt and verify 403 response
- [ ] T059 [US4] Verify all task routes require JWT authentication (no bypass routes)

**Checkpoint**: All authentication and authorization enforcement is complete. Backend rejects unauthorized requests with correct HTTP status codes.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T060 [P] Update README.md with authentication setup instructions in repository root
- [ ] T061 [P] Document shared secret generation process in README.md
- [ ] T062 [P] Document environment variable configuration in README.md
- [ ] T063 [P] Add CORS configuration update instructions for production deployment in README.md
- [ ] T064 Verify quickstart.md steps work end-to-end
- [ ] T065 Test complete authentication flow (register → login → API operations → logout)
- [ ] T066 Verify JWT token expiration handling (24-hour expiration)
- [ ] T067 Verify Better Auth database connection and user storage
- [ ] T068 Test production deployment with proper secrets management
- [ ] T069 Code review for security best practices (no hardcoded secrets, proper error messages)
- [ ] T070 Performance testing: Verify JWT verification adds <50ms latency per request

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 for JWT token issuance but is independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires US1 for login but is independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Cross-cutting validation, independently testable

### Within Each User Story

- Frontend UI tasks (login/register pages) can run in parallel
- Backend route protection tasks can run in parallel (all marked [P])
- API service updates can run sequentially (depend on getAuthHeaders() method)
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T006)
- All Foundational tasks marked [P] can run in parallel (T010, T011, T012)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within User Story 1: T013 and T014 can run in parallel (different pages)
- Within User Story 2: All backend route updates (T023-T037) can run in parallel (different routes)
- Within User Story 4: All validation tasks (T051-T054) can run in parallel (different validation checks)

---

## Parallel Example: User Story 2 (Backend Route Protection)

```bash
# Launch all backend route protection tasks together:
Task: "Add get_current_user_id dependency to create_task route"
Task: "Add get_current_user_id dependency to get_task_by_id route"
Task: "Add get_current_user_id dependency to update_task route"
Task: "Add get_current_user_id dependency to delete_task route"
Task: "Add get_current_user_id dependency to toggle_task_completion route"

# These can all run in parallel because they modify different route handlers
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T012) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T013-T019)
4. **STOP and VALIDATE**: Test user registration and login independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP: Users can register and login!)
3. Add User Story 2 → Test independently → Deploy/Demo (Users can manage tasks with authentication!)
4. Add User Story 3 → Test independently → Deploy/Demo (Users can logout securely!)
5. Add User Story 4 → Test independently → Deploy/Demo (Full security enforcement!)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Frontend authentication UI)
   - Developer B: User Story 2 (Backend route protection)
   - Developer C: User Story 3 (Logout functionality)
   - Developer D: User Story 4 (Security validation)
3. Stories complete and integrate independently

---

## Task Count Summary

- **Total Tasks**: 70
- **Setup (Phase 1)**: 6 tasks
- **Foundational (Phase 2)**: 6 tasks (BLOCKING)
- **User Story 1 (Phase 3)**: 7 tasks
- **User Story 2 (Phase 4)**: 26 tasks
- **User Story 3 (Phase 5)**: 5 tasks
- **User Story 4 (Phase 6)**: 9 tasks
- **Polish (Phase 7)**: 11 tasks

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**: Each user story has clear independent test criteria for validation

**Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1) = 19 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are OPTIONAL per constitution - not included in this task list
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend tasks focus on JWT verification and route protection
- Frontend tasks focus on Better Auth integration and UI
- All tasks include exact file paths for clarity
- Security is enforced through JWT middleware, not application logic
