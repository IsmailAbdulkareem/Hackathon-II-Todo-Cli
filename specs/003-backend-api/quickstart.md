# Quickstart: Backend REST API

**Feature**: 003-backend-api
**Date**: 2026-01-08

## Overview

This guide provides step-by-step instructions to set up and run the FastAPI backend locally. The backend provides 6 REST endpoints for task management with PostgreSQL persistence.

## Prerequisites

- Python 3.13 or higher
- PostgreSQL database (local or Neon Serverless)
- Git (for cloning the repository)
- Terminal/Command Prompt

## Setup Instructions

### 1. Navigate to Backend Directory

```bash
cd phase-02-fullstack-web/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install fastapi sqlmodel psycopg2-binary uvicorn python-dotenv pydantic-settings
```

**Dependencies Explained**:
- `fastapi`: Web framework for building APIs
- `sqlmodel`: ORM combining SQLAlchemy and Pydantic
- `psycopg2-binary`: PostgreSQL database driver
- `uvicorn`: ASGI server for running FastAPI
- `python-dotenv`: Load environment variables from .env file
- `pydantic-settings`: Type-safe configuration management

### 4. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
CORS_ORIGINS=http://localhost:3000
```

**For Neon Serverless PostgreSQL**:
```bash
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Configuration Options**:
- `DATABASE_URL`: PostgreSQL connection string (required)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: http://localhost:3000)

### 5. Initialize Database

The application will automatically create tables on first run. Alternatively, you can create them manually:

```python
# Run this in Python shell or create a script
from sqlmodel import SQLModel, create_engine
from src.models.task import Task
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)
```

### 6. Run the Development Server

```bash
# From backend/ directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Server Options**:
- `--reload`: Auto-reload on code changes (development only)
- `--host 0.0.0.0`: Listen on all network interfaces
- `--port 8000`: Port number (default: 8000)

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7. Verify Installation

Open your browser and navigate to:
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/api/user123/tasks (should return `[]`)

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | Get all tasks for a user |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get a single task |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion status |

## Testing the API

### Using cURL

**Create a Task**:
```bash
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk and eggs"}'
```

**Get All Tasks**:
```bash
curl http://localhost:8000/api/user123/tasks
```

**Toggle Completion**:
```bash
curl -X PATCH http://localhost:8000/api/user123/tasks/{task-id}/complete
```

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters and request body
5. Click "Execute"
6. View the response

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "user123"

# Create a task
response = requests.post(
    f"{BASE_URL}/api/{USER_ID}/tasks",
    json={"title": "Buy groceries", "description": "Milk and eggs"}
)
task = response.json()
print(f"Created task: {task['id']}")

# Get all tasks
response = requests.get(f"{BASE_URL}/api/{USER_ID}/tasks")
tasks = response.json()
print(f"Total tasks: {len(tasks)}")

# Toggle completion
task_id = task['id']
response = requests.patch(f"{BASE_URL}/api/{USER_ID}/tasks/{task_id}/complete")
updated_task = response.json()
print(f"Completed: {updated_task['completed']}")
```

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-asyncio httpx
```

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=src tests/
```

## Troubleshooting

### Database Connection Error

**Error**: `could not connect to server: Connection refused`

**Solution**:
1. Verify PostgreSQL is running: `pg_isready`
2. Check DATABASE_URL in .env file
3. Ensure database exists: `createdb todo_db`
4. For Neon, verify connection string includes `?sslmode=require`

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify Python version: `python --version` (should be 3.13+)

### Port Already in Use

**Error**: `[Errno 48] Address already in use`

**Solution**:
1. Kill process using port 8000: `lsof -ti:8000 | xargs kill -9` (macOS/Linux)
2. Or use a different port: `uvicorn main:app --port 8001`

### CORS Errors in Browser

**Error**: `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution**:
1. Verify CORS_ORIGINS in .env includes frontend URL
2. Restart the server after changing .env
3. Check CORSMiddleware configuration in main.py

## Development Workflow

### Making Changes

1. Edit code in `src/` directory
2. Server auto-reloads (if using `--reload` flag)
3. Test changes via Swagger UI or cURL
4. Run tests: `pytest`
5. Commit changes: `git add . && git commit -m "description"`

### Adding New Endpoints

1. Define route in `src/api/tasks.py`
2. Add request/response models if needed
3. Update OpenAPI documentation (automatic via FastAPI)
4. Write tests in `tests/test_api.py`
5. Update this quickstart guide if necessary

### Database Migrations

**Note**: Migrations are out of scope for this phase but can be added later using Alembic.

## Production Deployment

### Environment Variables

Set these in your production environment:
- `DATABASE_URL`: Production PostgreSQL connection string
- `CORS_ORIGINS`: Production frontend URL(s)

### Running in Production

```bash
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Security Considerations

- Use HTTPS in production
- Set specific CORS origins (not wildcard)
- Use environment variables for secrets
- Enable database connection pooling
- Implement rate limiting (future phase)

## Next Steps

1. **Frontend Integration**: Connect the Next.js frontend to this API
2. **Authentication**: Add JWT-based authentication (Phase III)
3. **Testing**: Write comprehensive test suite
4. **Deployment**: Deploy to cloud platform (Railway, Render, Fly.io)
5. **Monitoring**: Add logging and error tracking

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Neon PostgreSQL**: https://neon.tech/docs
- **OpenAPI Specification**: http://localhost:8000/docs

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation at http://localhost:8000/docs
3. Consult the specification at `specs/003-backend-api/spec.md`
4. Review the data model at `specs/003-backend-api/data-model.md`
