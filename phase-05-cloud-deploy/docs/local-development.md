# TaskAI Local Development Guide

## Overview

This guide covers setting up a local development environment for TaskAI, including running services individually, using Docker Compose, or deploying to Minikube.

## Prerequisites

### Required Software

- **Python 3.13+**: Backend services
- **Node.js 20+**: Frontend development
- **Docker 24+**: Container runtime
- **PostgreSQL 15+**: Database (or use Docker)
- **Kafka**: Message broker (or use Docker)
- **Dapr CLI 1.12+**: For local Dapr development

### Optional Tools

- **Minikube**: Local Kubernetes cluster
- **kubectl**: Kubernetes CLI
- **Postman/Insomnia**: API testing
- **VS Code**: Recommended IDE with extensions:
  - Python
  - ESLint
  - Prettier
  - Docker
  - Kubernetes

## Quick Start (Docker Compose)

The fastest way to get started is using Docker Compose:

```bash
cd infrastructure/docker-compose
docker-compose up
```

This starts:
- PostgreSQL (port 5432)
- Kafka + Zookeeper (port 9092)
- Backend API (port 8000)
- Recurring Service (port 8002)
- Notification Service (port 8001)
- Frontend (port 3000)

**Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/taskai.git
cd taskai/phase-05-cloud-deploy
```

### 2. Setup Backend Services

#### Backend API

```bash
cd services/backend-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Required: POSTGRES_*, JWT_SECRET, OPENAI_API_KEY

# Run database migrations (if using Alembic)
alembic upgrade head

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**With Dapr**:
```bash
dapr run --app-id backend-api --app-port 8000 --dapr-http-port 3500 \
  -- uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Recurring Service

```bash
cd services/recurring-service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

**With Dapr**:
```bash
dapr run --app-id recurring-service --app-port 8002 --dapr-http-port 3502 \
  -- uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

#### Notification Service

```bash
cd services/notification-service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with RESEND_API_KEY

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**With Dapr**:
```bash
dapr run --app-id notification-service --app-port 8001 --dapr-http-port 3501 \
  -- uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 3. Setup Frontend

```bash
cd services/frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

**Access**: http://localhost:3000

### 4. Setup Database

#### Using Docker

```bash
docker run -d \
  --name taskai-postgres \
  -e POSTGRES_USER=taskai \
  -e POSTGRES_PASSWORD=dev_password \
  -e POSTGRES_DB=taskai \
  -p 5432:5432 \
  postgres:15
```

#### Using Local PostgreSQL

```bash
# Create database
createdb taskai

# Create user
psql -c "CREATE USER taskai WITH PASSWORD 'dev_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE taskai TO taskai;"

# Run migrations
cd services/backend-api
alembic upgrade head
```

### 5. Setup Kafka

#### Using Docker

```bash
# Start Kafka with Zookeeper
docker-compose -f infrastructure/docker-compose/docker-compose.yml up kafka zookeeper
```

#### Using Local Kafka

```bash
# Download Kafka
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0

# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka (in another terminal)
bin/kafka-server-start.sh config/server.properties

# Create topics
bin/kafka-topics.sh --create --topic task-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
bin/kafka-topics.sh --create --topic reminders --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### 6. Setup Dapr (Local)

```bash
# Initialize Dapr
dapr init

# Verify installation
dapr --version

# Check Dapr components
ls ~/.dapr/components
```

**Create local Dapr components** (optional):

```bash
mkdir -p ~/.dapr/components

# Kafka Pub/Sub component
cat > ~/.dapr/components/kafka-pubsub.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "taskai-group"
EOF

# PostgreSQL State Store
cat > ~/.dapr/components/statestore.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=localhost port=5432 user=taskai password=dev_password dbname=taskai sslmode=disable"
EOF
```

## Development Workflows

### Running All Services

#### Option 1: Docker Compose (Recommended)

```bash
cd infrastructure/docker-compose
docker-compose up
```

#### Option 2: Individual Terminals

```bash
# Terminal 1: Backend API
cd services/backend-api
dapr run --app-id backend-api --app-port 8000 -- uvicorn main:app --reload

# Terminal 2: Recurring Service
cd services/recurring-service
dapr run --app-id recurring-service --app-port 8002 -- uvicorn main:app --reload

# Terminal 3: Notification Service
cd services/notification-service
dapr run --app-id notification-service --app-port 8001 -- uvicorn main:app --reload

# Terminal 4: Frontend
cd services/frontend
npm run dev
```

#### Option 3: Minikube

```bash
cd infrastructure/scripts
./setup-minikube.sh
./install-dapr.sh
./install-kafka.sh
./deploy-local.sh
```

### Hot Reload

- **Backend (FastAPI)**: Automatic with `--reload` flag
- **Frontend (Next.js)**: Automatic with `npm run dev`
- **Dapr**: Restart required for component changes

### Testing

#### Backend Tests

```bash
cd services/backend-api

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_tasks.py

# Run specific test
pytest tests/test_tasks.py::test_create_task
```

#### Frontend Tests

```bash
cd services/frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- TaskList.test.tsx
```

#### Integration Tests

```bash
# Start all services first
docker-compose up -d

# Run integration tests
cd tests/integration
pytest
```

### Debugging

#### Backend (VS Code)

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false,
      "cwd": "${workspaceFolder}/services/backend-api"
    }
  ]
}
```

#### Frontend (VS Code)

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug server-side",
      "type": "node-terminal",
      "request": "launch",
      "command": "npm run dev",
      "cwd": "${workspaceFolder}/services/frontend"
    },
    {
      "name": "Next.js: debug client-side",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000"
    }
  ]
}
```

#### Dapr Debugging

```bash
# View Dapr logs
dapr logs --app-id backend-api

# Enable debug logging
dapr run --app-id backend-api --app-port 8000 --log-level debug \
  -- uvicorn main:app --reload
```

### Database Management

#### Migrations (Alembic)

```bash
cd services/backend-api

# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

#### Database Console

```bash
# Connect to PostgreSQL
psql -h localhost -U taskai -d taskai

# Common queries
\dt                    # List tables
\d tasks.tasks         # Describe table
SELECT * FROM tasks.tasks LIMIT 10;
```

### API Testing

#### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Create task (with token)
curl -X POST http://localhost:8000/api/user-id/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","priority":"high"}'
```

#### Using Postman

1. Import collection from `docs/postman/TaskAI.postman_collection.json`
2. Set environment variables:
   - `base_url`: http://localhost:8000
   - `token`: (obtained from login)
3. Run requests

### Kafka Testing

#### View Messages

```bash
# Console consumer for task-events
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic task-events --from-beginning

# Console consumer for reminders
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic reminders --from-beginning
```

#### Publish Test Message

```bash
# Publish to task-events
echo '{"event_type":"created","task_id":"test-123"}' | \
  kafka-console-producer.sh --bootstrap-server localhost:9092 \
    --topic task-events
```

## Code Style & Linting

### Backend (Python)

```bash
cd services/backend-api

# Format code with black
black src/

# Sort imports
isort src/

# Lint with flake8
flake8 src/

# Type checking with mypy
mypy src/

# Run all checks
black src/ && isort src/ && flake8 src/ && mypy src/
```

### Frontend (TypeScript)

```bash
cd services/frontend

# Format with Prettier
npm run format

# Lint with ESLint
npm run lint

# Fix linting issues
npm run lint:fix

# Type checking
npm run type-check
```

## Environment Variables

### Backend API (.env)

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=taskai
POSTGRES_USER=taskai
POSTGRES_PASSWORD=dev_password

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Authentication
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Email
RESEND_API_KEY=re_...

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U taskai -d taskai -c "SELECT 1;"

# Check logs
docker logs taskai-postgres
```

### Kafka Connection Issues

```bash
# Check Kafka is running
docker ps | grep kafka

# Test connection
kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# Check logs
docker logs taskai-kafka
```

### Dapr Issues

```bash
# Check Dapr status
dapr --version

# Reinitialize Dapr
dapr uninstall
dapr init

# Check component configuration
cat ~/.dapr/components/kafka-pubsub.yaml
```

## Performance Tips

1. **Use Docker Compose**: Faster than individual services
2. **Enable Hot Reload**: Automatic code reloading
3. **Use Local Database**: Faster than Docker for development
4. **Disable Dapr**: For simple testing without event-driven features
5. **Use Minikube Cache**: `minikube cache add` for faster image loading

## Best Practices

1. **Use Virtual Environments**: Isolate Python dependencies
2. **Keep .env Files Local**: Never commit secrets
3. **Run Tests Before Commit**: Ensure code quality
4. **Use Type Hints**: Better IDE support and fewer bugs
5. **Write Tests**: Aim for >80% coverage
6. **Follow Code Style**: Use formatters and linters
7. **Document Changes**: Update README and docs
8. **Use Feature Branches**: Never commit directly to main
9. **Review PRs**: Get code reviews before merging
10. **Keep Dependencies Updated**: Regular security updates

## Next Steps

- [Deployment Guide](deployment-guide.md)
- [API Reference](api-reference.md)
- [Architecture Documentation](architecture.md)
- [MCP Tools Guide](mcp-tools.md)

---

**Last Updated**: 2026-02-14
**Version**: 1.0.0
