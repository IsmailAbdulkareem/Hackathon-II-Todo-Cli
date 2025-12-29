# The Evolution of Todo — Spec-Driven, Cloud-Native AI Application

**Phase I: In-Memory Todo Console Application**

A demonstration project showcasing Spec-Driven Development (SDD) with AI as the primary implementer. This project evolves across multiple phases, maintaining stable domain contracts while adapting interfaces and infrastructure.

---

## Project Overview

This project demonstrates:

- **Spec-Driven Development First**: All features begin with specifications before implementation
- **AI as Implementer, Human as Architect**: Claude Code generates all code based on human-defined requirements
- **Deterministic Behavior**: Non-LLM components are predictable and testable
- **Evolvability**: Domain model remains stable across phases while interfaces evolve
- **Clear Separation**: Domain logic, interfaces, and infrastructure are independently managed
- **Infrastructure as Code**: Declarative, reproducible environment and deployment configurations

---

## Quick Start

### Prerequisites

- **Python 3.13 or higher** - [Download Python](https://www.python.org/downloads/)
- **uv package manager** - Fast Python package manager by Astral

### Setup Instructions

For detailed setup instructions, see: **[Environment Setup Guide](specs/001-env-setup/quickstart.md)**

**Quick Setup**:

1. **Install uv** (if not already installed):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Create virtual environment**:
   ```bash
   uv venv
   ```

3. **Activate environment**:
   ```bash
   # macOS/Linux
   source .venv/bin/activate

   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

4. **Verify Python version**:
   ```bash
   python --version  # Should show 3.13+
   ```

---

## Using the Todo Application

### Run the Application

After setting up the environment:

```bash
python main.py
```

### Features

The application provides 5 core todo management features:

1. **Add Task** - Create new tasks with title and optional description
2. **View Tasks** - Display all tasks with status indicators ([ ] incomplete, [x] complete)
3. **Mark Complete/Incomplete** - Toggle task completion status
4. **Update Task** - Modify task title or description
5. **Delete Task** - Remove tasks from the list

For detailed usage instructions, see: **[Todo CLI Guide](specs/002-todo-cli/quickstart.md)**

### Example Session

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
Enter task description: Milk, eggs, bread
✓ Task created successfully! ID: 1

Enter choice (1-6): 2
Your Tasks:
ID  | Status | Title              | Description
----|--------|--------------------|-----------------
  1 | [ ]    | Buy groceries      | Milk, eggs, bread
```

**Note**: Tasks are stored in memory only and are lost when the application exits.

---

## Project Structure

```
.
├── src/                        # Application source code
│   ├── domain/                 # Domain entities
│   │   └── todo.py             # Todo dataclass
│   ├── service/                # Business logic
│   │   └── todo_service.py     # TodoService (CRUD operations)
│   └── cli/                    # CLI interface
│       └── todo_cli.py         # Menu-driven CLI
│
├── main.py                     # Application entry point
│
├── .specify/                   # Spec-Driven Development templates and scripts
│   ├── memory/
│   │   └── constitution.md     # Project principles and governance
│   ├── templates/              # Spec, plan, task templates
│   └── scripts/                # Automation scripts
│
├── specs/                      # Feature specifications
│   ├── 001-env-setup/          # Environment setup
│   │   ├── spec.md             # Feature requirements
│   │   ├── plan.md             # Architecture plan
│   │   ├── tasks.md            # Implementation tasks
│   │   ├── research.md         # Technical research
│   │   └── quickstart.md       # Setup guide
│   └── 002-todo-cli/           # Todo CLI application
│       ├── spec.md             # Feature requirements
│       ├── plan.md             # Architecture plan
│       ├── tasks.md            # Implementation tasks
│       ├── research.md         # Technical research
│       ├── data-model.md       # Todo entity definition
│       └── quickstart.md       # Usage guide
│
├── history/                    # Development history
│   ├── prompts/                # Prompt History Records (PHRs)
│   │   ├── constitution/
│   │   ├── 001-env-setup/
│   │   ├── 002-todo-cli/
│   │   └── general/
│   └── adr/                    # Architecture Decision Records
│
├── .claude/                    # Claude Code commands
│
├── pyproject.toml              # Project metadata and dependencies
├── .python-version             # Python version (3.13)
├── .gitignore                  # Git exclusions
└── README.md                   # This file

# Future Structure (Phase II+)
tests/                          # Test suite (when tests requested)
```

---

## Development Workflow

This project follows the **Spec-Driven Development (SDD)** methodology:

### 1. Specification (`/sp.specify`)
Define what needs to be built:
- User scenarios and acceptance criteria
- Functional requirements
- Success criteria
- Edge cases and constraints

### 2. Planning (`/sp.plan`)
Design the technical approach:
- Architecture decisions
- Technology choices
- File structure
- API contracts

### 3. Task Generation (`/sp.tasks`)
Break down implementation:
- Ordered task list
- Dependencies
- Parallel opportunities

### 4. Implementation (`/sp.implement`)
Execute the plan:
- Generate all code via Claude Code
- Follow TDD if tests required
- Validate against spec

### 5. Review and Iterate
- Verify implementation matches spec
- Refine spec if behavior needs adjustment
- Never manually edit generated code

---

## Constitution

This project is governed by **7 Core Principles** defined in [.specify/memory/constitution.md](.specify/memory/constitution.md):

1. **Spec-Driven Development First** - Specifications govern all implementation
2. **AI as Implementer, Human as Architect** - Clear division of responsibilities
3. **Deterministic Behavior** - Predictable, testable systems
4. **Evolvability Across Phases** - Stable domain contracts
5. **Clear Separation of Concerns** - Domain, interfaces, infrastructure layers
6. **Reusable Intelligence** - AI features must be explainable and fail-safe
7. **Infrastructure as Declarative** - Reproducible, version-controlled infrastructure

---

## Phase Roadmap

### Phase I: In-Memory Todo Console Application ✅ (Current)
- **Status**: Environment setup complete
- **Features**: Python 3.13+ environment with uv
- **Next**: Todo domain model and CLI interface

### Phase II: SQLite Persistence (Planned)
- Migrate from in-memory to SQLite storage
- Domain model remains unchanged
- Add persistence layer

### Phase III: Web API (Planned)
- Expose HTTP/REST API
- Domain model remains unchanged
- Add API interface layer

### Phase IV: AI-Powered Features (Planned)
- Natural language todo creation
- Smart scheduling and prioritization
- Domain model remains unchanged

### Phase V: Cloud Deployment (Planned)
- Deploy to cloud (AWS/GCP/Azure)
- Add authentication and multi-tenancy
- Domain model remains unchanged

---

## Contributing

This project demonstrates AI-driven development. Contributions should follow the Spec-Driven Development workflow:

1. **Create a Specification**: Use `/sp.specify <feature-description>` to generate a spec
2. **Review and Refine**: Human architect reviews and refines the spec
3. **Generate Plan**: Use `/sp.plan` to create implementation plan
4. **Generate Tasks**: Use `/sp.tasks` to break down work
5. **Implement**: Use `/sp.implement` to generate code via Claude Code
6. **Validate**: Ensure implementation matches specification

**Important**: All code is generated by AI. Manual code edits are not allowed per the constitution.

---

## Technology Stack

### Phase I
- **Language**: Python 3.13+
- **Package Manager**: uv (Astral)
- **Standard Library**: typing, dataclasses, uuid, datetime
- **Dependencies**: None (standard library only)

### Future Phases
- **Database**: SQLite (Phase II)
- **Web Framework**: TBD (Phase III)
- **AI SDKs**: TBD (Phase IV)
- **Cloud Platform**: TBD (Phase V)

---

## Documentation

- **Setup Guide**: [specs/001-env-setup/quickstart.md](specs/001-env-setup/quickstart.md)
- **Constitution**: [.specify/memory/constitution.md](.specify/memory/constitution.md)
- **Feature Specs**: [specs/](specs/)
- **Prompt History**: [history/prompts/](history/prompts/)
- **Architecture Decisions**: [history/adr/](history/adr/)

---

## License

[Specify your license here]

---

## Acknowledgments

- **Claude Code**: Primary implementation agent (Anthropic)
- **uv**: Fast Python package manager (Astral)
- **Spec-Driven Development**: Methodology ensuring AI-generated code meets human-defined requirements

---

**Built with AI • Guided by Specifications • Governed by Principles**
