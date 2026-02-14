# TaskAI - Phase 5: Cloud-Native Deployment

**Status:** ✅ Complete
**Architecture:** Microservices with Event-Driven Design
**Tech Stack:** FastAPI, Next.js, Kafka, Dapr, Kubernetes, PostgreSQL
**Deployment:** Minikube (local) / Cloud Kubernetes (production)

## Overview

TaskAI Phase 5 is a cloud-native, event-driven task management system built on microservices architecture. The system leverages Kubernetes for orchestration, Dapr for distributed application runtime, and Kafka for event streaming.

## Features

### Core Features
- ✅ **Task Management**: Create, read, update, delete tasks
- ✅ **User Authentication**: JWT-based authentication
- ✅ **Tag System**: Organize tasks with customizable tags
- ✅ **Advanced Search**: Full-text search with filters
- ✅ **Due Dates & Reminders**: Schedule tasks with email notifications
- ✅ **Recurring Tasks**: Automatic task generation based on recurrence patterns
- ✅ **AI-Powered Chat**: Natural language task creation with OpenAI GPT-4
- ✅ **Real-Time Sync**: Keep tasks synchronized across clients

### Technical Features
- 🏗️ **Microservices Architecture**: 4 independent services
- 📨 **Event-Driven**: Kafka for async communication
- 🔄 **Dapr Integration**: Service mesh capabilities
- ☸️ **Kubernetes Native**: Cloud-ready deployment
- 🔐 **Secure**: JWT authentication, encrypted secrets
- 📊 **Observable**: Health checks, logging, metrics
- 🚀 **Scalable**: Horizontal pod autoscaling

## Architecture

### Services

```
┌─────────────────────────────────────────────────────────────────┐
│                         Ingress (NGINX)                          │
│                      taskai.local / Cloud LB                     │
└────────────────┬────────────────────────────┬───────────────────┘
                 │                            │
                 ▼                            ▼
        ┌────────────────┐          ┌─────────────────┐
        │    Frontend    │          │   Backend API   │
        │   (Next.js)    │◄─────────┤   (FastAPI)     │
        │   Port: 3000   │  REST    │   Port: 8000    │
        └────────────────┘          └────────┬────────┘
                                             │
                                             │ Dapr Pub/Sub
                                             ▼
                                    ┌────────────────────┐
                                    │   Kafka (Strimzi)  │
                                    │  task-events topic │
                                    │  reminders topic   │
                                    └─────┬──────────┬───┘
                                          │          │
                        ┌─────────────────┘          └──────────────┐
                        ▼                                           ▼
              ┌──────────────────┐                    ┌──────────────────────┐
              │ Recurring Service│                    │ Notification Service │
              │   (FastAPI)      │                    │     (FastAPI)        │
              │   Port: 8002     │                    │     Port: 8001       │
              └──────────────────┘                    └──────────────────────┘
                        │                                           │
                        └───────────────┬───────────────────────────┘
                                        ▼
                                ┌───────────────┐
                                │  PostgreSQL   │
                                │  (Shared DB)  │
                                └───────────────┘
```

### Service Responsibilities

| Service | Port | Purpose |
|---------|------|---------|
| **Frontend** | 3000 | Next.js UI with React 19, real-time updates, AI chat interface |
| **Backend API** | 8000 | RESTful API, authentication, task CRUD, AI integration, event publishing |
| **Recurring Service** | 8002 | Subscribes to task events, generates recurring task instances |
| **Notification Service** | 8001 | Subscribes to reminder events, sends email notifications via Resend |

## Quick Start

### Prerequisites

- **Docker** 24+
- **kubectl** 1.28+
- **Minikube** 1.32+ (for local deployment)
- **Dapr CLI** 1.12+
- **Helm** 3.12+ (optional)

### Option 1: Local Deployment (Minikube)

```bash
# 1. Setup Minikube cluster
cd infrastructure/scripts
chmod +x *.sh
./setup-minikube.sh

# 2. Install Dapr
./install-dapr.sh

# 3. Install Kafka
./install-kafka.sh

# 4. Configure secrets (IMPORTANT!)
# Edit infrastructure/kubernetes/secrets.yaml with your credentials:
# - POSTGRES_PASSWORD
# - JWT_SECRET
# - OPENAI_API_KEY
# - RESEND_API_KEY

# 5. Deploy TaskAI
./deploy-local.sh

# 6. Add to /etc/hosts
echo "$(minikube ip) taskai.local" | sudo tee -a /etc/hosts

# 7. Access application
# Frontend: http://taskai.local
# API: http://taskai.local/api
# Health: http://taskai.local/health
```

### Option 2: Docker Compose (Development)

```bash
cd infrastructure/docker-compose
docker-compose up
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 3: Cloud Deployment

```bash
# 1. Configure kubectl for your cloud cluster
# Azure: az aks get-credentials --resource-group myRG --name myCluster
# GCP: gcloud container clusters get-credentials myCluster --zone us-central1-a
# AWS: aws eks update-kubeconfig --name myCluster --region us-east-1

# 2. Build and push images to your registry
REGISTRY="your-registry.azurecr.io"
cd services/backend-api
docker build -t $REGISTRY/taskai/backend-api:latest .
docker push $REGISTRY/taskai/backend-api:latest
# Repeat for other services...

# 3. Update image references in deployment manifests

# 4. Configure production secrets
kubectl create secret generic taskai-secrets \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -base64 24) \
  --from-literal=JWT_SECRET=$(openssl rand -base64 32) \
  --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY \
  --from-literal=RESEND_API_KEY=$RESEND_API_KEY \
  --namespace=taskai

# 5. Deploy to cloud
cd infrastructure/scripts
./deploy-cloud.sh prod
```

## Project Structure

```
phase-05-cloud-deploy/
├── services/                           # Microservices
│   ├── backend-api/                    # Core API service
│   │   ├── src/
│   │   │   ├── api/                    # REST endpoints
│   │   │   ├── core/                   # Config, database, auth
│   │   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── services/               # Business logic
│   │   │   └── schemas/                # Pydantic schemas
│   │   ├── tests/
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── recurring-service/              # Recurring task processor
│   │   ├── src/
│   │   │   ├── subscriber.py           # Dapr subscriber
│   │   │   ├── recurrence_engine.py    # Recurrence logic
│   │   │   └── dapr_client.py
│   │   ├── main.py
│   │   └── Dockerfile
│   │
│   ├── notification-service/           # Email notifications
│   │   ├── src/
│   │   │   ├── subscriber.py           # Dapr subscriber
│   │   │   ├── email_sender.py         # Resend integration
│   │   │   └── retry_handler.py
│   │   ├── main.py
│   │   └── Dockerfile
│   │
│   └── frontend/                       # Next.js UI
│       ├── src/
│       │   ├── app/                    # Next.js 16 app router
│       │   ├── components/             # React components
│       │   ├── services/               # API client
│       │   └── types/                  # TypeScript types
│       ├── public/
│       ├── Dockerfile
│       └── package.json
│
├── infrastructure/                     # Deployment configs
│   ├── kubernetes/                     # K8s manifests
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── deployments/
│   │   ├── services/
│   │   └── ingress/
│   │
│   ├── dapr/                          # Dapr components
│   │   ├── components/
│   │   │   ├── kafka-pubsub.yaml
│   │   │   ├── statestore.yaml
│   │   │   └── secrets.yaml
│   │   └── subscriptions/
│   │
│   ├── kafka/                         # Kafka configs
│   │   └── kafka-cluster.yaml
│   │
│   ├── scripts/                       # Deployment scripts
│   │   ├── setup-minikube.sh
│   │   ├── install-dapr.sh
│   │   ├── install-kafka.sh
│   │   ├── deploy-local.sh
│   │   ├── deploy-cloud.sh
│   │   └── teardown.sh
│   │
│   └── docker-compose/                # Local development
│       └── docker-compose.yml
│
└── docs/                              # Documentation
    ├── architecture.md
    ├── api-reference.md
    ├── deployment-guide.md
    ├── local-development.md
    └── mcp-tools.md
```

## Technology Stack

### Backend
- **Python 3.13+**: Modern Python with type hints
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: ORM for PostgreSQL
- **Pydantic**: Data validation
- **OpenAI GPT-4**: AI-powered natural language processing
- **Resend**: Email delivery service

### Frontend
- **Next.js 16**: React framework with App Router
- **React 19**: Latest React with concurrent features
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn/ui**: Component library

### Infrastructure
- **Kubernetes 1.28+**: Container orchestration
- **Dapr 1.12+**: Distributed application runtime
- **Apache Kafka**: Event streaming (via Strimzi)
- **PostgreSQL 15+**: Relational database
- **NGINX**: Ingress controller
- **Docker**: Containerization

## Development

### Local Development Setup

See [Local Development Guide](docs/local-development.md) for detailed instructions.

**Quick start**:
```bash
# Backend API
cd services/backend-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd services/frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd services/backend-api
pytest

# Frontend tests
cd services/frontend
npm test
```

### Code Quality

```bash
# Backend
black src/
isort src/
flake8 src/
mypy src/

# Frontend
npm run lint
npm run format
npm run type-check
```

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

See [API Reference](docs/api-reference.md) for complete documentation.

## Monitoring & Observability

### Health Checks

All services expose health endpoints:
```bash
curl http://taskai.local/health
```

### Logs

```bash
# View service logs
kubectl logs -f deployment/backend-api -n taskai

# View Dapr sidecar logs
kubectl logs -f deployment/backend-api -c daprd -n taskai

# View all logs
kubectl logs -f -l app=taskai -n taskai
```

### Metrics

```bash
# Install Prometheus + Grafana
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

## Scaling

### Horizontal Pod Autoscaler

```bash
# Auto-scale backend-api based on CPU
kubectl autoscale deployment backend-api \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n taskai

# View HPA status
kubectl get hpa -n taskai
```

### Manual Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment backend-api --replicas=5 -n taskai
```

## Security

- **Authentication**: JWT-based with secure token handling
- **Secrets Management**: Kubernetes Secrets, encrypted at rest
- **Network Security**: Service-to-service via ClusterIP only
- **Dapr mTLS**: Automatic mutual TLS between services
- **HTTPS**: TLS termination at ingress (production)

## Troubleshooting

### Common Issues

**Pods not starting**:
```bash
kubectl describe pod <pod-name> -n taskai
kubectl logs <pod-name> -n taskai
```

**Service connectivity**:
```bash
kubectl get endpoints -n taskai
kubectl get svc -n taskai
```

**Kafka issues**:
```bash
kubectl get kafka taskai-kafka -n taskai
kubectl logs -l strimzi.io/name=taskai-kafka-kafka -n taskai
```

See [Deployment Guide](docs/deployment-guide.md) for detailed troubleshooting.

## Cleanup

### Remove Deployment

```bash
cd infrastructure/scripts
./teardown.sh local   # For Minikube
./teardown.sh prod    # For cloud
```

### Complete Cleanup

```bash
# Delete namespace
kubectl delete namespace taskai

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment-guide.md)
- [Local Development](docs/local-development.md)
- [MCP Tools Guide](docs/mcp-tools.md)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Documentation**: https://docs.taskai.local
- **Issues**: https://github.com/your-org/taskai/issues
- **Email**: support@taskai.local

---

**Built with ❤️ using FastAPI, Next.js, Kubernetes, Dapr, and Kafka**
