# Research: Backend REST API with Persistent Storage

**Feature**: 003-backend-api
**Date**: 2026-01-08
**Status**: Complete

## Overview

This document captures research findings for implementing a FastAPI backend with SQLModel ORM and PostgreSQL database. All technical decisions are informed by framework best practices and the project's constitutional principles.

## Technology Stack Research

### FastAPI Framework

**Decision**: Use FastAPI 0.109+ as the web framework

**Rationale**:
- Native async/await support for high-performance I/O operations
- Automatic OpenAPI documentation generation
- Built-in request validation using Pydantic models
- Type hints throughout for better IDE support and error detection
- Excellent performance (comparable to Node.js and Go)
- Large ecosystem and active community

**Alternatives Considered**:
- **Flask**: Rejected - lacks native async support and automatic API documentation
- **Django REST Framework**: Rejected - too heavyweight for this use case, includes unnecessary features (admin panel, ORM with migrations we don't need)

### SQLModel ORM

**Decision**: Use SQLModel 0.0.14+ for database models and queries

**Rationale**:
- Combines SQLAlchemy and Pydantic for unified model definitions
- Single model class serves as both database model and API schema
- Type-safe queries with full IDE autocomplete
- Seamless integration with FastAPI (same author)
- Reduces code duplication between database and API layers

**Alternatives Considered**:
- **SQLAlchemy + Pydantic separately**: Rejected - requires duplicate model definitions
- **Tortoise ORM**: Rejected - less mature, smaller community, incompatible with SQLModel patterns

### Database Connection Management

**Decision**: Use connection pooling with SQLModel's engine configuration

**Rationale**:
- Connection pooling reduces overhead of creating new connections
- Neon Serverless PostgreSQL supports standard PostgreSQL connection strings
- SQLModel's `create_engine()` handles pooling automatically
- Dependency injection pattern for database sessions ensures proper cleanup

**Implementation Pattern**:
```python
# Recommended pattern from SQLModel documentation
from sqlmodel import create_engine, Session

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
```

### CORS Configuration

**Decision**: Use FastAPI's built-in CORSMiddleware

**Rationale**:
- Official FastAPI middleware for CORS handling
- Supports wildcard origins for development, specific origins for production
- Handles preflight requests automatically
- Configurable allowed methods and headers

**Implementation Pattern**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error Handling

**Decision**: Use FastAPI's HTTPException with custom exception handlers

**Rationale**:
- HTTPException provides standard HTTP status codes
- Custom exception handlers can format error responses consistently
- Validation errors automatically return 422 with detailed messages
- Database errors can be caught and converted to appropriate HTTP responses

**Implementation Pattern**:
```python
from fastapi import HTTPException

# For not found errors
raise HTTPException(status_code=404, detail="Task not found")

# For validation errors (automatic via Pydantic)
# FastAPI returns 422 with validation details
```

## Database Schema Design

### UUID vs Integer IDs

**Decision**: Use UUID (string) for task IDs

**Rationale**:
- Globally unique across all users and systems
- No sequential ID leakage (security consideration)
- Easier to merge data from multiple sources
- Aligns with specification requirement (FR-009)

**Implementation**: Use Python's `uuid.uuid4()` to generate IDs

### Timestamp Management

**Decision**: Use UTC timestamps with automatic management

**Rationale**:
- UTC avoids timezone confusion
- SQLModel supports `datetime` fields with automatic defaults
- `created_at` set once on creation
- `updated_at` set on creation and updated on modification

**Implementation Pattern**:
```python
from datetime import datetime
from sqlmodel import Field

created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Indexing Strategy

**Decision**: Create indexes on `user_id` and `id` fields

**Rationale**:
- Primary key (`id`) automatically indexed
- `user_id` needs index for efficient filtering (all queries filter by user)
- Composite index not needed (queries always filter by user_id first, then id)

**Implementation**: SQLModel's `index=True` parameter on field definition

## API Design Patterns

### Path Parameter vs Query Parameter for user_id

**Decision**: Use path parameter `/api/{user_id}/tasks`

**Rationale**:
- Aligns with specification requirements
- RESTful convention: path parameters for resource identification
- Prepares for future JWT authentication (user_id extracted from token)
- Clear ownership hierarchy in URL structure

### Request/Response Models

**Decision**: Use separate Pydantic models for create/update requests

**Rationale**:
- TaskCreate: Only fields user can provide (title, description)
- TaskUpdate: Same as TaskCreate (partial updates via PUT)
- Task: Full model with all fields (id, timestamps, user_id)
- Prevents users from setting id, timestamps, or user_id directly

**Implementation Pattern**:
```python
class TaskCreate(SQLModel):
    title: str
    description: str | None = None

class Task(TaskCreate, table=True):
    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    completed: bool = False
    created_at: datetime
    updated_at: datetime
```

### Toggle Completion Endpoint

**Decision**: Dedicated PATCH endpoint that inverts current status

**Rationale**:
- Simpler than requiring client to send current status
- Idempotent operation (multiple calls toggle back and forth)
- Aligns with specification (FR-006)
- Common pattern for boolean toggles in REST APIs

## Testing Strategy

### Test Database

**Decision**: Use in-memory SQLite for tests, PostgreSQL for development/production

**Rationale**:
- SQLite in-memory is fast and isolated (no cleanup needed)
- SQLModel supports both PostgreSQL and SQLite
- Tests run without external dependencies
- Production uses PostgreSQL for full feature support

**Implementation**: Pytest fixtures with separate test database engine

### Test Coverage

**Decision**: Focus on API endpoint tests and model validation tests

**Rationale**:
- API tests verify all 6 endpoints work correctly
- Model tests verify validation rules (title required, length constraints)
- Integration tests ensure database operations work
- No need for unit tests of framework code (FastAPI/SQLModel)

## Environment Configuration

### Configuration Management

**Decision**: Use Pydantic Settings for environment variables

**Rationale**:
- Type-safe configuration with validation
- Automatic loading from .env files
- Default values for development
- Required values enforced at startup

**Implementation Pattern**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
```

## Deployment Considerations

### Database Migrations

**Decision**: Use Alembic for database migrations (future phase)

**Rationale**:
- Standard migration tool for SQLAlchemy/SQLModel
- Version-controlled schema changes
- Supports rollback and forward migrations
- Not needed for initial development (SQLModel can create tables)

**Note**: Migrations deferred to deployment phase (out of scope for this feature)

### Development Server

**Decision**: Use uvicorn with auto-reload for development

**Rationale**:
- Official ASGI server for FastAPI
- Auto-reload watches for file changes
- Production-ready (can be used with gunicorn for multiple workers)

**Command**: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## Security Considerations

### SQL Injection Prevention

**Decision**: Use SQLModel's parameterized queries exclusively

**Rationale**:
- SQLModel automatically parameterizes all queries
- No raw SQL needed for this feature
- ORM prevents SQL injection by design

### Input Validation

**Decision**: Rely on Pydantic validation in request models

**Rationale**:
- Automatic validation of all request bodies
- Type checking, length constraints, required fields
- Returns 422 with detailed error messages
- No manual validation code needed

### User Isolation

**Decision**: Filter all queries by user_id from path parameter

**Rationale**:
- Every database query includes `WHERE user_id = ?`
- Prevents cross-user data access
- Enforced at query level, not application level
- Prepares for JWT authentication (user_id from token)

## Performance Optimization

### Query Optimization

**Decision**: Use eager loading for relationships (if added later)

**Rationale**:
- Single Task entity in this phase (no relationships)
- Future-proofing: use `selectinload()` for related entities
- Avoids N+1 query problems

### Response Caching

**Decision**: No caching in this phase

**Rationale**:
- Out of scope per specification
- Task data changes frequently (completion toggles)
- Caching adds complexity without clear benefit
- Can be added in future phase if needed

## Summary

All technical decisions are finalized with no remaining clarifications needed. The architecture follows FastAPI and SQLModel best practices while maintaining alignment with constitutional principles:

- **Deterministic**: Standard REST patterns, no AI components
- **Evolvable**: user_id path parameter enables future JWT integration
- **Separated**: Clear layers (models, api, core)
- **Declarative**: SQLModel models define schema, Pydantic validates input

**Ready for Phase 1**: Data model and API contract generation.
