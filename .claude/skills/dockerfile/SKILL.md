# Dockerfile Generator

**Critical for Phases:** IV, V

Generates optimized multi-stage Dockerfiles for containerization.

## Usage

```
/gen.dockerfile <app-type> <dependencies>

# Examples:
/gen.dockerfile "nextjs" "Next.js 15, React 18, TypeScript"
/gen.dockerfile "fastapi" "FastAPI, Python 3.13, SQLModel"
/gen.dockerfile "postgres" "PostgreSQL 15, Alpine"
```

## What It Generates

- Multi-stage Dockerfiles for smaller images
- Production-ready configuration
- Health check endpoints
- Non-root user security
- Environment variable support
- .dockerignore for optimal builds
- Docker Compose for local development

## Output Structure

```
phase-XX/
  ├── frontend/
  │   ├── Dockerfile          # Multi-stage Next.js build
  │   ├── .dockerignore       # Exclude unnecessary files
  │   └── docker-compose.yml # Local dev
  └── backend/
      ├── Dockerfile          # Multi-stage FastAPI build
      ├── .dockerignore       # Exclude unnecessary files
      └── docker-compose.yml # Local dev
```

## Features

- Multi-stage builds for smaller images
- Non-root user for security
- Layer caching for faster builds
- Health check endpoints
- Alpine variants for minimal footprint
- Production and development variants
- Proper signal handling
- Dependency caching
- Security scanning ready

## Phase Usage

- **Phase IV:** Frontend and backend containers
- **Phase IV:** PostgreSQL container
- **Phase V:** Multi-service containers (Kafka, Dapr)
- **Phase V:** Optimized production images

## Example Outputs

### Next.js Dockerfile (Frontend)
```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy built artifacts
COPY --from=builder --chown=nodejs:nodejs /app/.next ./.next
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./package.json
COPY --from=builder --chown=nodejs:nodejs /app/public ./public

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node --eval "require('http').get('http://localhost:3000', (r) => {if(r.statusCode !== 200) throw new Error(r.statusCode)})"

# Switch to non-root user
USER nodejs

# Start Next.js
CMD ["npm", "start"]
```

### FastAPI Dockerfile (Backend)
```dockerfile
# Base image
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN groupadd -r fastapi && useradd -r -g fastapi fastapi

# Copy application code
COPY --chown=fastapi:fastapi . .

# Switch to non-root user
USER fastapi

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Start FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### PostgreSQL Dockerfile (Database)
```dockerfile
FROM postgres:15-alpine

# Create non-root user
RUN groupadd -r postgres && useradd -r -g postgres postgres

# Create data directory
RUN mkdir -p /var/lib/postgresql/data && \
    chown -R postgres:postgres /var/lib/postgresql/data

# Expose port
EXPOSE 5432

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD pg_isready -U postgres

# Switch to non-root user
USER postgres

VOLUME ["/var/lib/postgresql/data"]
```

## .dockerignore

```
# Dependencies
node_modules
__pycache__
*.pyc
*.pyo
*.pyd

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode
.idea
.git

# Build artifacts
.next
dist
build
.pytest_cache

# OS
.DS_Store
Thumbs.db
```

## Docker Compose (Local Development)

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://todo:password@postgres:5432/todo
      - JWT_SECRET=your-secret-key
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=todo
      - POSTGRES_USER=todo
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## Docker Compose Commands

```bash
# Build and start all services
docker-compose up -d

# Build specific service
docker-compose build backend

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Execute command in container
docker-compose exec backend python -m pytest
```

## Production Build Commands

```bash
# Build image
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Tag for registry
docker tag todo-backend:latest your-registry/todo-backend:v1.0.0
docker tag todo-frontend:latest your-registry/todo-frontend:v1.0.0

# Push to registry
docker push your-registry/todo-backend:v1.0.0
docker push your-registry/todo-frontend:v1.0.0

# Run container
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  todo-backend:latest
```

## Optimization Techniques

1. **Layer Caching**: Order COPY commands by change frequency
2. **Multi-stage Builds**: Separate build and runtime stages
3. **Alpine Variants**: Use Alpine for minimal image size
4. **.dockerignore**: Exclude unnecessary files
5. **Combine RUN Commands**: Reduce layers with && chaining
6. **Non-root User**: Security best practice
7. **Health Checks**: Enable Kubernetes readiness probes
8. **Specific Versions**: Pin base images for reproducibility

## Image Size Benchmarks

| Service | Optimized | Unoptimized | Reduction |
|----------|-----------|---------------|------------|
| Next.js | ~150MB | ~500MB | 70% |
| FastAPI | ~120MB | ~300MB | 60% |
| PostgreSQL | ~200MB | ~300MB | 33% |

## Security Best Practices

- Always use non-root users
- Scan images for vulnerabilities (trivy, docker scout)
- Don't include secrets in images
- Use specific image versions (no `latest` tag in prod)
- Minimal attack surface (only required packages)
- Regular base image updates
- Signed images (if using registry)
