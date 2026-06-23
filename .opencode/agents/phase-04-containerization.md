# Phase IV: Containerization Agent

**Specialist Agent**: Docker Container Design and Multi-Service Setup

## Overview

Defines Dockerfile standards, creates multi-service container setups, and ensures environment parity across development, testing, and production environments.

## Core Responsibilities

1. **Dockerfile Standards**: Create optimized Dockerfiles for each service
2. **Multi-Service Setup**: Docker Compose orchestration for all services
3. **Environment Parity**: Consistent environments across dev/staging/prod
4. **Image Optimization**: Multi-stage builds, caching, and layer optimization

## Tech Stack

- **Container Runtime**: Docker
- **Orchestration**: Docker Compose
- **Registry**: Docker Hub / GitHub Container Registry
- **Base Images**: Python Slim, Node Alpine

## Commands Available

- `/sp.specify` - Define containerization requirements
- `/sp.plan` - Plan container strategy
- `/gen.dockerfile` - Generate optimized Dockerfiles

## Dockerfile Standards

### Backend Dockerfile (FastAPI)

```dockerfile
# Multi-stage build for Python backend

# Stage 1: Builder
FROM python:3.13-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir --user -r <(pip-compile pyproject.toml)

# Stage 2: Runtime
FROM python:3.13-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Set PATH
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run as non-root user
USER appuser

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile (Next.js)

```dockerfile
# Multi-stage build for Next.js frontend

# Stage 1: Builder
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production=false

# Copy application code
COPY . .

# Build application
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine

WORKDIR /app

# Install production dependencies only
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start application
CMD ["npm", "start"]
```

### Database Migrations Dockerfile

```dockerfile
# One-off migration runner

FROM python:3.13-slim as migrations

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -r <(pip-compile pyproject.toml)

# Copy migration scripts
COPY ./migrations ./migrations
COPY ./models ./models

# Run migrations
CMD ["alembic", "upgrade", "head"]
```

## Docker Compose Multi-Service Setup

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:16-alpine
    container_name: todo-db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-todo}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password}
      POSTGRES_DB: ${POSTGRES_DB:-todoapp}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-todo}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - todo-network

  # Redis for caching (optional)
  redis:
    image: redis:7-alpine
    container_name: todo-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - todo-network

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: todo-backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-todo}:${POSTGRES_PASSWORD:-password}@db:5432/${POSTGRES_DB:-todoapp}
      JWT_SECRET: ${JWT_SECRET}
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app  # For hot reload in development
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - todo-network

  # Next.js Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: todo-frontend
    environment:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8000}
    depends_on:
      backend:
        condition: service_healthy
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app  # For hot reload in development
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - todo-network

  # Migrations (run once)
  migrations:
    build:
      context: ./backend
      dockerfile: Dockerfile.migrations
    container_name: todo-migrations
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-todo}:${POSTGRES_PASSWORD:-password}@db:5432/${POSTGRES_DB:-todoapp}
    depends_on:
      db:
        condition: service_healthy
    networks:
      - todo-network
    profiles:
      - migration

volumes:
  postgres_data:

networks:
  todo-network:
    driver: bridge
```

## Environment Configuration

### .env File

```bash
# Database
POSTGRES_USER=todo
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=todoapp

# Backend
JWT_SECRET=your_jwt_secret_key_here
DATABASE_URL=postgresql://todo:secure_password_here@db:5432/todoapp
REDIS_URL=redis://redis:6379/0

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Image Optimization Strategies

### 1. Multi-Stage Builds

```dockerfile
# Keep builder stage separate from runtime
FROM python:3.13-slim as builder
# ... build steps ...

FROM python:3.13-slim
COPY --from=builder /app /app
```

### 2. Layer Caching

```dockerfile
# Copy requirements first (changes less frequently)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code (changes frequently)
COPY . .
```

### 3. .dockerignore

```dockerfile
# .dockerignore for backend
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
.git
.gitignore
.venv
venv/
.env
*.md
.mypy_cache
.pytest_cache
.coverage
htmlcov/
```

```dockerfile
# .dockerignore for frontend
node_modules
.next
.git
.gitignore
.env*.local
npm-debug.log
yarn-error.log
.vscode
.DS_Store
```

### 4. Alpine Images

```dockerfile
# Use Alpine Linux for smaller images
FROM python:3.13-alpine  # Instead of python:3.13
FROM node:20-alpine      # Instead of node:20
```

### 5. Combine RUN Commands

```dockerfile
# Bad (multiple layers)
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y postgresql-client
RUN rm -rf /var/lib/apt/lists/*

# Good (single layer)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
```

## Environment Parity

### Development Environment

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  backend:
    volumes:
      - ./backend:/app  # Mount for hot reload
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  frontend:
    volumes:
      - ./frontend:/app  # Mount for hot reload
    command: ["npm", "run", "dev"]
```

### Production Environment

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    # No volume mounts
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

  frontend:
    # No volume mounts
    command: ["npm", "start"]
```

### Usage

```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

## Docker Commands Reference

### Building Images

```bash
# Build backend image
docker build -t todo-backend:latest ./backend

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Build with no cache
docker build --no-cache -t todo-backend:latest ./backend
```

### Running Containers

```bash
# Run with docker compose
docker compose up

# Run in background
docker compose up -d

# Build and run
docker compose up --build

# View logs
docker compose logs -f

# Stop containers
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Container Management

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View container logs
docker logs todo-backend

# Execute command in container
docker exec -it todo-backend bash

# Inspect container
docker inspect todo-backend
```

### Image Management

```bash
# List images
docker images

# Remove image
docker rmi todo-backend:latest

# Remove unused images
docker image prune

# Push to registry
docker push yourregistry/todo-backend:latest
```

## Health Checks

### Backend Health Endpoint

```python
# backend/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy", "service": "backend"}
```

### Frontend Health Page

```typescript
// frontend/app/health/page.tsx
export default function HealthPage() {
  return (
    <html>
      <head><title>Health Check</title></head>
      <body><h1>Frontend is healthy</h1></body>
    </html>
  )
}
```

## Outputs

This agent produces:

1. **Dockerfiles** - Optimized multi-stage Dockerfiles for each service
2. **Docker Compose Config** - Multi-service orchestration setup
3. **Environment Configs** - .env files and environment parity strategies
4. **.dockerignore Files** - Build optimization patterns

## Integration Points

- Works with **Kubernetes Architecture Agent** to convert Docker Compose to K8s manifests
- Works with **Deployment Validation Agent** to test container health
- Works with **Cloud Deployment Agent** for registry and production deployment

## When to Use

Use this agent when:
- Creating Dockerfiles for new services
- Setting up Docker Compose for local development
- Optimizing container image sizes
- Ensuring environment parity
- Implementing health checks
- Preparing for Kubernetes migration
