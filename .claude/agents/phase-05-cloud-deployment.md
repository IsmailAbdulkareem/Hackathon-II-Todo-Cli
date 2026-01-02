# Phase V: Cloud Deployment Agent

**Specialist Agent**: Kafka + Dapr + DigitalOcean DOKS Deployment

## Overview

Deploys todo application to cloud infrastructure with Kafka for event streaming, Dapr for service mesh, and DigitalOcean DOKS for managed Kubernetes.

## Core Responsibilities

1. **Kafka Integration**: Set up Kafka clusters for event-driven architecture
2. **Dapr Service Mesh**: Configure Dapr for sidecar-based service-to-service communication
3. **Cloud K8s Deployment**: Deploy to DigitalOcean DOKS
4. **Infrastructure as Code**: Manage cloud resources with Terraform

## Tech Stack

- **Cloud Provider**: DigitalOcean
- **Kubernetes**: DOKS (DigitalOcean Kubernetes Service)
- **Event Streaming**: Apache Kafka (or DO Managed Kafka)
- **Service Mesh**: Dapr (Distributed Application Runtime)
- **IaC**: Terraform

## Commands Available

- `/sp.specify` - Define cloud deployment requirements
- `/sp.plan` - Plan infrastructure architecture
- `/gen.dapr-component` - Generate Dapr component configs
- `/gen.helm-chart` - Generate Helm charts

## Cloud Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   DigitalOcean DOKS                    │
│                   (Managed Kubernetes)                  │
└───────────────────┬────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼───┐     ┌──▼───┐     ┌──▼─────┐
│ Frontend│     │Backend│     │  Kafka │
│(Dapr)  │◄────►│(Dapr) │◄──►│ Cluster │
└───┬───┘     └───┬───┘     └────────┘
    │               │
    └───────┬───────┘
            │
       ┌────▼────┐
       │Postgres │
       │(Managed)│
       └─────────┘
```

## Terraform Infrastructure

### Provider Configuration

```hcl
# terraform/main.tf
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket = "todo-app-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "nyc3"
  }
}

provider "digitalocean" {
  token = var.do_token
}

provider "kubernetes" {
  config_path = "~/.kube/config"
  config_context = "do-nyc3-todo-cluster"
}
```

### DOKS Cluster

```hcl
# terraform/cluster.tf
resource "digitalocean_kubernetes_cluster" "todo_cluster" {
  name   = "todo-cluster"
  region = "nyc3"
  version = "1.28.2-do.0"

  node_pool {
    name       = "worker-pool"
    size       = "s-4vcpu-8gb"
    node_count = 3

    tags = ["todo-app", "worker"]
  }

  maintenance_policy {
    start_time = "04:00"
    day        = "sunday"
  }
}

output "kube_config" {
  value     = digitalocean_kubernetes_cluster.todo_cluster.kube_config[0].raw_config
  sensitive = true
}

output "cluster_endpoint" {
  value = digitalocean_kubernetes_cluster.todo_cluster.endpoint
}
```

### Managed Database

```hcl
# terraform/database.tf
resource "digitalocean_database_cluster" "postgres" {
  name       = "todo-db"
  engine     = "pg"
  version    = "16"
  size       = "db-s-2vcpu-4gb"
  region     = "nyc3"
  node_count = 1

  tags = ["todo-app", "postgres"]
}

resource "digitalocean_database_db" "todoapp" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "todoapp"
}

resource "digitalocean_database_user" "todo_user" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "todo_user"
}

output "database_host" {
  value = digitalocean_database_cluster.postgres.host
}

output "database_uri" {
  sensitive = true
  value     = "postgresql://${digitalocean_database_user.todo_user.name}@${digitalocean_database_cluster.postgres.host}:${digitalocean_database_cluster.postgres.port}/${digitalocean_database_db.todoapp.name}"
}
```

### Managed Kafka

```hcl
# terraform/kafka.tf
resource "digitalocean_kafka_cluster" "todo_kafka" {
  name          = "todo-kafka"
  region        = "nyc3"
  version       = "3.6.0"
  size          = "kafka-s-1vcpu-2gb"
  kafka_users = [
    {
      name = "todo-user"
      permission = "full"
    }
  ]
}

output "kafka_brokers" {
  value = digitalocean_kafka_cluster.todo_kafka.kafka_brokers
}

output "kafka_connect" {
  sensitive = true
  value     = digitalocean_kafka_cluster.todo_kafka.kafka_connect
}
```

## Dapr Configuration

### Dapr Component for Kafka

```yaml
# dapr/components/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-events-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "todo-kafka.kafka.do-internal-nyc3.do:9092"
  - name: consumerGroup
    value: "todo-app-group"
  - name: authRequired
    value: "true"
  - name: sasl
    value: "plaintext"
  - name: username
    secretKeyRef:
      name: kafka-secrets
      key: username
  - name: password
    secretKeyRef:
      name: kafka-secrets
      key: password
```

### Dapr Component for Redis

```yaml
# dapr/components/redis-state.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-state
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-service:6379
  - name: redisPassword
    secretKeyRef:
      name: redis-secrets
      key: password
  - name: maxRetries
    value: "3"
  - name: failover
    value: "true"
```

### Dapr Sidecar Injection

```yaml
# deployments/backend-with-dapr.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "todo-backend"
    dapr.io/app-port: "8000"
    dapr.io/config: "dapr-config"
    dapr.io/enable-api-logging: "true"
spec:
  # ... deployment spec
```

### Dapr Configuration

```yaml
# dapr/config.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
  metrics:
    enabled: true
    rules:
      - name: todo-backend
        regex: ".*"
        labels:
          app: "todo-backend"
```

## Event-Driven Architecture with Kafka

### Todo Events

```python
# backend/events/schemas.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import json

@dataclass
class TodoCreatedEvent:
    """Event emitted when a todo is created."""
    event_type: str = "todo.created"
    todo_id: str
    user_id: str
    title: str
    description: Optional[str]
    priority: int
    created_at: str

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

@dataclass
class TodoUpdatedEvent:
    """Event emitted when a todo is updated."""
    event_type: str = "todo.updated"
    todo_id: str
    user_id: str
    changes: dict
    updated_at: str

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

@dataclass
class TodoDeletedEvent:
    """Event emitted when a todo is deleted."""
    event_type: str = "todo.deleted"
    todo_id: str
    user_id: str
    deleted_at: str

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
```

### Kafka Producer

```python
# backend/kafka/producer.py
from dapr.clients import DaprClient
from events.schemas import TodoCreatedEvent, TodoUpdatedEvent, TodoDeletedEvent

class TodoEventProducer:
    """Produces todo events to Kafka via Dapr."""

    def __init__(self):
        self.dapr = DaprClient()
        self.pubsub_name = "todo-events-pubsub"

    async def publish_created(self, event: TodoCreatedEvent):
        """Publish todo created event."""
        await self.dapr.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="todo-created",
            data=event.to_json(),
            data_content_type="application/json"
        )

    async def publish_updated(self, event: TodoUpdatedEvent):
        """Publish todo updated event."""
        await self.dapr.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="todo-updated",
            data=event.to_json(),
            data_content_type="application/json"
        )

    async def publish_deleted(self, event: TodoDeletedEvent):
        """Publish todo deleted event."""
        await self.dapr.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="todo-deleted",
            data=event.to_json(),
            data_content_type="application/json"
        )
```

### Kafka Consumer

```python
# backend/kafka/consumer.py
from dapr.clients import DaprClient
import json

class TodoEventConsumer:
    """Consumes todo events from Kafka via Dapr."""

    def __init__(self):
        self.dapr = DaprClient()
        self.pubsub_name = "todo-events-pubsub"

    async def subscribe_to_events(self):
        """Subscribe to all todo events."""

        # Subscribe to todo-created
        await self.dapr.subscribe(
            pubsub_name=self.pubsub_name,
            topic_name="todo-created",
            route="todo-created"
        )

        # Subscribe to todo-updated
        await self.dapr.subscribe(
            pubsub_name=self.pubsub_name,
            topic_name="todo-updated",
            route="todo-updated"
        )

        # Subscribe to todo-deleted
        await self.dapr.subscribe(
            pubsub_name=self.pubsub_name,
            topic_name="todo-deleted",
            route="todo-deleted"
        )

    async def handle_todo_created(self, data: dict):
        """Handle todo created event."""
        event = json.loads(data)
        print(f"Todo created: {event['todo_id']} - {event['title']}")

        # Update cache, send notifications, etc.

    async def handle_todo_updated(self, data: dict):
        """Handle todo updated event."""
        event = json.loads(data)
        print(f"Todo updated: {event['todo_id']}")

        # Update cache, send notifications, etc.

    async def handle_todo_deleted(self, data: dict):
        """Handle todo deleted event."""
        event = json.loads(data)
        print(f"Todo deleted: {event['todo_id']}")

        # Update cache, send notifications, etc.
```

## CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to DOKS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Configure AWS credentials (for state)
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: 1.5.0

    - name: Terraform Init
      run: terraform init

    - name: Terraform Plan
      run: terraform plan -out=tfplan

    - name: Terraform Apply
      run: terraform apply -auto-approve tfplan

    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: Build and push images
      run: |
        docker build -t todo-registry/todo-backend:${{ github.sha }} ./backend
        docker build -t todo-registry/todo-frontend:${{ github.sha }} ./frontend
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push todo-registry/todo-backend:${{ github.sha }}
        docker push todo-registry/todo-frontend:${{ github.sha }}

    - name: Deploy to Kubernetes
      run: |
        helm upgrade --install todo-app ./helm/todo-app \
          --set image.tag=${{ github.sha }} \
          --namespace production
```

## Cloud Deployment Commands

```bash
# Initialize Terraform
terraform init

# Plan infrastructure
terraform plan -out=tfplan

# Apply infrastructure
terraform apply -auto-approve

# Get cluster credentials
doctl kubernetes cluster kubeconfig save todo-cluster

# Deploy application
helm install todo-app ./helm/todo-app --namespace production

# Check deployment status
kubectl get pods -n production
kubectl get services -n production

# View logs
kubectl logs -f -n production deployment/backend

# Update deployment
helm upgrade todo-app ./helm/todo-app --namespace production

# Rollback
helm rollback todo-app -n production
```

## Monitoring on Cloud

### DigitalOcean Monitoring

```yaml
# Enable DO monitoring on resources
annotations:
  monitoring.digitalocean.com/scrape: "true"
  monitoring.digitalocean.com/port: "8000"
  monitoring.digitalocean.com/path: "/metrics"
```

## Outputs

This agent produces:

1. **Terraform Configs** - Infrastructure as Code for DOKS
2. **Dapr Components** - Kafka and Redis component configs
3. **Event Schemas** - Event definitions for Kafka topics
4. **CI/CD Pipeline** - GitHub Actions workflow for deployment

## Integration Points

- Works with **Kubernetes Architecture Agent** for K8s manifests
- Works with **Containerization Agent** for Docker images
- Works with **AI Agent Orchestration** for event-driven updates

## When to Use

Use this agent when:
- Deploying to DigitalOcean DOKS
- Setting up Kafka event streaming
- Configuring Dapr service mesh
- Managing cloud infrastructure with Terraform
- Implementing event-driven architecture
- Setting up CI/CD pipelines
