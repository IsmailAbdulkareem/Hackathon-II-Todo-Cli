# Data Model: Phase V Advanced Features

## 1. Enhanced Task Entity

**Entity**: Enhanced Task
**Description**: Represents a todo item with extended attributes for advanced features
**Schema**:
```
{
  "id": UUID,
  "user_id": UUID, // References authenticated user
  "title": String,
  "description": String,
  "completed": Boolean,
  "created_at": ISO 8601 Timestamp,
  "updated_at": ISO 8601 Timestamp,
  "due_date": ISO 8601 Timestamp (optional),
  "priority": Enum("low", "medium", "high"),
  "tags": [String],
  "recurrence": Enum("none", "daily", "weekly", "monthly"),
  "reminder_offset_minutes": Integer (optional)
}
```

**Validation Rules**:
- `id`: UUID format, required
- `user_id`: UUID format, required, must match authenticated user
- `title`: String, required, max length 255 characters
- `due_date`: ISO 8601 format, optional, must be in future if set
- `priority`: Enum values only, defaults to "medium"
- `tags`: Array of strings, each max length 50, normalized to lowercase
- `recurrence`: Enum values only, defaults to "none"
- `reminder_offset_minutes`: Integer, optional, 0-2147483647, must be less than minutes between current time and due_date if set

**State Transitions**:
- Creation: New task → Active state
- Completion: Active → Completed state
- Due Date Passage: Active → Overdue state (if incomplete)
- Deletion: Any state → Deleted (soft delete with deleted_at timestamp)

**Relationships**:
- Belongs to exactly one user (via user_id)
- May generate multiple recurring instances (parent-child relationship)
- May have one associated reminder (if reminder_offset_minutes is set)

## 2. Task Event Entity

**Entity**: Task Event
**Description**: Represents a significant operation on a task for event-driven architecture
**Schema**:
```
{
  "id": UUID,
  "task_id": UUID,
  "event_type": Enum("TASK_CREATED", "TASK_UPDATED", "TASK_COMPLETED", "REMINDER_DUE"),
  "timestamp": ISO 8601 Timestamp,
  "payload": Object
}
```

**Validation Rules**:
- `id`: UUID format, required
- `task_id`: UUID format, required, must reference existing task
- `event_type`: Enum values only, required
- `timestamp`: ISO 8601 format, required, must be current or past time
- `payload`: Object, optional, maximum size 1KB

**Event Types**:
- `TASK_CREATED`: Emitted when a new task is created
- `TASK_UPDATED`: Emitted when a task is modified
- `TASK_COMPLETED`: Emitted when a task is marked as complete
- `REMINDER_DUE`: Emitted when a reminder time is reached

**Event Topics**:
- `task-events`: For TASK_CREATED, TASK_UPDATED, TASK_COMPLETED events
- `task-reminders`: For REMINDER_DUE events
- `task-recurring`: For recurring task generation events
- `task-audit`: For audit logging (all events)

## 3. Reminder Entity

**Entity**: Reminder
**Description**: Represents a scheduled notification for a task
**Schema**:
```
{
  "id": UUID,
  "task_id": UUID,
  "reminder_time": ISO 8601 Timestamp,
  "notification_sent": Boolean,
  "created_at": ISO 8601 Timestamp,
  "sent_at": ISO 8601 Timestamp (optional)
}
```

**Validation Rules**:
- `id`: UUID format, required
- `task_id`: UUID format, required, must reference existing task
- `reminder_time`: ISO 8601 format, required, must be in future
- `notification_sent`: Boolean, defaults to false
- `created_at`: ISO 8601 format, required, set on creation
- `sent_at`: ISO 8601 format, optional, set when notification is sent

**Lifecycle States**:
- Scheduled: Created, notification_sent = false
- Triggered: Reminder time reached, notification_sent = false
- Sent: Notification delivered, notification_sent = true

**Cancellation Rules**:
- Reminder is automatically cancelled when the associated task is completed
- Reminder is automatically cancelled when the associated task is deleted

## 4. Recurring Task Instance Entity

**Entity**: Recurring Task Instance
**Description**: Represents a single occurrence of a recurring task
**Schema**:
```
{
  "id": UUID,
  "parent_task_id": UUID, // References the original recurring task
  "instance_date": ISO 8601 Date,
  "instance_task_id": UUID, // References the actual task instance created
  "generation_completed": Boolean,
  "created_at": ISO 8601 Timestamp
}
```

**Validation Rules**:
- `id`: UUID format, required
- `parent_task_id`: UUID format, required, must reference existing recurring task
- `instance_date`: ISO 8601 date format, required
- `instance_task_id`: UUID format, required after generation
- `generation_completed`: Boolean, defaults to false
- `created_at`: ISO 8601 format, required, set on creation

**Generation Rules**:
- Daily: Generate next day at midnight UTC
- Weekly: Generate on same day of week as original task at midnight UTC
- Monthly: Generate on same day of month as original task at midnight UTC (last day of month if original day doesn't exist)

**Relationships**:
- References parent recurring task (via parent_task_id)
- Creates a new Enhanced Task instance (referenced by instance_task_id)

## 5. Indexing Strategy

**Required Indexes** for efficient querying:

**Enhanced Task**:
- `(user_id, created_at)` - For user's chronological task listing
- `(user_id, due_date)` - For due date filtering
- `(user_id, completed, due_date)` - For combined filtering
- `(user_id, priority)` - For priority-based sorting
- `(user_id, recurrence)` - For recurring task management
- `(user_id, completed, priority)` - For complex filtering

**Reminder**:
- `(reminder_time, notification_sent)` - For scheduled reminder processing
- `(task_id, notification_sent)` - For task-reminder lookup

**Recurring Task Instance**:
- `(parent_task_id, instance_date)` - For recurrence management
- `(instance_date, generation_completed)` - For scheduled generation

## 6. Data Validation Rules

**Cross-Entity Validation**:
- All user operations must validate user_id matches authenticated user
- Due dates cannot be in the past for new tasks (but allowed for existing tasks)
- Reminder offset must be less than time between current time and due date
- Recurring tasks cannot have recurrence and reminder_offset_minutes that conflict

**Business Logic Validation**:
- Tags must be normalized to lowercase
- Priority values must be valid enum values
- Recurrence values must be valid enum values
- Timestamps must be in ISO 8601 format
- Task completion cannot occur before due date for overdue check

## 7. State Transition Diagrams

### Task State Transitions
```
[Creation] -> Active State
Active -> [Complete Task] -> Completed State
Active -> [Due Date Passes] -> Overdue State (if incomplete)
Active/Overdue/Completed -> [Delete Task] -> Soft Deleted State
```

### Reminder State Transitions
```
[Task Created with Reminder] -> Scheduled State
Scheduled -> [Reminder Time Reached] -> Triggered State
Triggered -> [Notification Sent] -> Sent State
Any State -> [Task Completed/Deleted] -> Cancelled State
```

### Recurring Instance State Transitions
```
[Scheduled Generation Time] -> Pending Generation
Pending Generation -> [Instance Created] -> Generated State
Pending Generation -> [Generation Failed] -> Failed State
```

## 8. Storage Considerations

**Dapr State Store Keys**:
- Task: `task:{user_id}:{task_id}`
- Reminder: `reminder:{task_id}:{reminder_time}`
- Recurring Instance: `recurring_instance:{parent_task_id}:{instance_date}`

**Partition Strategy**:
- User-based partitioning for all entities to ensure data isolation
- Date-based partitioning for historical data management
- Event-based partitioning for audit logs

**Retention Policy**:
- Active tasks: Indefinite (based on user needs)
- Completed tasks: Retained for 90 days minimum
- Events: 30 days for audit, 7 days for operational events
- Reminders: Cleaned up after notification_sent = true or task completion/deletion