# Phase I: In-Memory Todo Console Application

**Status:** ✅ Complete
**Points:** 100
**Tech Stack:** Python 3.13+, Claude Code, Spec-Kit Plus
**Due Date:** Dec 7, 2025

## Overview

Phase I implements a basic in-memory todo CLI application demonstrating Spec-Driven Development principles. All data is stored in memory and lost when the application exits.

## Features

1. **Add Task** - Create new tasks with title and optional description
2. **View Tasks** - Display all tasks with status indicators ([ ] incomplete, [x] complete)
3. **Mark Complete/Incomplete** - Toggle task completion status
4. **Update Task** - Modify task title or description
5. **Delete Task** - Remove tasks from the list

## Quick Start

### Prerequisites
- Python 3.13 or higher
- uv package manager (fast Python package manager by Astral)

### Setup

1. **Install uv** (if not already installed):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Run the application:**
   ```bash
   uv run main.py
   ```

## Project Structure

```
phase-01-in-memory-console/
├── src/
│   ├── domain/
│   │   └── todo.py             # Todo dataclass entity
│   ├── service/
│   │   └── todo_service.py    # Business logic (CRUD)
│   └── cli/
│       └── todo_cli.py         # Menu-driven CLI interface
├── specs/
│   ├── 001-env-setup/          # Environment setup spec
│   └── 002-todo-cli/           # Todo CLI spec & tasks
├── main.py                     # Application entry point
├── pyproject.toml              # Project metadata
└── .python-version             # Python version (3.13)
```

## Example Session

```bash
$ uv run main.py
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
Enter task description: Milk, eggs, bread
✓ Task created successfully! ID: 1

Enter choice (1-6): 2
Your Tasks:
ID  | Status | Title              | Description
----|--------|--------------------|-----------------
  1 | [ ]    | Buy groceries      | Milk, eggs, bread
```

## Architecture

This phase demonstrates:
- **Domain-Driven Design**: Clean separation of domain entities, services, and interfaces
- **SDD Workflow**: All code generated from specifications using Claude Code
- **Python Standard Library Only**: No external dependencies beyond uv for environment management

### Key Components

- **Todo Entity** (src/domain/todo.py): Dataclass representing a todo item
- **TodoService** (src/service/todo_service.py): In-memory CRUD operations
- **TodoCLI** (src/cli/todo_cli.py): Interactive menu interface

## Limitations

- No persistence (all data lost on exit)
- No multi-user support
- No authentication
- CLI-only interface

## Next Steps

Phase II will add:
- PostgreSQL database persistence (Neon)
- FastAPI backend for REST API
- Next.js frontend for web UI
- Domain model remains unchanged

## Documentation

- [Environment Setup Guide](specs/001-env-setup/quickstart.md)
- [Todo CLI Guide](specs/002-todo-cli/quickstart.md)
- [Project Constitution](../.specify/memory/constitution.md)
