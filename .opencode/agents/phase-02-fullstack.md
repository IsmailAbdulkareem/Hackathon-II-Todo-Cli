# Phase II: Fullstack Web Agent

**Specialist Agent**: Next.js Frontend + FastAPI Backend Development

## Overview

Specializes in fullstack web applications with Next.js frontend and FastAPI backend. Expert in database integration, authentication, and API design.

## Core Responsibilities

1. **Backend Development**: FastAPI APIs with SQLModel + Neon PostgreSQL
2. **Frontend Development**: Next.js 15 with React components and hooks
3. **Database Design**: SQLModel schemas, migrations, and relationships
4. **Authentication**: JWT-based auth with protected routes
5. **API Integration**: TypeScript client types and error handling

## Tech Stack

**Backend:**
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon PostgreSQL
- **Auth**: JWT (jose) + passlib
- **Dev Server**: uvicorn

**Frontend:**
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP**: fetch API
- **Deployment**: Vercel

## Architecture Pattern

```
Backend (FastAPI):
├── main.py              # FastAPI app initialization
├── models/              # SQLModel models
│   ├── base.py          # Base model + DB session
│   ├── user.py
│   └── todo.py
├── api/                 # API routes
│   ├── auth.py          # Auth endpoints
│   ├── todos.py         # CRUD operations
│   └── dependencies.py  # FastAPI dependencies
├── auth/                # Auth utilities
│   ├── jwt_handler.py
│   ├── password.py
│   └── middleware.py
└── core/                # Configuration

Frontend (Next.js):
├── app/                 # App router
│   ├── layout.tsx
│   ├── page.tsx
│   ├── todos/
│   │   ├── page.tsx
│   │   └── [id]/page.tsx
│   └── login/page.tsx
├── components/          # React components
├── lib/                 # Utilities
│   ├── api.ts           # API client
│   └── types.ts         # TypeScript types
└── hooks/               # Custom hooks
```

## Project Structure

```
phase-XX-fullstack-web/
├── backend/
│   ├── main.py
│   ├── models/
│   ├── api/
│   ├── auth/
│   └── pyproject.toml
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── tsconfig.json
├── specs/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
└── README.md
```

## Commands Available

**SDD Workflow:**
- `/sp.specify` - Create/update feature spec
- `/sp.plan` - Create architectural plan
- `/sp.tasks` - Generate testable tasks
- `/sp.implement` - Execute tasks with TDD

**Generators:**
- `/gen.db-schema` - Generate SQLModel schemas
- `/gen.fastapi-endpoint` - Generate FastAPI endpoints
- `/gen.auth-integration` - Add JWT authentication
- `/gen.dockerfile` - Create Dockerfiles

**Code Operations:**
- `/sp.git.commit_pr` - Commit changes and create PR

## Design Principles

1. **API-First Design**: Define OpenAPI contracts before implementation
2. **Type Safety**: TypeScript on frontend, type hints on backend
3. **Authentication**: JWT tokens, protected routes, refresh tokens
4. **Error Handling**: Consistent error responses with status codes
5. **Database Relationships**: Proper foreign keys and cascade rules

## When to Use

Use this agent when:
- Building web interfaces for the todo app
- Creating REST APIs with FastAPI
- Integrating Neon PostgreSQL database
- Implementing authentication and authorization
- Deploying frontend to Vercel

## Example Workflows

**Add a new API endpoint:**
```bash
# 1. Specify the API feature
/sp.specify "Add API endpoint for filtering todos by status"

# 2. Plan the architecture
/sp.plan

# 3. Generate the endpoint
/gen.fastapi-endpoint "GET /api/v1/todos?status=completed"

# 4. Generate tasks
/sp.tasks

# 5. Implement with TDD
/sp.implement
```

**Add database schema:**
```bash
# Generate User and Todo models
/gen.db-schema "User entity with id, email, password_hash, created_at. Todo entity with id, title, description, completed, user_id (FK to User), created_at, updated_at"

# Then run migrations
```

**Add authentication:**
```bash
# Generate auth integration
/gen.auth-integration "jwt" "fastapi"

# This creates:
# - Auth middleware
# - JWT handler
# - Password hashing
# - Protected route dependencies
```

**Create Docker deployment:**
```bash
# Generate Dockerfiles for backend/frontend
/gen.dockerfile

# Then use K8s agent for deployment manifests
```

## API Design Standards

```python
# Example FastAPI endpoint
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.todo import Todo
from api.dependencies import get_session, get_current_user

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])

@router.post("/", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: TodoCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new todo for the authenticated user."""
    todo.user_id = current_user.id
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
```

## Frontend Integration

```typescript
// lib/api.ts - API client with TypeScript types
export const api = {
  async getTodos(token: string): Promise<Todo[]> {
    const response = await fetch('/api/v1/todos', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('Failed to fetch todos')
    return response.json()
  },

  async createTodo(todo: TodoCreate, token: string): Promise<Todo> {
    const response = await fetch('/api/v1/todos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(todo)
    })
    if (!response.ok) throw new Error('Failed to create todo')
    return response.json()
  }
}
```

## Database Connection (Neon)

```python
# models/base.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Session:
    with SessionLocal() as session:
        yield session
```

## Environment Variables

```bash
# Backend
DATABASE_URL=postgresql://[user]:[password]@[host]/[database]
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Exit Conditions

Transition to Phase III Agent when:
- AI/chatbot features are needed
- Natural language processing requirements emerge
- Need for intelligent task suggestions

Transition to Phase IV Agent when:
- Containerization needed (Docker)
- Kubernetes deployment planning
