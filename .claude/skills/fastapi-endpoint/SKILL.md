# FastAPI Endpoint Generator

**Critical for Phases:** II, III

Generates complete FastAPI route handlers with error handling, validation, and documentation.

## Usage

```
/gen.fastapi-endpoint "<resource>" "<operations>"

# Examples:
/gen.fastapi-endpoint "Todo" "GET list all, POST create, GET by id, PUT update, DELETE"
/gen.fastapi-endpoint "User" "GET profile, PUT update profile, DELETE account"
/gen.fastapi-endpoint "Chat" "POST send message, GET history, DELETE conversation"
```

## What It Generates

- FastAPI router with full CRUD operations
- Pydantic models for request/response
- Error handling with proper HTTP status codes
- Query parameter validation and filtering
- Pagination support for list endpoints
- OpenAPI/Swagger documentation
- Unit tests for each endpoint

## Output Structure

```
phase-XX/src/api/
  ├── todos/
  │   ├── router.py        # FastAPI router
  │   ├── schemas.py       # Pydantic models
  │   └── endpoints.py     # Route handlers
  └── dependencies.py        # Auth and database deps
```

## Features

- HTTP status code handling (200, 201, 404, 422, 500)
- Input validation with Pydantic
- Database error handling
- Custom exception classes
- Response models with proper typing
- Query filters (e.g., ?completed=true)
- Sort by any field
- Pagination (?page=1&limit=20)
- CORS configuration
- Rate limiting support

## Phase Usage

- **Phase II:** Todos CRUD (/api/todos), Users (/api/users)
- **Phase III:** Chat (/api/chat, /api/conversations)
- **Phase III:** AI endpoints (/api/ai/parse, /api/ai/suggest)

## Example Output

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])

@router.get("", response_model=List[TodoResponse])
def list_todos(
    completed: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List all todos with filtering and pagination."""
    query = select(Todo).where(Todo.user_id == current_user.id)
    if completed is not None:
        query = query.where(Todo.completed == completed)
    query = query.offset(skip).limit(limit)
    return session.exec(query).all()

@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(
    todo_data: TodoCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new todo."""
    todo = Todo(**todo_data.model_dump(), user_id=current_user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
```

## Error Handling

- 400 Bad Request - Invalid input
- 401 Unauthorized - Missing/invalid token
- 403 Forbidden - Resource belongs to another user
- 404 Not Found - Resource doesn't exist
- 422 Unprocessable Entity - Validation error
- 500 Internal Server Error - Database/connection issues
