# Feature Specification: Phase V - Advanced Features with Dapr-First Architecture

**Feature Branch**: `001-dapr-advanced-features`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Phase V Specification: Advanced Features with Dapr-First Architecture - Enhance the existing Todo application with advanced features and an event-driven architecture, using Dapr as the first-class abstraction for communication, state, scheduling, and pub/sub."

## Clarifications

### Session 2026-02-06

- Q: How should the system handle user authentication and task ownership? → A: Multi-user with existing authentication - Assume authentication exists from earlier phases, add user_id to task model for ownership
- Q: How should reminder notifications be delivered from backend to frontend? → A: Server-Sent Events (SSE) - Unidirectional server-to-client push
- Q: How should weekly and monthly recurring tasks determine their next generation date? → A: Anchor to original creation date - Weekly tasks recur on same day of week, monthly on same day of month as original task
- Q: When sorting tasks by priority, which order should be used? → A: High → Medium → Low (descending priority) - Most urgent tasks appear first
- Q: Which Dapr state store component should be used for task persistence? → A: Redis - In-memory data store with persistence

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Due Dates and Priorities (Priority: P1)

As a user, I want to set due dates and priorities on my tasks so that I can focus on what's most important and time-sensitive.

**Why this priority**: This is the foundation for task management - users need to know what's urgent and when things are due. Without this, the todo app is just a list with no context.

**Independent Test**: Can be fully tested by creating tasks with different due dates and priorities, then verifying they display correctly and can be filtered. Delivers immediate value by helping users organize their work.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I set a due date of "2026-02-10T15:00:00Z" and priority "high", **Then** the task is saved with these attributes and displays them in the task list
2. **Given** I have tasks with different priorities, **When** I view my task list, **Then** I can see the priority level (low/medium/high) for each task
3. **Given** I have a task with a due date, **When** the due date passes, **Then** the task is visually marked as overdue
4. **Given** I am editing an existing task, **When** I change the priority from "low" to "high", **Then** the change is persisted and reflected immediately

---

### User Story 2 - Task Tags and Organization (Priority: P2)

As a user, I want to tag my tasks with categories so that I can organize and find related tasks easily.

**Why this priority**: Tags provide flexible organization beyond simple lists. Users can categorize tasks by project, context, or any custom dimension that makes sense for their workflow.

**Independent Test**: Can be fully tested by creating tasks with various tags, then searching and filtering by those tags. Delivers value by enabling users to organize tasks their way.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I add tags ["work", "urgent", "client-meeting"], **Then** the task is saved with these tags
2. **Given** I have tasks with different tags, **When** I filter by tag "work", **Then** I see only tasks tagged with "work"
3. **Given** I am viewing a task, **When** I add a new tag "follow-up", **Then** the tag is added to the existing tags without removing others
4. **Given** I have multiple tasks, **When** I search for tasks containing tag "urgent", **Then** all tasks with that tag are returned

---

### User Story 3 - Recurring Tasks (Priority: P3)

As a user, I want to create tasks that repeat on a schedule so that I don't have to manually recreate routine tasks.

**Why this priority**: Automation of repetitive tasks saves time and ensures nothing is forgotten. This is valuable for users with regular responsibilities.

**Independent Test**: Can be fully tested by creating a recurring task (e.g., daily), waiting for the recurrence period, and verifying a new instance is automatically created. Delivers value by reducing manual task creation.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I set recurrence to "daily", **Then** the task is marked as recurring with daily frequency
2. **Given** I have a daily recurring task created on 2026-02-06, **When** the system runs at midnight on 2026-02-07, **Then** a new instance of the task is automatically created for 2026-02-07
3. **Given** I have a weekly recurring task, **When** I complete the current instance, **Then** the next instance is scheduled for one week later
4. **Given** I have a recurring task, **When** I delete it, **Then** future instances are not generated but existing instances remain

---

### User Story 4 - Task Reminders (Priority: P4)

As a user, I want to receive reminders before tasks are due so that I don't miss important deadlines.

**Why this priority**: Proactive notifications help users stay on top of their work. This builds on due dates (P1) to provide actionable alerts.

**Independent Test**: Can be fully tested by creating a task with a due date and reminder offset, then verifying the reminder is triggered at the correct time. Delivers value by preventing missed deadlines.

**Acceptance Scenarios**:

1. **Given** I am creating a task with due date "2026-02-10T15:00:00Z", **When** I set a reminder for 30 minutes before, **Then** the reminder is scheduled for "2026-02-10T14:30:00Z"
2. **Given** I have a task with a reminder scheduled, **When** the reminder time arrives, **Then** I receive an in-app notification with the task details
3. **Given** I have multiple tasks with reminders, **When** I view my notifications, **Then** I see all pending reminders sorted by time
4. **Given** I complete a task before the reminder time, **When** the reminder time arrives, **Then** no reminder is sent for that completed task

---

### User Story 5 - Advanced Search and Filtering (Priority: P5)

As a user, I want to search and filter my tasks by multiple criteria so that I can quickly find what I need.

**Why this priority**: As task lists grow, finding specific tasks becomes critical. This enhances usability for power users with many tasks.

**Independent Test**: Can be fully tested by creating diverse tasks and verifying search/filter operations return correct results. Delivers value by improving task discoverability.

**Acceptance Scenarios**:

1. **Given** I have tasks with various attributes, **When** I filter by priority "high" AND tag "work", **Then** I see only tasks matching both criteria
2. **Given** I have tasks with different due dates, **When** I sort by due date ascending, **Then** tasks are ordered from earliest to latest due date
3. **Given** I have completed and incomplete tasks, **When** I filter by completion status "incomplete", **Then** I see only tasks that are not completed
4. **Given** I have tasks with text content, **When** I search for "meeting", **Then** I see all tasks containing "meeting" in title or description

---

### User Story 6 - Event-Driven Architecture (Priority: P6)

As a system administrator, I want all significant task operations to emit events so that I can integrate with other systems and maintain audit logs.

**Why this priority**: This is infrastructure-level functionality that enables observability, integration, and compliance. It's essential for production systems but doesn't directly impact end users.

**Independent Test**: Can be fully tested by performing task operations and verifying events are published to the correct topics with proper schemas. Delivers value by enabling system integration and monitoring.

**Acceptance Scenarios**:

1. **Given** the system is running with Dapr pub/sub configured, **When** I create a new task, **Then** a "TASK_CREATED" event is published to the "task-events" topic
2. **Given** I complete a task, **When** the completion is saved, **Then** a "TASK_COMPLETED" event is published with the task ID and timestamp
3. **Given** a reminder is due, **When** the reminder time arrives, **Then** a "REMINDER_DUE" event is published to the "task-reminders" topic
4. **Given** a recurring task generates a new instance, **When** the new task is created, **Then** a "TASK_CREATED" event is published to the "task-recurring" topic

---

### Edge Cases

- What happens when a user sets a due date in the past? System should accept it and mark the task as immediately overdue.
- What happens when a recurring task's next instance would be created while the previous instance is still incomplete? System should create the new instance anyway (they are independent).
- What happens when Dapr is not available? System should gracefully degrade: store operations locally, queue events for later delivery, and log warnings.
- What happens when a user deletes a task that has a pending reminder? The reminder should be cancelled automatically.
- What happens when a user sets a reminder time that is after the due date? System should accept it but warn the user that the reminder is after the deadline.
- What happens when multiple tags have the same name but different casing (e.g., "Work" vs "work")? System should treat tags as case-insensitive and normalize to lowercase.
- What happens when a user tries to filter by a non-existent tag? System should return an empty result set without error.
- What happens when the system clock changes (e.g., daylight saving time)? All timestamps should use UTC to avoid ambiguity.
- What happens when a monthly recurring task is created on day 31 and the next month has only 30 days? The task should generate on the last day of that month (day 30).
- What happens when a weekly recurring task spans a daylight saving time change? The task should still generate on the correct day of week, maintaining the midnight UTC generation time.

## Requirements *(mandatory)*

### Functional Requirements

#### Task Enhancement Requirements

- **FR-001**: System MUST allow users to set a due date on any task using ISO 8601 timestamp format
- **FR-002**: System MUST support three priority levels: low, medium, and high
- **FR-003**: System MUST allow users to add multiple tags to a task, where each tag is a string
- **FR-004**: System MUST support recurring tasks with frequencies: daily, weekly, and monthly
- **FR-005**: System MUST allow users to set reminders that trigger X minutes before the due date
- **FR-006**: System MUST automatically generate new instances of recurring tasks at midnight UTC on the scheduled date
- **FR-007**: System MUST mark tasks as overdue when the current time exceeds the due date and the task is incomplete
- **FR-008**: System MUST normalize tags to lowercase to ensure case-insensitive matching
- **FR-009**: Weekly recurring tasks MUST generate on the same day of week as the original task (e.g., if created on Tuesday, recur every Tuesday)
- **FR-010**: Monthly recurring tasks MUST generate on the same day of month as the original task (e.g., if created on 15th, recur on 15th of each month)
- **FR-011**: For monthly recurring tasks created on day 29-31, if the target month has fewer days, the task MUST generate on the last day of that month

#### Search and Filter Requirements

- **FR-012**: System MUST allow users to filter tasks by priority level
- **FR-013**: System MUST allow users to filter tasks by one or more tags
- **FR-014**: System MUST allow users to filter tasks by due date range
- **FR-015**: System MUST allow users to filter tasks by completion status
- **FR-016**: System MUST allow users to sort tasks by due date (ascending or descending)
- **FR-017**: System MUST allow users to sort tasks by priority level in descending order (high → medium → low)
- **FR-018**: System MUST allow users to search tasks by text content in title or description
- **FR-019**: System MUST support combining multiple filters (AND logic)

#### Event-Driven Architecture Requirements

- **FR-020**: System MUST emit a "TASK_CREATED" event when a new task is created
- **FR-021**: System MUST emit a "TASK_UPDATED" event when a task is modified
- **FR-022**: System MUST emit a "TASK_COMPLETED" event when a task is marked as complete
- **FR-023**: System MUST emit a "REMINDER_DUE" event when a reminder time is reached
- **FR-024**: System MUST emit events to the "task-events" topic for task lifecycle events
- **FR-025**: System MUST emit events to the "task-reminders" topic for reminder events
- **FR-026**: System MUST emit events to the "task-recurring" topic for recurring task generation
- **FR-027**: System MUST emit events to the "task-audit" topic for audit logging
- **FR-028**: All events MUST follow the standard schema: task_id, event_type, timestamp (ISO 8601), payload

#### Dapr Integration Requirements

- **FR-029**: System MUST use Dapr Pub/Sub API for all event publishing (POST /v1.0/publish/{pubsub}/{topic})
- **FR-030**: System MUST use Dapr State Store API for all task persistence (GET/POST /v1.0/state/{store})
- **FR-031**: System MUST use Dapr Jobs API for scheduling reminders and recurring task generation
- **FR-032**: System MUST use Dapr Service Invocation API for internal service-to-service calls (POST /v1.0/invoke/{app-id}/method/{endpoint})
- **FR-033**: System MUST NOT use direct Kafka clients, cron jobs, message brokers, or state store SDKs
- **FR-034**: System MUST attempt to install Dapr CLI if not present before implementation
- **FR-035**: System MUST document any Dapr installation failures and continue with HTTP API targets
- **FR-036**: System MUST gracefully degrade when Dapr is unavailable: queue operations locally and retry

#### Architecture Requirements

- **FR-037**: Backend MUST be infrastructure-agnostic and not depend on specific Dapr implementations
- **FR-038**: Business logic MUST be separated from infrastructure concerns
- **FR-039**: System MUST run with Dapr sidecar (preferred mode)
- **FR-040**: System MUST run without Dapr sidecar (degraded mode with local fallbacks)
- **FR-041**: All code MUST be implemented in Phase III first, then reused in Phase IV without modification
- **FR-042**: Kubernetes deployment MUST use Dapr sidecar annotations (dapr.io/enabled, dapr.io/app-id, dapr.io/app-port)
- **FR-043**: System MUST enforce task ownership - users can only access their own tasks
- **FR-044**: System MUST include user_id in all task operations to ensure data isolation
- **FR-045**: System MUST use existing authentication mechanism from earlier phases (no new authentication implementation required)
- **FR-046**: System MUST deliver reminder notifications to frontend via Server-Sent Events (SSE)
- **FR-047**: Backend MUST maintain SSE connections per authenticated user for notification delivery
- **FR-048**: System MUST send reminder notifications only to the user who owns the task

### Key Entities

- **Enhanced Task**: Represents a todo item with extended attributes
  - Core attributes: id (UUID), title, description, completed (boolean), created_at, updated_at, user_id (UUID, references authenticated user)
  - New attributes: due_date (ISO 8601 timestamp, optional), priority (enum: low/medium/high), tags (list of strings), recurrence (enum: none/daily/weekly/monthly), reminder_offset_minutes (integer, optional)
  - Relationships: A task may generate multiple recurring instances (parent-child relationship); each task belongs to exactly one user

- **Task Event**: Represents a significant operation on a task
  - Attributes: task_id (UUID), event_type (enum: TASK_CREATED/TASK_UPDATED/TASK_COMPLETED/REMINDER_DUE), timestamp (ISO 8601), payload (JSON object with event-specific data)
  - Relationships: Each event references exactly one task

- **Reminder**: Represents a scheduled notification for a task
  - Attributes: task_id (UUID), reminder_time (ISO 8601 timestamp), notification_sent (boolean)
  - Relationships: Each reminder belongs to exactly one task

- **Recurring Task Instance**: Represents a single occurrence of a recurring task
  - Attributes: parent_task_id (UUID), instance_date (ISO 8601), instance_task_id (UUID)
  - Relationships: Each instance references a parent recurring task and creates a new task entity

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with due date, priority, and tags in under 30 seconds
- **SC-002**: Users can filter tasks by multiple criteria and see results in under 2 seconds
- **SC-003**: Recurring tasks are automatically generated within 5 minutes of the scheduled time
- **SC-004**: Reminders are delivered within 1 minute of the scheduled reminder time
- **SC-005**: System handles 1000 concurrent task operations without performance degradation
- **SC-006**: 100% of task lifecycle events are successfully published to event topics
- **SC-007**: System continues to function (with degraded features) when Dapr is unavailable
- **SC-008**: Search operations return results in under 1 second for task lists up to 10,000 items
- **SC-009**: 95% of users successfully use advanced features (tags, filters, priorities) within first session
- **SC-010**: Event delivery latency is under 500ms from operation to event publication

## Assumptions *(optional)*

### Technical Assumptions

- Dapr CLI can be installed via `winget install Dapr.CLI` on Windows development machines
- Dapr can be initialized in self-hosted mode via `dapr init` for local development
- Dapr can be installed in Kubernetes via `dapr install -k` for production deployment
- The existing Todo application has a backend API that can be extended
- The backend is built with FastAPI (Python) as specified in project constitution
- Redis is available as the Dapr state store component for task persistence
- Redis Streams is available as the Dapr pub/sub component for event messaging
- User authentication system exists from earlier phases (Phase I or II) and provides authenticated user context
- Authentication mechanism provides user_id that can be used for task ownership

### Business Assumptions

- Reminders are delivered as in-app notifications via Server-Sent Events (SSE) - not email or SMS
- Event retention period is 30 days for audit logs (industry standard)
- Recurring tasks are generated at midnight UTC (standard cron behavior)
- Weekly recurring tasks maintain the same day of week as the original task creation date
- Monthly recurring tasks maintain the same day of month as the original task creation date
- Tags are user-defined and not restricted to a predefined set
- Priority levels are sufficient with three tiers (low/medium/high)
- Users understand ISO 8601 timestamp format or the UI provides a date picker
- Completed recurring tasks do not prevent new instances from being generated
- The system operates in a single timezone (UTC) for all timestamp operations
- Frontend maintains SSE connection while user is active; notifications are queued if connection is lost

### Deployment Assumptions

- Phase III implementation will be tested locally with Dapr sidecar
- Phase IV deployment will use Minikube or similar local Kubernetes cluster
- Helm charts will be used for Kubernetes deployment
- The same codebase will be deployed in both Phase III and Phase IV without modification
- Dapr components (pubsub, state store) will be configured via Kubernetes manifests in Phase IV

## Dependencies *(optional)*

### External Dependencies

- **Dapr Runtime**: Version 1.12+ required for Jobs API support
- **Dapr CLI**: Required for local development and initialization
- **Redis**: Version 6.0+ required for Dapr state store and pub/sub components
- **Kubernetes Cluster**: Minikube 1.30+ or compatible for Phase IV deployment
- **Helm**: Version 3.0+ for Kubernetes deployment

### Internal Dependencies

- **Phase III Backend**: Existing FastAPI backend must be functional
- **Phase III Frontend**: Existing Next.js frontend must be functional
- **Phase IV Infrastructure**: Kubernetes cluster must be operational
- **Phase IV Helm Charts**: Existing Helm charts must be available for extension

### Feature Dependencies

- Task due dates and priorities (P1) must be implemented before reminders (P4) can function
- Event-driven architecture (P6) must be implemented before audit logging can be enabled
- Dapr integration must be completed before any event publishing or state management can work
- Search and filter (P5) depends on task enhancements (P1, P2) being implemented first

## Out of Scope *(optional)*

### Explicitly Excluded

- **Email or SMS notifications**: Reminders are in-app only
- **Calendar integration**: No sync with Google Calendar, Outlook, etc.
- **Task sharing or collaboration**: Tasks remain private to individual users
- **Task attachments**: No file uploads or attachments on tasks
- **Task comments or notes**: Only title and description fields
- **Custom recurrence patterns**: Only daily, weekly, monthly (no "every 2 weeks" or "last Friday of month")
- **Time zone support**: All timestamps in UTC only
- **Task dependencies**: No "task A must complete before task B" relationships
- **Task templates**: No ability to save and reuse task configurations
- **Bulk operations**: No multi-select and bulk edit/delete
- **Task history or versioning**: No tracking of changes over time
- **Advanced analytics**: No dashboards or reporting on task completion rates
- **Mobile push notifications**: In-app notifications only, no native mobile push
- **Offline support**: Requires active connection to Dapr and backend

### Future Considerations

- Multi-user collaboration features could be added in Phase VI
- Calendar integration could be added as a separate feature
- Custom recurrence patterns could be added if user demand is high
- Time zone support could be added for international users
- Mobile push notifications could be added with a mobile app

## Constraints *(optional)*

### Technical Constraints

- **Dapr-First Mandate**: All integrations MUST go through Dapr APIs - no direct client libraries
- **Infrastructure Agnostic**: Backend code must not depend on specific Dapr implementations
- **Phase III First**: All functionality must be implemented and tested in Phase III before Phase IV
- **No Code Changes**: Phase IV deployment must reuse Phase III code without modification
- **HTTP API Only**: Dapr integration must use HTTP endpoints, not gRPC or SDKs
- **Graceful Degradation**: System must function (with reduced features) when Dapr is unavailable

### Performance Constraints

- Event publishing must complete within 500ms
- Search and filter operations must return results within 2 seconds
- Recurring task generation must occur within 5 minutes of scheduled time
- Reminder delivery must occur within 1 minute of scheduled time
- System must handle 1000 concurrent operations without degradation

### Operational Constraints

- Dapr installation must be attempted before implementation begins
- Dapr installation failures must be documented but not block development
- All Dapr components must be configured via Kubernetes manifests in Phase IV
- Backend must expose port 8000 for Dapr sidecar communication
- Kubernetes pods must include required Dapr annotations

### Security Constraints

- All timestamps must use ISO 8601 format to prevent injection attacks
- Tag input must be sanitized to prevent XSS attacks
- Event payloads must not contain sensitive user data (passwords, tokens)
- State store access must be restricted to Dapr sidecar only
- Pub/sub topics must be scoped to prevent unauthorized access
- User authentication must be validated on every API request
- Task queries must be filtered by authenticated user_id to prevent unauthorized access
- User_id must never be accepted from client input - always derived from authenticated session

## Risks *(optional)*

### Technical Risks

- **Dapr Installation Failure**: Dapr may not install successfully on all development machines
  - Mitigation: Document installation process, provide fallback to HTTP API mocking

- **Dapr Unavailability**: Dapr sidecar may crash or become unavailable in production
  - Mitigation: Implement graceful degradation with local queuing and retry logic

- **Event Delivery Failures**: Pub/sub events may fail to deliver due to network issues
  - Mitigation: Implement retry logic with exponential backoff, dead letter queues

- **State Store Inconsistency**: State store may become inconsistent if Dapr fails mid-operation
  - Mitigation: Use Dapr's state management features (ETags, transactions) for consistency

- **Performance Degradation**: Event publishing may slow down under high load
  - Mitigation: Use asynchronous event publishing, implement rate limiting

### Integration Risks

- **Phase III to Phase IV Migration**: Code may not work identically in Kubernetes environment
  - Mitigation: Thorough testing in Phase III with Dapr sidecar, integration tests in Phase IV

- **Dapr Component Configuration**: Incorrect component configuration may cause runtime failures
  - Mitigation: Validate component configurations, provide example configurations in documentation

- **Kubernetes Deployment Issues**: Dapr annotations may not be applied correctly
  - Mitigation: Use Helm chart validation, test deployment in local Minikube cluster

### Operational Risks

- **Recurring Task Accumulation**: If system is down, many recurring tasks may need to be generated at once
  - Mitigation: Implement batch generation with rate limiting, skip missed instances if too old

- **Reminder Spam**: Many reminders may fire simultaneously if system is down
  - Mitigation: Implement reminder deduplication, batch notifications

- **Event Topic Overflow**: High event volume may overwhelm pub/sub system
  - Mitigation: Implement event sampling for high-frequency events, use separate topics for different priorities

## Notes *(optional)*

### Implementation Strategy

This feature represents a significant architectural shift to event-driven design with Dapr as the integration layer. The implementation should follow this phased approach:

1. **Phase III - Local Development**:
   - Install and configure Dapr in self-hosted mode
   - Implement task model enhancements (due dates, priorities, tags, recurrence)
   - Implement Dapr state store integration for task persistence
   - Implement Dapr pub/sub integration for event publishing
   - Implement Dapr jobs for reminders and recurring task generation
   - Implement search, filter, and sort APIs
   - Test all functionality locally with Dapr sidecar

2. **Phase IV - Kubernetes Deployment**:
   - Install Dapr into Kubernetes cluster
   - Configure Dapr components (state store, pub/sub) via manifests
   - Add Dapr annotations to backend pod specifications
   - Update Helm charts to include Dapr configuration
   - Deploy and test in Kubernetes environment
   - Verify no code changes were needed from Phase III

### Design Principles

- **Separation of Concerns**: Business logic must be independent of infrastructure
- **Fail-Safe Defaults**: System should degrade gracefully when dependencies are unavailable
- **Event Sourcing**: All significant operations should emit events for observability
- **Idempotency**: All operations should be idempotent to handle retries safely
- **Testability**: Each feature should be independently testable

### Testing Strategy

- **Unit Tests**: Test business logic without Dapr dependencies (use mocks)
- **Integration Tests**: Test Dapr integration with real Dapr sidecar in test mode
- **End-to-End Tests**: Test complete user flows from frontend to backend to events
- **Performance Tests**: Test system under load (1000 concurrent operations)
- **Failure Tests**: Test graceful degradation when Dapr is unavailable
- **Migration Tests**: Verify Phase III code works in Phase IV without changes

### Documentation Requirements

- Dapr installation guide for Windows (winget), macOS (brew), Linux (script)
- Redis installation and configuration guide for local development
- Dapr component configuration examples (Redis state store, Redis Streams pub/sub)
- Event schema documentation for all event types
- API documentation for new endpoints (search, filter, sort)
- SSE endpoint documentation for notification delivery
- Troubleshooting guide for common Dapr and Redis issues
- Migration guide from Phase III to Phase IV

---

**Next Steps**:
1. Run `/sp.clarify` if any requirements need further clarification
2. Run `/sp.plan` to create the implementation plan
3. Run `/sp.tasks` to generate the task breakdown
