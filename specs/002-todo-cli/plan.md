# Implementation Plan: Phase I – Todo In-Memory Python Console App

**Branch**: `002-todo-cli` | **Date**: 2025-12-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-todo-cli/spec.md`

**Note**: This plan defines the technical approach for implementing a CLI-based todo application with 5 core features (Add, View, Mark Complete, Update, Delete) using Python 3.13+ standard library and in-memory storage.

## Summary

Implement a command-line todo application demonstrating spec-driven development for hackathon judges. The application will support adding tasks with title/description, viewing all tasks with status indicators, marking tasks complete/incomplete, updating task details, and deleting tasks. All data stored in-memory (no persistence). Uses Python 3.13+ standard library exclusively with clean architecture pattern (domain, service, CLI layers).

**Technical Approach**: Build a menu-driven CLI application using Python's standard library. Implement clean architecture with three layers: Domain (Todo entity), Service (TodoService for CRUD operations), and CLI (user interface). Use incrementing integers for task IDs (simpler than UUIDs for CLI display). Store tasks in a dictionary keyed by ID for O(1) lookups.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (Python standard library only)
**Storage**: In-memory (Python dict, no persistence)
**Testing**: N/A (no tests required per spec FR-011)
**Target Platform**: Cross-platform CLI (Windows via WSL 2, macOS, Linux)
**Project Type**: single (console application)
**Performance Goals**: <1 second for list display (100 tasks), <100ms for CRUD operations, <2 second startup
**Constraints**: Standard library only, in-memory storage, CLI interface, no manual code edits (AI-generated)
**Scale/Scope**: Single-user session, 100+ tasks supported, 5 core features

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development First
✅ **PASS** - Specification exists at `specs/002-todo-cli/spec.md` with 5 user stories and 12 functional requirements

### Principle II: AI as Implementer, Human as Architect
✅ **PASS** - Human architect defined requirements; Claude Code will generate all implementation code

### Principle III: Deterministic Behavior Across Non-LLM Components
✅ **PASS** - Todo CRUD operations are deterministic; no AI/LLM components in Phase I

### Principle IV: Evolvability Across Phases Without Breaking Domain Contracts
✅ **PASS** - Todo domain model (Task entity) designed to be stable for future phases (Phase II: SQLite, Phase III: Web API)

### Principle V: Clear Separation of Domain Logic, Interfaces, and Infrastructure
✅ **PASS** - Clean architecture planned: Domain (entities), Service (business logic), CLI (interface), Infrastructure (in-memory storage)

### Principle VI: Reusable Intelligence Over One-Off Solutions
✅ **PASS** - No AI features in Phase I; principle will apply in Phase IV

### Principle VII: Infrastructure as Declarative and Reproducible
✅ **PASS** - Code is declarative; environment setup declarative (pyproject.toml from Feature 001)

**Overall Gate Result**: ✅ **PASSED** - No constitutional violations detected

## Project Structure

### Documentation (this feature)

```text
specs/002-todo-cli/
├── spec.md              # Feature specification
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (CLI patterns, architecture)
├── data-model.md        # Phase 1 output (Todo entity definition)
├── quickstart.md        # Phase 1 output (usage instructions)
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
# Project Root Structure (Single Project)
.
├── src/                        # Application source code (NEW)
│   ├── __init__.py
│   ├── domain/                 # Domain entities
│   │   ├── __init__.py
│   │   └── todo.py             # Todo dataclass
│   ├── service/                # Business logic
│   │   ├── __init__.py
│   │   └── todo_service.py     # TodoService (CRUD operations)
│   └── cli/                    # CLI interface
│       ├── __init__.py
│       └── todo_cli.py         # Main CLI application
│
├── main.py                     # Application entry point (NEW)
├── pyproject.toml              # Project metadata (exists from Feature 001)
├── .python-version             # Python 3.13 (exists from Feature 001)
├── .gitignore                  # Git exclusions (exists from Feature 001)
├── README.md                   # Project documentation (exists, will update)
│
├── specs/                      # Specifications
│   ├── 001-env-setup/
│   └── 002-todo-cli/
│
├── history/                    # PHRs and ADRs
│   ├── prompts/
│   │   ├── constitution/
│   │   ├── 001-env-setup/
│   │   └── 002-todo-cli/
│   └── adr/
│
├── .specify/                   # Templates and scripts
└── .claude/                    # Claude-specific commands
```

**Structure Decision**: Using **single project** structure (Option 1). This is a console application without separate frontend/backend. The `src/` directory contains three subdirectories following clean architecture: `domain/` (entities), `service/` (business logic), and `cli/` (user interface).

**New Files to Create**:
- `src/domain/todo.py` - Todo dataclass entity
- `src/service/todo_service.py` - TodoService for CRUD operations
- `src/cli/todo_cli.py` - CLI application with menu loop
- `main.py` - Entry point that instantiates CLI and starts application

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations detected. This section is intentionally left empty.

---

## Phase 0: Research & Architecture Decisions

**Objective**: Research CLI patterns and make key architectural decisions.

### Research Questions

1. **CLI Interaction Pattern**: Menu-driven vs command-line arguments?
2. **Task ID Format**: UUID vs incrementing integer?
3. **Storage Strategy**: Dict vs list for in-memory storage?
4. **Clean Architecture**: How to structure domain/service/CLI layers?
5. **Error Handling**: Exception types and user-friendly messages?
6. **Input Validation**: Where to validate (CLI layer vs service layer)?

### Research Output

Research findings documented in `research.md` covering:
- **CLI Pattern Decision**: Menu-driven loop (more user-friendly than args for 5 operations)
- **Task ID Decision**: Incrementing integers starting at 1 (simpler for CLI display)
- **Storage Decision**: Dictionary {id: Todo} for O(1) lookups
- **Architecture Decision**: Clean architecture with 3 layers
- **Error Handling**: Custom exceptions with user-friendly messages
- **Input Validation**: CLI layer validates format; service layer validates business rules

---

## Phase 1: Design & Data Model

**Objective**: Define Todo entity and CLI interface contracts.

### 1. Data Model (`data-model.md`)

**Todo Entity**:
```
Todo
├── id: int (unique, auto-increment starting at 1)
├── title: str (mandatory, max 200 chars)
├── description: str (optional, max 1000 chars, default: "")
├── completed: bool (default: False)
└── created_at: datetime (auto-set on creation)
```

**Validation Rules**:
- Title: MUST NOT be empty, MUST be ≤200 characters
- Description: MUST be ≤1000 characters
- ID: MUST be unique, MUST be positive integer
- Completed: MUST be boolean

**State Transitions**:
- New Task: completed=False
- Mark Complete: completed=False → True
- Mark Incomplete: completed=True → False

### 2. Service Layer Design

**TodoService** class:
```
Methods:
- add_task(title: str, description: str = "") -> Todo
- get_all_tasks() -> list[Todo]
- get_task_by_id(task_id: int) -> Todo | None
- update_task(task_id: int, title: str = None, description: str = None) -> bool
- delete_task(task_id: int) -> bool
- toggle_complete(task_id: int) -> bool
```

**Storage**:
- Private dict: `_tasks: dict[int, Todo]`
- Private counter: `_next_id: int` (starts at 1)

### 3. CLI Interface Design (`quickstart.md`)

**Menu Options**:
```
Todo Application - Main Menu
1. Add new task
2. View all tasks
3. Mark task complete/incomplete
4. Update task
5. Delete task
6. Exit

Enter choice (1-6):
```

**User Interactions**:
1. **Add Task**: Prompt for title → prompt for description (optional) → confirm creation
2. **View Tasks**: Display all tasks in formatted table with ID, status indicator, title, description
3. **Mark Complete**: Prompt for task ID → toggle status → confirm
4. **Update Task**: Prompt for task ID → prompt for new title (optional) → prompt for new description (optional) → confirm
5. **Delete Task**: Prompt for task ID → confirm deletion → execute
6. **Exit**: Display goodbye message → terminate application

**Output Format**:
```
ID | Status | Title              | Description
---|--------|--------------------|--------------------------
1  | [ ]    | Buy groceries      | Milk, eggs, bread
2  | [x]    | Finish report      | Complete quarterly analysis
```

**Error Messages**:
- "Error: Title cannot be empty"
- "Error: Task not found with ID {id}"
- "Error: Title too long (max 200 characters)"
- "Error: Description too long (max 1000 characters)"
- "Error: Invalid choice. Please enter 1-6."

### 4. No API Contracts Required

This is a CLI application with no external API. The "contract" is the CLI menu interface defined above.

### 5. Agent Context Update

Run agent context update script to add Python CLI patterns:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

---

## Phase 2: Implementation Planning

**Objective**: Define file-by-file implementation approach.

### File 1: `src/domain/todo.py`

**Purpose**: Define Todo entity as a dataclass

**Content Structure**:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Todo:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def toggle_complete(self) -> None:
        """Toggle completion status."""
        self.completed = not self.completed

    def __str__(self) -> str:
        """String representation for display."""
        status = "[x]" if self.completed else "[ ]"
        return f"{self.id:3d} | {status} | {self.title:30s} | {self.description}"
```

**Key Decisions**:
- Dataclass for simplicity (no manual __init__)
- `created_at` auto-set using `field(default_factory)`
- Toggle method on entity for convenience
- `__str__` for formatted display

### File 2: `src/service/todo_service.py`

**Purpose**: Business logic for CRUD operations

**Content Structure**:
```python
from typing import Optional
from src.domain.todo import Todo

class TodoService:
    def __init__(self):
        self._tasks: dict[int, Todo] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Todo:
        """Add new task. Raises ValueError if title empty or too long."""
        # Validation logic
        # Create Todo with next_id
        # Store in _tasks
        # Increment _next_id
        # Return created Todo
        pass

    def get_all_tasks(self) -> list[Todo]:
        """Return all tasks sorted by ID."""
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def get_task_by_id(self, task_id: int) -> Optional[Todo]:
        """Get task by ID or None if not found."""
        return self._tasks.get(task_id)

    def update_task(self, task_id: int, title: Optional[str] = None,
                    description: Optional[str] = None) -> bool:
        """Update task. Returns True if successful, False if not found."""
        # Find task
        # Validate inputs if provided
        # Update fields
        # Return success status
        pass

    def delete_task(self, task_id: int) -> bool:
        """Delete task. Returns True if successful, False if not found."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def toggle_complete(self, task_id: int) -> bool:
        """Toggle completion status. Returns True if successful."""
        task = self.get_task_by_id(task_id)
        if task:
            task.toggle_complete()
            return True
        return False
```

**Key Decisions**:
- Dict storage for O(1) lookups
- Auto-increment ID starting at 1
- Validation in service layer (business rules)
- Return bool for success/failure (update, delete, toggle)
- Return Optional[Todo] for get operations

### File 3: `src/cli/todo_cli.py`

**Purpose**: CLI interface with menu loop

**Content Structure**:
```python
from src.service.todo_service import TodoService

class TodoCLI:
    def __init__(self):
        self.service = TodoService()

    def run(self) -> None:
        """Main application loop."""
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            if choice == '6':
                print("\nGoodbye!")
                break
            self.handle_choice(choice)

    def display_menu(self) -> None:
        """Display main menu options."""
        # Print menu
        pass

    def get_user_choice(self) -> str:
        """Get and validate menu choice."""
        # Get input, validate 1-6
        pass

    def handle_choice(self, choice: str) -> None:
        """Route to appropriate handler based on choice."""
        handlers = {
            '1': self.add_task,
            '2': self.view_tasks,
            '3': self.toggle_task,
            '4': self.update_task,
            '5': self.delete_task
        }
        handlers[choice]()

    def add_task(self) -> None:
        """Handle add task flow."""
        # Prompt for title
        # Prompt for description
        # Call service.add_task()
        # Display success message
        pass

    def view_tasks(self) -> None:
        """Handle view tasks flow."""
        # Get all tasks from service
        # Display formatted table
        # Handle empty list case
        pass

    def toggle_task(self) -> None:
        """Handle toggle complete flow."""
        # Prompt for task ID
        # Call service.toggle_complete()
        # Display success/error message
        pass

    def update_task(self) -> None:
        """Handle update task flow."""
        # Prompt for task ID
        # Prompt for new title (optional)
        # Prompt for new description (optional)
        # Call service.update_task()
        # Display success/error message
        pass

    def delete_task(self) -> None:
        """Handle delete task flow."""
        # Prompt for task ID
        # Call service.delete_task()
        # Display success/error message
        pass
```

**Key Decisions**:
- Menu-driven loop (simpler than command-line args)
- Handler methods for each operation
- Input validation in CLI layer
- Error messages displayed to user

### File 4: `main.py`

**Purpose**: Application entry point

**Content**:
```python
#!/usr/bin/env python3
"""
Todo Application - Phase I: In-Memory Console App

This application demonstrates spec-driven development using Claude Code.
All code generated via AI following specification-first methodology.
"""

from src.cli.todo_cli import TodoCLI

def main():
    """Application entry point."""
    print("=== Todo Application - Phase I ===")
    print("In-memory storage (data not persisted)\n")

    cli = TodoCLI()
    cli.run()

if __name__ == "__main__":
    main()
```

**Key Decisions**:
- Simple entry point
- Welcome message explains in-memory limitation
- Instantiate CLI and call run()

### File 5: `__init__.py` files

Create empty `__init__.py` in:
- `src/`
- `src/domain/`
- `src/service/`
- `src/cli/`

These make directories proper Python packages.

---

## Phase 3: Post-Design Constitution Re-Check

**Re-evaluation after design decisions**:

### Principle I: Spec-Driven Development First
✅ **PASS** - All design decisions align with specification requirements

### Principle III: Deterministic Behavior
✅ **PASS** - All operations deterministic (dict storage, no randomness)

### Principle IV: Evolvability
✅ **PASS** - Domain model (Todo entity) can evolve to Phase II (SQLite) without breaking contract

### Principle V: Clear Separation of Concerns
✅ **PASS** - Three-layer architecture maintains clean separation:
  - Domain: `todo.py` (entity definition)
  - Service: `todo_service.py` (business logic)
  - CLI: `todo_cli.py` (user interface)

**Overall Re-Check Result**: ✅ **PASSED** - Design maintains constitutional compliance

---

## Success Criteria Mapping

Mapping spec success criteria to implementation:

- **SC-001** (Add task <10s): Menu-driven flow with clear prompts
- **SC-002** (View tasks <5s): Formatted table display with status indicators
- **SC-003** (Mark complete single command): Menu option 3 with ID prompt
- **SC-004** (Update immediate feedback): Update operation with confirmation message
- **SC-005** (Delete confirmation): Delete operation with success message
- **SC-006** (100+ tasks): Dict storage supports arbitrary scale
- **SC-007** (Clear errors): User-friendly error messages for all failure cases
- **SC-008** (100% features): All 5 operations implemented

---

## Risks and Mitigations

**Risk**: Menu-driven CLI might be less efficient than command-line args for power users
**Mitigation**: Acceptable for Phase I; Phase III can add CLI args if needed

**Risk**: Integer IDs reset on restart (not persistent)
**Mitigation**: Documented in-memory limitation; Phase II adds persistence

**Risk**: No input sanitization for special characters
**Mitigation**: Python string handling supports Unicode; quote escaping handled by input()

**Risk**: Long descriptions/titles might break display formatting
**Mitigation**: Truncate in __str__ method if exceeds column width

**Risk**: Concurrent access not supported (single-threaded)
**Mitigation**: Out of scope for Phase I single-user CLI

---

## Next Steps

After this plan is approved:

1. ✅ Generate `research.md` (Phase 0)
2. ✅ Generate `data-model.md` (Phase 1)
3. ✅ Generate `quickstart.md` (Phase 1)
4. ✅ Update agent context (Phase 1)
5. Run `/sp.tasks` to generate implementation task list
6. Run `/sp.implement` to execute tasks and create source code

---

## Hackathon Demonstration Notes

For judges:
1. Show Constitution → Spec → Plan → Tasks → Code progression
2. Run application: `python main.py`
3. Demonstrate all 5 features working
4. Show clean code structure (3 layers)
5. Show PHR history proving AI-generated code
6. Highlight zero external dependencies (standard library only)
7. Show in-memory constraint (data lost on exit)
