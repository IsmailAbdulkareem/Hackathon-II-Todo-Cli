# Phase 0: Research & Architectural Decisions

**Feature**: Phase 5 Part A - Advanced Task Management Features
**Date**: 2026-02-14
**Status**: Complete

## Overview

This document captures the research findings and architectural decisions for transforming the monolithic Todo application into TaskAI with microservices architecture, event-driven communication, and dual interface design.

## Key Architectural Decisions

### Decision 1: Microservices Architecture (4 Services)

**Decision**: Restructure from monolithic backend into 4 independent microservices:
1. Backend API (Port 8000) - Core task management, authentication, MCP server
2. Recurring Service (Port 8002) - Automatic recurring task creation
3. Notification Service (Port 8001) - Reminder email delivery
4. Frontend (Port 3000) - Dual interface (Chat + Tasks modes)

**Rationale**:
- **Independent Scaling**: Notification service can scale independently during high reminder load
- **Separation of Concerns**: Each service has single responsibility (task management, scheduling, notifications, UI)
- **Event-Driven Requirements**: Recurring tasks and reminders require asynchronous event processing
- **Deployment Flexibility**: Services can be deployed, updated, and rolled back independently
- **Technology Diversity**: Frontend (TypeScript/Next.js) and backend services (Python/FastAPI) use optimal languages for their domains

**Alternatives Considered**:
- **Monolithic Architecture**: Rejected because it cannot support exact-time reminder scheduling via Dapr Jobs API or event-driven recurring task creation. Would create tight coupling between task management, scheduling, and notifications.
- **2-Service Architecture (Backend + Frontend)**: Rejected because combining recurring logic and notifications in backend would create tight coupling and prevent independent scaling of notification delivery.
- **6+ Service Architecture (separate services for tags, search, etc.)**: Rejected as over-engineering. Current 4-service design provides sufficient separation without excessive operational complexity.

**Trade-offs**:
- **Increased Operational Complexity**: More services to deploy, monitor, and maintain
- **Network Latency**: Inter-service communication adds latency (mitigated by Dapr service invocation with <10ms overhead)
- **Distributed Transactions**: No distributed transactions needed (eventual consistency acceptable for recurring tasks and reminders)

---

### Decision 2: Event-Driven Architecture with Kafka

**Decision**: Use Apache Kafka (via Redpanda locally, Strimzi on Kubernetes) for asynchronous event communication between services.

**Topics**:
- `task-events`: Task lifecycle events (created, updated, completed, deleted)
- `reminders`: Scheduled reminder notifications
- `task-updates` (optional): Real-time sync events for frontend

**Rationale**:
- **Reliable Event Delivery**: Kafka provides at-least-once delivery guarantees for critical events (task completion → recurring task creation)
- **Event Sourcing**: Task events provide audit trail and enable event replay for debugging
- **Decoupling**: Services communicate via events without direct dependencies
- **Scalability**: Kafka handles 10,000+ concurrent users with horizontal scaling
- **Performance**: <5 second latency requirement for recurring task creation and reminder delivery achievable with Kafka's low-latency design

**Alternatives Considered**:
- **Direct HTTP Calls**: Rejected because it creates tight coupling, single points of failure, and cannot meet <5 second latency requirements with retries and circuit breakers.
- **Database Polling**: Rejected because polling introduces latency (minimum 1-5 second intervals) and increases database load. Cannot meet real-time requirements.
- **RabbitMQ**: Rejected because Kafka provides better horizontal scalability, event replay capabilities, and native Kubernetes integration via Strimzi operator.
- **Redis Pub/Sub**: Rejected because it lacks persistence and delivery guarantees. Lost events would cause missed recurring tasks and reminders.

**Trade-offs**:
- **Operational Complexity**: Kafka cluster requires monitoring, partition management, and rebalancing
- **Storage Requirements**: Event retention requires disk space (mitigated by 7-day retention policy)
- **Learning Curve**: Team must understand Kafka concepts (topics, partitions, consumer groups)

---

### Decision 3: Dapr Integration (5 Building Blocks)

**Decision**: Use Dapr (Distributed Application Runtime) for service coordination, providing:
1. **Pub/Sub**: Kafka abstraction for event publishing and subscription
2. **State Management**: PostgreSQL state store for chat conversation history
3. **Service Invocation**: Frontend → Backend with built-in retries, circuit breakers, mTLS
4. **Jobs API**: Exact-time reminder scheduling (NOT cron bindings)
5. **Secrets Management**: Kubernetes Secrets via Dapr API

**Rationale**:
- **Jobs API**: Only solution for exact-time reminder scheduling. Cron cannot schedule reminders at arbitrary times (e.g., "15 minutes before 2:37 PM"). Dapr Jobs API supports one-time scheduled jobs with exact timestamps.
- **Resilience Patterns**: Built-in retries (exponential backoff), circuit breakers, and timeouts without custom implementation
- **Polyglot Support**: Python services and TypeScript frontend use same Dapr APIs
- **Observability**: Automatic distributed tracing, metrics, and logging
- **Security**: mTLS between services without certificate management

**Alternatives Considered**:
- **Native Kafka Clients**: Rejected because it requires custom retry logic, circuit breakers, and connection management. Dapr provides these patterns out-of-the-box.
- **Custom Job Scheduling**: Rejected because implementing exact-time scheduling with persistence, failure recovery, and distributed coordination is complex. Dapr Jobs API provides this functionality.
- **Service Mesh (Istio)**: Rejected because Dapr provides application-level abstractions (Pub/Sub, State, Jobs) that service meshes don't offer. Dapr is lighter-weight for this use case.
- **Direct Service Calls**: Rejected because it lacks resilience patterns and would require custom implementation of retries, circuit breakers, and service discovery.

**Trade-offs**:
- **Dapr Dependency**: Services depend on Dapr sidecar availability
- **Sidecar Overhead**: Each service pod runs Dapr sidecar (~50MB memory, <10ms latency)
- **Dapr Learning Curve**: Team must understand Dapr concepts and APIs

---

### Decision 4: Shared PostgreSQL Database with Service-Specific Schemas

**Decision**: Use single PostgreSQL 15+ database with service-specific schemas:
- `public` schema: Shared tables (users, authentication)
- `tasks` schema: Backend API owns (tasks, tags, task_tags, reminders, recurrence_rules)
- `notifications` schema: Notification Service owns (notification_log, retry_attempts)
- `audit` schema: Recurring Service owns (task_audit, recurrence_history)

**Rationale**:
- **Data Consistency**: Single database ensures ACID transactions for task operations
- **Simplified Deployment**: One database to manage, backup, and monitor
- **Schema Isolation**: Service-specific schemas provide logical separation and ownership
- **Performance**: No cross-database joins or distributed transactions needed
- **Cost**: Single database instance reduces infrastructure costs

**Alternatives Considered**:
- **Database per Service**: Rejected because it requires distributed transactions for task operations, increases operational complexity (3+ databases), and complicates data consistency.
- **Shared Schema**: Rejected because it creates tight coupling and prevents independent schema evolution. Service-specific schemas provide better separation.
- **NoSQL (MongoDB)**: Rejected because relational data model (tasks, tags, many-to-many relationships) fits PostgreSQL better. ACID transactions required for task operations.

**Trade-offs**:
- **Shared Resource**: Database becomes shared dependency (mitigated by connection pooling and schema isolation)
- **Schema Coordination**: Schema changes require coordination between services (mitigated by migration scripts and versioning)

---

### Decision 5: Next.js 16 with App Router for Frontend

**Decision**: Use Next.js 16 with App Router, React 19, and Tailwind CSS for frontend.

**Rationale**:
- **Server Components**: React Server Components reduce client-side JavaScript and improve performance
- **App Router**: File-based routing with layouts simplifies dual interface structure (tasks/ and chat/ routes)
- **Built-in Optimization**: Automatic code splitting, image optimization, and font optimization
- **TypeScript Support**: First-class TypeScript support for type safety
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Vercel Deployment**: Seamless deployment to Vercel for frontend hosting

**Alternatives Considered**:
- **Create React App**: Rejected because it lacks server-side rendering, built-in routing, and optimization features. Next.js provides better performance and developer experience.
- **Vue.js/Nuxt**: Rejected because team has React expertise and React 19 provides better concurrent rendering for real-time sync.
- **Angular**: Rejected because it's heavier-weight and has steeper learning curve. Next.js provides simpler mental model for this use case.
- **Svelte/SvelteKit**: Rejected because smaller ecosystem and less mature tooling compared to Next.js.

**Trade-offs**:
- **Framework Lock-in**: Next.js-specific features (App Router, Server Components) create framework dependency
- **Build Complexity**: Next.js build process is more complex than simple React apps
- **Learning Curve**: App Router and Server Components require understanding new patterns

---

### Decision 6: FastAPI for Backend Services

**Decision**: Use FastAPI with Python 3.13+ for all backend services (Backend API, Recurring Service, Notification Service).

**Rationale**:
- **Async Support**: Native async/await for high-concurrency operations (10,000+ concurrent users)
- **Type Safety**: Pydantic models provide runtime validation and automatic OpenAPI schema generation
- **Performance**: FastAPI is one of the fastest Python frameworks (comparable to Node.js and Go)
- **Developer Experience**: Automatic interactive API docs (Swagger UI), type hints, and validation
- **Ecosystem**: Rich ecosystem for PostgreSQL (asyncpg), Kafka (aiokafka), and Dapr (dapr-python-sdk)

**Alternatives Considered**:
- **Django**: Rejected because it's synchronous by default and heavier-weight. FastAPI provides better async support and performance.
- **Flask**: Rejected because it lacks built-in async support, type validation, and automatic API documentation. FastAPI provides better developer experience.
- **Node.js/Express**: Rejected because Python provides better data processing libraries and team has Python expertise.
- **Go**: Rejected because Python provides faster development velocity and better AI/ML library support for chat interface.

**Trade-offs**:
- **Python Performance**: Python is slower than compiled languages (Go, Rust) but sufficient for this use case
- **GIL Limitations**: Python GIL limits CPU-bound parallelism (mitigated by async I/O and horizontal scaling)

---

### Decision 7: OpenAI GPT-4 with MCP for Chat Interface

**Decision**: Use OpenAI GPT-4 via Model Context Protocol (MCP) with 18 custom tools for task management.

**MCP Tools** (18 total):
1. `create_task` - Create new task with attributes
2. `update_task` - Update existing task
3. `delete_task` - Delete task
4. `complete_task` - Mark task as completed
5. `list_tasks` - List tasks with filters
6. `search_tasks` - Full-text search
7. `add_tag` - Add tag to task
8. `remove_tag` - Remove tag from task
9. `set_priority` - Set task priority (Low/Medium/High)
10. `set_due_date` - Set task due date
11. `add_reminder` - Add reminder to task
12. `remove_reminder` - Remove reminder from task
13. `create_recurring_task` - Create recurring task
14. `list_tags` - List all user tags
15. `filter_by_priority` - Filter tasks by priority
16. `filter_by_tags` - Filter tasks by tags
17. `filter_by_due_date` - Filter tasks by due date range
18. `get_task_details` - Get detailed task information

**Rationale**:
- **Natural Language Understanding**: GPT-4 provides best-in-class natural language understanding for task commands
- **MCP Protocol**: Standardized protocol for AI-tool integration with built-in error handling and validation
- **Tool Calling**: GPT-4 function calling enables structured task operations from natural language
- **Context Management**: MCP provides conversation history management via Dapr state store
- **Extensibility**: Easy to add new tools as features evolve

**Alternatives Considered**:
- **Claude 3.5 Sonnet**: Rejected because OpenAI GPT-4 has better function calling accuracy and MCP integration is more mature.
- **Open-Source LLMs (Llama 3, Mistral)**: Rejected because they require self-hosting infrastructure and have lower accuracy for function calling.
- **Rule-Based NLP**: Rejected because it cannot handle natural language variations and requires extensive pattern matching. GPT-4 provides better user experience.
- **Custom Fine-Tuned Model**: Rejected because it requires training data, infrastructure, and maintenance. GPT-4 provides sufficient accuracy out-of-the-box.

**Trade-offs**:
- **API Costs**: OpenAI API costs ~$0.01 per 1000 tokens (mitigated by caching and prompt optimization)
- **Latency**: API calls add 500-1000ms latency (acceptable for chat interface)
- **External Dependency**: Requires OpenAI API availability (mitigated by error handling and fallback messages)

---

### Decision 8: Kubernetes Deployment (Minikube Local, AKS/GKE/OKE Cloud)

**Decision**: Deploy to Kubernetes using:
- **Local Development**: Minikube with raw Kubernetes manifests
- **Cloud Deployment**: Azure Kubernetes Service (AKS), Google Kubernetes Engine (GKE), or Oracle Kubernetes Engine (OKE) with Helm charts

**Rationale**:
- **Container Orchestration**: Kubernetes provides automatic scaling, self-healing, and rolling updates
- **Dapr Integration**: Dapr is designed for Kubernetes with native sidecar injection
- **Kafka Integration**: Strimzi operator provides Kafka on Kubernetes
- **Multi-Cloud**: Helm charts enable deployment to any Kubernetes cluster (AKS, GKE, OKE)
- **Production-Ready**: Kubernetes is industry standard for microservices deployment

**Alternatives Considered**:
- **Docker Compose**: Rejected for production because it lacks orchestration, scaling, and self-healing. Used only for local development.
- **AWS ECS**: Rejected because it's AWS-specific and lacks Dapr integration. Kubernetes provides multi-cloud portability.
- **Serverless (Lambda/Cloud Functions)**: Rejected because microservices require persistent connections (Kafka consumers, Dapr sidecars) that don't fit serverless model.
- **VM-Based Deployment**: Rejected because it lacks container orchestration, automatic scaling, and self-healing.

**Trade-offs**:
- **Operational Complexity**: Kubernetes requires cluster management, monitoring, and troubleshooting
- **Resource Overhead**: Kubernetes control plane and Dapr sidecars consume resources
- **Learning Curve**: Team must understand Kubernetes concepts (pods, services, deployments, ingress)

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Backend Services | Python + FastAPI | 3.13+ | Async support, type safety, performance |
| Frontend | TypeScript + Next.js | 20+ / 16+ | Server components, App Router, optimization |
| Database | PostgreSQL | 15+ | ACID transactions, relational model, performance |
| Message Broker | Kafka (Redpanda/Strimzi) | Latest | Event-driven, reliable delivery, scalability |
| Service Coordination | Dapr | 1.12+ | Jobs API, Pub/Sub, resilience patterns |
| Chat AI | OpenAI GPT-4 | Latest | Natural language understanding, function calling |
| Container Orchestration | Kubernetes | 1.28+ | Microservices deployment, scaling, self-healing |
| Local Development | Minikube + Docker Compose | Latest | Production-like environment, fast iteration |
| Cloud Deployment | Helm 3 | 3.13+ | Templated deployment, multi-cloud portability |

---

## Performance Validation

| Requirement | Target | Solution | Validation Method |
|-------------|--------|----------|-------------------|
| Real-time sync | <100ms | Dapr service invocation + WebSocket | Load testing with 1000 concurrent users |
| Search/filter | <300ms | PostgreSQL full-text search + indexes | Query profiling with 10,000 tasks |
| Autocomplete | <200ms | PostgreSQL LIKE query + caching | Response time monitoring |
| Reminder delivery | <5s | Dapr Jobs API + exponential backoff | End-to-end latency testing |
| Recurring task creation | <5s | Kafka event processing + async handler | Event-to-creation latency monitoring |
| Concurrent users | 10,000+ | Horizontal scaling + connection pooling | Load testing with K6 or Locust |

---

## Security Considerations

| Concern | Solution | Implementation |
|---------|----------|----------------|
| Authentication | JWT tokens | Existing JWT system, validated in Backend API |
| Authorization | User-scoped data | All queries filtered by user_id |
| API Security | Rate limiting | Kubernetes Ingress rate limiting |
| Secrets Management | Dapr Secrets API | Kubernetes Secrets via Dapr |
| Inter-Service Communication | mTLS | Dapr automatic mTLS between services |
| Data Encryption | TLS in transit, encryption at rest | PostgreSQL encryption, HTTPS/TLS |
| Input Validation | Pydantic schemas | Automatic validation in FastAPI |
| SQL Injection | Parameterized queries | asyncpg with parameter binding |

---

## Deployment Strategy

### Local Development
1. Docker Compose for services + PostgreSQL + Redpanda
2. Dapr CLI for local sidecar execution
3. Hot reload for frontend (Next.js) and backend (FastAPI)

### Minikube (Local Kubernetes)
1. Minikube cluster with Dapr and Strimzi operators
2. Raw Kubernetes manifests for services
3. Port forwarding for local access

### Cloud Deployment (AKS/GKE/OKE)
1. Helm chart installation with environment-specific values
2. Managed PostgreSQL (Azure Database, Cloud SQL, OCI Database)
3. Managed Kafka (Confluent Cloud or Strimzi on K8s)
4. Ingress controller with TLS termination
5. Horizontal Pod Autoscaler for automatic scaling

---

## Monitoring and Observability

| Aspect | Solution | Implementation |
|--------|----------|----------------|
| Distributed Tracing | Dapr + Zipkin/Jaeger | Automatic trace propagation |
| Metrics | Prometheus + Grafana | Dapr metrics + custom application metrics |
| Logging | Structured logging + ELK/Loki | JSON logs with correlation IDs |
| Alerting | Prometheus Alertmanager | Alerts for service health, latency, errors |
| Health Checks | Kubernetes liveness/readiness probes | HTTP endpoints for health status |

---

## Migration Strategy

### Phase 1: Infrastructure Setup
1. Set up Kubernetes cluster (Minikube or cloud)
2. Install Dapr operator
3. Install Strimzi operator for Kafka
4. Configure PostgreSQL with service-specific schemas

### Phase 2: Service Migration
1. Extract Backend API from monolith (keep existing endpoints)
2. Create Recurring Service (new functionality)
3. Create Notification Service (new functionality)
4. Migrate Frontend to Next.js 16 with dual interface

### Phase 3: Event-Driven Integration
1. Add Kafka event publishing to Backend API
2. Implement event consumers in Recurring and Notification services
3. Configure Dapr Pub/Sub components

### Phase 4: Testing and Validation
1. Contract testing for API endpoints
2. Integration testing for event flows
3. Load testing for performance validation
4. End-to-end testing for user scenarios

### Phase 5: Deployment
1. Deploy to Minikube for local validation
2. Deploy to cloud (AKS/GKE/OKE) for production
3. Configure monitoring and alerting
4. Perform smoke tests and validation

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Kafka event loss | High | Low | At-least-once delivery, event replay, monitoring |
| Dapr sidecar failure | High | Low | Kubernetes automatic restart, health checks |
| Database connection exhaustion | High | Medium | Connection pooling, horizontal scaling |
| OpenAI API rate limits | Medium | Medium | Request caching, exponential backoff, fallback messages |
| Kubernetes cluster failure | High | Low | Multi-zone deployment, automatic failover |
| Service deployment failure | Medium | Medium | Rolling updates, health checks, automatic rollback |
| Performance degradation | Medium | Medium | Horizontal scaling, caching, query optimization |

---

## Next Steps

1. ✅ Phase 0 Complete: Research and architectural decisions documented
2. ⏭️ Phase 1: Create data-model.md with entity definitions
3. ⏭️ Phase 1: Generate API contracts in contracts/ directory
4. ⏭️ Phase 1: Create quickstart.md for local development setup
5. ⏭️ Phase 2: Generate tasks.md with implementation tasks (via /sp.tasks command)

---

**Research Complete**: 2026-02-14
**Next Command**: Continue with Phase 1 (data model and contracts generation)
