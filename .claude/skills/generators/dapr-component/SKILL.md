# Dapr Component Generator

**Critical for Phase:** V

Generates Dapr component configurations for pub/sub, state management, and secrets.

## Usage

```
/gen.dapr-component <component-type> "<config>"

# Examples:
/gen.dapr-component "pubsub.kafka" "Kafka brokers at localhost:9092, todo-events topic"
/gen.dapr-component "state.postgresql" "PostgreSQL connection, todo-keys table"
/gen.dapr-component "secret.kubernetes" "Kubernetes secret store for JWT and DB password"
/gen.dapr-component "bindings.cron" "Cron binding for daily reminder check"
```

## What It Generates

- Dapr component YAML files
- State store configurations
- Pub/sub broker settings
- Secret store definitions
- Binding configurations
- Scalers configuration
- Application config (config.yaml)

## Output Structure

```
phase-XX/k8s/dapr/
  ├── components/
  │   ├── pubsub-kafka.yaml         # Kafka pub/sub
  │   ├── state-postgres.yaml        # PostgreSQL state
  │   ├── secret-k8s.yaml          # Kubernetes secrets
  │   └── bindings-cron.yaml        # Cron bindings
  ├── config/
  │   └── dapr-config.yaml          # Dapr application config
  └── overlays/
      ├── dev/                       # Dev overrides
      ├── staging/                   # Staging overrides
      └── prod/                      # Production overrides
```

## Features

- Multiple state stores support
- Kafka pub/sub integration
- Kubernetes secret integration
- Input/output bindings
- Service invocation
- Actor state management
- Configuration management
- mTLS support

## Phase Usage

- **Phase V:** Kafka pub/sub component
- **Phase V:** PostgreSQL state store
- **Phase V:** Kubernetes secrets
- **Phase V:** Cron bindings for reminders
- **Phase V:** Dapr sidecar injection

## Example Outputs

### pubsub-kafka.yaml
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: production
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-broker-0.kafka.svc.cluster.local:9092,kafka-broker-1.kafka.svc.cluster.local:9092,kafka-broker-2.kafka.svc.cluster.local:9092"
  - name: authRequired
    value: "true"
  - name: sasl
    value: "plaintext"
  - name: consumerGroup
    value: "todo-consumer-group"
  - name: autoCommit
    value: "true"
  - name: initialOffset
    value: "newest"
  - name: maxMessageBytes
    value: "1024"
scopes:
  - todo-backend
  - ai-service
```

### state-postgres.yaml
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgres-state
  namespace: production
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secret
      key: connectionString
  - name: tableName
    value: "dapr_state"
  - name: cleanupInterval
    value: "1h"
  - name: maxConcurrentWrites
    value: "10"
  - name: keyPrefix
    value: "todo"
  - name: queryIndexes
    value: "id,created_at"
scopes:
  - todo-backend
  - ai-service
```

### secret-k8s.yaml
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secret-store
  namespace: production
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  - name: allowedSecrets
    value: "jwt-secret,postgres-password,api-key"
scopes:
  - todo-backend
  - ai-service
```

### bindings-cron.yaml
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: daily-reminder-cron
  namespace: production
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@daily"
  - name: direction
    value: "input"
  - name: data
    value: '{"action": "check_reminders"}'
scopes:
  - todo-backend
```

### dapr-config.yaml
```yaml
apiVersion: dapr.io/v1
kind: Configuration
metadata:
  name: dapr-config
  namespace: production
spec:
  # API tracing
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
  # Metrics
  metrics:
    enabled: true
    rules:
      - name: dapr-api
        labels:
          app: "todo-backend"
        regex: "dapr-api.*"
      - name: dapr-runtime
        labels:
          app: "todo-backend"
        regex: "dapr-runtime.*"
  # Application protocol
  http:
    maxRequestBodySize: 4
  # Feature flags
  features:
    - name: AppHealthCheck
      enabled: true
    - name: GracefulShutdown
      enabled: true
    - name: NameResolution
      enabled: true
  # mTLS configuration
  mtls:
    enabled: true
    workloadCertTTL: 3600s
  # API server
  api:
    allowedOrigins:
      - "https://todo.example.com"
    maxRequestSizeMB: 10
```

## Deployment with Dapr Sidecar

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  replicas: 3
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/config: "dapr-config"
        dapr.io/sidecar-cpu-request: "100m"
        dapr.io/sidecar-memory-request: "128Mi"
        dapr.io/sidecar-cpu-limit: "500m"
        dapr.io/sidecar-memory-limit: "512Mi"
    spec:
      containers:
        - name: todo-backend
          image: todo-backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DAPR_HTTP_PORT
              value: "3500"
            - name: DAPR_GRPC_PORT
              value: "50001"
```

## Dapr API Usage in Python

```python
from dapr.clients import DaprClient
import json

dapr = DaprClient()

# Save state
dapr.save_state(
    store_name="postgres-state",
    key=f"todo-{todo_id}",
    value=json.dumps(todo_data),
    state_metadata={"ttlInSeconds": 3600}
)

# Get state
state = dapr.get_state(store_name="postgres-state", key=f"todo-{todo_id}")

# Delete state
dapr.delete_state(store_name="postgres-state", key=f"todo-{todo_id}")

# Publish event
dapr.publish_event(
    pubsub_name="kafka-pubsub",
    topic="todo-events",
    data=json.dumps(event_data),
    metadata={"partitionKey": todo_id}
)

# Subscribe to topic
# (configured via subscriptions.yaml)
```

### subscriptions.yaml (Event Subscriptions)
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: todo-events-subscription
spec:
  topic: todo-events
  routes:
    - rule:
        match: 'event.type == "TodoCreated"'
      path: /api/v1/todos/handle-created
    - rule:
        match: 'event.type == "TodoCompleted"'
      path: /api/v1/todos/handle-completed
  pubsubname: kafka-pubsub
  deadLetterTopic: todo-events-dlt
```

## Component Types Supported

| Type | Description | Use Case |
|-------|-------------|-----------|
| `state.postgresql` | PostgreSQL state store | Actor state, user sessions |
| `state.redis` | Redis state store | Cache, fast lookups |
| `pubsub.kafka` | Kafka pub/sub | Event streaming |
| `pubsub.redis` | Redis pub/sub | Real-time events |
| `secretstores.kubernetes` | K8s secrets | Passwords, API keys |
| `bindings.cron` | Cron scheduler | Reminders, cleanup jobs |
| `bindings.http` | HTTP input/output | Webhook integrations |
| `bindings.smtp` | Email binding | Notifications |
| `bindings.mongodb` | MongoDB binding | Document storage |

## Configuration Files

```
k8s/dapr/
  ├── components/           # Component definitions
  ├── config/
  │   └── dapr-config.yaml
  ├── subscriptions/       # Event subscriptions
  ├── overlays/
  │   ├── dev/
  │   ├── staging/
  │   └── prod/
  └── secrets/             # Dapr secrets
```

## Best Practices

- Use secrets store for sensitive data
- Enable mTLS for production
- Configure tracing for observability
- Use consumer groups for scaling
- Set appropriate retention for state
- Configure dead-letter topics
- Enable health checks
- Set resource limits on sidecar
- Use partition keys for Kafka ordering
- Configure TTL for state to avoid bloat

## Dapr CLI Commands

```bash
# Initialize Dapr in Kubernetes
dapr init --kubernetes --runtime-version=1.13.0

# Verify Dapr installation
dapr status --kubernetes

# List components
dapr components -k

# List configurations
dapr configurations -k

# Get logs
dapr logs --kubernetes --app-id todo-backend --namespace production

# Uninstall Dapr
dapr uninstall --kubernetes
```
