# Data Model: Todo Entity

**Feature**: Phase I – Todo In-Memory Python Console App
**Date**: 2025-12-28
**Purpose**: Define the Todo entity structure, validation rules, and state transitions

## Entity: Todo

### Attributes

| Attribute | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `id` | int | Yes | Auto-assigned | Unique, positive integer, starts at 1 | Unique identifier for the task |
| `title` | str | Yes | None | Non-empty, ≤200 characters | Short description of the task |
| `description` | str | No | "" (empty string) | ≤1000 characters | Detailed explanation of the task |
| `completed` | bool | Yes | False | Boolean | Completion status flag |
| `created_at` | datetime | Yes | Auto-assigned | Valid datetime | Timestamp of task creation |

### Python Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Todo:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

**Implementation Notes**:
- Uses Python dataclass for automatic `__init__`, `__repr__`, `__eq__`
- `created_at` auto-set using `field(default_factory=datetime.now)`
- All attributes have type hints for clarity

---

## Validation Rules

### Title Validation
- **MUST NOT be empty** - Rejected: `""`, `"   "` (whitespace only)
- **MUST NOT exceed 200 characters** - Rejected: strings longer than 200 chars
- **MAY contain any Unicode characters** - Accepted: letters, numbers, symbols, emoji
- **Whitespace trimmed** - Leading/trailing whitespace removed before validation

**Examples**:
- ✅ Valid: `"Buy groceries"`, `"Finish report 📝"`, `"A" * 200`
- ❌ Invalid: `""`, `"   "`, `"A" * 201`

### Description Validation
- **MAY be empty** - Accepted: `""` (optional field)
- **MUST NOT exceed 1000 characters** - Rejected: strings longer than 1000 chars
- **MAY contain any Unicode characters** - Accepted: letters, numbers, symbols, emoji
- **Whitespace preserved** - Leading/trailing whitespace not automatically trimmed

**Examples**:
- ✅ Valid: `""`, `"Milk, eggs, bread"`, `"A" * 1000`
- ❌ Invalid: `"A" * 1001`

### ID Validation
- **Auto-assigned by TodoService** - Users never provide IDs
- **MUST be unique** - Enforced by incrementing counter
- **MUST be positive integer** - Starts at 1, increments by 1
- **Never reused** - Even after deletion (acceptable for Phase I in-memory)

**Examples**:
- ✅ Valid: `1`, `2`, `3`, `100`
- ❌ Invalid: `0`, `-1`, `1.5` (enforced by type system)

### Completed Validation
- **MUST be boolean** - Enforced by type system
- **Defaults to False** - New tasks are incomplete
- **Toggled via service method** - Users don't set directly

**Examples**:
- ✅ Valid: `True`, `False`
- ❌ Invalid: `1`, `"true"`, `None` (enforced by type system)

---

## State Transitions

### Task Lifecycle

```
┌─────────────┐
│   Created   │ (completed=False, ID assigned)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Incomplete  │ [Status: [ ]]
└──────┬──────┘
       │
       │ toggle_complete()
       │
       ▼
┌─────────────┐
│  Complete   │ [Status: [x]]
└──────┬──────┘
       │
       │ toggle_complete()
       │
       ▼
┌─────────────┐
│ Incomplete  │ [Status: [ ]]
└──────┬──────┘
       │
       │ delete_task()
       │
       ▼
┌─────────────┐
│   Deleted   │ (removed from storage)
└─────────────┘
```

### State Transition Rules

1. **Creation** → **Incomplete**
   - Trigger: `TodoService.add_task(title, description)`
   - Result: New Todo with `completed=False`, unique ID, current timestamp
   - Validation: Title must be non-empty and ≤200 chars

2. **Incomplete** ↔ **Complete** (Bidirectional)
   - Trigger: `TodoService.toggle_complete(task_id)` or `Todo.toggle_complete()`
   - Result: `completed` flips (False → True or True → False)
   - Validation: Task ID must exist

3. **Any State** → **Deleted**
   - Trigger: `TodoService.delete_task(task_id)`
   - Result: Task removed from storage permanently
   - Validation: Task ID must exist
   - Note: ID not reused (acceptable for Phase I)

4. **Update** (No State Change)
   - Trigger: `TodoService.update_task(task_id, title, description)`
   - Result: Title and/or description modified, completion status unchanged
   - Validation: Task ID must exist, new title must pass validation if provided

---

## Entity Methods

### Toggle Complete

```python
def toggle_complete(self) -> None:
    """Toggle completion status between True and False."""
    self.completed = not self.completed
```

**Purpose**: Convenience method for state transition
**Usage**: Called by `TodoService.toggle_complete()`
**Side Effects**: Modifies `completed` attribute in-place

### String Representation

```python
def __str__(self) -> str:
    """Format task for display in CLI table."""
    status = "[x]" if self.completed else "[ ]"
    return f"{self.id:3d} | {status} | {self.title:30s} | {self.description}"
```

**Purpose**: Formatted display for CLI
**Format**: `ID | Status | Title | Description`
**Example Output**: `  1 | [ ] | Buy groceries                  | Milk, eggs, bread`

---

## Relationships

### Todo ↔ TodoService

**Relationship Type**: Managed Collection
**Cardinality**: Many Todos managed by one TodoService

```
TodoService (1) ─────manages────── (0..*) Todo
```

**Storage**: `TodoService._tasks: dict[int, Todo]`
**Access Pattern**: Direct access by ID via dictionary lookup

**No relationships between Todo entities** - Tasks are independent

---

## Invariants

Conditions that must always be true:

1. **Unique IDs**: No two Todo instances have the same `id`
2. **Valid Title**: `title` is never empty and never exceeds 200 characters
3. **Valid Description**: `description` never exceeds 1000 characters
4. **Boolean Completed**: `completed` is always `True` or `False`
5. **Valid Timestamp**: `created_at` is always a valid `datetime` object
6. **Positive IDs**: `id` is always a positive integer (≥1)

**Enforcement**:
- Type system enforces type constraints (int, str, bool, datetime)
- TodoService enforces business rule constraints (length, non-empty)
- Dataclass provides immutable defaults

---

## Examples

### Example 1: Simple Task

```python
Todo(
    id=1,
    title="Buy groceries",
    description="Milk, eggs, bread",
    completed=False,
    created_at=datetime(2025, 12, 28, 10, 30, 0)
)
```

**Display**: `  1 | [ ] | Buy groceries                  | Milk, eggs, bread`

### Example 2: Complete Task

```python
Todo(
    id=2,
    title="Finish report",
    description="Complete quarterly analysis",
    completed=True,
    created_at=datetime(2025, 12, 28, 9, 15, 0)
)
```

**Display**: `  2 | [x] | Finish report                  | Complete quarterly analysis`

### Example 3: Task Without Description

```python
Todo(
    id=3,
    title="Call dentist",
    description="",
    completed=False,
    created_at=datetime(2025, 12, 28, 11, 45, 0)
)
```

**Display**: `  3 | [ ] | Call dentist                   |`

---

## Evolution to Phase II (SQLite Persistence)

**Changes Required**:
- Add `id` as primary key in database schema
- Map `datetime` to ISO 8601 string for storage
- Add `updated_at` timestamp (optional enhancement)

**No Breaking Changes**:
- Entity structure remains identical
- Service layer interface unchanged
- CLI layer unaffected

**Backward Compatibility**: Phase II can read/write Phase I entity structure without modification.
