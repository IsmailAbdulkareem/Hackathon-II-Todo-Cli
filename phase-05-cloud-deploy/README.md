# Phase V: Advanced Cloud Deployment

**Status:** 🔜 Pending
**Points:** 300
**Tech Stack:** Kafka, Dapr, DigitalOcean DOKS
**Due Date:** Jan 18, 2026

## Overview

Phase V deploys the application to DigitalOcean Kubernetes (DOKS) with enterprise-grade features including Kafka event streaming and Dapr for distributed application runtime.

## What's New

### Event Streaming
- **Kafka**: Distributed event bus for async processing
- **Event Sourcing**: Complete audit trail of todo changes
- **CQRS Pattern**: Separate read/write models
- **Event Replay**: Rebuild state from event log

### Dapr Integration
- **Service Invocation**: Secure service-to-service communication
- **State Management**: Abstraction for multiple stores
- **Pub/Sub**: Decoupled event publishing
- **Secrets Management**: Secure credential handling
- **Distributed Tracing**: End-to-end observability

### Cloud-Native
- **DigitalOcean DOKS**: Managed Kubernetes
- **Auto-scaling**: Cluster auto-scaler
- **GitOps**: ArgoCD for continuous delivery
- **CI/CD**: GitHub Actions for automation
- **Multi-region**: Global deployment strategy

## Prerequisites

```bash
# Install doctl (DigitalOcean CLI)
curl -sSL https://dl.digitalocean.com/doctl/install.sh | sh

# Install ArgoCD CLI
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x argocd-linux-amd64
sudo mv argocd-linux-amd64 /usr/local/bin/argocd

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Install Kafka CLI Tools (kafkacat)
# For event inspection and debugging
sudo apt-get install kafkacat
```

## Quick Start

### 1. Create DigitalOcean Kubernetes Cluster

```bash
# Authenticate with DigitalOcean
doctl auth init

# Create DOKS cluster
doctl kubernetes cluster create todo-app-cluster \
  --region nyc1 \
  --version latest \
  --node-pool "name=worker-pool;count=3;size=s-4vcpu-8gb" \
  --auto-upgrade

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-app-cluster

# Verify connection
kubectl get nodes
```

### 2. Set Up Kafka (Strimzi)

```bash
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka

# Deploy Kafka cluster
kubectl apply -f k8s/kafka/kafka-cluster.yaml

# Wait for Kafka to be ready
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=300s -n kafka

# Create topics
kubectl apply -f k8s/kafka/topics.yaml
```

### 3. Install Dapr

```bash
# Initialize Dapr in Kubernetes
dapr init --kubernetes --enable-ha=true --enable-mtls=true

# Verify installation
dapr status --kubernetes

# Install Dapr components (Redis for state, Kafka for pub/sub)
kubectl apply -f k8s/dapr/components/
```

### 4. Deploy Application with ArgoCD

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get initial admin password
argocd admin initial-password -n argocd

# Create application from git
argocd app create todo-app \
  --repo https://github.com/your-org/todo-app.git \
  --path phase-05-cloud-deploy/argo \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace production

# Sync application
argocd app sync todo-app
```

### 5. Access Application

```bash
# Get external IP
kubectl get svc -n production

# Access via load balancer or ingress
http://<external-ip>
```

## Project Structure

```
phase-05-cloud-deploy/
├── k8s/
│   ├── kafka/
│   │   ├── kafka-cluster.yaml    # Kafka cluster definition
│   │   ├── topics.yaml           # Kafka topics
│   │   └── connectors.yaml       # Kafka Connect
│   ├── dapr/
│   │   ├── components/           # Dapr components
│   │   │   ├── pubsub.yaml       # Kafka pub/sub
│   │   │   ├── state.yaml        # Redis state
│   │   │   └── secret.yaml       # Secret store
│   │   └── config/
│   │       └── dapr-config.yaml  # Dapr config
│   ├── base/                    # Kustomize base
│   └── overlays/
│       ├── production/
│       └── staging/
├── argo/
│   ├── Application.yaml         # ArgoCD app definition
│   └── kustomization.yaml
├── terraform/                   # Infrastructure as Code
│   ├── main.tf                  # DO resources
│   ├── variables.tf             # Variables
│   └── outputs.tf               # Outputs
├── src/
│   ├── events/                   # Event sourcing
│   │   ├── todo_events.py       # Event definitions
│   │   ├── event_store.py       # Event storage
│   │   └── projection.py        # Read projections
│   ├── sagas/                   # Saga orchestration
│   │   └── todo_saga.py         # Distributed transactions
│   └── dapr/                    # Dapr integration
│       ├── dapr_client.py       # Dapr client
│       └── actors.py            # Virtual actors
├── github-workflows/            # CI/CD
│   ├── build-and-push.yml
│   ├── deploy.yml
│   └── drift-detection.yml
└── monitoring/
    ├── prometheus/
    ├── grafana/
    └── alerts/
```

## Event Architecture

### Kafka Topics

| Topic | Purpose | Partitions | Retention |
|-------|---------|------------|-----------|
| `todo-events` | Todo change events | 3 | 7 days |
| `todo-commands` | Incoming commands | 3 | 7 days |
| `todo-notifications` | Notification events | 2 | 1 day |
| `todo-analytics` | Analytics events | 3 | 30 days |

### Event Types

```json
// TodoCreatedEvent
{
  "eventId": "uuid",
  "eventType": "TodoCreated",
  "aggregateId": "todo-123",
  "data": {
    "title": "Buy groceries",
    "description": "Milk, eggs"
  },
  "timestamp": "2025-12-31T10:00:00Z"
}

// TodoCompletedEvent
{
  "eventId": "uuid",
  "eventType": "TodoCompleted",
  "aggregateId": "todo-123",
  "data": {
    "completedBy": "user-456"
  },
  "timestamp": "2025-12-31T14:30:00Z"
}
```

## Dapr Architecture

### Services with Dapr Sidecars

```
[Frontend] --(HTTP)--> [Frontend Dapr Sidecar]
                                      |
                                      v
[Backend Service] <--(gRPC)--> [Backend Dapr Sidecar] --(Pub/Sub)--> [Kafka]
                                     |
                                     v
                                  [Dapr State Store (Redis)]
                                     |
                                     v
                                  [Dapr Secret Store]
```

### Dapr Capabilities Used

1. **Service Invocation**
   ```python
   # Call backend service
   dapr.invoke_method(
       app_id='todo-backend',
       method_name='create-todo',
       data=todo_data
   )
   ```

2. **Pub/Sub**
   ```python
   # Publish event
   dapr.publish_event(
       pubsub_name='kafka-pubsub',
       topic='todo-events',
       data=event_data
   )
   ```

3. **State Management**
   ```python
   # Save state
   dapr.save_state(
       store_name='redis-store',
       key='todo-123',
       value=todo_data
   )
   ```

4. **Secret Management**
   ```python
   # Get secret
   secret = dapr.get_secret(
       secret_store_name='kubernetes',
       key='database-password'
   )
   ```

## CI/CD Pipeline (GitHub Actions)

### Build & Push
```yaml
name: Build and Push
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: |
          docker build -t todo-backend:${{ github.sha }} ./backend
          docker build -t todo-frontend:${{ github.sha }} ./frontend
      - name: Push to registry
        run: |
          docker push todo-backend:${{ github.sha }}
          docker push todo-frontend:${{ github.sha }}
```

### Deploy to Production
```yaml
name: Deploy
on:
  push:
    tags: ['v*']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Update ArgoCD app
        run: |
          argocd app sync todo-app
          argocd app wait todo-app
```

## Monitoring & Observability

### Prometheus + Grafana Stack

```bash
# Deploy Prometheus Operator
kubectl apply -f monitoring/prometheus-operator/

# Deploy Grafana
kubectl apply -f monitoring/grafana/

# Access Grafana
kubectl port-forward svc/grafana 3000:80 -n monitoring
```

### Key Metrics to Monitor

- **Application Metrics**
  - Request rate (RPS)
  - Error rate (5xx)
  - Latency (p95, p99)
  - Active connections

- **Kafka Metrics**
  - Message throughput
  - Consumer lag
  - Partition size
  - Producer errors

- **Dapr Metrics**
  - Sidecar latency
  - Service invocation success rate
  - Pub/sub message rate
  - State operations

- **Kubernetes Metrics**
  - Pod restarts
  - CPU/Memory usage
  - Network traffic
  - PVC usage

### Alerting (Prometheus AlertManager)

```yaml
# Critical alerts
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  annotations:
    summary: "High error rate detected"

- alert: KafkaConsumerLag
  expr: kafka_consumergroup_lag > 1000
  annotations:
    summary: "Kafka consumer lag is high"

- alert: PodNotReady
  expr: kube_pod_status_ready{condition="true"} == 0
  annotations:
    summary: "Pod is not ready"
```

## Disaster Recovery & Backup

### Backup Strategy

1. **Database Backups**
   - Automated daily snapshots
   - Point-in-time recovery
   - Cross-region replication

2. **Kafka Data Backup**
   - Mirror topics to DR cluster
   - Retention policy: 30 days
   - Regular compaction

3. **Kubernetes Backups**
   - Velero for cluster backups
   - Etcd snapshots
   - Config/Secret backup

### Rollback Procedure

```bash
# ArgoCD rollback
argocd app sync todo-app --revision <previous-commit>

# Manual Kubernetes rollback
kubectl rollout undo deployment/todo-backend

# Kafka topic reset (if needed)
kubectl delete kafkatopic todo-events -n kafka
kubectl apply -f k8s/kafka/topics.yaml
```

## Security

### Zero Trust Architecture

- **mTLS**: Mutual TLS for all service communication
- **RBAC**: Strict role-based access control
- **Network Policies**: Default deny all
- **Secrets**: Encrypted at rest and in transit

### Compliance

- **Audit Logging**: All actions logged
- **Data Encryption**: AES-256 for sensitive data
- **PII Protection**: Data masking for logs
- **SOC2 Ready**: Security controls in place

## Cost Optimization

### DigitalOcean Costs

- **DOKS Cluster**: $120/month (3x s-4vcpu-8gb)
- **Load Balancer**: $20/month
- **Block Storage**: $0.10/GB/month
- **Kafka**: Included in cluster (or $60/month external)

### Optimization Strategies

1. **Auto-scaling**
   ```yaml
   clusterAutoscaler:
     enabled: true
     minNodes: 2
     maxNodes: 5
   ```

2. **Spot Instances** (if supported)
3. **Resource Limits**: Prevent over-provisioning
4. **Image Optimization**: Multi-stage builds

## Performance Tuning

### Kafka Tuning

```yaml
# Producer optimization
acks: all
compression.type: lz4
linger.ms: 10
batch.size: 32768

# Consumer optimization
fetch.min.bytes: 1024
max.poll.records: 500
fetch.max.wait.ms: 500
```

### Dapr Tuning

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
spec:
  tracing:
    samplingRate: "1"
  featureFlags:
    name: "enableGracefulShutdown"
    enabled: true
```

## Multi-Region Deployment

### Active-Active Setup

```
Region A (nyc1)    Region B (sfo1)
     |                    |
[App Cluster]        [App Cluster]
     |                    |
[Event Bus A]  <--->  [Event Bus B]
     |                    |
[Database A]          [Database B]
```

### Cross-Region Replication

- Kafka MirrorMaker 2.0
- Database replication (PostgreSQL)
- DNS round-robin or geo-routing
- Session affinity if needed

## Testing

### Chaos Engineering

```bash
# Install Chaos Mesh
kubectl apply -f https://mirrors.chaos-mesh.org/v1.3.0/install.yaml

# Test pod failure
kubectl apply -f chaos/pod-kill-experiment.yaml

# Test network partition
kubectl apply -f chaos/network-partition.yaml
```

### Load Testing

```bash
# Use k6 or Locust
k6 run scripts/load-test.js

# Test metrics
- Target: 1000 RPS
- P95 latency: < 100ms
- Error rate: < 0.1%
```

## Documentation

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Dapr Documentation](https://docs.dapr.io/)
- [DigitalOcean DOKS Docs](https://docs.digitalocean.com/products/kubernetes/)
- [ArgoCD Documentation](https://argoproj.github.io/argo-cd/)

## Cleanup

```bash
# Delete ArgoCD application
argocd app delete todo-app

# Delete DOKS cluster
doctl kubernetes cluster delete todo-app-cluster

# Remove local tools (optional)
dapr uninstall --kubernetes
```

---

**Total Project Points: 1,000**
**Estimated Completion: January 18, 2026**
