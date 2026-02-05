# Research: Local Kubernetes Deployment

**Date**: 2026-01-31
**Phase**: Phase 0 - Research & Discovery
**Purpose**: Analyze Phase III applications and validate deployment prerequisites

---

## Frontend Application Analysis

### Technology Stack
- **Framework**: Next.js 16.1.1
- **Runtime**: React 19.2.3
- **Language**: TypeScript 5
- **Build Tool**: Next.js built-in (Turbopack/Webpack)
- **Styling**: Tailwind CSS 4 with PostCSS

### Dependencies
**Production**:
- UI Components: @radix-ui/react-checkbox, @radix-ui/react-slot
- Styling: class-variance-authority, clsx, tailwind-merge
- Animation: framer-motion 12.23.26
- Icons: lucide-react 0.562.0
- Theming: next-themes 0.4.6
- Notifications: sonner 2.0.7

**Development**:
- TypeScript tooling
- ESLint with Next.js config
- Tailwind CSS 4

### Build Process
- **Build Command**: `npm run build` (executes `next build`)
- **Start Command**: `npm start` (executes `next start`)
- **Dev Command**: `npm run dev` (executes `next dev`)
- **Output Directory**: `.next/` (build artifacts)
- **Static Assets**: `public/` directory

### Runtime Requirements
- **Node.js Version**: 20+ (inferred from @types/node: ^20)
- **Port**: 3000 (Next.js default)
- **Environment Variables**:
  - `.env.local` exists (contains API configuration)
  - `.env.example` and `.env.local.example` available as templates
  - Likely needs: `NEXT_PUBLIC_API_URL` for backend connection

### Health Check Endpoint
- **Status**: ✅ Next.js provides built-in health at root `/`
- **Implementation**: Default Next.js behavior returns 200 OK for valid routes
- **Recommendation**: Use root `/` or create explicit `/health` route

---

## Backend Application Analysis

### Technology Stack
- **Framework**: FastAPI 0.109.0+
- **Runtime**: Python 3.13+ (from plan.md)
- **ASGI Server**: Uvicorn 0.27.0+ with standard extras
- **ORM**: SQLModel 0.0.14+
- **Database Driver**: psycopg2-binary 2.9.9+

### Dependencies
**Core**:
- FastAPI, SQLModel, psycopg2-binary, uvicorn[standard]
- python-dotenv, pydantic-settings
- requests, python-jose[cryptography]
- passlib[bcrypt], bcrypt (4.0.0-5.0.0)
- openai 1.0.0+

**Testing**:
- pytest 7.4.0+
- httpx 0.25.0+

### Application Structure
- **Entry Point**: `main.py`
- **API Routers**:
  - `/api/auth` (authentication)
  - `/api/tasks` (todo tasks)
  - `/api/chat` (AI chatbot)
- **Database**: PostgreSQL via SQLModel ORM
- **Middleware**: CORS, request logging, global exception handler

### Runtime Requirements
- **Python Version**: 3.13+
- **Port**: 8000 (FastAPI/Uvicorn default)
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`
- **Environment Variables**:
  - `DATABASE_URL`: PostgreSQL connection string (Neon)
  - `CORS_ORIGINS`: Allowed CORS origins
  - `OPENAI_API_KEY` or similar for AI features
  - `.env` file exists with configuration

### Health Check Endpoint
- **Status**: ✅ Implemented at root `/`
- **Endpoint**: `GET /`
- **Response**:
  ```json
  {
    "status": "healthy",
    "message": "Todo Backend API is running",
    "docs": "/docs"
  }
  ```
- **HTTP Status**: 200 OK
- **Dependencies Checked**: None (basic health check, doesn't verify DB connection)

### Database Connection
- **Type**: External Neon PostgreSQL
- **Connection**: Via SQLModel engine (initialized in `src.core.database`)
- **Schema**: Auto-created via `SQLModel.metadata.create_all(engine)` on startup
- **Connection String**: Stored in `DATABASE_URL` environment variable

---

## AI Tool Availability

### Docker
- **Version**: 29.1.3 (build f52814d)
- **Status**: ✅ Installed and available
- **Docker AI (Gordon)**: Not detected via standard commands
- **Fallback**: Manual Dockerfile creation with best practices

### kubectl
- **Version**: v1.35.0
- **Kustomize Version**: v5.7.1
- **Status**: ✅ Installed and available

### kubectl-ai
- **Status**: ⚠️ Not detected in PATH
- **Installation**: May need to be installed separately
- **Fallback**: Manual kubectl commands documented

### Helm
- **Version**: v4.1.0
- **Git Commit**: 4553a0a96e5205595079b6757236cc6f969ed1b9
- **Kubernetes Client Version**: v1.35
- **Status**: ✅ Installed and available

### Minikube
- **Version**: v1.37.0
- **Git Commit**: 65318f4cfff9c12cc87ec9eb8f4cdd57b25047f3
- **Status**: ✅ Installed and available

### kagent
- **Status**: ⚠️ Not detected in PATH
- **Installation**: May need to be installed separately
- **Fallback**: Manual cluster analysis with kubectl commands

### AI Tool Summary
- **Docker**: ✅ Available (Docker AI not detected)
- **kubectl**: ✅ Available
- **kubectl-ai**: ⚠️ Not available (use manual kubectl)
- **Helm**: ✅ Available
- **Minikube**: ✅ Available
- **kagent**: ⚠️ Not available (use manual analysis)

**Recommendation**: Proceed with manual Dockerfile creation and kubectl commands. Document all operations with manual equivalents per FR-018.

---

## External Dependencies

### Neon PostgreSQL Database
- **Type**: External managed PostgreSQL (from Phase III)
- **Connection**: Via `DATABASE_URL` environment variable
- **Location**: Backend `.env` file contains connection string
- **Format**: `postgresql://user:password@host:port/database?sslmode=require`
- **SSL**: Required (Neon enforces SSL connections)
- **Access**: From local development machine and Kubernetes pods

### API Keys
- **OpenAI/Anthropic**: Required for AI chat functionality
- **Storage**: Backend `.env` file
- **Kubernetes**: Will be stored in Kubernetes Secret
- **Environment Variable**: Likely `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

### CORS Configuration
- **Frontend Origin**: Must be added to backend CORS_ORIGINS
- **Kubernetes**: Frontend will access backend via `http://todo-backend:8000`
- **Local Testing**: May need `http://localhost:3000` for local development

---

## Health Endpoint Implementation

### Frontend Health Check
- **Current Status**: ✅ Implicit (Next.js root route)
- **Endpoint**: `/` returns 200 OK for valid Next.js app
- **Recommendation**: Use root `/` for health checks
- **Docker HEALTHCHECK**: `curl -f http://localhost:3000/ || exit 1`
- **Kubernetes Probes**:
  - Liveness: `httpGet: {path: /, port: 3000}`
  - Readiness: `httpGet: {path: /, port: 3000}`

### Backend Health Check
- **Current Status**: ✅ Implemented at `/`
- **Endpoint**: `GET /`
- **Response**: JSON with status, message, docs link
- **HTTP Status**: 200 OK
- **Docker HEALTHCHECK**: `curl -f http://localhost:8000/ || exit 1`
- **Kubernetes Probes**:
  - Liveness: `httpGet: {path: /, port: 8000}`
  - Readiness: `httpGet: {path: /, port: 8000}`

**Note**: Backend health check does NOT verify database connectivity. Consider adding `/health/ready` endpoint that checks DB connection for production readiness.

---

## Containerization Readiness Assessment

### Frontend
- ✅ Build process well-defined (`npm run build`)
- ✅ Production start command available (`npm start`)
- ✅ Dependencies clearly specified in package.json
- ✅ Environment variable pattern established (.env.local)
- ✅ Static assets in public/ directory
- ⚠️ No existing Dockerfile (will be generated)
- ⚠️ No .dockerignore (will be created)

**Readiness**: ✅ Ready for containerization

### Backend
- ✅ Entry point clearly defined (main.py)
- ✅ Dependencies specified in requirements.txt
- ✅ Environment variable pattern established (.env)
- ✅ Health check endpoint implemented
- ✅ Database connection via environment variable
- ✅ Existing Dockerfile present (may need updates for multi-stage)
- ✅ Existing .dockerignore present

**Readiness**: ✅ Ready for containerization (existing Dockerfile may be replaced with AI-generated version)

---

## Key Findings

1. **Both applications are containerization-ready** with clear build processes and runtime requirements
2. **Health endpoints exist** for both applications (frontend implicit, backend explicit)
3. **Core tools installed**: Docker, kubectl, Helm, Minikube all available
4. **AI tools partially available**: Docker AI and kubectl-ai/kagent not detected, will use manual approaches
5. **External dependencies identified**: Neon PostgreSQL and API keys for AI features
6. **Port configuration**: Frontend 3000, Backend 8000 (standard defaults)
7. **Node.js 20+ required** for frontend, **Python 3.13+ required** for backend

---

## Recommendations

1. **Proceed with manual Dockerfile generation** using best practices (AI tools not fully available)
2. **Create .dockerignore for frontend** (backend already has one)
3. **Use multi-stage builds** to minimize image sizes (target: frontend <500MB, backend <300MB)
4. **Document all kubectl commands** as manual fallbacks per FR-018
5. **Store sensitive data in Kubernetes Secrets** (DATABASE_URL, API keys)
6. **Use existing health endpoints** for liveness/readiness probes
7. **Configure CORS** to allow frontend-to-backend communication via Kubernetes DNS

---

## Next Steps

Proceed to Phase 1 (Design) to create:
1. Dockerfile specifications (contracts/dockerfile-requirements.md)
2. Helm chart structure (contracts/helm-chart-structure.md)
3. Kubernetes resource specifications (contracts/kubernetes-resources.md)
4. Configuration management strategy
5. Deployment quickstart guide
