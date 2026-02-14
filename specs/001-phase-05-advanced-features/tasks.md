# Tasks: Phase 5 Part A - Advanced Task Management Features

**Input**: Design documents from `/specs/001-phase-05-advanced-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT included as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md, this project uses microservices architecture:
- **Backend API**: `phase-05-cloud-deploy/services/backend-api/`
- **Frontend**: `phase-05-cloud-deploy/services/frontend/`
- **Recurring Service**: `phase-05-cloud-deploy/services/recurring-service/`
- **Notification Service**: `phase-05-cloud-deploy/services/notification-service/`
- **Infrastructure**: `phase-05-cloud-deploy/infrastructure/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize infrastructure components required for microservices architecture

- [X] T001 Create infrastructure directory structure per plan.md in phase-05-cloud-deploy/infrastructure/
- [X] T002 [P] Create Dapr Pub/Sub component configuration in infrastructure/dapr/components/kafka-pubsub.yaml
- [X] T003 [P] Create Dapr State Store component configuration in infrastructure/dapr/components/statestore.yaml
- [X] T004 [P] Create Dapr Secrets component configuration in infrastructure/dapr/components/secrets.yaml
- [X] T005 [P] Create Dapr Jobs API component configuration in infrastructure/dapr/components/jobs.yaml
- [X] T006 [P] Create Redpanda docker-compose configuration for local development in infrastructure/kafka/local/docker-compose.yml
- [X] T007 [P] Create PostgreSQL schema initialization scripts for tasks, notifications, and audit schemas in services/backend-api/migrations/
- [X] T008 Create unified docker-compose.yml for all services in infrastructure/docker-compose/docker-compose.yml
- [X] T009 [P] Update backend-api requirements.txt with Dapr SDK, aiokafka, OpenAI SDK, Resend SDK
- [X] T010 [P] Update frontend package.json with real-time sync dependencies and Dapr JavaScript SDK

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 Create database migration for tasks schema with tasks, tags, task_tags, reminders, recurrence_rules tables in services/backend-api/migrations/001_create_tasks_schema.sql
- [X] T012 [P] Extend existing Task model with priority, is_recurring, parent_task_id, recurrence_rule_id fields in services/backend-api/src/models/task.py
- [X] T013 [P] Create Tag model in services/backend-api/src/models/tag.py
- [X] T014 [P] Create Reminder model in services/backend-api/src/models/reminder.py
- [X] T015 [P] Create RecurrenceRule model in services/backend-api/src/models/recurrence.py
- [X] T016 Create Dapr client wrapper with pub/sub and service invocation methods in services/backend-api/src/core/dapr.py
- [X] T017 Create EventPublisher service for Kafka event publishing in services/backend-api/src/services/event_publisher.py
- [X] T018 Update database.py to support multiple schemas (public, tasks, notifications, audit) in services/backend-api/src/core/database.py
- [X] T019 Update config.py with Kafka, Dapr, OpenAI, and Resend configuration in services/backend-api/src/core/config.py
- [X] T020 Create Pydantic schemas for Tag in services/backend-api/src/schemas/tag.py
- [X] T021 [P] Create Pydantic schemas for Reminder in services/backend-api/src/schemas/reminder.py
- [X] T022 [P] Create Pydantic schemas for RecurrenceRule in services/backend-api/src/schemas/recurrence.py
- [X] T023 Update existing task schema with new fields (priority, tags, reminders, recurrence) in services/backend-api/src/schemas/task.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 + User Story 5 - Task Organization & Real-Time Sync (Priority: P1) 🎯 MVP

**Goal**: Users can organize tasks with priorities and tags, search/filter tasks, and see changes synchronized in real-time between interfaces

**Independent Test**: Create a task with high priority and "work" tag in graphical interface, verify it appears immediately with correct attributes. Search for the task, apply filters, and verify results update in real-time.

**Why Combined**: US5 (real-time sync) is foundational for the dual interface design. Implementing it with US1 ensures the core task management features work seamlessly across both interfaces from the start.

### Backend Implementation for US1 + US5

- [X] T024 [P] [US1] Create TagService with CRUD operations and autocomplete in services/backend-api/src/services/tag_service.py
- [X] T025 [P] [US1] Create SearchService with full-text search and filtering logic in services/backend-api/src/services/search_service.py
- [X] T026 [US1] Extend existing TaskService with priority management, tag operations, and event publishing in services/backend-api/src/services/task_service.py
- [X] T027 [US1] Create tags API endpoints (GET /api/tags, POST /api/tags, PUT /api/tags/{id}, DELETE /api/tags/{id}) in services/backend-api/src/api/tags.py
- [X] T028 [US1] Create search API endpoint (GET /api/search) in services/backend-api/src/api/search.py
- [X] T029 [US1] Extend existing tasks API with priority and tag operations (POST /api/tasks/{id}/tags, DELETE /api/tasks/{id}/tags) in services/backend-api/src/api/tasks.py
- [X] T030 [US1] Update task list endpoint to support filtering by priority, tags, completion status, and sorting in services/backend-api/src/api/tasks.py
- [X] T031 [US5] Publish TaskCreated, TaskUpdated, TaskCompleted, TaskDeleted events via EventPublisher in services/backend-api/src/services/task_service.py
- [X] T032 [US5] Create real-time sync endpoint for frontend polling/WebSocket in services/backend-api/src/api/realtime.py

### Frontend Implementation for US1 + US5

- [X] T033 [P] [US1] Create FilterPanel component with priority, tag, status, date filters in services/frontend/src/components/tasks/FilterPanel.tsx
- [X] T034 [P] [US1] Create SearchBar component with real-time search in services/frontend/src/components/tasks/SearchBar.tsx
- [X] T035 [P] [US1] Create TagPill component for displaying colored tags in services/frontend/src/components/tasks/TagPill.tsx
- [X] T036 [US1] Extend TaskList component with priority indicators, tag display, and filter/sort controls in services/frontend/src/components/tasks/TaskList.tsx
- [X] T037 [US1] Extend TaskForm component with priority selector, tag input with autocomplete, and validation in services/frontend/src/components/tasks/TaskForm.tsx
- [X] T038 [US1] Create tag management API client methods in services/frontend/src/services/api.ts
- [X] T039 [US1] Create search and filter API client methods in services/frontend/src/services/api.ts
- [X] T040 [US5] Create real-time sync service with polling/WebSocket for task updates in services/frontend/src/services/realtime.ts
- [X] T041 [US5] Integrate real-time sync into TaskList to auto-update on changes in services/frontend/src/components/tasks/TaskList.tsx
- [X] T042 [US1] Update TypeScript types with new task fields (priority, tags, reminders, recurrence) in services/frontend/src/lib/types.ts

**Checkpoint**: At this point, User Stories 1 AND 5 should be fully functional - users can organize tasks and see real-time synchronization

---

## Phase 4: User Story 2 - Schedule Tasks with Due Dates and Reminders (Priority: P2)

**Goal**: Users can set due dates with optional times and configure multiple reminders that are delivered at exact scheduled times

**Independent Test**: Create a task with due date set to tomorrow at 2pm, add reminders for 15min and 1hr before. Verify visual indicators show "due soon" status and reminders are scheduled correctly.

### Notification Service Creation for US2

- [X] T043 [US2] Create notification-service directory structure in services/notification-service/
- [X] T044 [P] [US2] Create notification service configuration in services/notification-service/src/config.py
- [X] T045 [P] [US2] Create Dapr client for pub/sub in services/notification-service/src/dapr_client.py
- [X] T046 [US2] Create email sender with Resend API integration in services/notification-service/src/email_sender.py
- [X] T047 [US2] Create retry handler with exponential backoff (3 attempts: 0s, 5min, 15min) in services/notification-service/src/retry_handler.py
- [X] T048 [US2] Create Dapr subscriber for reminders topic in services/notification-service/src/subscriber.py
- [X] T049 [US2] Create FastAPI app with Dapr subscriber routes in services/notification-service/main.py
- [X] T050 [P] [US2] Create Dockerfile for notification-service in services/notification-service/Dockerfile
- [X] T051 [P] [US2] Create requirements.txt for notification-service in services/notification-service/requirements.txt
- [X] T052 [US2] Create Dapr subscription configuration for notification-service in infrastructure/dapr/subscriptions/notification-service-sub.yaml
- [X] T053 [US2] Create database migration for notifications schema with notification_log table in services/backend-api/migrations/002_create_notifications_schema.sql

### Backend Implementation for US2

- [X] T054 [US2] Create ReminderService with scheduling via Dapr Jobs API in services/backend-api/src/services/reminder_service.py
- [X] T055 [US2] Create reminder API endpoints (POST /api/tasks/{id}/reminders, DELETE /api/tasks/{id}/reminders) in services/backend-api/src/api/tasks.py
- [X] T056 [US2] Extend TaskService to handle due date validation and reminder scheduling in services/backend-api/src/services/task_service.py
- [X] T057 [US2] Publish ReminderScheduled events when reminders are created in services/backend-api/src/services/reminder_service.py
- [X] T058 [US2] Update task list endpoint to include due date status indicators (overdue, due today, due soon) in services/backend-api/src/api/tasks.py

### Frontend Implementation for US2

- [X] T059 [US2] Extend TaskForm with due date picker (date + optional time) and timezone awareness in services/frontend/src/components/tasks/TaskForm.tsx
- [X] T060 [US2] Extend TaskForm with reminder configuration UI (15min, 1hr, 1day, 1week, custom) in services/frontend/src/components/tasks/TaskForm.tsx
- [X] T061 [US2] Extend TaskList to display due date badges with color indicators (red=overdue, yellow=today, orange=soon) in services/frontend/src/components/tasks/TaskList.tsx
- [X] T062 [US2] Create reminder API client methods in services/frontend/src/services/api.ts
- [X] T063 [US2] Add due date filtering to FilterPanel component in services/frontend/src/components/tasks/FilterPanel.tsx

**Checkpoint**: At this point, User Story 2 should be fully functional - users can schedule tasks and receive timely reminders

---

## Phase 5: User Story 4 - Interact via Natural Language Chat (Priority: P2)

**Goal**: Users can manage tasks using conversational language through a chat interface powered by AI

**Independent Test**: Type "Add a high priority task to review the quarterly report by Friday with work tag" in chat interface, verify task is created with correct attributes (high priority, due date = Friday, work tag).

### Backend Implementation for US4

- [X] T064 [P] [US4] Create MCP tool definitions for task operations (create, read, update, delete, search, filter) in services/backend-api/src/services/mcp_server.py
- [X] T065 [P] [US4] Create MCP tool definitions for tag operations (add, remove, list) in services/backend-api/src/services/mcp_server.py
- [X] T066 [P] [US4] Create MCP tool definitions for reminder operations (add, remove) in services/backend-api/src/services/mcp_server.py
- [X] T067 [US4] Create MCP server with OpenAI GPT-4 integration and tool routing in services/backend-api/src/services/mcp_server.py
- [X] T068 [US4] Create chat API endpoint (POST /api/chat/message) with conversation state management in services/backend-api/src/api/chat.py
- [X] T069 [US4] Implement natural language date parsing (tomorrow, next Friday, in 2 weeks) in services/backend-api/src/services/mcp_server.py
- [X] T070 [US4] Implement ambiguity handling with clarifying questions (show up to 5 matches with numbers) in services/backend-api/src/services/mcp_server.py

### Frontend Implementation for US4

- [X] T071 [US4] Create chat page route in services/frontend/src/app/chat/page.tsx
- [X] T072 [P] [US4] Create ChatInterface component with message input and display in services/frontend/src/components/chat/chat-interface.tsx
- [X] T073 [P] [US4] Create MessageList component for displaying conversation history in services/frontend/src/components/chat/message-list.tsx
- [X] T074 [P] [US4] Create InputBox component with send button and keyboard shortcuts (integrated into ChatInterface)
- [X] T075 [US4] Create chat API client methods (implemented inline in ChatInterface)
- [X] T076 [US4] Integrate real-time sync to update chat when tasks change in graphical interface in services/frontend/src/components/chat/chat-interface.tsx
- [X] T077 [US4] Add navigation between chat and tasks modes in services/frontend/src/app/layout.tsx

**Checkpoint**: At this point, User Story 4 should be fully functional - users can manage tasks via natural language chat

---

## Phase 6: User Story 3 - Create Recurring Tasks (Priority: P3)

**Goal**: Users can create tasks that repeat on a schedule, with automatic creation of next instance upon completion

**Independent Test**: Create a recurring task "Weekly team meeting" set to repeat every Monday. Complete the task, verify next instance is automatically created for the following Monday with correct date.

### Recurring Service Creation for US3

- [X] T078 [US3] Create recurring-service directory structure in services/recurring-service/
- [X] T079 [P] [US3] Create recurring service configuration in services/recurring-service/src/config.py
- [X] T080 [P] [US3] Create Dapr client for pub/sub and service invocation in services/recurring-service/src/dapr_client.py
- [X] T081 [US3] Create recurrence engine with next occurrence calculation logic in services/recurring-service/src/recurrence_engine.py
- [X] T082 [US3] Implement daily recurrence pattern (every N days) in services/recurring-service/src/recurrence_engine.py
- [X] T083 [US3] Implement weekly recurrence pattern (specific days of week) in services/recurring-service/src/recurrence_engine.py
- [X] T084 [US3] Implement monthly recurrence pattern (specific day of month) in services/recurring-service/src/recurrence_engine.py
- [X] T085 [US3] Implement yearly recurrence pattern (specific date) in services/recurring-service/src/recurrence_engine.py
- [X] T086 [US3] Handle edge cases (Feb 30 → Feb 28/29, invalid dates) in services/recurring-service/src/recurrence_engine.py
- [X] T087 [US3] Create Dapr subscriber for task-events topic (listen for TaskCompleted) in services/recurring-service/src/subscriber.py
- [X] T088 [US3] Create FastAPI app with Dapr subscriber routes in services/recurring-service/main.py
- [X] T089 [P] [US3] Create Dockerfile for recurring-service in services/recurring-service/Dockerfile
- [X] T090 [P] [US3] Create requirements.txt for recurring-service in services/recurring-service/requirements.txt
- [X] T091 [US3] Create Dapr subscription configuration for recurring-service in infrastructure/dapr/subscriptions/recurring-service-sub.yaml
- [X] T092 [US3] Create database migration for audit schema with task_audit table in services/backend-api/migrations/004_create_audit_schema.sql

### Backend Implementation for US3

- [X] T093 [US3] Create RecurrenceRuleService with CRUD operations in services/backend-api/src/services/recurrence_rule_service.py
- [X] T094 [US3] Extend TaskService to handle recurring task creation and series management in services/backend-api/src/services/task_service.py
- [X] T095 [US3] Add recurrence rule validation (interval >= 1, valid days/dates) in services/backend-api/src/services/recurrence_rule_service.py
- [X] T096 [US3] Update task creation endpoint to accept recurrence rule in services/backend-api/src/api/tasks.py
- [X] T097 [US3] Create endpoint for editing recurring series vs single instance in services/backend-api/src/api/tasks.py
- [X] T098 [US3] Create endpoint for deleting recurring series vs single instance in services/backend-api/src/api/tasks.py
- [X] T099 [US3] Publish TaskCompleted events with recurrence rule data in services/backend-api/src/services/task_service.py
- [X] T100 [US3] Add recurring task filtering to task list endpoint in services/backend-api/src/api/tasks.py

### Frontend Implementation for US3

- [X] T101 [US3] Create RecurrenceRuleBuilder component with pattern selection UI in services/frontend/src/components/tasks/RecurrenceSelector.tsx
- [X] T102 [US3] Extend TaskForm with recurrence rule builder integration in services/frontend/src/components/tasks/TaskForm.tsx
- [X] T103 [US3] Add recurring task icon indicator to TaskList in services/frontend/src/components/tasks/TaskList.tsx
- [X] T104 [US3] Display "next occurrence" date for recurring tasks in services/frontend/src/components/tasks/TaskList.tsx
- [X] T105 [US3] Create UI for editing series vs single instance with confirmation dialog in services/frontend/src/components/tasks/RecurringTaskDialog.tsx
- [X] T106 [US3] Create UI for deleting series vs single instance with confirmation dialog in services/frontend/src/components/tasks/RecurringTaskDialog.tsx
- [X] T107 [US3] Add recurring task filtering to FilterPanel in services/frontend/src/components/tasks/FilterPanel.tsx
- [X] T108 [US4] Extend MCP server with recurring task tools (create recurring, edit series, delete series) in services/backend-api/src/services/mcp_server.py

**Checkpoint**: At this point, User Story 3 should be fully functional - users can create and manage recurring tasks with automatic next instance creation

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and deployment readiness

### Kubernetes Deployment Configuration

- [X] T109 [P] Create Kubernetes namespace manifest in infrastructure/kubernetes/namespace.yaml
- [X] T110 [P] Create Kubernetes ConfigMap for shared configuration in infrastructure/kubernetes/configmap.yaml
- [X] T111 [P] Create Kubernetes Secrets manifest in infrastructure/kubernetes/secrets.yaml
- [X] T112 [P] Create backend-api deployment manifest in infrastructure/kubernetes/deployments/backend-api.yaml
- [X] T113 [P] Create recurring-service deployment manifest in infrastructure/kubernetes/deployments/recurring-service.yaml
- [X] T114 [P] Create notification-service deployment manifest in infrastructure/kubernetes/deployments/notification-service.yaml
- [X] T115 [P] Create frontend deployment manifest in infrastructure/kubernetes/deployments/frontend.yaml
- [X] T116 [P] Create backend-api service manifest in infrastructure/kubernetes/services/backend-api-service.yaml
- [X] T117 [P] Create recurring-service service manifest in infrastructure/kubernetes/services/recurring-service.yaml
- [X] T118 [P] Create notification-service service manifest in infrastructure/kubernetes/services/notification-service.yaml
- [X] T119 [P] Create frontend service manifest in infrastructure/kubernetes/services/frontend-service.yaml
- [X] T120 [P] Create ingress manifest for external access in infrastructure/kubernetes/ingress/ingress.yaml

### Deployment Scripts

- [X] T121 [P] Create Minikube setup script in infrastructure/scripts/setup-minikube.sh
- [X] T122 [P] Create Dapr installation script in infrastructure/scripts/install-dapr.sh
- [X] T123 [P] Create Kafka (Strimzi) installation script in infrastructure/scripts/install-kafka.sh
- [X] T124 Create local deployment script in infrastructure/scripts/deploy-local.sh
- [X] T125 [P] Create cloud deployment script in infrastructure/scripts/deploy-cloud.sh
- [X] T126 [P] Create teardown script in infrastructure/scripts/teardown.sh

### Documentation and Validation

- [X] T127 [P] Create architecture documentation in docs/architecture.md
- [X] T128 [P] Create API reference documentation in docs/api-reference.md
- [X] T129 [P] Create deployment guide in docs/deployment-guide.md
- [X] T130 [P] Create local development guide in docs/local-development.md
- [X] T131 [P] Create MCP tools documentation in docs/mcp-tools.md
- [X] T132 Update README.md with Phase 5 features and architecture overview
- [ ] T133 Run quickstart.md validation for all three setup options (Docker Compose, Minikube, Local)
- [ ] T134 Verify all environment variables are documented in .env.example files
- [ ] T135 Code cleanup and remove unused imports across all services

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - Phase 3 (US1 + US5): Can start after Foundational - No dependencies on other stories
  - Phase 4 (US2): Can start after Foundational - No dependencies on other stories
  - Phase 5 (US4): Can start after Foundational - Integrates with US1 but independently testable
  - Phase 6 (US3): Can start after Foundational - No dependencies on other stories
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 + 5 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires notification-service creation
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires recurring-service creation

### Within Each User Story

- Backend models before services
- Services before API endpoints
- Backend endpoints before frontend components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Frontend components within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- All Kubernetes manifests marked [P] can be created in parallel
- All deployment scripts marked [P] can be created in parallel
- All documentation tasks marked [P] can be created in parallel

---

## Parallel Example: User Story 1 + 5

```bash
# Launch all backend models together:
Task T024: "Create TagService with CRUD operations and autocomplete"
Task T025: "Create SearchService with full-text search and filtering logic"

# Launch all frontend components together:
Task T033: "Create FilterPanel component with priority, tag, status, date filters"
Task T034: "Create SearchBar component with real-time search"
Task T035: "Create TagPill component for displaying colored tags"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 5 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T023) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 + 5 (T024-T042)
4. **STOP and VALIDATE**: Test task organization and real-time sync independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 5 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 4 → Test independently → Deploy/Demo
5. Add User Story 3 → Test independently → Deploy/Demo
6. Add Polish → Final deployment
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + 5 (backend)
   - Developer B: User Story 1 + 5 (frontend)
   - Developer C: User Story 2 (notification-service)
   - Developer D: User Story 4 (chat interface)
   - Developer E: User Story 3 (recurring-service)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included as they were not explicitly requested in the specification
- Existing code (backend-api, frontend) will be extended, not recreated
- New services (recurring-service, notification-service) will be created from scratch
- Infrastructure directory will be created with all deployment configurations
- Follow plan.md folder structure with ✅ EXISTS, 🆕 NEW, 📝 (needs extension) markers
