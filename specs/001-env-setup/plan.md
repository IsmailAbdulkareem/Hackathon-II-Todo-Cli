# Implementation Plan: Phase I – Environment & Package Setup

**Branch**: `001-env-setup` | **Date**: 2025-12-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-env-setup/spec.md`

**Note**: This plan defines the technical approach for establishing a minimal, reproducible Python 3.13+ development environment using `uv`.

## Summary

Establish a foundational Python development environment that enables developers to work on Phase I (In-Memory Todo Console Application) without dependency conflicts or version mismatches. The environment will use Python 3.13+ and be managed exclusively with the `uv` package manager. No external runtime dependencies will be installed in Phase I, relying solely on Python's standard library (typing, dataclasses, uuid, datetime).

**Technical Approach**: Use `uv` to create a virtual environment with Python 3.13+, generate a minimal `pyproject.toml` configuration file, and provide clear setup documentation that works across Windows, macOS, and Linux.

## Technical Context

**Language/Version**: Python 3.13 or higher
**Primary Dependencies**: None (uv for environment management only)
**Storage**: N/A (environment setup feature)
**Testing**: N/A (no tests for Phase I per spec)
**Target Platform**: Cross-platform (Windows, macOS, Linux)
**Project Type**: single (console application)
**Performance Goals**: Environment creation <2 minutes, activation <5 seconds
**Constraints**: No external runtime dependencies, reproducible across platforms, no admin privileges required
**Scale/Scope**: Single developer environment, Phase I only (in-memory operations)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development First
✅ **PASS** - Specification exists at `specs/001-env-setup/spec.md` with clear scope and acceptance criteria

### Principle II: AI as Implementer, Human as Architect
✅ **PASS** - Human architect defined requirements; Claude Code will generate environment configuration files

### Principle III: Deterministic Behavior Across Non-LLM Components
✅ **PASS** - Environment setup is deterministic (same commands → same environment)

### Principle IV: Evolvability Across Phases Without Breaking Domain Contracts
✅ **PASS** - Environment setup is infrastructure; does not define domain contracts

### Principle V: Clear Separation of Domain Logic, Interfaces, and Infrastructure
✅ **PASS** - This is pure infrastructure (environment configuration); no domain logic involved

### Principle VI: Reusable Intelligence Over One-Off Solutions
✅ **PASS** - No AI-powered features in this infrastructure setup

### Principle VII: Infrastructure as Declarative and Reproducible
✅ **PASS** - Will use declarative `pyproject.toml`; `uv` commands are reproducible and version-controlled

**Overall Gate Result**: ✅ **PASSED** - No constitutional violations detected

## Project Structure

### Documentation (this feature)

```text
specs/001-env-setup/
├── spec.md              # Feature specification
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (uv best practices)
├── quickstart.md        # Phase 1 output (setup instructions)
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

Since this is an environment setup feature, no application source code will be created. The following project structure will be established:

```text
# Project Root Structure
.
├── .venv/                      # Virtual environment (created by uv, gitignored)
├── pyproject.toml              # Project metadata and dependencies (Phase I: empty deps)
├── .python-version             # Python version specification (3.13+)
├── README.md                   # Project overview and setup instructions
├── .gitignore                  # Ignore .venv/, __pycache__, etc.
├── specs/                      # Specifications (already exists)
│   └── 001-env-setup/
├── history/                    # PHRs and ADRs (already exists)
│   ├── prompts/
│   └── adr/
├── .specify/                   # Templates and scripts (already exists)
│   ├── memory/
│   ├── templates/
│   └── scripts/
└── .claude/                    # Claude-specific commands (already exists)

# Future structure (created in later phases)
src/                            # Application source code (Phase II+)
├── models/                     # Domain entities
├── services/                   # Business logic
└── cli/                        # CLI interface

tests/                          # Test suite (if requested in future specs)
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Using **single project** structure (Option 1 from template). This is a console application without separate frontend/backend or mobile components. The `src/` directory will be created in future phases when actual application code is implemented.

**Phase I Scope**: Only environment configuration files (`pyproject.toml`, `.python-version`, `README.md`, `.gitignore`) will be created. Application directories (`src/`, `tests/`) are explicitly out of scope per the specification.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations detected. This section is intentionally left empty.

---

## Phase 0: Research & Best Practices

**Objective**: Research `uv` best practices and resolve any technical unknowns for environment setup.

### Research Questions

1. What is the recommended `pyproject.toml` structure for `uv` projects?
2. How does `uv` handle Python version specification?
3. What are the standard `uv` commands for environment creation and activation across platforms?
4. How should `.gitignore` be configured for `uv` projects?
5. What is the recommended directory name for virtual environments with `uv`?

### Research Output

Research findings will be documented in `research.md` covering:
- `uv` project initialization best practices
- Cross-platform environment activation commands
- Python version pinning strategies
- Dependency management approach (even with zero dependencies)
- Common pitfalls and error handling

---

## Phase 1: Design & Configuration

**Objective**: Design the environment configuration files and setup documentation.

### Deliverables

Since this feature does not involve data models or API contracts, Phase 1 will produce:

1. **quickstart.md** - Developer setup instructions
   - Prerequisites (installing `uv` and Python 3.13+)
   - Environment creation steps
   - Environment activation commands (platform-specific)
   - Verification steps (check Python version)
   - Troubleshooting common issues

2. **Configuration File Designs** - Documented in this plan (see Phase 2)

### No Data Model Required

This feature does not involve domain entities. `data-model.md` is not applicable.

### No API Contracts Required

This feature does not expose APIs or interfaces. `contracts/` directory is not applicable.

---

## Phase 2: Implementation Planning

**Objective**: Define concrete implementation steps for environment setup.

### File: `pyproject.toml`

**Purpose**: Define project metadata and dependencies (empty for Phase I)

**Content Structure**:
```toml
[project]
name = "todo-evolution"
version = "0.1.0"
description = "The Evolution of Todo - Spec-Driven, Cloud-Native AI Application (Phase I)"
requires-python = ">=3.13"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
# UV-specific configuration (if needed)
```

**Key Decisions**:
- Empty `dependencies = []` for Phase I (only standard library)
- `requires-python = ">=3.13"` enforces minimum Python version
- Minimal build system configuration (hatchling is lightweight)

### File: `.python-version`

**Purpose**: Specify Python version for `uv` and other tools

**Content**:
```
3.13
```

### File: `README.md`

**Purpose**: Project overview and quick setup instructions

**Content Outline**:
1. Project description (reference to Constitution and spec-driven approach)
2. Quick Start (link to `specs/001-env-setup/quickstart.md`)
3. Project structure overview
4. Contributing guidelines (reference to spec-driven workflow)
5. License information (if applicable)

### File: `.gitignore`

**Purpose**: Exclude virtual environment and Python artifacts from version control

**Content**:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
.venv/
venv/
ENV/
env/

# UV
.uv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### Setup Commands

**Documentation for `quickstart.md`**:

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

3. **Activate virtual environment**:
   ```bash
   # macOS/Linux
   source .venv/bin/activate

   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1

   # Windows (CMD)
   .venv\Scripts\activate.bat
   ```

4. **Verify Python version**:
   ```bash
   python --version  # Should show 3.13+
   ```

5. **Install dependencies** (none for Phase I, but command for future):
   ```bash
   uv pip install -e .
   ```

### Validation Steps

After setup, developers should verify:
- ✅ Virtual environment directory `.venv/` exists
- ✅ Python version is 3.13 or higher
- ✅ Environment activates without errors
- ✅ Standard library modules are available (typing, dataclasses, uuid, datetime)

---

## Phase 3: Post-Design Constitution Re-Check

**Re-evaluation after design decisions**:

### Principle I: Spec-Driven Development First
✅ **PASS** - All design decisions align with specification requirements

### Principle VII: Infrastructure as Declarative and Reproducible
✅ **PASS** - `pyproject.toml` is declarative; `uv` commands are reproducible

**Overall Re-Check Result**: ✅ **PASSED** - Design maintains constitutional compliance

---

## Success Criteria Mapping

Mapping spec success criteria to implementation:

- **SC-001** (Setup in <5 min): 4-step process (install uv, create venv, activate, verify)
- **SC-002** (Cross-platform): Commands documented for Windows/macOS/Linux
- **SC-003** (100% consistency): Declarative `pyproject.toml` ensures identical environments
- **SC-004** (First-attempt success): Clear error messages and troubleshooting section in quickstart.md
- **SC-005** (No external deps): `dependencies = []` in pyproject.toml
- **SC-006** (Complete docs): quickstart.md provides step-by-step instructions

---

## Risks and Mitigations

**Risk**: Developer lacks `uv` installation
**Mitigation**: quickstart.md includes installation instructions for all platforms

**Risk**: Python 3.13+ not available
**Mitigation**: quickstart.md links to Python.org download page and version check command

**Risk**: Virtual environment conflicts
**Mitigation**: Standard `.venv/` directory name; clear in `.gitignore`

**Risk**: Silent setup failures
**Mitigation**: Verification steps included in quickstart.md

---

## Next Steps

After this plan is approved:

1. ✅ Generate `research.md` (Phase 0)
2. ✅ Generate `quickstart.md` (Phase 1)
3. ✅ Update agent context (Phase 1)
4. Run `/sp.tasks` to generate implementation task list
5. Run `/sp.implement` to execute tasks and create configuration files
