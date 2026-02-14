# TaskAI API Reference

## Overview

TaskAI provides a RESTful API for task management with advanced features including AI-powered natural language processing, tag management, search, filtering, and reminders.

**Base URL**: `http://taskai.local/api` (local) or `https://your-domain.com/api` (production)

**Authentication**: JWT Bearer token required for all endpoints except `/health`

## Authentication

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

### Register

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**: Same as login

### Using Authentication

Include the JWT token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Tasks API

### Create Task

```http
POST /api/{user_id}/tasks
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "status": "pending",
  "priority": "high",
  "due_date": "2026-02-20T17:00:00Z",
  "is_recurring": false,
  "tags": ["work", "documentation"]
}
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "status": "pending",
  "priority": "high",
  "due_date": "2026-02-20T17:00:00Z",
  "is_recurring": false,
  "recurrence_pattern": null,
  "tags": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "work",
      "color": "#3B82F6"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "name": "documentation",
      "color": "#10B981"
    }
  ],
  "created_at": "2026-02-14T10:00:00Z",
  "updated_at": "2026-02-14T10:00:00Z"
}
```

### Create Task with Natural Language (AI)

```http
POST /api/{user_id}/tasks/ai
Authorization: Bearer {token}
Content-Type: application/json

{
  "prompt": "Remind me to call the dentist tomorrow at 2pm"
}
```

**Response**: Same as Create Task (AI extracts title, due date, etc.)

### Get All Tasks

```http
GET /api/{user_id}/tasks
Authorization: Bearer {token}
```

**Query Parameters**:
- `status` (optional): Filter by status (pending, in_progress, completed)
- `priority` (optional): Filter by priority (low, medium, high)
- `tag` (optional): Filter by tag name
- `due_before` (optional): Filter tasks due before date (ISO 8601)
- `due_after` (optional): Filter tasks due after date (ISO 8601)
- `search` (optional): Full-text search in title and description
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Example**:
```http
GET /api/{user_id}/tasks?status=pending&priority=high&tag=work&limit=20
```

**Response**:
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete project documentation",
      "status": "pending",
      "priority": "high",
      "due_date": "2026-02-20T17:00:00Z",
      "tags": ["work", "documentation"],
      "created_at": "2026-02-14T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### Get Task by ID

```http
GET /api/{user_id}/tasks/{task_id}
Authorization: Bearer {token}
```

**Response**: Single task object (same structure as Create Task response)

### Update Task

```http
PUT /api/{user_id}/tasks/{task_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated title",
  "status": "in_progress",
  "priority": "medium"
}
```

**Response**: Updated task object

### Delete Task

```http
DELETE /api/{user_id}/tasks/{task_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "message": "Task deleted successfully"
}
```

### Search Tasks

```http
GET /api/{user_id}/tasks/search
Authorization: Bearer {token}
```

**Query Parameters**:
- `q` (required): Search query
- `limit` (optional): Number of results (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Example**:
```http
GET /api/{user_id}/tasks/search?q=documentation&limit=10
```

**Response**: Same as Get All Tasks

## Tags API

### Create Tag

```http
POST /api/{user_id}/tags
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "urgent",
  "color": "#EF4444"
}
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "urgent",
  "color": "#EF4444",
  "created_at": "2026-02-14T10:00:00Z"
}
```

### Get All Tags

```http
GET /api/{user_id}/tags
Authorization: Bearer {token}
```

**Response**:
```json
{
  "tags": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "name": "urgent",
      "color": "#EF4444",
      "task_count": 5
    }
  ]
}
```

### Get Tag Suggestions (Autocomplete)

```http
GET /api/{user_id}/tags/suggestions
Authorization: Bearer {token}
```

**Query Parameters**:
- `q` (required): Search prefix
- `limit` (optional): Number of results (default: 10)

**Example**:
```http
GET /api/{user_id}/tags/suggestions?q=wor&limit=5
```

**Response**:
```json
{
  "suggestions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "work",
      "color": "#3B82F6"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440005",
      "name": "workout",
      "color": "#F59E0B"
    }
  ]
}
```

### Update Tag

```http
PUT /api/{user_id}/tags/{tag_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "super-urgent",
  "color": "#DC2626"
}
```

**Response**: Updated tag object

### Delete Tag

```http
DELETE /api/{user_id}/tags/{tag_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "message": "Tag deleted successfully"
}
```

## Reminders API

### Create Reminder

```http
POST /api/{user_id}/tasks/{task_id}/reminders
Authorization: Bearer {token}
Content-Type: application/json

{
  "scheduled_time": "2026-02-20T15:45:00Z",
  "reminder_type": "15min"
}
```

**Reminder Types**:
- `15min`: 15 minutes before due date
- `1hr`: 1 hour before due date
- `1day`: 1 day before due date
- `1week`: 1 week before due date
- `custom`: Custom time (use scheduled_time)

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "scheduled_time": "2026-02-20T15:45:00Z",
  "reminder_type": "15min",
  "status": "scheduled",
  "created_at": "2026-02-14T10:00:00Z"
}
```

### Get Task Reminders

```http
GET /api/{user_id}/tasks/{task_id}/reminders
Authorization: Bearer {token}
```

**Response**:
```json
{
  "reminders": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440006",
      "scheduled_time": "2026-02-20T15:45:00Z",
      "reminder_type": "15min",
      "status": "scheduled"
    }
  ]
}
```

### Delete Reminder

```http
DELETE /api/{user_id}/tasks/{task_id}/reminders/{reminder_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "message": "Reminder deleted successfully"
}
```

## Real-Time Sync API

### Get Latest Updates

```http
GET /api/{user_id}/sync
Authorization: Bearer {token}
```

**Query Parameters**:
- `since` (optional): ISO 8601 timestamp for incremental sync

**Example**:
```http
GET /api/{user_id}/sync?since=2026-02-14T10:00:00Z
```

**Response**:
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "action": "updated",
      "data": { /* task object */ },
      "timestamp": "2026-02-14T10:05:00Z"
    }
  ],
  "tags": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "action": "created",
      "data": { /* tag object */ },
      "timestamp": "2026-02-14T10:03:00Z"
    }
  ],
  "last_sync": "2026-02-14T10:05:00Z"
}
```

## Health Check

### Service Health

```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "backend-api",
  "version": "1.0.0",
  "timestamp": "2026-02-14T10:00:00Z",
  "dependencies": {
    "database": "healthy",
    "kafka": "healthy",
    "dapr": "healthy"
  }
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "due_date",
      "reason": "Invalid date format"
    }
  }
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate tag name)
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Codes

- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_ERROR`: Authentication failed
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource conflict
- `INTERNAL_ERROR`: Internal server error
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable

## Rate Limiting

- **Rate Limit**: 100 requests per minute per user
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

**Example**:
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1708000000
```

## Pagination

List endpoints support pagination:

**Query Parameters**:
- `limit`: Number of results per page (default: 50, max: 100)
- `offset`: Number of results to skip (default: 0)

**Response Headers**:
- `X-Total-Count`: Total number of results
- `Link`: Pagination links (first, prev, next, last)

**Example**:
```http
HTTP/1.1 200 OK
X-Total-Count: 250
Link: <http://taskai.local/api/tasks?limit=50&offset=0>; rel="first",
      <http://taskai.local/api/tasks?limit=50&offset=50>; rel="next",
      <http://taskai.local/api/tasks?limit=50&offset=200>; rel="last"
```

## Webhooks (Future)

Webhook support for real-time notifications (planned feature):

- Task created
- Task updated
- Task completed
- Task deleted
- Reminder triggered

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://taskai.local/api"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create task
response = requests.post(
    f"{BASE_URL}/user-id/tasks",
    headers=headers,
    json={
        "title": "New task",
        "priority": "high"
    }
)
task = response.json()
print(f"Created task: {task['id']}")
```

### JavaScript/TypeScript

```typescript
const BASE_URL = "http://taskai.local/api";
const TOKEN = "your-jwt-token";

const headers = {
  "Authorization": `Bearer ${TOKEN}`,
  "Content-Type": "application/json"
};

// Create task
const response = await fetch(`${BASE_URL}/user-id/tasks`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    title: "New task",
    priority: "high"
  })
});

const task = await response.json();
console.log(`Created task: ${task.id}`);
```

### cURL

```bash
# Create task
curl -X POST http://taskai.local/api/user-id/tasks \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New task",
    "priority": "high"
  }'
```

## Versioning

API versioning is handled via URL path:

- Current version: `/api/v1/...` (default, can omit `/v1`)
- Future versions: `/api/v2/...`

## Support

For API support and questions:
- Documentation: https://docs.taskai.local
- GitHub Issues: https://github.com/your-org/taskai/issues
- Email: support@taskai.local

---

**Last Updated**: 2026-02-14
**API Version**: 1.0.0
