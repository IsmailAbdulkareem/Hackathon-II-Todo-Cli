# Phase II: Backend API Agent

**Specialist Agent**: FastAPI / SQLModel Backend Development

## Overview

Designs and implements RESTful APIs, defines data models with validation rules, and establishes consistent error handling conventions for the todo application backend.

## Core Responsibilities

1. **Define REST Endpoints**: Design clean, RESTful API paths and methods
2. **Data Models & Validation**: Create SQLModel models with Pydantic validation
3. **Error Handling Conventions**: Standardize error responses and status codes
4. **API Documentation**: Auto-generate OpenAPI/Swagger documentation

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (via Neon)
- **Validation**: Pydantic v2
- **Documentation**: OpenAPI 3.0 (auto-generated)

## Project Structure

```
backend/
├── main.py                  # FastAPI app initialization
├── models/                  # SQLModel database models
│   ├── base.py              # Base model + DB session
│   ├── user.py              # User model
│   └── todo.py              # Todo model
├── api/                     # API route handlers
│   ├── __init__.py
│   ├── dependencies.py      # FastAPI dependencies (auth, DB session)
│   ├── auth.py              # Auth endpoints
│   ├── todos.py             # Todo CRUD endpoints
│   └── users.py             # User profile endpoints
├── auth/                    # Authentication utilities
│   ├── jwt_handler.py       # JWT token generation/validation
│   ├── password.py          # Password hashing
│   └── middleware.py        # Auth middleware
├── exceptions/              # Custom exceptions
│   └── custom.py            # Domain-specific exceptions
├── core/                    # Configuration
│   └── config.py            # Settings and env variables
└── pyproject.toml           # Python dependencies
```

## Commands Available

- `/sp.specify` - Define API specifications
- `/sp.plan` - Plan API architecture
- `/gen.fastapi-endpoint` - Generate FastAPI endpoint code
- `/gen.db-schema` - Generate SQLModel schemas
- `/gen.auth-integration` - Add JWT authentication

## API Design Conventions

### RESTful URL Patterns

```
# Resources (plural, kebab-case)
GET    /api/v1/todos              # List todos
POST   /api/v1/todos              # Create todo
GET    /api/v1/todos/{id}         # Get specific todo
PATCH  /api/v1/todos/{id}         # Update todo
DELETE /api/v1/todos/{id}         # Delete todo

# Nested resources
GET    /api/v1/users/{id}/todos   # Get user's todos

# Auth endpoints
POST   /api/v1/auth/login         # Login
POST   /api/v1/auth/register      # Register
POST   /api/v1/auth/refresh       # Refresh token
POST   /api/v1/auth/logout       # Logout

# User profile
GET    /api/v1/users/me           # Get current user
PATCH  /api/v1/users/me          # Update profile
```

### HTTP Status Codes

```
200 OK              - Successful GET/PUT/PATCH
201 Created         - Successful POST
204 No Content      - Successful DELETE
400 Bad Request     - Validation error
401 Unauthorized    - Invalid or missing auth token
403 Forbidden       - Insufficient permissions
404 Not Found       - Resource doesn't exist
409 Conflict        - Duplicate resource
422 Unprocessable    - Validation failure
500 Internal Error  - Server error
```

## Data Models & Validation

### SQLModel Base Pattern

```python
# models/base.py
from sqlmodel import SQLModel, create_engine, Session, Field
from sqlalchemy.orm import sessionmaker
from typing import Generator
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@host/db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class BaseModel(SQLModel):
    """Base model with common fields."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TimestampMixin(SQLModel):
    """Mixin for timestamp fields."""
    updated_at: Optional[datetime] = Field(default=None)

# Database configuration
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

### Todo Model Example

```python
# models/todo.py
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime
import uuid

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TodoBase(SQLModel):
    """Base Todo fields."""
    title: str = Field(min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TodoStatus = Field(default=TodoStatus.PENDING)

class Todo(TodoBase, table=True):
    """Todo database model."""
    __tablename__ = "todos"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    user: "User" = Relationship(back_populates="todos")

# Pydantic schemas for API
class TodoCreate(TodoBase):
    """Schema for creating a todo."""
    pass

class TodoUpdate(SQLModel):
    """Schema for updating a todo (all optional)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TodoStatus] = None

class TodoRead(TodoBase):
    """Schema for reading a todo."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime]
```

## Endpoint Implementation

### Example: Todo CRUD Endpoints

```python
# api/todos.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional, List
from models.todo import Todo, TodoCreate, TodoUpdate, TodoRead
from models.base import get_session
from api.dependencies import get_current_user
from models.user import User

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])

@router.get("/", response_model=List[TodoRead])
async def list_todos(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List all todos for the authenticated user, with optional filtering."""
    query = select(Todo).where(Todo.user_id == current_user.id)

    if status:
        query = query.where(Todo.status == status)

    query = query.offset(skip).limit(limit).order_by(Todo.created_at.desc())
    todos = session.exec(query).all()
    return todos

@router.post("/", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: TodoCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new todo for the authenticated user."""
    db_todo = Todo.from_orm(todo)
    db_todo.user_id = current_user.id
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific todo by ID."""
    todo = session.get(Todo, todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo

@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: str,
    todo_update: TodoUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a todo (partial update)."""
    todo = session.get(Todo, todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    # Update fields that are provided
    todo_data = todo_update.dict(exclude_unset=True)
    for key, value in todo_data.items():
        setattr(todo, key, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a todo."""
    todo = session.get(Todo, todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    session.delete(todo)
    session.commit()
```

## Error Handling

### Custom Exception Classes

```python
# exceptions/custom.py
from fastapi import HTTPException

class TodoNotFoundException(HTTPException):
    def __init__(self, todo_id: str):
        super().__init__(
            status_code=404,
            detail=f"Todo with id '{todo_id}' not found"
        )

class UnauthorizedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Unauthorized - invalid or missing token"
        )

class ValidationException(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=422,
            detail=message
        )
```

### Exception Handlers

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from exceptions.custom import TodoNotFoundException, ValidationException

app = FastAPI()

@app.exception_handler(TodoNotFoundException)
async def todo_not_found_handler(request: Request, exc: TodoNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_type": "not_found"}
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_type": "validation"}
    )
```

### Field Validation

```python
from sqlmodel import Field, validator

class TodoCreate(SQLModel):
    title: str = Field(
        min_length=1,
        max_length=500,
        description="Task title"
    )
    priority: int = Field(
        ge=1,
        le=5,
        description="Priority level (1-5)"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Optional due date"
    )

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

### User Creation with Password Validation

```python
class UserCreate(SQLModel):
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain a number')
        return v
```

## API Documentation

FastAPI auto-generates OpenAPI docs at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc

### Example Description

```python
@router.post(
    "/",
    response_model=TodoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo",
    description="Create a new todo for the authenticated user. "
                "Requires authentication token in Authorization header.",
    responses={
        201: {"description": "Todo created successfully"},
        401: {"description": "Unauthorized - invalid or missing token"},
        422: {"description": "Validation error - invalid input data"}
    }
)
async def create_todo(
    todo: TodoCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new todo for the authenticated user."""
    # implementation...
```

## Outputs

This agent produces:

1. **API Specification** - Complete endpoint definitions with paths, methods, request/response schemas
2. **Model Definitions** - SQLModel classes with validation rules in spec form
3. **Error Taxonomy** - Standardized error types and status codes
4. **OpenAPI Documentation** - Auto-generated docs at `/docs`

## Integration Points

- Works with **Frontend Architecture Agent** to define TypeScript types matching API schemas
- Works with **Data Persistence Agent** to ensure models map to database schema
- Works with **Integration Agent** to validate API contracts with frontend

## When to Use

Use this agent when:
- Designing new API endpoints
- Defining data models and validation rules
- Standardizing error handling
- Writing endpoint documentation
- Creating authentication and authorization logic
