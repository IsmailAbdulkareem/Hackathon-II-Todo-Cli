# Quick Start: Todo CLI Application

**Feature**: Phase I – Todo In-Memory Python Console App
**Purpose**: User guide for running and using the todo application
**Estimated Time**: 2 minutes to start using

---

## Prerequisites

Before running the application, ensure you have completed Feature 001 (Environment Setup):

1. **Python 3.13+ installed** - Verify: `python --version`
2. **Virtual environment activated** - Run: `source .venv/bin/activate` (Unix) or `.venv\Scripts\Activate.ps1` (Windows)
3. **Application code implemented** - Run `/sp.implement` to generate source code

---

## Running the Application

### Start the Application

From the project root directory:

```bash
python main.py
```

**Expected Output**:
```
=== Todo Application - Phase I ===
In-memory storage (data not persisted)

Todo Application - Main Menu
1. Add new task
2. View all tasks
3. Mark task complete/incomplete
4. Update task
5. Delete task
6. Exit

Enter choice (1-6):
```

---

## Feature Guide

### 1. Add New Task

**Menu Choice**: 1

**Flow**:
1. System prompts: `Enter task title:`
2. You enter: `Buy groceries`
3. System prompts: `Enter task description (optional, press Enter to skip):`
4. You enter: `Milk, eggs, bread` (or press Enter for empty description)
5. System displays: `Task created successfully! ID: 1`

**Example Session**:
```
Enter choice (1-6): 1

Enter task title: Buy groceries
Enter task description (optional, press Enter to skip): Milk, eggs, bread

Task created successfully! ID: 1
```

**Validation**:
- Title cannot be empty (error displayed if empty)
- Title max 200 characters (error displayed if exceeded)
- Description max 1000 characters (error displayed if exceeded)

---

### 2. View All Tasks

**Menu Choice**: 2

**Flow**:
1. System displays all tasks in formatted table

**Example Output** (with tasks):
```
Enter choice (1-6): 2

Your Tasks:
================================================================================
ID  | Status | Title                          | Description
----|--------|--------------------------------|---------------------------
  1 | [ ]    | Buy groceries                  | Milk, eggs, bread
  2 | [x]    | Finish report                  | Complete quarterly analysis
  3 | [ ]    | Call dentist                   |

Total tasks: 3 | Completed: 1 | Pending: 2
```

**Example Output** (no tasks):
```
Enter choice (1-6): 2

Your task list is empty. Add your first task!
```

**Status Indicators**:
- `[ ]` - Incomplete task
- `[x]` - Completed task

---

### 3. Mark Task Complete/Incomplete

**Menu Choice**: 3

**Flow**:
1. System prompts: `Enter task ID:`
2. You enter: `1`
3. System toggles completion status
4. System displays: `Task 1 marked as complete!` (or "incomplete" if toggling back)

**Example Session** (marking complete):
```
Enter choice (1-6): 3

Enter task ID: 1

Task 1 marked as complete!
```

**Example Session** (marking incomplete):
```
Enter choice (1-6): 3

Enter task ID: 1

Task 1 marked as incomplete!
```

**Error Handling**:
- If task ID doesn't exist: `Error: Task not found with ID 99`
- If invalid input: `Error: Please enter a valid numeric ID`

---

### 4. Update Task

**Menu Choice**: 4

**Flow**:
1. System prompts: `Enter task ID:`
2. You enter: `1`
3. System prompts: `Enter new title (press Enter to keep current):`
4. You enter new title or press Enter to skip
5. System prompts: `Enter new description (press Enter to keep current):`
6. You enter new description or press Enter to skip
7. System displays: `Task 1 updated successfully!`

**Example Session** (update title only):
```
Enter choice (1-6): 4

Enter task ID: 1
Enter new title (press Enter to keep current): Buy groceries and supplies
Enter new description (press Enter to keep current): [Press Enter]

Task 1 updated successfully!
```

**Example Session** (update both):
```
Enter choice (1-6): 4

Enter task ID: 2
Enter new title (press Enter to keep current): Complete quarterly report
Enter new description (press Enter to keep current): Add charts and submit by Friday

Task 2 updated successfully!
```

**Validation**:
- At least one field (title or description) must be updated
- Same validation rules as adding tasks (title non-empty, length limits)

**Error Handling**:
- If task ID doesn't exist: `Error: Task not found with ID 99`
- If both fields skipped: `Error: No changes provided. Please update at least one field.`

---

### 5. Delete Task

**Menu Choice**: 5

**Flow**:
1. System prompts: `Enter task ID:`
2. You enter: `1`
3. System displays: `Task 1 deleted successfully!`

**Example Session**:
```
Enter choice (1-6): 5

Enter task ID: 3

Task 3 deleted successfully!
```

**Error Handling**:
- If task ID doesn't exist: `Error: Task not found with ID 99`
- If invalid input: `Error: Please enter a valid numeric ID`

**Note**: Deleted task IDs are not reused in the current session.

---

### 6. Exit Application

**Menu Choice**: 6

**Flow**:
1. System displays: `Goodbye! Your tasks were not saved (in-memory storage).`
2. Application terminates

**Example Session**:
```
Enter choice (1-6): 6

Goodbye! Your tasks were not saved (in-memory storage).
```

**Important**: All tasks are lost when exiting (in-memory only for Phase I).

---

## Sample Workflow

Complete example session demonstrating all features:

```bash
$ python main.py
=== Todo Application - Phase I ===
In-memory storage (data not persisted)

Todo Application - Main Menu
1. Add new task
2. View all tasks
3. Mark task complete/incomplete
4. Update task
5. Delete task
6. Exit

Enter choice (1-6): 1

Enter task title: Buy groceries
Enter task description (optional, press Enter to skip): Milk, eggs, bread

Task created successfully! ID: 1

Enter choice (1-6): 1

Enter task title: Finish report
Enter task description (optional, press Enter to skip): Complete quarterly analysis

Task created successfully! ID: 2

Enter choice (1-6): 2

Your Tasks:
================================================================================
ID  | Status | Title                          | Description
----|--------|--------------------------------|---------------------------
  1 | [ ]    | Buy groceries                  | Milk, eggs, bread
  2 | [ ]    | Finish report                  | Complete quarterly analysis

Total tasks: 2 | Completed: 0 | Pending: 2

Enter choice (1-6): 3

Enter task ID: 2

Task 2 marked as complete!

Enter choice (1-6): 2

Your Tasks:
================================================================================
ID  | Status | Title                          | Description
----|--------|--------------------------------|---------------------------
  1 | [ ]    | Buy groceries                  | Milk, eggs, bread
  2 | [x]    | Finish report                  | Complete quarterly analysis

Total tasks: 2 | Completed: 1 | Pending: 1

Enter choice (1-6): 6

Goodbye! Your tasks were not saved (in-memory storage).
```

---

## Error Messages Reference

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `Error: Title cannot be empty` | Empty or whitespace-only title | Provide a non-empty title |
| `Error: Title too long (max 200 characters)` | Title exceeds 200 chars | Shorten the title |
| `Error: Description too long (max 1000 characters)` | Description exceeds 1000 chars | Shorten the description |
| `Error: Task not found with ID X` | Task ID doesn't exist | Use a valid task ID from the list |
| `Error: Invalid choice. Please enter 1-6.` | Menu choice not 1-6 | Enter a number from 1 to 6 |
| `Error: Please enter a valid numeric ID` | Non-numeric ID entered | Enter a number (e.g., 1, 2, 3) |

---

## Important Notes

### In-Memory Storage Limitation

**All tasks are lost when the application exits.**

This is a Phase I constraint:
- ✅ Acceptable: Tasks persist during application session
- ❌ Not Supported: Tasks do not persist after exit
- 📌 Future: Phase II adds SQLite persistence

### Task IDs

- IDs are assigned sequentially starting at 1
- IDs increment even after task deletion
- IDs reset when application restarts
- IDs are unique within a session

### Performance

- Supports 100+ tasks without noticeable slowdown
- Instant response for all operations (<100ms)
- No pagination needed for Phase I scope

---

## Troubleshooting

**Issue**: Application doesn't start
**Solution**: Ensure virtual environment is activated and Python 3.13+ is installed

**Issue**: "Module not found" error
**Solution**: Ensure you're running from project root directory, not inside `src/`

**Issue**: Changes not reflected
**Solution**: Restart application (in-memory storage is session-based)

**Issue**: Unicode characters display incorrectly
**Solution**: Ensure terminal supports UTF-8 encoding

---

## Next Steps

After using the application:

1. **Provide Feedback**: Note any usability issues for improvement
2. **Demo to Judges**: Showcase all 5 features and spec-driven workflow
3. **Prepare for Phase II**: Identify requirements for SQLite persistence
4. **Review Code**: Examine generated source code in `src/` directory

---

**Built with AI • Guided by Specifications • Governed by Principles**
