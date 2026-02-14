# Quickstart Guide: TaskAI Local Development

**Feature**: Phase 5 Part A - Advanced Task Management Features
**Date**: 2026-02-14
**Target**: Local development environment setup

## Overview

This guide walks you through setting up TaskAI for local development using Docker Compose and Minikube. Choose the approach that best fits your development workflow.

## Prerequisites

### Required Software

- **Docker Desktop** 4.25+ (includes Docker Compose)
- **Python** 3.13+
- **Node.js** 20+ with npm
- **Git** 2.40+

### Optional (for Kubernetes development)

- **Minikube** 1.32+
- **kubectl** 1.28+
- **Helm** 3.13+
- **Dapr CLI** 1.12+

---

## Option 1: Docker Compose (Recommended for Quick Start)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd "Hackathon II - Todo Spec-Driven Development/phase-05-cloud-deploy"
```

### Step 2: Set Up Environment Variables

```bash
# Backend API
cp services/backend-api/.env.example services/backend-api/.env

# Edit services/backend-api/.env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/taskai
KAFKA_BOOTSTRAP_SERVERS=redpanda:9092
OPENAI_API_KEY=your-openai-api-key
RESEND_API_KEY=your-resend-api-key
JWT_SECRET=your-secret-key-change-in-production

# Recurring Service
cp services/recurring-service/.env.example services/recurring-service/.env

# Edit services/recurring-service/.env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/taskai
KAFKA_BOOTSTRAP_SERVERS=redpanda:9092

# Notification Service
cp services/notification-service/.env.example services/notification-service/.env

# Edit services/notification-service/.env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/taskai
KAFKA_BOOTSTRAP_SERVERS=redpanda:9092
RESEND_API_KEY=your-resend-api-key

# Frontend
cp services/frontend/.env.example services/frontend/.env.local

# Edit services/frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 3: Start Services

```bash
cd infrastructure/docker-compose
docker-compose up -d
```

This starts:
- PostgreSQL (Port 5432)
- Redpanda (Kafka-compatible, Port 9092)
- Backend API (Port 8000)
- Recurring Service (Port 8002)
- Notification Service (Port 8001)
- Frontend (Port 3000)

### Step 4: Initialize Database

```bash
# Run database migrations
docker-compose exec backend-api python -m alembic upgrade head

# Or manually create schemas
docker-compose exec postgres psql -U postgres -d taskai -c "
CREATE SCHEMA IF NOT EXISTS tasks;
CREATE SCHEMA IF NOT EXISTS notifications;
CREATE SCHEMA IF NOT EXISTS audit;
"
```

### Step 5: Verify Services

```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health

# Check frontend
open http://localhost:3000
```

### Step 6: View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend-api
docker-compose logs -f recurring-service
docker-compose logs -f notification-service
docker-compose logs -f frontend
```

### Step 7: Stop Services

```bash
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## Option 2: Minikube (Production-Like Environment)

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable ingress addon
minikube addons enable ingress
```

### Step 2: Install Dapr

```bash
# Install Dapr on Kubernetes
cd infrastructure/scripts
./install-dapr.sh

# Verify Dapr installation
kubectl get pods -n dapr-system
```

### Step 3: Install Kafka (Strimzi Operator)

```bash
# Install Strimzi operator and Kafka cluster
./install-kafka.sh

# Verify Kafka installation
kubectl get kafka -n kafka
kubectl get pods -n kafka
```

### Step 4: Create Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace taskai

# Create secrets
kubectl create secret generic taskai-secrets \
  --from-literal=database-url=postgresql://postgres:postgres@postgres:5432/taskai \
  --from-literal=jwt-secret=your-secret-key-change-in-production \
  --from-literal=openai-api-key=your-openai-api-key \
  --from-literal=resend-api-key=your-resend-api-key \
  -n taskai
```

### Step 5: Deploy Services

```bash
# Deploy all services
./deploy-local.sh

# Or manually apply manifests
kubectl apply -f ../kubernetes/namespace.yaml
kubectl apply -f ../kubernetes/configmap.yaml
kubectl apply -f ../kubernetes/secrets.yaml
kubectl apply -f ../kubernetes/deployments/
kubectl apply -f ../kubernetes/services/
kubectl apply -f ../kubernetes/ingress/
```

### Step 6: Configure Dapr Components

```bash
# Apply Dapr components
kubectl apply -f ../dapr/components/
kubectl apply -f ../dapr/subscriptions/
```

### Step 7: Access Services

```bash
# Get Minikube IP
minikube ip

# Port forward services
kubectl port-forward -n taskai svc/backend-api 8000:8000
kubectl port-forward -n taskai svc/frontend 3000:3000

# Or use ingress
echo "$(minikube ip) taskai.local" | sudo tee -a /etc/hosts
open http://taskai.local
```

### Step 8: View Logs

```bash
# Backend API logs
kubectl logs -n taskai -l app=backend-api -f

# Recurring Service logs
kubectl logs -n taskai -l app=recurring-service -f

# Notification Service logs
kubectl logs -n taskai -l app=notification-service -f

# Frontend logs
kubectl logs -n taskai -l app=frontend -f
```

### Step 9: Cleanup

```bash
# Delete all resources
./teardown.sh

# Or manually
kubectl delete namespace taskai
kubectl delete namespace kafka
kubectl delete namespace dapr-system

# Stop Minikube
minikube stop
minikube delete
```

---

## Option 3: Local Development (Without Containers)

### Step 1: Install Dependencies

```bash
# Backend API
cd services/backend-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Recurring Service
cd ../recurring-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Notification Service
cd ../notification-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Step 2: Start Infrastructure Services

```bash
# Start PostgreSQL and Redpanda with Docker Compose
cd infrastructure/docker-compose
docker-compose up -d postgres redpanda
```

### Step 3: Initialize Database

```bash
# Create database
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE taskai;"

# Create schemas
docker-compose exec postgres psql -U postgres -d taskai -c "
CREATE SCHEMA IF NOT EXISTS tasks;
CREATE SCHEMA IF NOT EXISTS notifications;
CREATE SCHEMA IF NOT EXISTS audit;
"

# Run migrations (if using Alembic)
cd ../../services/backend-api
alembic upgrade head
```

### Step 4: Start Dapr Sidecars

```bash
# Terminal 1: Backend API with Dapr
cd services/backend-api
dapr run --app-id backend-api --app-port 8000 --dapr-http-port 3500 \
  --components-path ../../infrastructure/dapr/components \
  -- uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Recurring Service with Dapr
cd services/recurring-service
dapr run --app-id recurring-service --app-port 8002 --dapr-http-port 3502 \
  --components-path ../../infrastructure/dapr/components \
  -- uvicorn main:app --reload --host 0.0.0.0 --port 8002

# Terminal 3: Notification Service with Dapr
cd services/notification-service
dapr run --app-id notification-service --app-port 8001 --dapr-http-port 3501 \
  --components-path ../../infrastructure/dapr/components \
  -- uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Terminal 4: Frontend
cd services/frontend
npm run dev
```

### Step 5: Verify Services

```bash
# Check Dapr sidecars
dapr list

# Test API
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health

# Open frontend
open http://localhost:3000
```

---

## Development Workflow

### Hot Reload

**Backend Services (FastAPI)**:
- Changes to Python files automatically reload the server
- No restart needed for code changes

**Frontend (Next.js)**:
- Changes to TypeScript/React files automatically reload
- Fast Refresh preserves component state

### Running Tests

```bash
# Backend API tests
cd services/backend-api
pytest

# With coverage
pytest --cov=src --cov-report=html

# Recurring Service tests
cd services/recurring-service
pytest

# Notification Service tests
cd services/notification-service
pytest

# Frontend tests
cd services/frontend
npm test

# E2E tests
npm run test:e2e
```

### Database Migrations

```bash
# Create new migration
cd services/backend-api
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Viewing Kafka Messages

```bash
# Using Redpanda Console (if running)
open http://localhost:8080

# Using kafka-console-consumer
docker-compose exec redpanda rpk topic consume task-events
docker-compose exec redpanda rpk topic consume reminders
```

### Debugging

**Backend Services**:
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debugger
python -m debugpy --listen 5678 --wait-for-client -m uvicorn main:app --reload
```

**Frontend**:
```bash
# Enable debug mode
export NODE_ENV=development
export DEBUG=*

# Run with inspector
node --inspect node_modules/.bin/next dev
```

---

## Common Issues and Solutions

### Issue: Port Already in Use

**Solution**:
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Issue: Database Connection Failed

**Solution**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U postgres -d taskai -c "SELECT 1;"

# Restart PostgreSQL
docker-compose restart postgres
```

### Issue: Kafka Connection Failed

**Solution**:
```bash
# Check Redpanda is running
docker-compose ps redpanda

# Check topics
docker-compose exec redpanda rpk topic list

# Restart Redpanda
docker-compose restart redpanda
```

### Issue: Dapr Sidecar Not Starting

**Solution**:
```bash
# Check Dapr installation
dapr --version

# Reinitialize Dapr
dapr uninstall
dapr init

# Check Dapr components
dapr components -k  # Kubernetes
ls infrastructure/dapr/components/  # Local
```

### Issue: Frontend Build Errors

**Solution**:
```bash
# Clear Next.js cache
cd services/frontend
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

---

## API Testing

### Using cURL

```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Create task (with JWT token)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title":"Buy groceries","priority":"High"}'

# List tasks
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>"
```

### Using Swagger UI

Open http://localhost:8000/docs for interactive API documentation.

---

## Monitoring and Observability

### Dapr Dashboard

```bash
# Start Dapr dashboard
dapr dashboard

# Open in browser
open http://localhost:8080
```

### Prometheus Metrics

```bash
# Backend API metrics
curl http://localhost:8000/metrics

# Dapr metrics
curl http://localhost:3500/metrics
```

### Distributed Tracing

```bash
# View traces in Zipkin (if configured)
open http://localhost:9411
```

---

## Next Steps

1. ✅ Local environment set up
2. ⏭️ Implement Backend API endpoints (see tasks.md)
3. ⏭️ Implement Recurring Service logic
4. ⏭️ Implement Notification Service
5. ⏭️ Build Frontend dual interface
6. ⏭️ Write tests for all services
7. ⏭️ Deploy to cloud (AKS/GKE/OKE)

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Dapr Documentation](https://docs.dapr.io/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Quickstart Guide Complete**: 2026-02-14
**Next Command**: `/sp.tasks` to generate implementation tasks
