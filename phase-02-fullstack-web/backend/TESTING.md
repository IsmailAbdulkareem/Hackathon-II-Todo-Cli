# Backend API Testing Instructions

**Feature**: 003-backend-api
**Date**: 2026-01-08
**Status**: Implementation Complete

## Prerequisites

Before testing, ensure you have:
1. Python 3.13+ installed
2. PostgreSQL database (local or Neon Serverless)
3. Virtual environment activated
4. Dependencies installed
5. `.env` file configured with valid DATABASE_URL

## Setup Steps

### 1. Navigate to Backend Directory

```bash
cd phase-02-fullstack-web/backend
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install fastapi sqlmodel psycopg2-binary uvicorn python-dotenv pydantic-settings
```

### 4. Configure Environment

Create `.env` file with your database credentials:

```bash
# For local PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
CORS_ORIGINS=http://localhost:3000

# For Neon Serverless PostgreSQL
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
CORS_ORIGINS=http://localhost:3000
```

### 5. Start the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Testing Endpoints

### Test 1: Health Check

**Endpoint**: `GET /`

```bash
curl http://localhost:8000/
```

**Expected Response** (200 OK):
```json
{
  "status": "healthy",
  "message": "Todo Backend API is running",
  "docs": "/docs"
}
```

### Test 2: API Documentation

**Endpoint**: `GET /docs`

Open in browser: http://localhost:8000/docs

**Expected**: Swagger UI with all 6 endpoints visible

### Test 3: Retrieve All Tasks (Empty)

**Endpoint**: `GET /api/{user_id}/tasks`
**User Story**: US1

```bash
curl http://localhost:8000/api/user123/tasks
```

**Expected Response** (200 OK):
```json
[]
```

### Test 4: Create a New Task

**Endpoint**: `POST /api/{user_id}/tasks`
**User Story**: US2

```bash
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk and eggs"}'
```

**Expected Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": false,
  "created_at": "2026-01-08T12:00:00.000000Z",
  "updated_at": "2026-01-08T12:00:00.000000Z"
}
```

**Save the task ID** from the response for subsequent tests.

### Test 5: Retrieve All Tasks (With Data)

**Endpoint**: `GET /api/{user_id}/tasks`
**User Story**: US1

```bash
curl http://localhost:8000/api/user123/tasks
```

**Expected Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user123",
    "title": "Buy groceries",
    "description": "Milk and eggs",
    "completed": false,
    "created_at": "2026-01-08T12:00:00.000000Z",
    "updated_at": "2026-01-08T12:00:00.000000Z"
  }
]
```

### Test 6: Retrieve Single Task

**Endpoint**: `GET /api/{user_id}/tasks/{id}`
**User Story**: US6

```bash
# Replace {task-id} with actual ID from Test 4
curl http://localhost:8000/api/user123/tasks/{task-id}
```

**Expected Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": false,
  "created_at": "2026-01-08T12:00:00.000000Z",
  "updated_at": "2026-01-08T12:00:00.000000Z"
}
```

### Test 7: Toggle Task Completion (First Toggle)

**Endpoint**: `PATCH /api/{user_id}/tasks/{id}/complete`
**User Story**: US5

```bash
# Replace {task-id} with actual ID
curl -X PATCH http://localhost:8000/api/user123/tasks/{task-id}/complete
```

**Expected Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": true,
  "created_at": "2026-01-08T12:00:00.000000Z",
  "updated_at": "2026-01-08T12:05:00.000000Z"
}
```

**Verify**: `completed` changed from `false` to `true`, `updated_at` timestamp updated

### Test 8: Toggle Task Completion (Second Toggle)

**Endpoint**: `PATCH /api/{user_id}/tasks/{id}/complete`
**User Story**: US5

```bash
# Replace {task-id} with actual ID
curl -X PATCH http://localhost:8000/api/user123/tasks/{task-id}/complete
```

**Expected Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": false,
  "created_at": "2026-01-08T12:00:00.000000Z",
  "updated_at": "2026-01-08T12:06:00.000000Z"
}
```

**Verify**: `completed` changed from `true` back to `false`, `updated_at` timestamp updated again

### Test 9: Update Task

**Endpoint**: `PUT /api/{user_id}/tasks/{id}`
**User Story**: US3

```bash
# Replace {task-id} with actual ID
curl -X PUT http://localhost:8000/api/user123/tasks/{task-id} \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries and supplies", "description": "Milk, eggs, bread, and butter"}'
```

**Expected Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "title": "Buy groceries and supplies",
  "description": "Milk, eggs, bread, and butter",
  "completed": false,
  "created_at": "2026-01-08T12:00:00.000000Z",
  "updated_at": "2026-01-08T12:10:00.000000Z"
}
```

**Verify**: Title and description updated, `updated_at` timestamp updated, `id` and `created_at` unchanged

### Test 10: Delete Task

**Endpoint**: `DELETE /api/{user_id}/tasks/{id}`
**User Story**: US4

```bash
# Replace {task-id} with actual ID
curl -X DELETE http://localhost:8000/api/user123/tasks/{task-id}
```

**Expected Response** (204 No Content):
```
(empty response body)
```

### Test 11: Verify Deletion

**Endpoint**: `GET /api/{user_id}/tasks`

```bash
curl http://localhost:8000/api/user123/tasks
```

**Expected Response** (200 OK):
```json
[]
```

**Verify**: Task list is empty again

## Error Handling Tests

### Test 12: Task Not Found

```bash
curl http://localhost:8000/api/user123/tasks/invalid-id
```

**Expected Response** (404 Not Found):
```json
{
  "detail": "Task not found"
}
```

### Test 13: User Isolation

Create a task for user123, then try to access it as user456:

```bash
# Create task for user123
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Private task", "description": "Only for user123"}'

# Try to access as user456 (replace {task-id} with actual ID)
curl http://localhost:8000/api/user456/tasks/{task-id}
```

**Expected Response** (404 Not Found):
```json
{
  "detail": "Task not found"
}
```

### Test 14: Validation Error (Empty Title)

```bash
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "", "description": "Test"}'
```

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "title"],
      "msg": "Title cannot be empty or whitespace only",
      "input": "",
      "ctx": {"error": {}}
    }
  ]
}
```

### Test 15: Validation Error (Title Too Long)

```bash
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"$(python -c 'print("a" * 501)')\", \"description\": \"Test\"}"
```

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "title"],
      "msg": "String should have at most 500 characters",
      "input": "aaa...",
      "ctx": {"max_length": 500}
    }
  ]
}
```

## Integration Testing with Swagger UI

1. Open http://localhost:8000/docs in your browser
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters and request body
5. Click "Execute"
6. View the response

**Recommended Test Flow**:
1. GET /api/user123/tasks (verify empty)
2. POST /api/user123/tasks (create task)
3. GET /api/user123/tasks (verify task appears)
4. PATCH /api/user123/tasks/{id}/complete (toggle completion)
5. PUT /api/user123/tasks/{id} (update task)
6. GET /api/user123/tasks/{id} (verify single task)
7. DELETE /api/user123/tasks/{id} (delete task)
8. GET /api/user123/tasks (verify empty again)

## Success Criteria

All tests should pass with expected responses:
- ✅ Health check returns 200 OK
- ✅ API documentation accessible at /docs
- ✅ Empty task list returns empty array
- ✅ Task creation returns 201 with generated UUID
- ✅ Task retrieval returns all user's tasks
- ✅ Single task retrieval returns correct task
- ✅ Toggle completion inverts status and updates timestamp
- ✅ Task update modifies title/description and updates timestamp
- ✅ Task deletion returns 204 and removes task
- ✅ User isolation enforced (404 for other users' tasks)
- ✅ Validation errors return 422 with details
- ✅ Database errors return 500 with generic message

## Troubleshooting

### Server Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install fastapi sqlmodel psycopg2-binary uvicorn python-dotenv pydantic-settings
```

### Database Connection Error

**Error**: `could not connect to server: Connection refused`

**Solution**: Verify DATABASE_URL in .env file and ensure PostgreSQL is running

### CORS Errors

**Error**: Browser console shows CORS policy error

**Solution**: Verify CORS_ORIGINS in .env includes frontend URL (http://localhost:3000)

## Next Steps

After successful testing:
1. Integrate with frontend (Phase 2 frontend already exists at phase-02-fullstack-web/frontend)
2. Add authentication (Phase III - JWT-based)
3. Deploy to production environment
4. Add monitoring and logging
5. Implement rate limiting

## Documentation

- Specification: `specs/003-backend-api/spec.md`
- Implementation Plan: `specs/003-backend-api/plan.md`
- Data Model: `specs/003-backend-api/data-model.md`
- API Contract: `specs/003-backend-api/contracts/openapi.yaml`
- Quickstart Guide: `specs/003-backend-api/quickstart.md`
