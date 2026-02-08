# Quickstart Guide: Phase V Advanced Features

## Overview
This guide provides step-by-step instructions to set up and run the Todo application with advanced features (due dates, priorities, tags, recurring tasks, reminders, search/filter) using Dapr for event-driven architecture.

## Prerequisites
- Python 3.13+ with pip
- Node.js 20+ with npm
- Dapr CLI 1.12+
- Redis 6.0+ (for Dapr state store and pub/sub)
- Git

## Dapr Installation

### Install Dapr CLI
```bash
# On Windows (using Winget)
winget install Dapr.CLI

# On macOS (using Homebrew)
brew install dapr/tap/dapr-cli

# On Linux
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

### Verify Installation
```bash
dapr --version
# Expected: Dapr CLI version >= 1.12.0
```

### Initialize Dapr (Self-Hosted)
```bash
dapr init
# This installs Dapr runtime and default components (Redis, Zipkin)
```

### Verify Dapr Runtime
```bash
dapr status -w
# Should show daprd running
```

## Redis Setup

### Using Dapr's Default Redis (Recommended for local development)
Dapr installs a default Redis container during `dapr init`. This is sufficient for local development.

### Using Separate Redis Installation
If you prefer a separate Redis installation:
```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Using package managers
# On Ubuntu/Debian
sudo apt-get install redis-server

# On macOS
brew install redis
brew services start redis
```

## Backend Setup

### Clone and Navigate
```bash
# If starting from scratch
git clone <repository-url>
cd <repository-name>

# If continuing with existing repository
cd <repository-directory>
```

### Backend Dependencies
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# If no requirements.txt exists, install core dependencies
pip install fastapi uvicorn dapr dapr-ext-grpc python-multipart pydantic
```

### Dapr Configuration Files
Create the following Dapr component configuration files in `backend/dapr/components/`:

**statestore.yaml**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
  - name: actorStateStore
    value: "true"
```

**pubsub.yaml**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

### Run Backend with Dapr
```bash
# Run backend with Dapr sidecar
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 -- uvicorn src.main:app --reload

# Alternative: Run without Dapr (for testing fallback capabilities)
uvicorn src.main:app --reload
```

### Verify Backend
- Open http://localhost:8000/docs to access FastAPI documentation
- API endpoints should be available
- Dapr dashboard at http://localhost:8080 (if Dapr is running)

## Frontend Setup

### Navigate to Frontend
```bash
cd frontend
```

### Install Dependencies
```bash
npm install
```

### Environment Configuration
Create `.env.local` file with:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DAPR_HTTP_PORT=3500
```

### Run Frontend
```bash
npm run dev
```

### Verify Frontend
- Open http://localhost:3000 in browser
- UI should load and connect to backend
- Authentication flow should work

## Testing the Features

### Basic Task Operations
1. Create a task with due date and priority:
   ```bash
   curl -X POST http://localhost:8000/api/tasks \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer <valid-token>" \
   -d '{"title": "Test task", "due_date": "2026-12-31T23:59:59Z", "priority": "high", "tags": ["test", "important"]}'
   ```

2. Search and filter tasks:
   ```bash
   curl "http://localhost:8000/api/tasks/search?priority=high&completed=false" \
   -H "Authorization: Bearer <valid-token>"
   ```

### SSE Notifications
1. Open SSE stream:
   ```bash
   curl -H "Authorization: Bearer <valid-token>" http://localhost:8000/api/notifications/stream
   ```

2. Create a task with reminder and verify notification appears in SSE stream

## Running with Docker (Optional)

### Build Images
```bash
# Build backend
cd backend
docker build -t todo-backend .

# Build frontend
cd frontend
docker build -t todo-frontend .
```

### Docker Compose with Dapr
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  todo-backend:
    image: todo-backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
    command: [
      "dapr", "run",
      "--app-id", "todo-backend",
      "--app-port", "8000",
      "--dapr-http-port", "3500",
      "--",
      "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"
    ]

  todo-frontend:
    image: todo-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - todo-backend
```

### Start Services
```bash
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **Dapr Not Found**
   - Ensure Dapr CLI is installed and in PATH
   - Run `dapr uninstall` and `dapr init` again

2. **Redis Connection Issues**
   - Check if Redis is running on port 6379
   - Verify Redis password configuration

3. **Authentication Errors**
   - Ensure valid authentication token is being passed
   - Check that authentication system from earlier phases is running

4. **SSE Connection Issues**
   - Verify backend is running and accessible
   - Check CORS settings if accessing from different origin

### Debugging Commands

```bash
# Check Dapr sidecars
dapr status

# List Dapr applications
dapr list

# Check component health
curl http://localhost:3500/v1.0/healthz

# View Dapr logs
dapr logs <app-id>
```

## Scaling for Production

### Kubernetes Setup
For Phase IV, use:
- Helm charts to deploy to Kubernetes
- Proper Dapr annotations in deployments
- Managed Redis (AWS ElastiCache, Azure Cache, etc.)
- Ingress controller for traffic routing

### Performance Tuning
- Adjust Dapr component settings based on load
- Configure Redis with appropriate memory and persistence
- Optimize database queries and indexes
- Implement caching where appropriate

## Next Steps

1. Explore the API documentation at http://localhost:8000/docs
2. Review the event-driven architecture components
3. Test the advanced features (recurring tasks, reminders, search/filter)
4. Review the source code structure and implementation
5. Prepare for Phase IV Kubernetes deployment