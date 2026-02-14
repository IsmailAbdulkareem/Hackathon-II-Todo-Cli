---
title: Todo Backend API
emoji: ✅
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Todo Backend API

FastAPI backend for Todo application with PostgreSQL persistence.

## 🚀 Features

- 6 REST endpoints for full CRUD operations
- PostgreSQL database persistence
- **JWT Authentication**: Stateless token-based authentication
- **User Isolation**: Users can only access their own resources
- **Two-Stage Security**: 401 for authentication, 403 for authorization
- Automatic OpenAPI documentation
- CORS support for frontend integration
- Request logging and error handling

## 📚 API Documentation

Once deployed, visit `/docs` for interactive Swagger UI documentation.

## 🔗 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/docs` | Interactive API documentation |
| GET | `/api/{user_id}/tasks` | Get all tasks for a user |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get a single task |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle task completion |

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **Server**: Uvicorn

## 📝 Example Usage

### Create a Task

```bash
curl -X POST "https://YOUR-SPACE.hf.space/api/user123/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Task", "description": "Task description"}'
```

### Get All Tasks

```bash
curl "https://YOUR-SPACE.hf.space/api/user123/tasks"
```

### Toggle Completion

```bash
curl -X PATCH "https://YOUR-SPACE.hf.space/api/user123/tasks/{task-id}/complete"
```

## 🔐 Environment Variables

Required secrets (set in Space settings):

- `DATABASE_URL` - PostgreSQL connection string
- `CORS_ORIGINS` - Comma-separated list of allowed origins

## 📖 Documentation

For more information, see the [API Specification](https://github.com/your-repo/specs/003-backend-api/spec.md).

## 🤝 Contributing

This is part of a Spec-Driven Development hackathon project.

## 📄 License

MIT License
