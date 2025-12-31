# Generators Skill Set

A collection of code and configuration generators for the Todo Spec-Driven Development project across all 5 phases.

**Purpose:** Accelerate development by generating boilerplate code, configurations, and infrastructure definitions with proper patterns and best practices.

**When to Use:**
- Starting a new phase (II-V)
- Adding new database entities
- Creating new API endpoints
- Setting up infrastructure (Docker, K8s, Dapr)
- Adding AI/MCP tools

**Available Generators:**
1. `db-schema` - SQLModel classes and migrations
2. `fastapi-endpoint` - FastAPI route handlers
3. `mcp-tool` - MCP tool implementations
4. `auth-integration` - Authentication middleware
5. `helm-chart` - Kubernetes Helm charts
6. `dockerfile` - Docker container definitions
7. `dapr-component` - Dapr component configs
8. `event-schema` - Kafka event payloads

**Usage:**
```
/gen.<generator-name> <parameters>

# Example:
/gen.db-schema "User entity with id, email, password_hash"
/gen.fastapi-endpoint Todo "GET list, POST create, PUT update, DELETE"
/gen.mcp-tool add_task "Add new todo with title and description"
/gen.helm-chart "backend service with PostgreSQL database"
/gen.dockerfile nextjs "Next.js 15 app"
```

**Generated Output Standards:**
- Follows project constitution principles
- Type-safe with proper typing
- Includes error handling and validation
- Production-ready patterns
- Well-documented with docstrings
- Unit tests included

**Design Philosophy:**
- Minimal viable generation
- Clear separation of concerns
- Reusable across phases
- No assumptions about business logic
- Explicit defaults, easy to override
