# Todo Backend API

FastAPI backend for Todo application with PostgreSQL persistence.

## Features

- 6 REST endpoints for full CRUD operations on tasks
- User isolation via user_id path parameters
- PostgreSQL database persistence using SQLModel ORM
- Automatic OpenAPI documentation
- CORS support for frontend integration

## Prerequisites

- Python 3.13 or higher
- PostgreSQL database (local or Neon Serverless)
- Virtual environment tool (venv)

## Quick Start

### 1. Create Virtual Environment

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install fastapi sqlmodel psycopg2-binary uvicorn python-dotenv pydantic-settings
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update with your database credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
CORS_ORIGINS=http://localhost:3000
```

### 4. Run Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | Get all tasks for a user |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get a single task |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion status |

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel database models
│   │   └── task.py      # Task entity model
│   ├── api/             # FastAPI route handlers
│   │   └── tasks.py     # Task CRUD endpoints
│   └── core/            # Configuration and utilities
│       ├── config.py    # Environment configuration
│       └── database.py  # Database connection management
├── tests/               # Test suite
├── main.py              # FastAPI application entry point
├── pyproject.toml       # Project metadata and dependencies
├── .env.example         # Environment variable template
└── README.md            # This file
```

## Development

### Running Tests

```bash
pip install pytest pytest-asyncio httpx
pytest
```

### Code Quality

Follow the project constitution principles defined in `.specify/memory/constitution.md`.

## Production Deployment

### Environment Configuration

Set these environment variables in your production environment:

```bash
DATABASE_URL=postgresql://user:password@production-host:5432/todo_db
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Deployment Options

#### Option 1: Using Gunicorn (Recommended for Production)

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Worker Configuration**:
- Workers: `(2 x CPU cores) + 1` (e.g., 4 workers for 2 cores)
- Worker class: `uvicorn.workers.UvicornWorker` (for async support)
- Timeout: 30 seconds (default)

#### Option 2: Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install fastapi sqlmodel psycopg2-binary uvicorn gunicorn python-dotenv pydantic-settings

COPY . .

EXPOSE 8000

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

Build and run:

```bash
docker build -t todo-backend .
docker run -p 8000:8000 --env-file .env todo-backend
```

#### Option 3: Cloud Platforms

**Railway**:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

**Render**:
- Connect GitHub repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

**Fly.io**:
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

### Database Setup

#### Neon Serverless PostgreSQL (Recommended)

1. Create account at https://neon.tech
2. Create new project
3. Copy connection string
4. Set `DATABASE_URL` environment variable with `?sslmode=require` suffix

#### Local PostgreSQL

```bash
# Create database
createdb todo_db

# Set DATABASE_URL
export DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
```

### Security Checklist

Before deploying to production:

- [ ] Use HTTPS (TLS/SSL certificates)
- [ ] Set specific CORS origins (not wildcard `*`)
- [ ] Use environment variables for all secrets
- [ ] Enable database connection pooling (already configured)
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting (future enhancement)
- [ ] Enable database backups
- [ ] Use strong database passwords
- [ ] Keep dependencies updated

### Monitoring and Logging

The application includes built-in request logging. View logs:

```bash
# Development
uvicorn main:app --log-level info

# Production (with gunicorn)
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --log-level info --access-logfile - --error-logfile -
```

### Health Checks

Use the root endpoint for health checks:

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Todo Backend API is running",
  "docs": "/docs"
}
```

### Performance Tuning

**Database Connection Pool** (already configured in `src/core/database.py`):
- Pool size: 5 connections
- Max overflow: 10 connections
- Pre-ping: Enabled (verifies connections before use)

**Gunicorn Workers**:
- Start with 4 workers
- Monitor CPU and memory usage
- Adjust based on load

### Troubleshooting Production Issues

**High Memory Usage**:
- Reduce number of gunicorn workers
- Check for database connection leaks
- Monitor with `htop` or cloud platform metrics

**Slow Response Times**:
- Check database query performance
- Verify connection pooling is working
- Add database indexes if needed
- Monitor with application logs

**Database Connection Errors**:
- Verify DATABASE_URL is correct
- Check database is accessible from production server
- Verify SSL mode for Neon (`?sslmode=require`)
- Check connection pool settings

## Documentation

For detailed setup and testing instructions, see:
- Testing Guide: `TESTING.md`
- Quickstart Guide: `specs/003-backend-api/quickstart.md`
- API Contract: `specs/003-backend-api/contracts/openapi.yaml`
- Data Model: `specs/003-backend-api/data-model.md`

## Support

For issues or questions, consult the specification at `specs/003-backend-api/spec.md`.
