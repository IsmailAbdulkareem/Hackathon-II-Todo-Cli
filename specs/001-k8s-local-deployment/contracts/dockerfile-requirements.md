# Dockerfile Requirements

**Date**: 2026-01-31
**Purpose**: Define multi-stage Dockerfile specifications for frontend and backend applications

---

## Frontend Dockerfile Specification

### Build Strategy: Multi-Stage

**Stage 1: Dependencies**
- Base Image: `node:20-alpine`
- Purpose: Install dependencies
- Steps:
  1. Set working directory to `/app`
  2. Copy `package.json` and `package-lock.json`
  3. Run `npm ci --only=production` for production dependencies
  4. Run `npm ci` for all dependencies (including dev for build)

**Stage 2: Builder**
- Base Image: `node:20-alpine`
- Purpose: Build Next.js application
- Steps:
  1. Copy dependencies from Stage 1
  2. Copy all source code (src/, public/, config files)
  3. Copy environment files (.env.example as template)
  4. Run `npm run build` to create production build
  5. Output: `.next/` directory with optimized build

**Stage 3: Runtime**
- Base Image: `node:20-alpine`
- Purpose: Serve production application
- Steps:
  1. Set working directory to `/app`
  2. Copy `package.json` and `package-lock.json`
  3. Copy production dependencies from Stage 1
  4. Copy `.next/` build output from Stage 2
  5. Copy `public/` directory for static assets
  6. Copy `next.config.ts` for runtime configuration
  7. Expose port 3000
  8. Set environment variable `NODE_ENV=production`
  9. Add HEALTHCHECK: `curl -f http://localhost:3000/ || exit 1`
  10. CMD: `["npm", "start"]` (runs `next start`)

### Image Size Target
- **Target**: < 500MB
- **Strategy**: Use alpine base images, multi-stage builds, production-only dependencies

### Security Considerations
- ✅ No secrets baked into image
- ✅ Use .dockerignore to exclude sensitive files
- ✅ Run as non-root user (Node.js default in alpine)
- ✅ Minimal base image (alpine)

### Environment Variables
- `NEXT_PUBLIC_API_URL`: Backend API URL (injected at runtime via ConfigMap)
- `NODE_ENV`: Set to `production`
- `PORT`: Default 3000

---

## Backend Dockerfile Specification

### Build Strategy: Multi-Stage

**Stage 1: Dependencies**
- Base Image: `python:3.13-slim`
- Purpose: Install Python dependencies
- Steps:
  1. Set working directory to `/app`
  2. Install system dependencies: `curl` (for healthcheck)
  3. Copy `requirements.txt`
  4. Create virtual environment: `python -m venv /opt/venv`
  5. Activate venv and install dependencies: `pip install --no-cache-dir -r requirements.txt`

**Stage 2: Runtime**
- Base Image: `python:3.13-slim`
- Purpose: Run FastAPI application
- Steps:
  1. Set working directory to `/app`
  2. Install runtime system dependencies: `curl`, `libpq5` (PostgreSQL client)
  3. Copy virtual environment from Stage 1: `/opt/venv`
  4. Copy application code: `main.py`, `src/`, `migrations/` (if exists)
  5. Create non-root user: `appuser` (UID 1000)
  6. Change ownership of `/app` to `appuser`
  7. Switch to non-root user: `USER appuser`
  8. Set PATH to include venv: `ENV PATH="/opt/venv/bin:$PATH"`
  9. Expose port 8000
  10. Add HEALTHCHECK: `curl -f http://localhost:8000/ || exit 1`
  11. CMD: `["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`

### Image Size Target
- **Target**: < 300MB
- **Strategy**: Use slim base images, multi-stage builds, no cache in pip install, minimal system dependencies

### Security Considerations
- ✅ No secrets baked into image
- ✅ Use .dockerignore to exclude sensitive files
- ✅ Run as non-root user (`appuser`)
- ✅ Minimal base image (slim, not full Python)
- ✅ No development dependencies in final image

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (injected at runtime via Secret)
- `CORS_ORIGINS`: Allowed CORS origins (injected via ConfigMap)
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: AI service credentials (injected via Secret)
- `LOG_LEVEL`: Logging level (default: INFO)

---

## Common Dockerfile Best Practices

### Layer Optimization
1. Order layers from least to most frequently changing
2. Combine RUN commands where possible to reduce layers
3. Use `.dockerignore` to exclude unnecessary files
4. Clean up package manager caches in the same RUN command

### Health Checks
- Both images include HEALTHCHECK instructions
- Interval: 30s (default)
- Timeout: 3s (default)
- Retries: 3 (default)
- Start period: 40s (allow time for application startup)

### Labels
Add standard labels to both images:
```dockerfile
LABEL maintainer="todo-chatbot-team"
LABEL version="0.1.0"
LABEL description="Todo Chatbot [Frontend|Backend]"
```

### Build Arguments
Support build-time customization:
- Frontend: `ARG NODE_VERSION=20`
- Backend: `ARG PYTHON_VERSION=3.13`

---

## Validation Requirements

### hadolint
Both Dockerfiles must pass hadolint validation:
```bash
hadolint Dockerfile
```

Common issues to avoid:
- DL3008: Pin versions in apt-get install
- DL3013: Pin versions in pip install (use requirements.txt)
- DL3018: Pin versions in apk add
- DL3059: Multiple consecutive RUN commands
- DL4006: Set SHELL option -o pipefail

### Build Time
- Frontend: Must build in < 5 minutes (SC-001)
- Backend: Must build in < 5 minutes (SC-001)

### Image Size
- Frontend: Must be < 500MB
- Backend: Must be < 300MB

### Security Scan
- No HIGH or CRITICAL vulnerabilities in base images
- No secrets in image history: `docker history <image> | grep -i secret`

---

## .dockerignore Requirements

### Frontend .dockerignore
```
node_modules/
.next/
.git/
.env
.env.local
.env*.local
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store
Thumbs.db
coverage/
.vscode/
.idea/
*.swp
*.swo
dist/
build/
```

### Backend .dockerignore
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.env
.env.local
.venv/
venv/
ENV/
env/
.git/
.gitignore
*.log
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.DS_Store
Thumbs.db
.vscode/
.idea/
*.swp
*.swo
tests/
*.md
Dockerfile
.dockerignore
```

---

## Implementation Notes

1. **AI Tool Availability**: Docker AI not detected. Dockerfiles will be created manually following these specifications.

2. **Existing Dockerfile**: Backend has an existing Dockerfile. It should be replaced with the multi-stage version specified here for consistency and optimization.

3. **nginx Configuration**: Frontend will use Next.js standalone server (`next start`), not nginx. If nginx is needed for advanced routing, it can be added in a future iteration.

4. **Database Migrations**: Backend Dockerfile copies `migrations/` directory if it exists. Migrations should be run as a Kubernetes Job or init container, not during image build.

5. **Build Context**: Both Dockerfiles assume build context is the application directory (frontend/ or backend/), not the repository root.
