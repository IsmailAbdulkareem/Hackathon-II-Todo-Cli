# TaskAI Architecture

## Overview

TaskAI is a cloud-native, event-driven task management system built on microservices architecture. The system leverages Kubernetes for orchestration, Dapr for distributed application runtime, and Kafka for event streaming.

## Architecture Diagram

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

## Core Components

### 1. Frontend Service
- **Technology**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Port**: 3000
- **Responsibilities**:
  - User interface for task management
  - Real-time task updates via WebSocket/polling
  - Tag management with autocomplete
  - Advanced filtering and search
  - Due date and reminder management
  - AI-powered natural language task creation

### 2. Backend API Service
- **Technology**: Python 3.13+, FastAPI
- **Port**: 8000
- **Dapr App ID**: backend-api
- **Responsibilities**:
  - RESTful API for task CRUD operations
  - User authentication and authorization (JWT)
  - Tag management and search
  - AI integration (OpenAI GPT-4) for natural language processing
  - Event publishing to Kafka via Dapr
  - Real-time synchronization endpoint
  - Due date validation and reminder scheduling

### 3. Recurring Service
- **Technology**: Python 3.13+, FastAPI
- **Port**: 8002
- **Dapr App ID**: recurring-service
- **Responsibilities**:
  - Subscribe to task-events topic
  - Calculate next occurrence for recurring tasks
  - Create new task instances based on recurrence rules
  - Handle recurrence patterns (daily, weekly, monthly, custom)
  - Audit trail for recurring task generation

### 4. Notification Service
- **Technology**: Python 3.13+, FastAPI
- **Port**: 8001
- **Dapr App ID**: notification-service
- **Responsibilities**:
  - Subscribe to reminders topic
  - Send email notifications via Resend API
  - Retry logic for failed notifications
  - Notification delivery tracking
  - Support for multiple notification types (15min, 1hr, 1day, 1week, custom)

## Data Architecture

### Database Schema

TaskAI uses PostgreSQL with service-specific schemas:

```sql
-- Schema: public (shared)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Schema: tasks (backend-api owns)
CREATE SCHEMA tasks;

CREATE TABLE tasks.tasks (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(50) DEFAULT 'medium',
    due_date TIMESTAMP,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tasks.tags (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7),
    UNIQUE(user_id, name)
);

CREATE TABLE tasks.task_tags (
    task_id UUID REFERENCES tasks.tasks(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tasks.tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

-- Schema: notifications (notification-service owns)
CREATE SCHEMA notifications;

CREATE TABLE notifications.notification_log (
    id UUID PRIMARY KEY,
    task_id UUID,
    user_id UUID,
    notification_type VARCHAR(50),
    status VARCHAR(50),
    sent_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0
);

-- Schema: audit (recurring-service owns)
CREATE SCHEMA audit;

CREATE TABLE audit.task_audit (
    id UUID PRIMARY KEY,
    task_id UUID,
    action VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Indexes

```sql
-- Performance indexes
CREATE INDEX idx_tasks_user_id ON tasks.tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks.tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks.tasks(due_date);
CREATE INDEX idx_tasks_created_at ON tasks.tasks(created_at);

-- Full-text search index
CREATE INDEX idx_tasks_search ON tasks.tasks USING GIN(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Tag indexes
CREATE INDEX idx_tags_user_id ON tasks.tags(user_id);
CREATE INDEX idx_task_tags_task_id ON tasks.task_tags(task_id);
CREATE INDEX idx_task_tags_tag_id ON tasks.task_tags(tag_id);
```

## Event-Driven Architecture

### Event Flow

1. **Task Creation/Update** (Backend API):
   ```python
   # Backend API publishes event
   await dapr_client.publish_event(
       pubsub_name="kafka-pubsub",
       topic_name="task-events",
       data={
           "event_type": "created",  # or "updated", "completed", "deleted"
           "task_id": task.id,
           "task_data": task.dict(),
           "user_id": user_id,
           "timestamp": datetime.utcnow().isoformat()
       }
   )
   ```

2. **Recurring Task Processing** (Recurring Service):
   ```python
   # Recurring Service subscribes to task-events
   @app.post("/task-events")
   async def handle_task_event(event: TaskEvent):
       if event.event_type == "completed" and event.task_data.is_recurring:
           next_task = calculate_next_occurrence(event.task_data)
           await create_next_task(next_task)
   ```

3. **Reminder Notifications** (Notification Service):
   ```python
   # Notification Service subscribes to reminders
   @app.post("/reminders")
   async def handle_reminder(reminder: Reminder):
       await send_email_notification(reminder)
   ```

### Kafka Topics

- **task-events**: Task lifecycle events (created, updated, completed, deleted)
  - Partitions: 3
  - Retention: 7 days
  - Consumers: recurring-service

- **reminders**: Scheduled reminder notifications
  - Partitions: 3
  - Retention: 7 days
  - Consumers: notification-service

## Dapr Integration

### Components

1. **Pub/Sub (Kafka)**:
   ```yaml
   apiVersion: dapr.io/v1alpha1
   kind: Component
   metadata:
     name: kafka-pubsub
   spec:
     type: pubsub.kafka
     metadata:
     - name: brokers
       value: "taskai-kafka-kafka-bootstrap.taskai.svc.cluster.local:9092"
     - name: consumerGroup
       value: "taskai-group"
   ```

2. **State Store (PostgreSQL)**:
   ```yaml
   apiVersion: dapr.io/v1alpha1
   kind: Component
   metadata:
     name: statestore
   spec:
     type: state.postgresql
     metadata:
     - name: connectionString
       value: "host=postgres port=5432 user=taskai password=secret dbname=taskai"
   ```

3. **Secrets Store (Kubernetes)**:
   ```yaml
   apiVersion: dapr.io/v1alpha1
   kind: Component
   metadata:
     name: kubernetes-secrets
   spec:
     type: secretstores.kubernetes
   ```

### Sidecar Pattern

Each service (except frontend) runs with a Dapr sidecar:

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend-api"
  dapr.io/app-port: "8000"
  dapr.io/enable-api-logging: "true"
  dapr.io/log-level: "info"
```

## Deployment Architecture

### Kubernetes Resources

- **Namespaces**: taskai (production), taskai-dev (development)
- **Deployments**: 4 services with configurable replicas
- **Services**: ClusterIP for internal communication
- **Ingress**: NGINX for external access
- **ConfigMaps**: Shared configuration
- **Secrets**: Sensitive data (credentials, API keys)

### Resource Allocation

| Service | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|----------|-------------|-----------|----------------|--------------|
| Backend API | 2 | 250m | 500m | 256Mi | 512Mi |
| Recurring Service | 1 | 100m | 250m | 128Mi | 256Mi |
| Notification Service | 1 | 100m | 250m | 128Mi | 256Mi |
| Frontend | 2 | 250m | 500m | 256Mi | 512Mi |

### Health Checks

All services implement health checks:

- **Liveness Probe**: Ensures container is running
  - Path: `/health` (backend services), `/` (frontend)
  - Initial Delay: 30s
  - Period: 10s

- **Readiness Probe**: Ensures service is ready to accept traffic
  - Path: `/health` (backend services), `/` (frontend)
  - Initial Delay: 10s
  - Period: 5s

## Security Architecture

### Authentication & Authorization

- **JWT-based authentication**: Stateless token-based auth
- **Token expiration**: Configurable (default: 24 hours)
- **Password hashing**: bcrypt with salt
- **HTTPS**: TLS termination at ingress

### Secrets Management

- **Kubernetes Secrets**: Encrypted at rest
- **Environment Variables**: Injected from ConfigMaps/Secrets
- **No hardcoded credentials**: All sensitive data externalized

### Network Security

- **Service-to-service**: Internal ClusterIP services
- **External access**: Only through ingress
- **Dapr mTLS**: Automatic mutual TLS between services

## Scalability

### Horizontal Scaling

- **Backend API**: Scale to handle increased load
- **Frontend**: Scale for more concurrent users
- **Recurring/Notification Services**: Single replica (stateful processing)

### Vertical Scaling

- Adjust resource limits based on monitoring
- Use Horizontal Pod Autoscaler (HPA) for automatic scaling

### Database Scaling

- **Read replicas**: For read-heavy workloads
- **Connection pooling**: Optimize database connections
- **Partitioning**: For large datasets

## Monitoring & Observability

### Metrics

- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Dapr metrics**: Built-in observability

### Logging

- **Structured logging**: JSON format
- **Log aggregation**: ELK stack or cloud-native solutions
- **Dapr logging**: Sidecar logs for distributed tracing

### Tracing

- **Distributed tracing**: Dapr + Zipkin/Jaeger
- **Request correlation**: Trace IDs across services

## Disaster Recovery

### Backup Strategy

- **Database backups**: Daily automated backups
- **Configuration backups**: GitOps approach
- **Kafka topic retention**: 7 days

### High Availability

- **Multi-replica deployments**: For critical services
- **Pod disruption budgets**: Ensure availability during updates
- **Health checks**: Automatic pod restart on failure

## Technology Stack Summary

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend | Python 3.13+, FastAPI |
| Database | PostgreSQL 15+ |
| Message Broker | Apache Kafka (Strimzi) |
| Runtime | Dapr 1.12+ |
| Orchestration | Kubernetes 1.28+ |
| Ingress | NGINX Ingress Controller |
| AI | OpenAI GPT-4 |
| Email | Resend API |

## Future Enhancements

- **Caching layer**: Redis for improved performance
- **GraphQL API**: Alternative to REST
- **WebSocket support**: Real-time bidirectional communication
- **Mobile apps**: React Native or Flutter
- **Advanced analytics**: Task completion insights
- **Collaboration features**: Shared tasks and teams
- **Integration APIs**: Third-party service integrations

---

**Last Updated**: 2026-02-14
**Version**: 1.0.0
