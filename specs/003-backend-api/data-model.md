# Data Model: Backend REST API

**Feature**: 003-backend-api
**Date**: 2026-01-08
**Status**: Complete

## Overview

This document defines the data model for the Task entity and its database representation. The model is implemented using SQLModel, which combines SQLAlchemy (database) and Pydantic (validation) into a single unified model.

## Entity: Task

### Description

Represents a todo item belonging to a specific user. Tasks track completion status, timestamps, and user ownership. All tasks are scoped to a user_id to enforce isolation.

### Fields

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | string (UUID) | Primary key, required, unique | Auto-generated | Unique identifier for the task |
| user_id | string | Required, indexed, max 255 chars | From path parameter | Owner of the task (user identifier) |
| title | string | Required, non-empty, max 500 chars | None | Task name/summary |
| description | string | Optional, max 2000 chars | null | Detailed task description |
| completed | boolean | Required | false | Completion status |
| created_at | datetime (UTC) | Required | Current timestamp | When task was created |
| updated_at | datetime (UTC) | Required | Current timestamp | When task was last modified |

### Validation Rules

**Title**:
- MUST NOT be empty or whitespace-only
- MUST NOT exceed 500 characters
- Required for create and update operations

**Description**:
- Optional field (can be null)
- MUST NOT exceed 2000 characters if provided
- Empty string treated as null

**User ID**:
- MUST NOT be empty
- MUST NOT exceed 255 characters
- Provided via path parameter, not request body

**Completed**:
- Boolean value only (true/false)
- Defaults to false on creation
- Toggled via dedicated PATCH endpoint

**Timestamps**:
- Always stored in UTC timezone
- created_at set once on creation, never modified
- updated_at set on creation and updated on every modification
- Automatically managed by the system

### Indexes

- **Primary Index**: `id` (automatic, unique)
- **Secondary Index**: `user_id` (for efficient filtering by user)

**Rationale**: All queries filter by user_id first, so indexing this field is critical for performance. The id field is automatically indexed as the primary key.

### State Transitions

```
[New Task]
    ↓ (POST /api/{user_id}/tasks)
[Created: completed=false]
    ↓ (PATCH /api/{user_id}/tasks/{id}/complete)
[Completed: completed=true]
    ↓ (PATCH /api/{user_id}/tasks/{id}/complete)
[Incomplete: completed=false]
    ↓ (DELETE /api/{user_id}/tasks/{id})
[Deleted]
```

**Notes**:
- Tasks can be updated (PUT) in any state
- Completion status can be toggled indefinitely
- Deletion is permanent (no soft delete)

## Request/Response Models

### TaskCreate (Request Body for POST)

Used when creating a new task.

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | Yes | Non-empty, max 500 chars |
| description | string | No | Max 2000 chars |

**Example**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

### TaskUpdate (Request Body for PUT)

Used when updating an existing task. Same structure as TaskCreate.

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | Yes | Non-empty, max 500 chars |
| description | string | No | Max 2000 chars |

**Example**:
```json
{
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips"
}
```

### Task (Response Model)

Full task object returned by all endpoints.

| Field | Type | Description |
|-------|------|-------------|
| id | string | UUID identifier |
| user_id | string | Owner identifier |
| title | string | Task name |
| description | string \| null | Task details |
| completed | boolean | Completion status |
| created_at | string (ISO 8601) | Creation timestamp |
| updated_at | string (ISO 8601) | Last modification timestamp |

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-08T10:30:00Z",
  "updated_at": "2026-01-08T10:30:00Z"
}
```

## Database Schema

### Table: tasks

```sql
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

**Notes**:
- VARCHAR(36) for UUID string representation
- TEXT for description (supports up to 2000 chars)
- TIMESTAMP stores UTC datetime
- Index on user_id for efficient filtering

## Relationships

**Current Phase**: No relationships (single entity)

**Future Phases**: Potential relationships to consider:
- Task → User (when user authentication is added)
- Task → Category/Tag (if categorization is added)
- Task → Comment (if task comments are added)

## Data Integrity

### Constraints

1. **User Isolation**: All queries MUST filter by user_id
2. **Title Required**: Cannot create or update task without title
3. **Length Limits**: Enforced at validation layer (Pydantic) and database layer
4. **UUID Uniqueness**: Guaranteed by UUID v4 generation algorithm

### Validation Strategy

**Layer 1 - API (Pydantic)**:
- Type checking (string, boolean, datetime)
- Required field validation
- Length constraints (max 500 for title, max 2000 for description)
- Returns HTTP 422 on validation failure

**Layer 2 - Database (PostgreSQL)**:
- NOT NULL constraints
- VARCHAR length limits
- Primary key uniqueness
- Index integrity

## Error Scenarios

| Scenario | Validation Layer | HTTP Status | Error Message |
|----------|------------------|-------------|---------------|
| Missing title | Pydantic | 422 | "field required" |
| Empty title | Pydantic | 422 | "ensure this value has at least 1 character" |
| Title too long | Pydantic | 422 | "ensure this value has at most 500 characters" |
| Description too long | Pydantic | 422 | "ensure this value has at most 2000 characters" |
| Invalid user_id (empty) | Application | 422 | "user_id cannot be empty" |
| Task not found | Application | 404 | "Task not found" |
| Task belongs to different user | Application | 404 | "Task not found" |

## Migration Strategy

**Initial Setup**: SQLModel can create tables automatically using `SQLModel.metadata.create_all(engine)`

**Future Migrations**: Use Alembic for schema changes:
- Adding new fields
- Modifying constraints
- Creating new indexes
- Data migrations

**Note**: Migrations are out of scope for this phase but the model is designed to support them.

## Performance Considerations

### Query Patterns

**Most Common**:
1. Get all tasks for user: `SELECT * FROM tasks WHERE user_id = ?`
2. Get single task: `SELECT * FROM tasks WHERE id = ? AND user_id = ?`
3. Create task: `INSERT INTO tasks VALUES (...)`
4. Update task: `UPDATE tasks SET ... WHERE id = ? AND user_id = ?`
5. Delete task: `DELETE FROM tasks WHERE id = ? AND user_id = ?`

**Optimization**:
- Index on user_id ensures fast filtering (O(log n) instead of O(n))
- Primary key on id ensures fast lookups
- No joins needed (single table)
- Expected query time: <10ms for indexed queries

### Scalability

**Current Design Supports**:
- Up to 10,000 tasks per user (per specification)
- Hundreds of concurrent users
- Millions of total tasks across all users

**Limitations**:
- No pagination (out of scope)
- No full-text search on title/description
- No sorting or filtering beyond user_id

## Summary

The Task entity is a simple, well-defined model with clear validation rules and efficient indexing. The design supports the current requirements while remaining extensible for future phases (authentication, relationships, advanced features).

**Key Design Decisions**:
- UUID for globally unique IDs
- UTC timestamps for consistency
- Indexed user_id for performance
- Separate request/response models for security
- Pydantic validation for type safety
