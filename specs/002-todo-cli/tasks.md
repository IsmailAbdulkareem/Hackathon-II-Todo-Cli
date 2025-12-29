# Tasks: Phase I – Todo In-Memory Python Console App

**Input**: Design documents from `/specs/002-todo-cli/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No tests required for Phase I per specification (standard library only, hackathon scope)

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/` at repository root
- All paths relative to: `D:\Projects\spec-driven-development-hacathon\Hackathon II - Todo Spec-Driven Development`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create project source structure and __init__ files

- [x] T001 Create `src/` directory structure (domain/, service/, cli/ subdirectories)
- [x] T002 [P] Create empty `src/__init__.py`
- [x] T003 [P] Create empty `src/domain/__init__.py`
- [x] T004 [P] Create empty `src/service/__init__.py`
- [x] T005 [P] Create empty `src/cli/__init__.py`

**Checkpoint**: Source directory structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain entity that ALL user stories depend on

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [x] T006 Create Todo entity dataclass in `src/domain/todo.py` with all attributes (id, title, description, completed, created_at) and methods (toggle_complete, __str__)

**Checkpoint**: Todo entity defined - user story implementation can now begin

---

## Phase 3: User Story 1 - Add New Todo Task (Priority: P1) 🎯 MVP

**Goal**: Enable users to create new tasks with title and optional description

**Independent Test**: Add tasks and verify they appear in task list with correct details

### Implementation for User Story 1

- [x] T007 [US1] Implement `TodoService.__init__()` with storage dict and ID counter in `src/service/todo_service.py`
- [x] T008 [US1] Implement `TodoService.add_task(title, description)` method with validation in `src/service/todo_service.py`
- [x] T009 [US1] Implement `TodoCLI.__init__()` and basic structure in `src/cli/todo_cli.py`
- [x] T010 [US1] Implement `TodoCLI.add_task()` method (prompts and service call) in `src/cli/todo_cli.py`

**Checkpoint**: User Story 1 functional - users can add tasks

---

## Phase 4: User Story 2 - View All Todo Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to see all tasks with status indicators

**Independent Test**: Add multiple tasks and verify list displays all with correct status

### Implementation for User Story 2

- [x] T011 [P] [US2] Implement `TodoService.get_all_tasks()` method in `src/service/todo_service.py`
- [x] T012 [P] [US2] Implement `TodoService.get_task_by_id(task_id)` method in `src/service/todo_service.py`
- [x] T013 [US2] Implement `TodoCLI.view_tasks()` method with formatted table display in `src/cli/todo_cli.py`

**Checkpoint**: User Stories 1 AND 2 functional - users can add and view tasks (MVP!)

---

## Phase 5: User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Enable users to toggle task completion status

**Independent Test**: Create tasks, mark complete, verify status changes, unmark

### Implementation for User Story 3

- [x] T014 [US3] Implement `TodoService.toggle_complete(task_id)` method in `src/service/todo_service.py`
- [x] T015 [US3] Implement `TodoCLI.toggle_task()` method (prompt for ID and service call) in `src/cli/todo_cli.py`

**Checkpoint**: User Stories 1, 2, AND 3 functional - core todo workflow complete

---

## Phase 6: User Story 4 - Update Task Details (Priority: P3)

**Goal**: Enable users to modify task title or description

**Independent Test**: Create task, update title/description, verify changes saved

### Implementation for User Story 4

- [x] T016 [US4] Implement `TodoService.update_task(task_id, title, description)` method with validation in `src/service/todo_service.py`
- [x] T017 [US4] Implement `TodoCLI.update_task()` method (prompts and service call) in `src/cli/todo_cli.py`

**Checkpoint**: User Stories 1-4 functional - full CRUD operations available

---

## Phase 7: User Story 5 - Delete Todo Task (Priority: P3)

**Goal**: Enable users to remove tasks from list

**Independent Test**: Create tasks, delete specific task, verify removal

### Implementation for User Story 5

- [x] T018 [US5] Implement `TodoService.delete_task(task_id)` method in `src/service/todo_service.py`
- [x] T019 [US5] Implement `TodoCLI.delete_task()` method (prompt for ID and service call) in `src/cli/todo_cli.py`

**Checkpoint**: All 5 user stories functional - complete feature set

---

## Phase 8: CLI Integration & Entry Point

**Purpose**: Wire up menu system and application entry point

- [x] T020 Implement `TodoCLI.display_menu()` method in `src/cli/todo_cli.py`
- [x] T021 Implement `TodoCLI.get_user_choice()` method with input validation in `src/cli/todo_cli.py`
- [x] T022 Implement `TodoCLI.handle_choice(choice)` method routing to handlers in `src/cli/todo_cli.py`
- [x] T023 Implement `TodoCLI.run()` main loop in `src/cli/todo_cli.py`
- [x] T024 Create `main.py` entry point with welcome message and CLI instantiation

**Checkpoint**: Application fully integrated - all features accessible via menu

---

## Phase 9: Polish & Validation

**Purpose**: Final improvements and validation

- [x] T025 Add error handling for edge cases (empty list, invalid IDs, input errors) across all CLI methods
- [x] T026 Add input trimming and sanitization in CLI layer
- [x] T027 Verify all error messages match quickstart.md specifications
- [x] T028 Test complete workflow (add → view → toggle → update → delete → exit)
- [x] T029 Update README.md with todo CLI usage section

**Checkpoint**: Application ready for hackathon demonstration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2
- **Phase 4 (US2)**: Depends on Phase 2 (can run parallel with Phase 3)
- **Phase 5 (US3)**: Depends on Phase 2 (can run parallel with Phases 3-4)
- **Phase 6 (US4)**: Depends on Phase 2 (can run parallel with Phases 3-5)
- **Phase 7 (US5)**: Depends on Phase 2 (can run parallel with Phases 3-6)
- **Phase 8 (Integration)**: Depends on Phases 3-7 complete
- **Phase 9 (Polish)**: Depends on Phase 8 complete

### Task Dependencies

**Phase 1 Tasks** (T001-T005):
- T001 must complete before T002-T005
- T002-T005 marked [P] - can run in parallel after T001

**Phase 2 Task** (T006):
- Blocks all subsequent phases

**Phase 3 Tasks** (T007-T010):
- T007, T008 can run in parallel (different methods in same file)
- T009 must complete before T010
- T007-T008 independent of T009-T010

**Phase 4 Tasks** (T011-T013):
- T011, T012 marked [P] - can run in parallel (different methods)
- T013 depends on T011 completion

**Phase 5-7 Tasks** (T014-T019):
- Service methods (T014, T016, T018) can run in parallel
- Each CLI method depends on its corresponding service method

**Phase 8 Tasks** (T020-T024):
- T020-T022 can run in parallel
- T023 depends on T020-T022
- T024 depends on T023

**Phase 9 Tasks** (T025-T029):
- T025-T027 can run in parallel
- T028 depends on T025-T027
- T029 can run in parallel with T025-T028

### Parallel Opportunities

**After Phase 2 completes, user stories can proceed in parallel**:

```bash
# Service layer methods (different parts of same file - sequential within file)
Task T008: Implement add_task method
Task T011: Implement get_all_tasks method
Task T012: Implement get_task_by_id method
Task T014: Implement toggle_complete method
Task T016: Implement update_task method
Task T018: Implement delete_task method

# CLI layer methods (different parts of same file - sequential within file)
Task T010: Implement add_task CLI method
Task T013: Implement view_tasks CLI method
Task T015: Implement toggle_task CLI method
Task T017: Implement update_task CLI method
Task T019: Implement delete_task CLI method
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006)
3. Complete Phase 3: US1 - Add Task (T007-T010)
4. Complete Phase 4: US2 - View Tasks (T011-T013)
5. **STOP and VALIDATE**: Test adding and viewing tasks
6. Demo MVP to judges if needed

### Full Feature Delivery

1. Complete MVP (Phases 1-4)
2. Add Phase 5: US3 - Mark Complete (T014-T015)
3. Add Phase 6: US4 - Update Task (T016-T017)
4. Add Phase 7: US5 - Delete Task (T018-T019)
5. Complete Phase 8: Integration (T020-T024)
6. Complete Phase 9: Polish (T025-T029)
7. **VALIDATE**: Test all 5 features end-to-end

### Sequential Execution (Recommended for Single Developer)

Follow phase order 1→2→3→4→5→6→7→8→9, completing each phase before moving to next. This ensures working application at each checkpoint.

---

## Notes

- [P] tasks = different files or independent code sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- main.py created last (depends on TodoCLI.run() being complete)
