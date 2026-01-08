# Feature Specification: Backend REST API with Persistent Storage

**Feature Branch**: `003-backend-api`
**Created**: 2026-01-08
**Status**: Draft
**Input**: User description: "Phase II – Backend REST API with Persistent Storage (No Authentication)"

## Overview

Build a production-quality REST API backend that provides persistent task management capabilities. This API serves as the data layer for the frontend application and establishes the foundation for future authentication integration. The API uses user_id as a path parameter to scope all operations, preparing the architecture for JWT-based authentication in a later phase.

## User Scenarios & Testing

### User Story 1 - Retrieve All Tasks for a User (Priority: P1)

A frontend developer needs to fetch all tasks belonging to a specific user to display in the UI. They make a GET request with the user's ID and receive a JSON array of all tasks associated with that user, including completed and pending tasks.

**Why this priority**: This is the foundational read operation. Without the ability to retrieve tasks, no other functionality can be demonstrated or tested. This delivers immediate value by enabling the frontend to display existing data.

**Independent Test**: Can be fully tested by seeding the database with sample tasks for a user, making a GET request to `/api/{user_id}/tasks`, and verifying the response contains all expected tasks with correct data structure.

**Acceptance Scenarios**:

1. **Given** a user with ID "user123" has 5 tasks in the database, **When** a GET request is made to `/api/user123/tasks`, **Then** the response returns HTTP 200 with a JSON array containing all 5 tasks with complete task details (id, title, description, completed status, timestamps)

2. **Given** a user with ID "user456" has no tasks in the database, **When** a GET request is made to `/api/user456/tasks`, **Then** the response returns HTTP 200 with an empty JSON array `[]`

3. **Given** tasks exist for multiple users, **When** a GET request is made to `/api/user123/tasks`, **Then** the response contains only tasks belonging to user123 and excludes tasks from other users

---

### User Story 2 - Create a New Task (Priority: P1)

A frontend developer needs to create a new task for a user. They send a POST request with task details (title, optional description, optional priority) and receive the newly created task with a generated ID and timestamps.

**Why this priority**: Task creation is the primary write operation and core functionality of a todo application. Without this, users cannot add new tasks, making the system read-only and non-functional for its primary purpose.

**Independent Test**: Can be fully tested by sending a POST request to `/api/{user_id}/tasks` with valid task data, verifying the response contains the created task with a generated ID, and confirming the task persists in the database.

**Acceptance Scenarios**:

1. **Given** a valid user_id "user123", **When** a POST request is made to `/api/user123/tasks` with JSON body `{"title": "Buy groceries", "description": "Milk and eggs"}`, **Then** the response returns HTTP 201 with the created task including a unique id, the provided title and description, completed=false, and created_at/updated_at timestamps

2. **Given** a POST request with only required fields, **When** the request body is `{"title": "Simple task"}`, **Then** the response returns HTTP 201 with the task having null description and default completed=false

3. **Given** an invalid request, **When** a POST request is made without a title field, **Then** the response returns HTTP 422 with an error message indicating title is required

4. **Given** a task is created for user123, **When** another user (user456) attempts to retrieve all tasks, **Then** the newly created task does not appear in user456's task list

---

### User Story 3 - Update an Existing Task (Priority: P2)

A frontend developer needs to modify an existing task's details (title, description, or priority). They send a PUT request with the task ID and updated fields, and receive the updated task with a new updated_at timestamp.

**Why this priority**: Users frequently need to modify task details as circumstances change. While not as critical as creation and retrieval, editing is essential for practical task management and maintaining data accuracy.

**Independent Test**: Can be fully tested by creating a task, sending a PUT request to `/api/{user_id}/tasks/{id}` with modified data, and verifying the response reflects the changes while preserving the original id and created_at timestamp.

**Acceptance Scenarios**:

1. **Given** user123 has a task with id "task-abc" and title "Old title", **When** a PUT request is made to `/api/user123/tasks/task-abc` with body `{"title": "New title", "description": "Updated description"}`, **Then** the response returns HTTP 200 with the task showing the new title and description, an updated updated_at timestamp, and the same id and created_at

2. **Given** a task belongs to user123, **When** user456 attempts to update it via `/api/user456/tasks/task-abc`, **Then** the response returns HTTP 404 indicating the task was not found (enforcing user isolation)

3. **Given** an invalid task ID, **When** a PUT request is made to `/api/user123/tasks/nonexistent-id`, **Then** the response returns HTTP 404 with an error message

---

### User Story 4 - Delete a Task (Priority: P2)

A frontend developer needs to permanently remove a task from the system. They send a DELETE request with the task ID and receive confirmation of deletion.

**Why this priority**: Users need the ability to remove outdated or completed tasks to maintain a clean task list. While important for data hygiene, this is less frequent than creation and retrieval operations.

**Independent Test**: Can be fully tested by creating a task, sending a DELETE request to `/api/{user_id}/tasks/{id}`, verifying HTTP 204 response, and confirming the task no longer appears in subsequent GET requests.

**Acceptance Scenarios**:

1. **Given** user123 has a task with id "task-xyz", **When** a DELETE request is made to `/api/user123/tasks/task-xyz`, **Then** the response returns HTTP 204 with no body, and subsequent GET requests to `/api/user123/tasks` do not include the deleted task

2. **Given** a task belongs to user123, **When** user456 attempts to delete it via `/api/user456/tasks/task-xyz`, **Then** the response returns HTTP 404 (enforcing user isolation and preventing cross-user deletions)

3. **Given** an invalid task ID, **When** a DELETE request is made to `/api/user123/tasks/nonexistent-id`, **Then** the response returns HTTP 404

---

### User Story 5 - Toggle Task Completion Status (Priority: P1)

A frontend developer needs to mark a task as complete or incomplete. They send a PATCH request to a dedicated completion endpoint and receive the updated task with toggled completion status.

**Why this priority**: Completion tracking is fundamental to task management. Users need to easily track progress and see what's done versus what's pending. This is a high-frequency operation that must be simple and reliable.

**Independent Test**: Can be fully tested by creating a task (completed=false), sending a PATCH request to `/api/{user_id}/tasks/{id}/complete`, verifying the task now has completed=true, and sending another PATCH to toggle it back to false.

**Acceptance Scenarios**:

1. **Given** user123 has a task with id "task-123" and completed=false, **When** a PATCH request is made to `/api/user123/tasks/task-123/complete`, **Then** the response returns HTTP 200 with the task showing completed=true and an updated updated_at timestamp

2. **Given** a task with completed=true, **When** a PATCH request is made to the complete endpoint, **Then** the response returns HTTP 200 with completed=false (toggle behavior)

3. **Given** a task belongs to user123, **When** user456 attempts to toggle completion via `/api/user456/tasks/task-123/complete`, **Then** the response returns HTTP 404 (enforcing user isolation)

---

### User Story 6 - Retrieve a Single Task by ID (Priority: P2)

A frontend developer needs to fetch details for a specific task. They send a GET request with the task ID and receive the complete task object.

**Why this priority**: While less common than retrieving all tasks, fetching individual tasks is useful for detail views, deep linking, and verifying specific task state after operations.

**Independent Test**: Can be fully tested by creating a task, noting its ID, and sending a GET request to `/api/{user_id}/tasks/{id}` to verify the response contains the complete task details.

**Acceptance Scenarios**:

1. **Given** user123 has a task with id "task-456", **When** a GET request is made to `/api/user123/tasks/task-456`, **Then** the response returns HTTP 200 with the complete task object including all fields

2. **Given** a task belongs to user123, **When** user456 attempts to retrieve it via `/api/user456/tasks/task-456`, **Then** the response returns HTTP 404 (enforcing user isolation)

3. **Given** an invalid task ID, **When** a GET request is made to `/api/user123/tasks/nonexistent-id`, **Then** the response returns HTTP 404

---

### Edge Cases

- What happens when a user_id contains special characters or is extremely long?
  - System should handle URL-encoded user_id values and enforce reasonable length limits (e.g., 255 characters)

- How does the API handle concurrent updates to the same task?
  - Last-write-wins strategy with updated_at timestamp reflecting the most recent modification

- What happens when the database connection is lost during a request?
  - System should return HTTP 503 Service Unavailable with a descriptive error message

- How does the API handle malformed JSON in request bodies?
  - System should return HTTP 422 Unprocessable Entity with validation error details

- What happens when a task title exceeds reasonable length (e.g., 10,000 characters)?
  - System should enforce maximum length constraints (title: 500 chars, description: 2000 chars) and return HTTP 422 if exceeded

- How does the API handle requests with missing Content-Type headers?
  - System should return HTTP 415 Unsupported Media Type if Content-Type is not application/json for POST/PUT requests

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a GET endpoint at `/api/{user_id}/tasks` that returns all tasks for the specified user_id as a JSON array
- **FR-002**: System MUST provide a POST endpoint at `/api/{user_id}/tasks` that creates a new task with the provided data and returns the created task with HTTP 201
- **FR-003**: System MUST provide a GET endpoint at `/api/{user_id}/tasks/{id}` that returns a single task by ID with HTTP 200, or HTTP 404 if not found
- **FR-004**: System MUST provide a PUT endpoint at `/api/{user_id}/tasks/{id}` that updates an existing task and returns the updated task with HTTP 200, or HTTP 404 if not found
- **FR-005**: System MUST provide a DELETE endpoint at `/api/{user_id}/tasks/{id}` that removes a task and returns HTTP 204, or HTTP 404 if not found
- **FR-006**: System MUST provide a PATCH endpoint at `/api/{user_id}/tasks/{id}/complete` that toggles the completion status and returns the updated task with HTTP 200
- **FR-007**: System MUST enforce user isolation by ensuring all task operations are scoped to the user_id in the path parameter
- **FR-008**: System MUST validate that task title is required and non-empty for POST and PUT operations, returning HTTP 422 if validation fails
- **FR-009**: System MUST automatically generate unique task IDs for newly created tasks
- **FR-010**: System MUST automatically set created_at timestamp when creating tasks
- **FR-011**: System MUST automatically update updated_at timestamp when modifying tasks
- **FR-012**: System MUST persist all task data in a relational database (no in-memory storage)
- **FR-013**: System MUST return proper HTTP status codes: 200 (success), 201 (created), 204 (deleted), 404 (not found), 422 (validation error), 503 (service unavailable)
- **FR-014**: System MUST return JSON responses for all endpoints with consistent error message format
- **FR-015**: System MUST handle CORS to allow frontend applications from different origins to access the API
- **FR-016**: System MUST enforce maximum length constraints (title: 500 characters, description: 2000 characters)
- **FR-017**: System MUST default completed to false when creating new tasks if not specified
- **FR-018**: System MUST preserve task ownership by preventing cross-user access (user456 cannot access user123's tasks)

### Non-Functional Requirements

- **NFR-001**: API responses must complete within 500ms for single-task operations under normal load
- **NFR-002**: API must handle at least 100 concurrent requests without degradation
- **NFR-003**: Database queries must use proper indexing on user_id and task id fields
- **NFR-004**: API must log all requests with timestamp, endpoint, user_id, and response status
- **NFR-005**: Error responses must include descriptive messages without exposing internal system details

### Key Entities

- **Task**: Represents a todo item with the following attributes:
  - id: Unique identifier (string, auto-generated)
  - user_id: Owner identifier (string, required, indexed)
  - title: Task name (string, required, max 500 chars)
  - description: Task details (string, optional, max 2000 chars)
  - completed: Completion status (boolean, default false)
  - created_at: Creation timestamp (datetime, auto-generated)
  - updated_at: Last modification timestamp (datetime, auto-updated)

## Success Criteria

### Measurable Outcomes

- **SC-001**: Frontend developers can retrieve all tasks for a user in a single API call with response time under 500ms
- **SC-002**: Frontend developers can create a new task and receive the created task with generated ID in under 300ms
- **SC-003**: All task operations (create, read, update, delete, toggle) return appropriate HTTP status codes (200, 201, 204, 404, 422) according to specification
- **SC-004**: Tasks created by one user are completely isolated and inaccessible to other users (100% isolation)
- **SC-005**: API handles 100 concurrent task creation requests without errors or data loss
- **SC-006**: All task data persists across server restarts (verified by creating tasks, restarting server, and retrieving tasks)
- **SC-007**: API returns consistent JSON response format for all endpoints with proper error messages for validation failures
- **SC-008**: Toggle completion endpoint successfully changes task status from false to true and back with each request

## Dependencies & Assumptions

### Dependencies

- Relational database system (PostgreSQL-compatible) for persistent storage
- Database connection library compatible with the backend framework
- JSON serialization/deserialization capabilities
- HTTP server capable of handling RESTful requests

### Assumptions

- user_id values are provided by the caller and treated as trusted input (no validation of user existence)
- Database schema and tables are created before the API starts (migrations handled separately)
- Network connectivity between API server and database is reliable
- Frontend will handle user authentication and provide valid user_id values in API requests
- Task IDs are globally unique across all users (not just unique per user)
- Timestamps are stored in UTC timezone
- API will be accessed over HTTP/HTTPS with standard REST conventions
- Database supports concurrent access with proper transaction isolation
- Maximum expected task list size per user is under 10,000 tasks (no pagination required in this phase)

## Out of Scope

The following are explicitly NOT included in this specification:

- User authentication or authorization mechanisms
- JWT token generation, validation, or middleware
- User registration or login endpoints
- Password hashing or credential storage
- Session management
- Rate limiting or API throttling
- Task filtering, sorting, or search capabilities
- Pagination for large task lists
- Task categories, tags, or labels
- Task due dates or reminders
- Task priority levels beyond basic storage
- Bulk operations (create/update/delete multiple tasks)
- Task sharing or collaboration features
- Audit logging or change history
- API versioning strategy
- Deployment configuration or containerization
- Frontend integration or CORS configuration details
- Performance monitoring or metrics collection
- Automated testing or CI/CD pipelines
