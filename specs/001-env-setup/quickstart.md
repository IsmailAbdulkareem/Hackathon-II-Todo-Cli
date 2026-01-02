# Quick Start: Environment Setup

**Feature**: Phase I – Environment & Package Setup
**Purpose**: Step-by-step guide to set up the Python 3.13+ development environment
**Estimated Time**: 5 minutes

---

## Prerequisites

Before starting, ensure you have:

1. **Python 3.13 or higher** installed on your system
   - Check version: `python --version` or `python3 --version`
   - If not installed: [Download Python 3.13+](https://www.python.org/downloads/)

2. **`uv` package manager** installed
   - Check if installed: `uv --version`
   - If not installed, see [Installation](#step-1-install-uv) below

---

## Step 1: Install UV

If you don't have `uv` installed, follow the platform-specific instructions:

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, restart your terminal or run:

```bash
source $HOME/.cargo/env
```

### Windows (PowerShell)

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, restart PowerShell.

### Verify Installation

```bash
uv --version
```

Expected output: `uv 0.x.x` (version number may vary)

---

## Step 2: Clone the Repository

If you haven't already cloned the repository:

```bash
git clone <repository-url>
cd "Hackathon II - Todo Spec-Driven Development"
```

---

## Step 3: Create Virtual Environment

From the project root directory, run:

```bash
uv venv
```

Expected output:
```
Using Python 3.13.x
Creating virtual environment at .venv
```

**Note**: This creates a `.venv/` directory in your project root. This directory is ignored by Git.

---

## Step 4: Activate Virtual Environment

Choose the command appropriate for your platform and shell:

### macOS / Linux (bash/zsh)

```bash
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

### Windows (Command Prompt)

```cmd
.venv\Scripts\activate.bat
```

### Windows (Git Bash)

```bash
source .venv/Scripts/activate
```

**Success Indicator**: Your command prompt should now show `(.venv)` prefix:

```
(.venv) user@machine:~/project$
```

---

## Step 5: Verify Python Version

After activating the environment, verify Python version:

```bash
python --version
```

Expected output:
```
Python 3.13.x
```

**Important**: Within the activated environment, always use `python` (not `python3`) for consistency.

---

## Step 6: Verify Standard Library Modules

Phase I relies solely on Python's standard library. Verify access to required modules:

```bash
python -c "import typing, dataclasses, uuid, datetime; print('All standard library modules available')"
```

Expected output:
```
All standard library modules available
```

---

## Step 7: (Future Phases) Install Dependencies

**Note**: Phase I has no external dependencies. For future phases, when dependencies are added:

```bash
uv pip install -e .
```

This installs the project in editable mode along with any dependencies defined in `pyproject.toml`.

---

## Troubleshooting

### Issue: `uv: command not found`

**Cause**: `uv` is not installed or not in your PATH.

**Solution**:
1. Verify installation: `which uv` (Unix) or `where uv` (Windows)
2. If not installed, follow [Step 1: Install UV](#step-1-install-uv)
3. If installed but not found, add to PATH:
   - **Unix**: Add `export PATH="$HOME/.cargo/bin:$PATH"` to `~/.bashrc` or `~/.zshrc`
   - **Windows**: Add `%USERPROFILE%\.cargo\bin` to system PATH

### Issue: `No such version: 3.13`

**Cause**: Python 3.13+ is not installed on your system.

**Solution**:
1. Download and install Python 3.13+ from [python.org](https://www.python.org/downloads/)
2. Verify installation: `python3.13 --version`
3. Retry `uv venv`

### Issue: Virtual environment already exists

**Cause**: `.venv/` directory already exists from previous setup attempt.

**Solution**:
1. Delete existing environment: `rm -rf .venv` (Unix) or `rmdir /s .venv` (Windows)
2. Recreate: `uv venv`

### Issue: Permission denied errors

**Cause**: Attempting to create virtual environment in protected directory.

**Solution**:
1. Verify you have write permissions in the project directory
2. Do NOT use `sudo` or run as administrator (unnecessary for virtual environments)
3. If issues persist, check directory ownership: `ls -la` (Unix)

### Issue: Activation script not found

**Cause**: Virtual environment was not created successfully.

**Solution**:
1. Verify `.venv/` directory exists: `ls -la .venv` (Unix) or `dir .venv` (Windows)
2. If missing, recreate: `uv venv`
3. Check for error messages during creation

### Issue: Python version mismatch after activation

**Cause**: Multiple Python installations; `uv` selected wrong version.

**Solution**:
1. Specify Python explicitly: `uv venv --python 3.13`
2. Or use full path: `uv venv --python /path/to/python3.13`

---

## Verification Checklist

After completing setup, verify:

- [ ] `uv --version` shows installed version
- [ ] `.venv/` directory exists in project root
- [ ] Virtual environment activates without errors
- [ ] Command prompt shows `(.venv)` prefix when activated
- [ ] `python --version` returns `3.13.x` or higher
- [ ] Standard library modules (typing, dataclasses, uuid, datetime) import successfully
- [ ] No external packages installed: `pip list` shows only `pip`, `setuptools`, `wheel`

**All checks passed?** ✅ You're ready to proceed with Phase I development!

---

## Deactivating the Environment

When finished working, deactivate the virtual environment:

```bash
deactivate
```

Your command prompt prefix `(.venv)` will disappear, indicating you're back in the system Python environment.

---

## Next Steps

With your environment set up, you can now:

1. Review the project constitution: `.specify/memory/constitution.md`
2. Explore feature specifications: `specs/001-env-setup/spec.md`
3. Read the implementation plan: `specs/001-env-setup/plan.md`
4. Wait for Phase II specifications to begin application development

**Important**: Phase I focuses solely on environment setup. No application code (models, services, CLI) will be created until Phase II specifications are defined.

---

## Additional Resources

- **UV Documentation**: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
- **Python 3.13 Release Notes**: [https://docs.python.org/3.13/whatsnew/3.13.html](https://docs.python.org/3.13/whatsnew/3.13.html)
- **Virtual Environments Guide**: [https://docs.python.org/3/tutorial/venv.html](https://docs.python.org/3/tutorial/venv.html)
- **Project Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)

---

**Questions or Issues?**

If you encounter problems not covered in the troubleshooting section:

1. Check that all prerequisites are met
2. Review error messages carefully (often contain solution hints)
3. Verify you're running commands from the project root directory
4. Consult UV documentation for advanced troubleshooting
