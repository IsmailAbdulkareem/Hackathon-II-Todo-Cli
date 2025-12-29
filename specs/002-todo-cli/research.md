# Research: CLI Todo Application Architecture & Design Patterns

**Feature**: Phase I – Todo In-Memory Python Console App
**Date**: 2025-12-28
**Purpose**: Research CLI patterns, architecture decisions, and Python best practices for todo application

## Executive Summary

This research document consolidates findings on building a CLI-based todo application using Python 3.13+ standard library. Key decisions cover CLI interaction patterns, data structures, clean architecture implementation, and error handling strategies.

---

## Research Question 1: CLI Interaction Pattern

### Decision

Use **menu-driven loop** with numbered options (1-6).

### Rationale

**Advantages of Menu-Driven**:
- More user-friendly for applications with multiple operations (5 in our case)
- Clear presentation of all available options
- No need to remember command syntax
- Easier error handling (validate single digit 1-6)
- Better for hackathon demonstration (judges can see all features at once)

**Disadvantages of Command-Line Args**:
- Requires remembering syntax for each operation
- More complex argument parsing
- Less discoverable for new users
- Requires help text/documentation for all commands

**Example Menu**:
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

### Alternatives Considered

- **Command-line arguments** (`python main.py add "title"`): Rejected - requires users to remember syntax, less demo-friendly
- **REPL-style** (todo> add "title"): Rejected - adds complexity for minimal benefit
- **Hybrid** (menu + args): Rejected - over-engineered for Phase I

---

## Research Question 2: Task ID Format

### Decision

Use **incrementing integers** starting at 1.

### Rationale

**Advantages of Integers**:
- Simple for users to type (ID: 1, 2, 3 vs UUID: 550e8400-e29b-41d4-a716-446655440000)
- Natural ordering for display
- Easier to demonstrate in hackathon ("mark task 1 complete")
- No external dependency (UUIDs need uuid module but still stdlib)
- Smaller memory footprint

**Disadvantages**:
- IDs reset on application restart (acceptable for in-memory Phase I)
- Not globally unique (acceptable for single-user CLI)

**Implementation**:
```python
class TodoService:
    def __init__(self):
        self._next_id = 1  # Start at 1 (more natural than 0)

    def add_task(...):
        task_id = self._next_id
        self._next_id += 1
```

### Alternatives Considered

- **UUID**: Rejected - unnecessarily complex for CLI, harder to type/remember
- **Zero-based indexing**: Rejected - 1-based more natural for non-programmers
- **Hash-based**: Rejected - not human-friendly

---

## Research Question 3: Storage Strategy

### Decision

Use **dict[int, Todo]** for in-memory storage.

### Rationale

**Advantages of Dict**:
- O(1) lookups by ID (vs O(n) for list)
- Natural key-value mapping (ID → Todo)
- Direct access for update/delete/toggle operations
- Simple to implement

**Dict vs List Comparison**:
| Operation | Dict | List |
|-----------|------|------|
| Get by ID | O(1) | O(n) |
| Add | O(1) | O(1) |
| Delete | O(1) | O(n) |
| Update | O(1) | O(n) |
| View All | O(n) | O(n) |

**Implementation**:
```python
class TodoService:
    def __init__(self):
        self._tasks: dict[int, Todo] = {}

    def get_task_by_id(self, task_id: int) -> Optional[Todo]:
        return self._tasks.get(task_id)  # O(1) lookup
```

### Alternatives Considered

- **List**: Rejected - O(n) lookups for get/update/delete operations
- **OrderedDict**: Rejected - dict maintains insertion order in Python 3.7+ (no need)
- **Custom data structure**: Rejected - over-engineered

---

## Research Question 4: Clean Architecture Implementation

### Decision

Use **three-layer architecture**: Domain, Service, CLI.

### Rationale

**Layer Responsibilities**:

1. **Domain Layer** (`src/domain/`):
   - Contains Todo entity (dataclass)
   - No dependencies on other layers
   - Pure Python data structures
   - Business rules embedded in entity (e.g., toggle_complete method)

2. **Service Layer** (`src/service/`):
   - Contains TodoService (business logic)
   - Depends only on Domain layer
   - Manages storage (in-memory dict)
   - Validates business rules
   - No knowledge of CLI (could be reused for web API in Phase III)

3. **CLI Layer** (`src/cli/`):
   - Contains TodoCLI (user interface)
   - Depends on Service layer
   - Handles user input/output
   - Formats display
   - Validates input format (not business rules)

**Dependency Flow**:
```
CLI → Service → Domain
(CLI depends on Service, Service depends on Domain, Domain has no dependencies)
```

**Evolvability for Future Phases**:
- Phase II (SQLite): Replace in-memory dict in Service with database calls
- Phase III (Web API): Add API layer alongside CLI (both use same Service)
- Domain layer never changes

### Alternatives Considered

- **Single file**: Rejected - violates separation of concerns, hard to evolve
- **Two layers** (CLI+Service combined): Rejected - couples UI to business logic
- **Four+ layers**: Rejected - over-engineered for Phase I scope

---

## Research Question 5: Error Handling Strategy

### Decision

Use **ValueError exceptions** for business rule violations with user-friendly messages in CLI layer.

### Rationale

**Exception Strategy**:
- Service layer raises `ValueError` for business rule violations
- CLI layer catches exceptions and displays user-friendly messages
- System errors (e.g., KeyboardInterrupt) propagate to main()

**Example**:
```python
# Service layer
def add_task(self, title: str, description: str = "") -> Todo:
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    if len(title) > 200:
        raise ValueError("Title too long (max 200 characters)")
    # Create and return task

# CLI layer
def add_task(self):
    try:
        title = input("Enter title: ")
        description = input("Enter description (optional): ")
        task = self.service.add_task(title, description)
        print(f"Task created successfully! ID: {task.id}")
    except ValueError as e:
        print(f"Error: {e}")
```

**User-Friendly Error Messages**:
- "Error: Title cannot be empty" (not "ValueError: empty string")
- "Error: Task not found with ID 99" (not "KeyError: 99")
- "Error: Invalid choice. Please enter 1-6." (not "ValueError: invalid literal")

### Alternatives Considered

- **Custom exceptions** (TodoNotFoundError, etc.): Rejected - overkill for Phase I
- **Return None for errors**: Rejected - less Pythonic, harder to distinguish success/failure
- **Status codes**: Rejected - not idiomatic Python

---

## Research Question 6: Input Validation Strategy

### Decision

**Two-layer validation**:
- CLI layer: Validates format (e.g., choice 1-6, ID is numeric)
- Service layer: Validates business rules (e.g., title not empty, title ≤200 chars)

### Rationale

**Separation of Concerns**:
- CLI validation prevents invalid input from reaching service
- Service validation enforces business rules (reusable across interfaces)
- Clear responsibility boundaries

**Example**:

**CLI Layer (Format Validation)**:
```python
def get_user_choice(self) -> str:
    while True:
        choice = input("Enter choice (1-6): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        print("Error: Invalid choice. Please enter 1-6.")
```

**Service Layer (Business Rule Validation)**:
```python
def add_task(self, title: str, description: str = "") -> Todo:
    # Business rule: title cannot be empty
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    # Business rule: title max length
    if len(title) > 200:
        raise ValueError("Title too long (max 200 characters)")
```

### Alternatives Considered

- **All validation in CLI**: Rejected - couples business rules to UI
- **All validation in Service**: Rejected - allows invalid format to reach service
- **No validation**: Rejected - violates spec FR-008 (clear error messages)

---

## Additional Best Practices

### Python 3.13+ Features to Use

1. **Type Hints**: Use throughout for clarity
   ```python
   def add_task(self, title: str, description: str = "") -> Todo:
   ```

2. **Dataclasses**: Use for Todo entity (less boilerplate)
   ```python
   @dataclass
   class Todo:
       id: int
       title: str
   ```

3. **Union Types** (Python 3.10+ syntax):
   ```python
   def get_task_by_id(self, task_id: int) -> Todo | None:
   ```

4. **String Methods**: Use `.strip()` to handle whitespace
   ```python
   title = input("Title: ").strip()
   ```

### Display Formatting

**Table Format**:
```
ID  | Status | Title                          | Description
----|--------|--------------------------------|---------------------------
  1 | [ ]    | Buy groceries                  | Milk, eggs, bread
  2 | [x]    | Finish report                  | Complete quarterly analysis
```

**Implementation**:
```python
def __str__(self) -> str:
    status = "[x]" if self.completed else "[ ]"
    # Truncate title/description if too long
    title = self.title[:30]
    desc = self.description[:50]
    return f"{self.id:3d} | {status} | {title:30s} | {desc}"
```

### Performance Considerations

For 100+ tasks:
- Dict lookups: O(1) - instant
- Display all: O(n) - < 1 second for 100 tasks
- Sorting: O(n log n) - negligible for 100 tasks

**No optimization needed for Phase I scope.**

---

## Conclusions

Research confirms technical approach is sound:

✅ Menu-driven CLI is most user-friendly for hackathon demo
✅ Integer IDs are simpler than UUIDs for CLI
✅ Dict storage provides O(1) lookups
✅ Clean architecture enables Phase II/III evolution
✅ Exception-based error handling is Pythonic
✅ Two-layer validation separates concerns appropriately

**Recommendation**: Proceed with implementation plan as defined in `plan.md`. No changes to technical approach required based on research findings.

---

## References

- Python Dataclasses: https://docs.python.org/3/library/dataclasses.html
- Python Type Hints: https://docs.python.org/3/library/typing.html
- Clean Architecture: Robert C. Martin (Uncle Bob)
- Python Standard Library: https://docs.python.org/3/library/
