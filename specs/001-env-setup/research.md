# Research: UV Package Manager Best Practices

**Feature**: Phase I – Environment & Package Setup
**Date**: 2025-12-28
**Purpose**: Research `uv` best practices for Python 3.13+ environment setup

## Executive Summary

This research document consolidates findings on using `uv` (Astral's fast Python package manager) for creating reproducible, cross-platform development environments. Key findings support the technical decisions documented in `plan.md`.

---

## Research Question 1: Recommended `pyproject.toml` Structure

### Decision

Use PEP 621 compliant `pyproject.toml` with minimal configuration:

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
```

### Rationale

- **PEP 621 Compliance**: `uv` fully supports PEP 621 project metadata standard
- **Minimal Build System**: Hatchling is lightweight, pure-Python, and works seamlessly with `uv`
- **Empty Dependencies**: Explicitly listing `dependencies = []` documents the Phase I constraint (no external packages)
- **Python Version Constraint**: `requires-python = ">=3.13"` enforces minimum version during environment creation

### Alternatives Considered

- **setuptools**: Heavier, legacy approach; hatchling is more modern and lighter
- **poetry-core**: Requires poetry tooling; `uv` works better with standard PEP 621
- **No build-system**: Would prevent future packaging; better to include minimal config now

---

## Research Question 2: Python Version Specification

### Decision

Use `.python-version` file containing `3.13` at repository root.

### Rationale

- **Tool Compatibility**: `.python-version` is recognized by `uv`, `pyenv`, `asdf`, and other version managers
- **Simplicity**: Single line file (`3.13`) is clear and minimal
- **Version Flexibility**: Specifying `3.13` (not `3.13.0`) allows any patch version (3.13.0, 3.13.1, etc.)
- **Combined with pyproject.toml**: `.python-version` specifies exact version; `pyproject.toml` specifies minimum

### Alternatives Considered

- **pyproject.toml only**: Does not help tools auto-select Python version
- **Hard-coding 3.13.0**: Too restrictive; patch versions should be acceptable
- **Range like 3.13-3.14**: Introduces version drift; better to be explicit

---

## Research Question 3: Standard UV Commands for Environment Creation

### Decision

Use the following command sequence:

1. **Install uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` (Windows)
2. **Create venv**: `uv venv`
3. **Activate venv**: `source .venv/bin/activate` (Unix) or `.venv\Scripts\Activate.ps1` (Windows PowerShell)
4. **Install project**: `uv pip install -e .` (for future phases with dependencies)

### Rationale

- **uv venv**: Creates virtual environment in `.venv/` by default (standard convention)
- **Cross-platform activation**: Different shells require different activation scripts; documentation must cover all
- **Editable install**: `-e` flag (editable mode) allows development without reinstalling after code changes
- **Fast execution**: `uv` is 10-100x faster than `pip` for most operations

### Platform-Specific Activation

| Platform | Shell | Command |
|----------|-------|---------|
| macOS/Linux | bash/zsh | `source .venv/bin/activate` |
| Windows | PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows | CMD | `.venv\Scripts\activate.bat` |
| Windows | Git Bash | `source .venv/Scripts/activate` |

### Alternatives Considered

- **python -m venv**: Slower, less feature-rich than `uv venv`
- **virtualenv**: Third-party tool; adds unnecessary dependency
- **conda**: Heavy, complex, designed for scientific computing (overkill for Phase I)

---

## Research Question 4: `.gitignore` Configuration

### Decision

Include comprehensive Python and `uv`-specific patterns:

```gitignore
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

### Rationale

- **Virtual Environment**: `.venv/` is the default `uv` venv directory and must be ignored
- **Python Artifacts**: Compiled bytecode (`__pycache__`, `*.pyc`) should never be committed
- **UV Cache**: `.uv/` stores `uv`'s local cache and should be ignored
- **IDE/OS Files**: Prevent platform-specific files from polluting the repository

### Alternatives Considered

- **Minimal .gitignore**: Risked committing environment or cache files
- **Python.gitignore template**: Too broad for Phase I; our version is tailored to project needs

---

## Research Question 5: Virtual Environment Directory Name

### Decision

Use `.venv/` (with leading dot) as the virtual environment directory name.

### Rationale

- **UV Default**: `uv venv` creates `.venv/` by default
- **Hidden Directory**: Leading dot hides directory in Unix file browsers (cleaner workspace)
- **Standard Convention**: Most modern Python projects use `.venv/` over `venv/`
- **Tool Recognition**: IDEs (VS Code, PyCharm) automatically detect `.venv/`

### Alternatives Considered

- **venv/**: No leading dot; more visible but non-standard for `uv`
- **Custom name**: Would require `uv venv <name>` in documentation; adds complexity
- **.env/**: Conflicts with common environment variable file naming

---

## Additional Best Practices

### Environment Isolation

- Always activate the virtual environment before running Python commands
- Use `python` (not `python3`) within activated environment for consistency
- Verify Python version after activation: `python --version`

### Dependency Management

For future phases with external dependencies:

1. Add to `pyproject.toml` under `[project] dependencies = [...]`
2. Run `uv pip sync` to install exact dependencies
3. Consider `uv pip compile` for generating lock files (if dependency pinning needed)

### Error Handling

Common setup issues and solutions:

| Issue | Symptom | Solution |
|-------|---------|----------|
| `uv` not found | `command not found: uv` | Install `uv` or add to PATH |
| Python 3.13+ unavailable | `No such version: 3.13` | Install Python 3.13+ from python.org |
| Permission denied | `Permission denied` error | Run without `sudo`; check directory permissions |
| Existing venv conflict | Environment already exists | Delete `.venv/` and recreate |

### Performance Considerations

- **UV Speed**: Environment creation typically completes in <10 seconds
- **Cache Benefits**: `uv` caches packages in `~/.cache/uv/` (Unix) or `%LOCALAPPDATA%\uv\cache` (Windows)
- **Offline Mode**: Once cached, `uv` can operate offline for repeated installs

---

## Conclusions

Research confirms that `uv` is well-suited for Phase I requirements:

✅ Supports Python 3.13+ with version enforcement
✅ Creates reproducible environments via `pyproject.toml`
✅ Works cross-platform (Windows, macOS, Linux)
✅ Fast environment creation (<2 minutes target easily met)
✅ Standard conventions (`.venv/`, PEP 621) align with Python ecosystem best practices

**Recommendation**: Proceed with implementation plan as defined in `plan.md`. No changes to technical approach required based on research findings.

---

## References

- UV Documentation: https://github.com/astral-sh/uv
- PEP 621 (Project Metadata): https://peps.python.org/pep-0621/
- Python Packaging User Guide: https://packaging.python.org/
- Hatchling Build Backend: https://hatch.pypa.io/latest/
