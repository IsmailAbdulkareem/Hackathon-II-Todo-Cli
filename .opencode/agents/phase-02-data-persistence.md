# Phase II: Data Persistence Agent

**Specialist Agent**: SQLModel + Neon PostgreSQL Database Design

## Overview

Designs database schemas, creates migration strategies, and ensures Phase I in-memory logic maps cleanly to database persistence for the todo application.

## Core Responsibilities

1. **Design Schema**: Create normalized database schemas with proper relationships
2. **Migration Strategy**: Define database migration and rollback procedures
3. **Phase I Mapping**: Ensure console app logic translates to database operations
4. **Performance Optimization**: Add indexes and constraints for efficient queries

## Tech Stack

- **Database**: PostgreSQL (Neon Cloud)
- **ORM**: SQLModel (built on SQLAlchemy)
- **Migrations**: Alembic (SQLAlchemy migrations)
- **Connection**: psycopg3 (PostgreSQL adapter)

## Project Structure

```
backend/
├── models/                  # SQLModel database models
│   ├── base.py              # Base model + engine
│   ├── user.py              # User table
│   ├── todo.py              # Todo table
│   └── conversation.py      # For Phase III
├── migrations/              # Alembic migrations
│   ├── env.py               # Alembic config
│   ├── script.py.mako       # Migration template
│   └── versions/
│       ├── 001_initial_setup.py
│       ├── 002_add_indexes.py
│       └── 003_add_audit_fields.py
├── seed/                    # Seed data scripts
│   ├── __init__.py
│   └── seed_users.py
└── pyproject.toml
```

## Commands Available

- `/sp.specify` - Define database schema specifications
- `/sp.plan` - Plan migration strategy
- `/gen.db-schema` - Generate SQLModel schemas from natural language
- `/sp.implement` - Execute migrations with TDD

## Database Schema Design

### Core Tables

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);

-- Todos table
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_status ON todos(status);
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
```

### Phase I to Database Mapping

| Phase I (In-Memory) | Phase II (Database) | Notes |
|---------------------|---------------------|-------|
| `dict[str, Todo]` | `todos` table | Map dict key → UUID |
| `Todo.title` | `title VARCHAR(500)` | Add length constraint |
| `Todo.description` | `description TEXT` | Support long text |
| `Todo.completed` | `completed BOOLEAN` | Add status enum |
| (none) | `user_id UUID FK` | Add ownership |
| (none) | `created_at` | Add timestamp |
| (none) | `updated_at` | Add audit field |

## SQLModel Implementation

### Base Model

```python
# models/base.py
from sqlmodel import SQLModel, create_engine, Session, Field
from sqlalchemy.orm import sessionmaker
from typing import Generator
from datetime import datetime
import os
import uuid

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get DB session."""
    with SessionLocal() as session:
        yield session

def init_db():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)
```

### User Model

```python
# models/user.py
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    todos: list["Todo"] = Relationship(back_populates="user")
```

### Todo Model

```python
# models/todo.py
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None)
    status: TodoStatus = Field(default=TodoStatus.PENDING)
    priority: int = Field(default=1, ge=1, le=5)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    user: "User" = Relationship(back_populates="todos")
```

## Migration Strategy

### Using Alembic

```python
# Install Alembic
# uv add alembic

# Initialize Alembic
# alembic init migrations

# migrations/env.py
from sqlmodel import SQLModel
from models.base import engine
from models import user, todo

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=SQLModel.metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

### Example Migration

```python
# migrations/versions/001_initial_setup.py
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    op.create_table(
        'todos',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_todos_user_id', 'todos', ['user_id'])
    op.create_index('idx_todos_status', 'todos', ['status'])

def downgrade():
    op.drop_index('idx_todos_status', 'todos')
    op.drop_index('idx_todos_user_id', 'todos')
    op.drop_table('todos')
    op.drop_index('idx_users_email', 'users')
    op.drop_table('users')
```

### Running Migrations

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Add audit fields"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Persistence Rules

### 1. Foreign Key Constraints

- **ON DELETE CASCADE**: When user deleted, delete all their todos
- **ON UPDATE CASCADE**: Update user_id references when user ID changes
- **NOT NULL**: Required fields must have values

### 2. Indexes

```sql
-- Index for user lookups
CREATE INDEX idx_todos_user_id ON todos(user_id);

-- Index for status filtering
CREATE INDEX idx_todos_status ON todos(status);

-- Composite index for user + status queries
CREATE INDEX idx_todos_user_status ON todos(user_id, status);

-- Descending index for timeline queries
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
```

### 3. Data Validation

- **Email format**: Regex validation at application layer
- **Password strength**: bcrypt hashing with salt
- **Title length**: 1-500 characters
- **Priority range**: 1-5 integer
- **Status enum**: pending/in_progress/completed

### 4. Timestamps

- **created_at**: Auto-generated on INSERT, never updated
- **updated_at**: Auto-update on UPDATE (via trigger or application logic)

```python
# Trigger for auto-updating updated_at
from sqlalchemy import DDL

trigger = DDL('''
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';

    CREATE TRIGGER update_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_todos_updated_at
        BEFORE UPDATE ON todos
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
''')

event.listen(SQLModel.metadata, 'after_create', trigger.execute)
```

## Seed Data

```python
# seed/seed_users.py
from sqlmodel import Session
from models.base import engine, init_db
from models.user import User
from auth.password import hash_password

def seed_users():
    """Create initial test users."""
    init_db()

    with Session(engine) as session:
        # Test user
        user = User(
            email="test@example.com",
            password_hash=hash_password("Test123!"),
        )
        session.add(user)

        # Admin user
        admin = User(
            email="admin@example.com",
            password_hash=hash_password("Admin123!"),
        )
        session.add(admin)

        session.commit()

if __name__ == "__main__":
    seed_users()
    print("Seed data created successfully!")
```

## Database Connection (Neon)

```bash
# .env file
DATABASE_URL=postgresql://[user]:[password]@[ep-xxx].us-east-2.aws.neon.tech/neondb?sslmode=require
```

## Outputs

This agent produces:

1. **Database Schema Specification** - Complete table definitions with columns, types, constraints
2. **Migration Strategy** - Alembic migration files for schema evolution
3. **Persistence Rules** - Foreign keys, indexes, validation rules
4. **Phase I Mapping Document** - Mapping of in-memory structures to database tables

## Integration Points

- Works with **Backend API Agent** to ensure models match API schemas
- Works with **Frontend Architecture Agent** to define TypeScript types
- Works with **Integration Agent** to validate data contracts

## When to Use

Use this agent when:
- Designing new database tables or relationships
- Creating database migrations
- Adding indexes or constraints for performance
- Seeding test data
- Mapping Phase I in-memory logic to database
- Designing audit fields and timestamps
