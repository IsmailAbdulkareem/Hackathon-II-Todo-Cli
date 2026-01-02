# Database Schema Generator

**Critical for Phases:** II, III, V

Generates SQLModel classes, relationships, and Neon DB migrations from entity descriptions.

## Usage

```
/gen.db-schema "<entity descriptions>"

# Example:
/gen.db-schema "User entity with id, email, password_hash, created_at. Todo entity with id, title, description, completed, user_id (FK to User), created_at, updated_at. One-to-many User to Todos"
```

## What It Generates

- SQLModel class definitions with proper field types
- Foreign key relationships with cascade rules
- Indexes for performance
- Neon DB migration file
- Seed data for testing
- Base model with common fields

## Output Structure

```
phase-XX/src/models/
  ├── base.py              # Base SQLModel and DB session
  ├── user.py              # User SQLModel
  ├── todo.py              # Todo SQLModel
  └── migrations/
      ├── 001_create_initial_tables.sql
      └── 002_add_indexes.sql
```

## Features

- UUID primary keys
- Timestamp fields (created_at, updated_at) with auto-update
- Soft delete support
- Enum fields for status
- Cascade delete relationships
- Snake_case table naming
- Proper typing with Optional

## Phase Usage

- **Phase II:** Users, Todos tables
- **Phase III:** Conversations, Messages tables
- **Phase V:** Event tables, TaskHistory tables

## Example Output

```python
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    todos: list["Todo"] = Relationship(back_populates="user")

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    user_id: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="todos")
```

## Best Practices Applied

- Pydantic v2 style models
- Proper typing with Optional
- Field constraints (max_length, unique)
- Cascade delete relationships
- Index on foreign keys and email
- UTC timestamps
- UUID for security
