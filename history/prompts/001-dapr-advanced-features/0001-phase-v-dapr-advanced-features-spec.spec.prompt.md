---
id: 0001
title: phase-v-dapr-advanced-features-spec
stage: spec
date: 2026-02-06
surface: CLI
model: claude-sonnet-4-5-20250929
feature: 001-dapr-advanced-features
branch: 001-dapr-advanced-features
user: system
command: /sp.specify
labels: [specification, dapr, event-driven, phase-v, advanced-features, recurring-tasks, reminders, pub-sub]
links:
  spec: specs/001-dapr-advanced-features/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/001-dapr-advanced-features/spec.md
    status: created
    lines: 429
    purpose: Complete Phase V specification with 6 user stories, 39 functional requirements, and comprehensive architecture details
  - path: specs/001-dapr-advanced-features/checklists/requirements.md
    status: created
    lines: 75
    purpose: Quality validation checklist confirming spec completeness and readiness for planning
tests:
  - N/A (specification phase - no tests yet)
---

## Prompt

```
Phase V Specification: Advanced Features with Dapr-First Architecture
Status

Phase: V
Applies To: Phase III (Backend-first), then Phase IV (Kubernetes)
Priority: Dapr is mandatory and must be used as the primary integration layer

1. Objective

Enhance the existing Todo application with advanced features and an event-driven architecture, using Dapr as the first-class abstraction for communication, state, scheduling, and pub/sub.

All new functionality must be implemented in Phase III first (shared codebase), then reused without logic changes in Phase IV (Kubernetes deployment).

2. Hard Requirement: Dapr First
2.1 Mandatory Rule

❗ All integrations MUST go through Dapr APIs first
❌ No direct Kafka clients
❌ No direct cron jobs
❌ No direct message brokers
❌ No direct state store SDKs

If Dapr is not installed:
- Installation must be attempted first
- Failure must be documented
- Code must still target Dapr HTTP APIs

3. Dapr Installation Requirement
3.1 Local Development (Phase III)

Before implementing features:
# Install Dapr CLI (if missing)
winget install Dapr.CLI

# Initialize Dapr (self-hosted)
dapr init

If installation fails:
- Document error
- Continue implementation using Dapr HTTP endpoints (mocked or assumed)

3.2 Kubernetes (Phase IV)

Before deployment:
# Install Dapr into Kubernetes cluster
dapr install -k

# Verify installation
dapr status -k

If Kubernetes installation fails:
- Capture error output
- Proceed with Dapr annotations and specs regardless

4. Advanced Features (Functional Scope)

These features must be implemented once and shared across Phase III and Phase IV.

4.1 Task Enhancements

Each Todo task must support:
- Recurring Tasks: daily, weekly, monthly
- Due Dates: ISO timestamp
- Reminders: Notify X minutes before due date
- Priority: low | medium | high
- Tags: List of strings (e.g. ["work", "urgent"])
- Search / Filter / Sort: by priority, tag, due date, completion status

5. Event-Driven Architecture (Dapr Pub/Sub)
5.1 Event Model

All significant actions MUST emit events via Dapr Pub/Sub.

Event Topics:
- task-events: Task created / updated / completed
- task-reminders: Reminder due
- task-recurring: Recurring task generation
- task-audit: Audit log stream

5.2 Event Schema (Standard)

All events must follow this structure:
{
  "task_id": "uuid",
  "event_type": "TASK_CREATED | TASK_COMPLETED | REMINDER_DUE",
  "timestamp": "ISO-8601",
  "payload": {}
}

6. Dapr Capabilities to Use (Required)
6.1 Pub/Sub

Replace Kafka producers with Dapr pub/sub
Use HTTP API: POST /v1.0/publish/{pubsub}/{topic}

6.2 State Store

Tasks must be persisted via Dapr state store
No direct DB access in business logic
Use: GET /v1.0/state/{store}, POST /v1.0/state/{store}

6.3 Jobs / Scheduling

Reminders and recurring tasks must use Dapr Jobs
No OS cron, No Celery / background workers

6.4 Service Invocation

Internal service-to-service calls must use:
POST /v1.0/invoke/{app-id}/method/{endpoint}

7. Backend Architecture Rules (Phase III)

- FastAPI backend
- All side effects routed through Dapr
- Business logic must be infrastructure-agnostic
- Backend must run: With Dapr (preferred), Without Dapr (graceful failure or mock)

8. Phase III Implementation Order (MANDATORY)

1. Verify or install Dapr CLI
2. Write specs for advanced features
3. Implement task model changes
4. Implement Dapr-based pub/sub
5. Implement Dapr state store logic
6. Implement reminders via Dapr jobs
7. Add search/filter/sort APIs
8. Test locally with Dapr sidecar (if available)

9. Phase IV Reuse Strategy

Phase IV must:
- Reuse Phase III backend code without modification
- Add Dapr sidecar via Kubernetes annotations
- Add Dapr components (pubsub, state store)
- Deploy via Helm

10. Kubernetes (Phase IV) Dapr Annotations

All backend pods must include:
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-backend"
  dapr.io/app-port: "8000"

11. Acceptance Criteria
Must Have (Phase V Pass)

- Dapr is attempted and documented
- Backend uses Dapr APIs exclusively
- Events emitted on task lifecycle
- Recurring tasks auto-generated

Part A: Advanced Features (Building the sophisticated functionality)
Step 1: Implement Advanced Features

- Recurring Tasks: Tasks that repeat (daily, weekly, monthly)
- Due Dates & Reminders: Set deadlines and get notifications
- Priorities: Mark tasks as high/medium/low priority
- Tags: Categorize tasks (#work, #personal, etc.)
- Search, Filter, Sort: Find and organize tasks easily

Step 2: Add Event-Driven Architecture
Think of this as a notification system:

- When you create a task → Send an event
- When you complete a task → Send an event
- When a reminder is due → Send an event
- These events trigger other services automatically
```

## Response snapshot

Created comprehensive Phase V specification for Advanced Features with Dapr-First Architecture:

**Branch**: 001-dapr-advanced-features

**Specification Structure**:
- 6 prioritized user stories (P1-P6) covering task enhancements, tags, recurring tasks, reminders, search/filter, and event-driven architecture
- 39 functional requirements organized into 5 categories: Task Enhancement (FR-001 to FR-008), Search/Filter (FR-009 to FR-016), Event-Driven Architecture (FR-017 to FR-025), Dapr Integration (FR-026 to FR-033), Architecture (FR-034 to FR-039)
- 10 measurable success criteria with specific performance targets
- 4 key entities: Enhanced Task, Task Event, Reminder, Recurring Task Instance
- Comprehensive sections: Assumptions (technical, business, deployment), Dependencies (external, internal, feature), Out of Scope, Constraints (technical, performance, operational, security), Risks (technical, integration, operational), Notes (implementation strategy, design principles, testing strategy, documentation requirements)

**Quality Validation**: All checklist items passed
- No implementation details leaked into specification
- All requirements testable and unambiguous
- Success criteria measurable and technology-agnostic
- 8 edge cases identified
- Scope clearly bounded with explicit exclusions

**Key Architectural Decisions**:
- Dapr-first mandate: All integrations through Dapr APIs only (no direct Kafka, cron, message brokers, or state store SDKs)
- Graceful degradation when Dapr unavailable
- Phase III implementation first, Phase IV reuse without code changes
- Infrastructure-agnostic business logic
- Event-driven architecture with 4 event topics

**Files Created**:
1. specs/001-dapr-advanced-features/spec.md (429 lines)
2. specs/001-dapr-advanced-features/checklists/requirements.md (75 lines)

## Outcome

- ✅ Impact: Created production-ready specification with 6 prioritized user stories, 39 functional requirements, 10 measurable success criteria, and comprehensive architectural guidance for Dapr-first event-driven implementation
- 🧪 Tests: N/A (specification phase - tests will be defined in tasks phase)
- 📁 Files: 2 files created (spec.md with complete specification, requirements.md with quality validation checklist showing all items passed)
- 🔁 Next prompts: /sp.clarify (optional - no clarifications needed based on validation), /sp.plan (create implementation plan), /sp.tasks (generate task breakdown)
- 🧠 Reflection: Successfully created comprehensive specification balancing user-facing features (P1-P5) with infrastructure concerns (P6). Strong emphasis on Dapr-first architecture while maintaining graceful degradation. Clear prioritization enables incremental delivery. Specification maintains proper separation between business requirements and technical implementation throughout.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification completed successfully with all quality checks passed
- Graders run and results (PASS/FAIL): Manual validation checklist - PASS (all items validated)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
