# Tasks: Backend REST API with Persistent Storage

**Input**: Design documents from `/specs/003-backend-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are excluded per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `phase-02-fullstack-web/backend/`
- Backend paths: `backend/src/`, `backend/tests/`
- All paths relative to repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure: phase-02-fullstack-web/backend/src/{models,api,core}
- [ ] T002 Initialize Python project with pyproject.toml and dependencies (fastapi, sqlmodel, psycopg2-binary, uvicorn, python-dotenv, pydantic-settings)
- [ ] T003 [P] Create .env.example file with DATABASE_URL and CORS_ORIGINS templates in phase-02-fullstack-web/backend/
- [ ] T004 [P] Create README.md with setup instructions in phase-02-fullstack-web/backend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create database configuration in phase-02-fullstack-web/backend/src/core/config.py (Settings class with DATABASE_URL, CORS_ORIGINS)
- [ ] T006 Create database connection management in phase-02-fullstack-web/backend/src/core/database.py (engine, get_session dependency)
- [ ] T007 Create Task model in phase-02-fullstack-web/backend/src/models/task.py (SQLModel with id, user_id, title, description, completed, created_at, updated_at)
- [ ] T008 Create FastAPI application in phase-02-fullstack-web/backend/main.py (app initialization, CORS middleware, startup event for table creation)
- [ ] T009 Create API router structure in phase-02-fullstack-web/backend/src/api/tasks.py (empty router, register with main app)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Retrieve All Tasks for a User (Priority: P1) 🎯 MVP

**Goal**: Enable frontend to fetch all tasks for a specific user to display in the UI

**Independent Test**: Seed database with tasks for user123, make GET request to /api/user123/tasks, verify response contains all tasks with correct structure

### Implementation for User Story 1

- [ ] T010 [US1] Implement GET /api/{user_id}/tasks endpoint in phase-02-fullstack-web/backend/src/api/tasks.py (query tasks filtered by user_id, return JSON array)
- [ ] T011 [US1] Add response model TaskRead to phase-02-fullstack-web/backend/src/models/task.py (Pydantic model for API responses)
- [ ] T012 [US1] Add error handling for database connection failures in GET /api/{user_id}/tasks endpoint
- [ ] T013 [US1] Verify empty array response when user has no tasks

**Checkpoint**: At this point, User Story 1 should be fully functional - can retrieve all tasks for any user

---

## Phase 4: User Story 2 - Create a New Task (Priority: P1)

**Goal**: Enable frontend to create new tasks for a user with title and optional description

**Independent Test**: Send POST request to /api/user123/tasks with task data, verify response contains created task with generated ID and timestamps, confirm task persists in database

### Implementation for User Story 2

- [ ] T014 [US2] Add TaskCreate request model to phase-02-fullstack-web/backend/src/models/task.py (title: str, description: str | None)
- [ ] T015 [US2] Implement POST /api/{user_id}/tasks endpoint in phase-02-fullstack-web/backend/src/api/tasks.py (create task with UUID, set user_id from path, return 201)
- [ ] T016 [US2] Add validation for required title field (non-empty, max 500 chars)
- [ ] T017 [US2] Add validation for optional description field (max 2000 chars)
- [ ] T018 [US2] Set default values: completed=false, created_at=now, updated_at=now
- [ ] T019 [US2] Add error handling for validation failures (return 422 with details)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - can create and retrieve tasks

---

## Phase 5: User Story 5 - Toggle Task Completion Status (Priority: P1)

**Goal**: Enable frontend to mark tasks as complete or incomplete with a single action

**Independent Test**: Create task with completed=false, send PATCH to /api/user123/tasks/{id}/complete, verify completed=true, send PATCH again, verify completed=false

### Implementation for User Story 5

- [ ] T020 [US5] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint in phase-02-fullstack-web/backend/src/api/tasks.py (toggle completed status, update updated_at)
- [ ] T021 [US5] Add user isolation check: return 404 if task belongs to different user
- [ ] T022 [US5] Add error handling for task not found (return 404)
- [ ] T023 [US5] Verify updated_at timestamp changes on each toggle

**Checkpoint**: At this point, User Stories 1, 2, AND 5 should all work independently - core task management functional

---

## Phase 6: User Story 6 - Retrieve a Single Task by ID (Priority: P2)

**Goal**: Enable frontend to fetch details for a specific task

**Independent Test**: Create task and note its ID, send GET to /api/user123/tasks/{id}, verify response contains complete task object

### Implementation for User Story 6

- [ ] T024 [US6] Implement GET /api/{user_id}/tasks/{id} endpoint in phase-02-fullstack-web/backend/src/api/tasks.py (query by id and user_id, return single task)
- [ ] T025 [US6] Add user isolation check: return 404 if task belongs to different user
- [ ] T026 [US6] Add error handling for invalid task ID (return 404)

**Checkpoint**: At this point, User Stories 1, 2, 5, AND 6 should all work independently

---

## Phase 7: User Story 3 - Update an Existing Task (Priority: P2)

**Goal**: Enable frontend to modify task title and description

**Independent Test**: Create task, send PUT to /api/user123/tasks/{id} with modified data, verify response shows changes with updated updated_at timestamp

### Implementation for User Story 3

- [ ] T027 [US3] Add TaskUpdate request model to phase-02-fullstack-web/backend/src/models/task.py (same as TaskCreate)
- [ ] T028 [US3] Implement PUT /api/{user_id}/tasks/{id} endpoint in phase-02-fullstack-web/backend/src/api/tasks.py (update title/description, set updated_at=now)
- [ ] T029 [US3] Add user isolation check: return 404 if task belongs to different user
- [ ] T030 [US3] Add validation for title (required, non-empty, max 500 chars)
- [ ] T031 [US3] Add validation for description (optional, max 2000 chars)
- [ ] T032 [US3] Preserve id and created_at (do not allow modification)
- [ ] T033 [US3] Add error handling for task not found (return 404)

**Checkpoint**: At this point, User Stories 1, 2, 3, 5, AND 6 should all work independently

---

## Phase 8: User Story 4 - Delete a Task (Priority: P2)

**Goal**: Enable frontend to permanently remove tasks

**Independent Test**: Create task, send DELETE to /api/user123/tasks/{id}, verify 204 response, confirm task no longer appears in GET /api/user123/tasks

### Implementation for User Story 4

- [ ] T034 [US4] Implement DELETE /api/{user_id}/tasks/{id} endpoint in phase-02-fullstack-web/backend/src/api/tasks.py (delete task, return 204)
- [ ] T035 [US4] Add user isolation check: return 404 if task belongs to different user
- [ ] T036 [US4] Add error handling for task not found (return 404)
- [ ] T037 [US4] Verify task is permanently deleted (no soft delete)

**Checkpoint**: All user stories should now be independently functional - complete CRUD operations available

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T038 [P] Add request logging middleware in phase-02-fullstack-web/backend/main.py (log timestamp, endpoint, user_id, status)
- [ ] T039 [P] Add global exception handler for database errors in phase-02-fullstack-web/backend/main.py (return 500 with generic message)
- [ ] T040 [P] Add input sanitization for user_id path parameter (max 255 chars, URL-encoded)
- [ ] T041 [P] Verify OpenAPI documentation at /docs matches contracts/openapi.yaml
- [ ] T042 Run quickstart.md validation: setup, create task, retrieve tasks, toggle completion, update task, delete task
- [ ] T043 [P] Add database connection pooling configuration in phase-02-fullstack-web/backend/src/core/database.py
- [ ] T044 [P] Update README.md with deployment instructions and environment variables

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories

**Note**: All user stories are independently testable and can be implemented in parallel after Foundational phase completes.

### Within Each User Story

- Models before endpoints
- Core implementation before error handling
- Validation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All Polish tasks marked [P] can run in parallel (T038, T039, T040, T041, T043, T044)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: After Foundational Phase

```bash
# All P1 user stories can start together:
Task: "Implement GET /api/{user_id}/tasks endpoint" (US1)
Task: "Implement POST /api/{user_id}/tasks endpoint" (US2)
Task: "Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint" (US5)

# All P2 user stories can start together (after P1 or in parallel):
Task: "Implement GET /api/{user_id}/tasks/{id} endpoint" (US6)
Task: "Implement PUT /api/{user_id}/tasks/{id} endpoint" (US3)
Task: "Implement DELETE /api/{user_id}/tasks/{id} endpoint" (US4)
```

---

## Implementation Strategy

### MVP First (P1 User Stories Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T009) - CRITICAL
3. Complete Phase 3: User Story 1 (T010-T013) - Retrieve tasks
4. Complete Phase 4: User Story 2 (T014-T019) - Create tasks
5. Complete Phase 5: User Story 5 (T020-T023) - Toggle completion
6. **STOP and VALIDATE**: Test all P1 stories independently
7. Deploy/demo MVP with core functionality

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (read-only MVP)
3. Add User Story 2 → Test independently → Deploy/Demo (create + read MVP)
4. Add User Story 5 → Test independently → Deploy/Demo (full P1 MVP)
5. Add User Story 6 → Test independently → Deploy/Demo
6. Add User Story 3 → Test independently → Deploy/Demo
7. Add User Story 4 → Test independently → Deploy/Demo (complete CRUD)
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is done:
   - Developer A: User Story 1 (T010-T013)
   - Developer B: User Story 2 (T014-T019)
   - Developer C: User Story 5 (T020-T023)
3. Then proceed to P2 stories:
   - Developer A: User Story 6 (T024-T026)
   - Developer B: User Story 3 (T027-T033)
   - Developer C: User Story 4 (T034-T037)
4. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 44
- Setup: 4 tasks
- Foundational: 5 tasks (BLOCKING)
- User Story 1 (P1): 4 tasks
- User Story 2 (P1): 6 tasks
- User Story 5 (P1): 4 tasks
- User Story 6 (P2): 3 tasks
- User Story 3 (P2): 7 tasks
- User Story 4 (P2): 4 tasks
- Polish: 7 tasks

**Parallel Opportunities**: 10 tasks marked [P]

**MVP Scope** (P1 stories only): 19 tasks (Setup + Foundational + US1 + US2 + US5)

**Independent Test Criteria**:
- US1: Can retrieve all tasks for a user (empty array or populated list)
- US2: Can create new tasks with validation
- US5: Can toggle task completion status
- US6: Can retrieve single task by ID
- US3: Can update task title and description
- US4: Can delete tasks permanently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included per specification (not explicitly requested)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
