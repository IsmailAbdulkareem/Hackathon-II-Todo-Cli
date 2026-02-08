# Task Breakdown: Phase V Advanced Features with Dapr-First Architecture

**Feature**: Advanced Features with Dapr-First Architecture
**Date**: 2026-02-06
**Input**: Specification from `/specs/001-dapr-advanced-features/spec.md`
**Plan**: Architecture and design from `/specs/001-dapr-advanced-features/plan.md`

**Note**: This template is filled in by the `/sp.tasks` command. See `.specify/templates/commands/tasks.md` for the execution workflow.

## Overview

Implementation of advanced task management features (due dates, priorities, tags, recurring tasks, reminders, search/filter) with Dapr-first architecture on top of existing phase-03-ai-chatbot codebase. All integrations go through Dapr APIs (Pub/Sub, State Store, Jobs, Service Invocation) with graceful degradation when Dapr is available. Multi-user task ownership with Server-Sent Events for real-time notifications. Implementation extends existing backend (phase-03-ai-chatbot/backend) and frontend (phase-03-ai-chatbot/frontend).

## Implementation Strategy

**MVP Scope**: User Story 1 (Task Due Dates and Priorities) - basic task enhancement with due dates and priorities
**Approach**: Incremental delivery with each user story building on previous work
**Delivery**: Phase 1 (setup) → Phase 2 (foundational) → Phase 3+ (user stories in priority order) → Phase 6 (polish)

---

## Phase 1: Project Setup and Dapr Integration

**Goal**: Integrate Dapr into existing phase-03-ai-chatbot codebase with required components

- [X] T001 Update backend requirements.txt to include Dapr SDK dependencies
- [X] T002 Create Dapr component configuration files in phase-03-ai-chatbot/backend/dapr/components/
- [X] T003 Create Dapr state store component configuration for Redis in phase-03-ai-chatbot/backend/dapr/components/statestore.yaml
- [X] T004 Create Dapr pub/sub component configuration for Redis Streams in phase-03-ai-chatbot/backend/dapr/components/pubsub.yaml
- [X] T005 Create Dapr jobs component configuration in phase-03-ai-chatbot/backend/dapr/components/jobs.yaml
- [X] T006 Update backend Dockerfile to support Dapr sidecar in phase-03-ai-chatbot/backend/Dockerfile
- [X] T007 Add Dapr configuration in phase-03-ai-chatbot/backend/dapr/config.yaml
- [ ] T008 Install and configure Redis for development environment
- [ ] T009 Set up development environment with Dapr CLI installation
- [ ] T010 Create Dapr integration test configuration

## Phase 2: Enhanced Task Model Implementation

**Goal**: Extend existing task model with new attributes while maintaining backward compatibility

- [X] T011 Update Task model in phase-03-ai-chatbot/backend/src/models/task.py to include due_date, priority, tags, recurrence, reminder_offset_minutes
- [X] T012 Add validation rules for new task attributes in phase-03-ai-chatbot/backend/src/models/task.py
- [X] T013 Update TaskCreate model in phase-03-ai-chatbot/backend/src/models/task.py to include new fields
- [X] T014 Update TaskUpdate model in phase-03-ai-chatbot/backend/src/models/task.py to include new fields
- [X] T015 Update TaskRead model in phase-03-ai-chatbot/backend/src/models/task.py to include new fields
- [X] T016 Add database migration for new task fields in phase-03-ai-chatbot/backend/migrations/
- [X] T017 Update SQLAlchemy model to handle JSON fields for tags in phase-03-ai-chatbot/backend/src/models/task.py
- [X] T018 Add due date validation logic in phase-03-ai-chatbot/backend/src/models/task.py
- [X] T019 Add priority enum validation in phase-03-ai-chatbot/backend/src/models/task.py
- [X] T020 Add recurrence validation logic in phase-03-ai-chatbot/backend/src/models/task.py

## Phase 3: User Story 1 - Task Due Dates and Priorities (Priority: P1)

**Goal**: Enable users to set due dates and priorities on tasks for better organization and urgency indication

**Independent Test**: Can be fully tested by creating tasks with different due dates and priorities, then verifying they display correctly and can be filtered. Delivers immediate value by helping users organize their work.

- [X] T021 [US1] Update Task API endpoints in phase-03-ai-chatbot/backend/src/api/tasks.py to support due_date and priority
- [X] T022 [US1] Update GET /api/{user_id}/tasks to return due_date and priority fields
- [X] T023 [US1] Update POST /api/{user_id}/tasks to accept due_date and priority parameters
- [X] T024 [US1] Update PUT /api/{user_id}/tasks/{id} to accept due_date and priority updates
- [X] T025 [US1] Add due date formatting and display logic in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T026 [US1] Add priority validation in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T027 [US1] Update frontend Task type in phase-03-ai-chatbot/frontend/src/types/todo.ts to include due_date and priority
- [X] T028 [US1] Update frontend TodoForm component in phase-03-ai-chatbot/frontend/src/components/todo/todo-form.tsx to include due date and priority inputs
- [X] T029 [US1] Update frontend TodoList component in phase-03-ai-chatbot/frontend/src/components/todo/todo-list.tsx to display due date and priority indicators
- [X] T030 [US1] Add overdue task detection logic in phase-03-ai-chatbot/frontend/src/components/todo/todo-list.tsx
- [X] T031 [US1] Update API service to handle new task fields in phase-03-ai-chatbot/frontend/src/lib/api-service.ts
- [X] T032 [US1] Update API config to include new task fields in phase-03-ai-chatbot/frontend/src/lib/api-config.ts
- [ ] T033 [US1] Create unit tests for due_date and priority business logic in phase-03-ai-chatbot/backend/tests/
- [X] T034 [US1] Create integration tests for Task CRUD with due_date and priority in phase-03-ai-chatbot/backend/tests/

## Phase 4: User Story 2 - Task Tags and Organization (Priority: P2)

**Goal**: Allow users to tag tasks with categories for flexible organization and easy finding of related tasks

**Independent Test**: Can be fully tested by creating tasks with various tags, then searching and filtering by those tags. Delivers value by enabling users to organize tasks their way.

- [X] T035 [US2] Update Task model to support tags field in phase-03-ai-chatbot/backend/src/models/task.py
- [X] T036 [US2] Update Task API endpoints in phase-03-ai-chatbot/backend/src/api/tasks.py to support tags
- [X] T037 [US2] Update POST /api/{user_id}/tasks to accept tags parameter
- [X] T038 [US2] Update PUT /api/{user_id}/tasks/{id} to accept tags updates
- [X] T039 [US2] Add tag validation and normalization logic in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T040 [US2] Create frontend tag input component in phase-03-ai-chatbot/frontend/src/components/todo/tag-input.tsx
- [X] T041 [US2] Update TodoForm component in phase-03-ai-chatbot/frontend/src/components/todo/todo-form.tsx to include tag input
- [X] T042 [US2] Update TodoList component in phase-03-ai-chatbot/frontend/src/components/todo/todo-list.tsx to display tags
- [X] T043 [US2] Add tag filtering functionality in phase-03-ai-chatbot/frontend/src/hooks/use-todos.ts
- [X] T044 [US2] Create tag validation in phase-03-ai-chatbot/frontend/src/types/todo.ts
- [ ] T045 [US2] Create unit tests for tag validation and normalization in phase-03-ai-chatbot/backend/tests/
- [ ] T046 [US2] Create integration tests for tag-based filtering in phase-03-ai-chatbot/backend/tests/

## Phase 5: User Story 3 - Recurring Tasks (Priority: P3)

**Goal**: Enable users to create tasks that repeat on a schedule to automate routine task recreation

**Independent Test**: Can be fully tested by creating a recurring task (e.g., daily), waiting for the recurrence period, and verifying a new instance is automatically created. Delivers value by reducing manual task creation.

- [X] T047 [US3] Update Task model to support recurrence field in phase-03-ai-chatbot/backend/src/models/task.py
- [X] T048 [US3] Create RecurringTaskService in phase-03-ai-chatbot/backend/src/services/recurring_service.py
- [X] T049 [US3] Implement recurrence calculation functions for daily/weekly/monthly patterns in phase-03-ai-chatbot/backend/src/services/recurring_service.py
- [X] T050 [US3] Create Dapr Jobs API integration for scheduling recurring task generation in phase-03-ai-chatbot/backend/src/services/recurring_service.py
- [X] T051 [US3] Create recurring task generation callback endpoint in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T052 [US3] Implement proper month-end handling for recurring tasks in phase-03-ai-chatbot/backend/src/services/recurring_service.py
- [X] T053 [US3] Update frontend to include recurrence options in phase-03-ai-chatbot/frontend/src/components/todo/todo-form.tsx
- [X] T054 [US3] Create recurring task management UI components in phase-03-ai-chatbot/frontend/src/components/todo/recurring-picker.tsx
- [ ] T055 [US3] Add recurring task deletion logic (cancel future generations) in phase-03-ai-chatbot/backend/src/services/recurring_service.py
- [X] T056 [US3] Create unit tests for recurrence calculation algorithms in phase-03-ai-chatbot/backend/tests/
- [X] T057 [US3] Create integration tests for recurring task generation in phase-03-ai-chatbot/backend/tests/

## Phase 6: User Story 4 - Task Reminders (Priority: P4)

**Goal**: Enable users to receive reminders before tasks are due to prevent missing important deadlines

**Independent Test**: Can be fully tested by creating a task with a due date and reminder offset, then verifying the reminder is triggered at the correct time. Delivers value by preventing missed deadlines.

- [X] T058 [US4] Update Task model to support reminder_offset_minutes in phase-03-ai-chatbot/backend/src/models/task.py
- [X] T059 [US4] Create ReminderService in phase-03-ai-chatbot/backend/src/services/reminder_service.py
- [X] T060 [US4] Implement reminder validation logic in phase-03-ai-chatbot/backend/src/services/reminder_service.py
- [X] T061 [US4] Create Dapr Jobs API integration for scheduling reminder triggers in phase-03-ai-chatbot/backend/src/services/reminder_service.py
- [X] T062 [US4] Create Server-Sent Events endpoint for real-time reminder notifications in phase-03-ai-chatbot/backend/src/api/notifications.py
- [X] T063 [US4] Implement NotificationManager for handling SSE connections in phase-03-ai-chatbot/backend/src/core/sse_manager.py
- [X] T064 [US4] Create reminder cancellation logic when tasks are completed/deleted in phase-03-ai-chatbot/backend/src/services/reminder_service.py
- [X] T065 [US4] Update frontend to include reminder configuration in phase-03-ai-chatbot/frontend/src/components/todo/todo-form.tsx
- [X] T066 [US4] Create SSE client in frontend to receive notifications in phase-03-ai-chatbot/frontend/src/hooks/use-notifications.ts
- [X] T067 [US4] Create reminder notification UI components in phase-03-ai-chatbot/frontend/src/components/todo/reminder-notifications.tsx
- [X] T068 [US4] Create unit tests for reminder scheduling logic in phase-03-ai-chatbot/backend/tests/
- [X] T069 [US4] Create integration tests for reminder triggering and SSE delivery in phase-03-ai-chatbot/backend/tests/

## Phase 7: User Story 5 - Advanced Search and Filtering (Priority: P5)

**Goal**: Enable users to search and filter tasks by multiple criteria for improved task discoverability

**Independent Test**: Can be fully tested by creating diverse tasks and verifying search/filter operations return correct results. Delivers value by improving task discoverability.

- [X] T070 [US5] Create search endpoint with text matching in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T071 [US5] Implement filter functionality by priority, tags, due date range, completion status in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T072 [US5] Implement sort functionality by due_date, priority, created_at, updated_at in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T073 [US5] Create compound filter logic (AND combination of criteria) in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T074 [US5] Add pagination support for search/filter results in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T075 [US5] Update frontend search and filter UI components in phase-03-ai-chatbot/frontend/src/components/todo/filter-bar.tsx
- [X] T076 [US5] Implement real-time search as user types in phase-03-ai-chatbot/frontend/src/hooks/use-search.ts
- [X] T077 [US5] Add sort controls in frontend UI in phase-03-ai-chatbot/frontend/src/components/todo/sort-selector.tsx
- [X] T078 [US5] Update useTodos hook to support advanced filtering in phase-03-ai-chatbot/frontend/src/hooks/use-todos.ts
- [X] T079 [US5] Create unit tests for search and filtering algorithms in phase-03-ai-chatbot/backend/tests/
- [X] T080 [US5] Create integration tests for search/filter endpoint in phase-03-ai-chatbot/backend/tests/

## Phase 8: User Story 6 - Event-Driven Architecture (Priority: P6)

**Goal**: Implement event publishing for all significant task operations to enable system integration and audit logging

**Independent Test**: Can be fully tested by performing task operations and verifying events are published to the correct topics with proper schemas. Delivers value by enabling system integration and monitoring.

- [X] T081 [US6] Create event publisher implementation using Dapr Pub/Sub API in phase-03-ai-chatbot/backend/src/core/event_publisher.py
- [X] T082 [US6] Implement TASK_CREATED event publishing on task creation in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T083 [US6] Implement TASK_UPDATED event publishing on task updates in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T084 [US6] Implement TASK_COMPLETED event publishing on task completion in phase-03-ai-chatbot/backend/src/api/tasks.py
- [X] T085 [US6] Implement REMINDER_DUE event publishing when reminder triggers in phase-03-ai-chatbot/backend/src/services/reminder_service.py
- [X] T086 [US6] Implement recurring task generation event publishing in phase-03-ai-chatbot/backend/src/services/recurring_service.py
- [X] T087 [US6] Create event schema validation for all event types in phase-03-ai-chatbot/backend/src/core/event_publisher.py
- [ ] T088 [US6] Create event subscriber endpoints for task-events, task-reminders, task-recurring topics in phase-03-ai-chatbot/backend/src/api/events.py
- [ ] T089 [US6] Create audit logging service that consumes all events in phase-03-ai-chatbot/backend/src/services/audit_service.py
- [ ] T090 [US6] Add event publishing unit tests with mock Dapr client in phase-03-ai-chatbot/backend/tests/
- [ ] T091 [US6] Create integration tests for event publishing to Dapr in phase-03-ai-chatbot/backend/tests/

## Phase 9: Dapr Integration and Repository Layer

**Goal**: Implement repository pattern with Dapr adapters to maintain clean architecture

- [ ] T092 Create TaskRepository interface in phase-03-ai-chatbot/backend/src/core/repository_interface.py
- [ ] T093 Create DaprTaskRepository implementation in phase-03-ai-chatbot/backend/src/services/dapr_task_repository.py
- [ ] T094 Create DaprStateStoreAdapter in phase-03-ai-chatbot/backend/src/core/dapr_state_adapter.py
- [ ] T095 Create DaprPubSubAdapter in phase-03-ai-chatbot/backend/src/core/dapr_pubsub_adapter.py
- [ ] T096 Create DaprJobsAdapter in phase-03-ai-chatbot/backend/src/core/dapr_jobs_adapter.py
- [ ] T097 Update existing API endpoints to use repository pattern in phase-03-ai-chatbot/backend/src/api/tasks.py
- [ ] T098 Create fallback repository for graceful degradation when Dapr unavailable in phase-03-ai-chatbot/backend/src/services/fallback_task_repository.py
- [ ] T099 Update dependency injection to use repository pattern in phase-03-ai-chatbot/backend/src/api/tasks.py
- [ ] T100 Create unit tests for repository implementations in phase-03-ai-chatbot/backend/tests/

## Phase 10: Polish & Cross-Cutting Concerns

**Goal**: Implement graceful degradation, security, monitoring, and other cross-cutting concerns

- [ ] T101 Implement Dapr fallback strategies when unavailable (local queuing, retry) in phase-03-ai-chatbot/backend/src/services/fallback/
- [ ] T102 Add comprehensive error handling and logging for all endpoints in phase-03-ai-chatbot/backend/src/core/error_handler.py
- [ ] T103 Implement request validation and sanitization for security in phase-03-ai-chatbot/backend/src/core/validation.py
- [ ] T104 Add authentication validation to all endpoints using JWT middleware in phase-03-ai-chatbot/backend/src/core/auth.py
- [ ] T105 Implement user_id-based task ownership validation in repository layer in phase-03-ai-chatbot/backend/src/core/auth.py
- [ ] T106 Create comprehensive API documentation with OpenAPI in phase-03-ai-chatbot/backend/src/api/main.py
- [ ] T107 Add performance monitoring and metrics collection in phase-03-ai-chatbot/backend/src/core/metrics.py
- [ ] T108 Implement comprehensive test suite (unit, integration, e2e) in phase-03-ai-chatbot/backend/tests/ and phase-03-ai-chatbot/frontend/tests/
- [ ] T109 Add proper shutdown and cleanup procedures in phase-03-ai-chatbot/backend/main.py
- [ ] T110 Create deployment configurations for Phase IV Kubernetes in phase-03-ai-chatbot/infrastructure/
- [ ] T111 Add security audit logging for all sensitive operations in phase-03-ai-chatbot/backend/src/services/audit_service.py
- [ ] T112 Implement proper data sanitization to prevent XSS in phase-03-ai-chatbot/backend/src/core/validation.py
- [ ] T113 Create backup and recovery procedures for Redis data in phase-03-ai-chatbot/backend/src/core/data_backup.py
- [ ] T114 Add comprehensive health check endpoints in phase-03-ai-chatbot/backend/src/api/health.py
- [ ] T115 Perform final integration testing with all features enabled in phase-03-ai-chatbot/tests/integration/

---

## Dependencies

**Phase 1 requires**: Basic Dapr setup and component configuration
**Phase 2 requires**: Phase 1 complete, updates to existing task models
**Phase 3 (US1) requires**: Phase 2 complete, extends existing API endpoints
**Phase 4 (US2) requires**: Phase 3 complete, uses updated models
**Phase 5 (US3) requires**: Phase 2 complete, for recurrence field
**Phase 6 (US4) requires**: Phase 2 complete, for reminder field
**Phase 7 (US5) requires**: Phase 2 complete, for filtering by new fields
**Phase 8 (US6) requires**: Phase 2 complete, for event publishing
**Phase 9 requires**: All previous phases for repository implementation
**Phase 10 requires**: All user story phases complete

**Parallel Opportunities**:
- [P] Phases 3 (US1) and 5 (US3) can be developed in parallel as they extend different aspects of the task entity
- [P] Phases 4 (US2) and 6 (US4) can be developed in parallel as they also extend different aspects
- [P] Backend and frontend development for each user story can be done in parallel after the backend API is defined
- [P] Repository layer (Phase 9) can be developed in parallel with API extensions

## Independent Test Criteria

**User Story 1**: Users can create tasks with due dates and priorities, view them with proper visual indicators, and tasks become visually marked as overdue when due date passes
**User Story 2**: Users can add tags to tasks, filter by tags, and search by tags to find related tasks
**User Story 3**: Recurring tasks generate new instances automatically according to the specified schedule (daily, weekly, monthly)
**User Story 4**: Reminders are triggered at the correct time before due dates and delivered to the user via SSE notifications
**User Story 5**: Users can apply multiple filters simultaneously and sort tasks by various criteria with acceptable performance
**User Story 6**: Events are published to appropriate topics for all significant operations and can be consumed by other services

## Performance Targets

- 1000 concurrent task operations
- <2s filter results
- <1s search operations for up to 10,000 tasks
- <500ms event publishing latency
- <1min reminder delivery
- <5min recurring task generation

## Success Metrics

- All 48 functional requirements from specification are met
- All 10 success criteria are achieved
- MVP (User Story 1) delivers value in under 30 seconds of task creation
- All tests pass (unit, integration, e2e)
- Zero code changes required between Phase III and Phase IV