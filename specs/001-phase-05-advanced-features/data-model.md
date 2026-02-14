# Data Model: Phase 5 Part A - Advanced Task Management Features

**Feature**: Phase 5 Part A - Advanced Task Management Features
**Date**: 2026-02-14
**Database**: PostgreSQL 15+ with service-specific schemas

## Overview

This document defines the data model for TaskAI, including entities, relationships, validation rules, and state transitions. The model uses a shared PostgreSQL database with service-specific schemas for logical separation.

## Database Schemas

### Schema: `public` (Shared)
Owned by: All services (read-only for most)
Purpose: Shared authentication and user data

### Schema: `tasks` (Backend API)
Owned by: Backend API service
Purpose: Task management, tags, reminders, recurrence rules

### Schema: `notifications` (Notification Service)
Owned by: Notification Service
Purpose: Notification delivery tracking and retry logic

### Schema: `audit` (Recurring Service)
Owned by: Recurring Service
Purpose: Recurring task audit trail and history

---

## Entity Definitions

### Entity: User (Existing)

**Schema**: `public`
**Table**: `users`
**Owner**: Backend API (read-only for other services)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt password hash |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`

**Validation Rules**:
- Email must be valid format (validated by application)
- Password must be hashed with bcrypt (never stored in plaintext)

---

### Entity: Task

**Schema**: `tasks`
**Table**: `tasks`
**Owner**: Backend API

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique task identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → users(id) | Task owner |
| title | VARCHAR(500) | NOT NULL | Task title |
| description | TEXT | NULL | Task description (optional) |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| priority | VARCHAR(10) | NOT NULL, DEFAULT 'Low' | Priority level: Low, Medium, High |
| due_date | TIMESTAMP WITH TIME ZONE | NULL | Due date with optional time |
| is_recurring | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether task is recurring |
| parent_task_id | UUID | NULL, FOREIGN KEY → tasks(id) | Parent task for recurring series |
| recurrence_rule_id | UUID | NULL, FOREIGN KEY → recurrence_rules(id) | Recurrence pattern reference |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for user-scoped queries)
- INDEX on `user_id, completed` (for filtering by completion status)
- INDEX on `user_id, priority` (for filtering by priority)
- INDEX on `user_id, due_date` (for filtering by due date)
- INDEX on `user_id, is_recurring` (for filtering recurring tasks)
- INDEX on `parent_task_id` (for finding recurring series instances)
- GIN INDEX on `to_tsvector('english', title || ' ' || COALESCE(description, ''))` (for full-text search)

**Validation Rules**:
- `title` must be 1-500 characters
- `priority` must be one of: 'Low', 'Medium', 'High'
- `due_date` must be timezone-aware (stored in UTC, displayed in user's timezone)
- If `is_recurring` is TRUE, `recurrence_rule_id` must be set
- If `parent_task_id` is set, task is part of recurring series
- `completed` tasks cannot have future reminders scheduled

**State Transitions**:
```
[Created] → [Active] → [Completed]
    ↓           ↓
[Deleted]   [Deleted]

Recurring tasks:
[Completed] → [Next Instance Created] (via Recurring Service)
```

---

### Entity: Tag

**Schema**: `tasks`
**Table**: `tags`
**Owner**: Backend API

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique tag identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → users(id) | Tag owner |
| name | VARCHAR(100) | NOT NULL | Tag name (case-insensitive) |
| color | VARCHAR(7) | NOT NULL | Hex color code (e.g., #FF5733) |
| usage_count | INTEGER | NOT NULL, DEFAULT 0 | Number of tasks using this tag |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `user_id, LOWER(name)` (case-insensitive uniqueness)
- INDEX on `user_id` (for user-scoped queries)

**Validation Rules**:
- `name` must be 1-100 characters
- `name` is case-insensitive (stored as-is, compared with LOWER())
- `color` must be valid hex color code (#RRGGBB format)
- `color` is auto-assigned on creation (from predefined palette) but can be changed by user
- `usage_count` is automatically updated when tasks are tagged/untagged

**Color Palette** (auto-assigned):
```
#FF5733 (Red-Orange)
#33FF57 (Green)
#3357FF (Blue)
#FF33F5 (Magenta)
#F5FF33 (Yellow)
#33FFF5 (Cyan)
#FF8C33 (Orange)
#8C33FF (Purple)
#33FF8C (Mint)
#FF3333 (Red)
```

---

### Entity: TaskTag (Join Table)

**Schema**: `tasks`
**Table**: `task_tags`
**Owner**: Backend API

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| task_id | UUID | NOT NULL, FOREIGN KEY → tasks(id) ON DELETE CASCADE | Task reference |
| tag_id | UUID | NOT NULL, FOREIGN KEY → tags(id) ON DELETE CASCADE | Tag reference |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Association timestamp |

**Indexes**:
- PRIMARY KEY on `(task_id, tag_id)`
- INDEX on `tag_id` (for reverse lookup)

**Validation Rules**:
- Maximum 10 tags per task (enforced by application)
- Duplicate task-tag associations prevented by primary key

---

### Entity: Reminder

**Schema**: `tasks`
**Table**: `reminders`
**Owner**: Backend API

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique reminder identifier |
| task_id | UUID | NOT NULL, FOREIGN KEY → tasks(id) ON DELETE CASCADE | Task reference |
| user_id | UUID | NOT NULL, FOREIGN KEY → users(id) | Reminder owner |
| scheduled_time | TIMESTAMP WITH TIME ZONE | NOT NULL | Exact reminder time |
| reminder_type | VARCHAR(20) | NOT NULL | Type: 15min, 1hr, 1day, 1week, custom |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Status: pending, sent, failed |
| dapr_job_id | VARCHAR(255) | NULL | Dapr Jobs API job identifier |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `task_id` (for task-scoped queries)
- INDEX on `user_id, scheduled_time` (for user's upcoming reminders)
- INDEX on `status, scheduled_time` (for pending reminders)
- INDEX on `dapr_job_id` (for Dapr job lookup)

**Validation Rules**:
- `scheduled_time` must be in the future when created
- `reminder_type` must be one of: '15min', '1hr', '1day', '1week', 'custom'
- `status` must be one of: 'pending', 'sent', 'failed'
- Maximum 5 reminders per task (enforced by application)
- `dapr_job_id` is set when reminder is scheduled via Dapr Jobs API

**State Transitions**:
```
[pending] → [sent] (successful delivery)
[pending] → [failed] (after 3 retry attempts)
```

---

### Entity: RecurrenceRule

**Schema**: `tasks`
**Table**: `recurrence_rules`
**Owner**: Backend API

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique recurrence rule identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → users(id) | Rule owner |
| recurrence_type | VARCHAR(20) | NOT NULL | Type: daily, weekly, monthly, yearly, custom |
| interval | INTEGER | NOT NULL, DEFAULT 1 | Interval (e.g., every N days) |
| days_of_week | INTEGER[] | NULL | Days of week (0=Sunday, 6=Saturday) for weekly |
| day_of_month | INTEGER | NULL | Day of month (1-31) for monthly |
| month_of_year | INTEGER | NULL | Month (1-12) for yearly |
| custom_pattern | TEXT | NULL | Custom cron-like pattern (if custom type) |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for user-scoped queries)

**Validation Rules**:
- `recurrence_type` must be one of: 'daily', 'weekly', 'monthly', 'yearly', 'custom'
- `interval` must be >= 1
- For `weekly` type: `days_of_week` must be set (array of 0-6)
- For `monthly` type: `day_of_month` must be 1-31 or NULL (for relative dates like "first Monday")
- For `yearly` type: `month_of_year` must be 1-12
- For `custom` type: `custom_pattern` must be valid cron expression

**Recurrence Patterns**:
- **Daily**: Every N days (interval = N)
- **Weekly**: Specific days of week (days_of_week = [1, 3, 5] for Mon, Wed, Fri)
- **Monthly**: Specific day of month (day_of_month = 15 for 15th of each month)
- **Yearly**: Specific date (month_of_year = 12, day_of_month = 25 for Dec 25)
- **Custom**: Cron expression (custom_pattern = "0 9 * * 1-5" for weekdays at 9am)

---

### Entity: NotificationLog

**Schema**: `notifications`
**Table**: `notification_log`
**Owner**: Notification Service

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique log entry identifier |
| reminder_id | UUID | NOT NULL | Reminder reference (from tasks.reminders) |
| user_id | UUID | NOT NULL | User reference |
| task_id | UUID | NOT NULL | Task reference |
| attempt_number | INTEGER | NOT NULL, DEFAULT 1 | Retry attempt number (1-3) |
| status | VARCHAR(20) | NOT NULL | Status: sent, failed, retrying |
| email_provider_response | TEXT | NULL | Response from email provider (Resend) |
| error_message | TEXT | NULL | Error message if failed |
| sent_at | TIMESTAMP WITH TIME ZONE | NULL | Successful delivery timestamp |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Log entry timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `reminder_id` (for reminder-scoped queries)
- INDEX on `user_id, created_at` (for user notification history)
- INDEX on `status, created_at` (for failed notification monitoring)

**Validation Rules**:
- `attempt_number` must be 1-3 (max 3 retry attempts)
- `status` must be one of: 'sent', 'failed', 'retrying'
- `sent_at` is set only when status = 'sent'

**Retry Logic**:
```
Attempt 1: Immediate (0 seconds)
Attempt 2: After 5 minutes (300 seconds)
Attempt 3: After 15 minutes (900 seconds)
After 3 attempts: Mark as failed
```

---

### Entity: TaskAudit

**Schema**: `audit`
**Table**: `task_audit`
**Owner**: Recurring Service

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique audit entry identifier |
| task_id | UUID | NOT NULL | Task reference |
| user_id | UUID | NOT NULL | User reference |
| parent_task_id | UUID | NULL | Parent task for recurring series |
| event_type | VARCHAR(50) | NOT NULL | Event: created, completed, next_instance_created |
| event_data | JSONB | NULL | Event payload (task state snapshot) |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Event timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `task_id` (for task history)
- INDEX on `parent_task_id` (for recurring series history)
- INDEX on `user_id, created_at` (for user activity timeline)
- GIN INDEX on `event_data` (for JSONB queries)

**Validation Rules**:
- `event_type` must be one of: 'created', 'completed', 'next_instance_created', 'deleted'
- `event_data` contains full task state at time of event (for audit trail)

---

## Relationships

### One-to-Many Relationships

1. **User → Tasks**
   - One user has many tasks
   - Foreign key: `tasks.user_id` → `users.id`
   - Cascade: DELETE CASCADE (delete user deletes all tasks)

2. **User → Tags**
   - One user has many tags
   - Foreign key: `tags.user_id` → `users.id`
   - Cascade: DELETE CASCADE (delete user deletes all tags)

3. **User → Reminders**
   - One user has many reminders
   - Foreign key: `reminders.user_id` → `users.id`
   - Cascade: DELETE CASCADE (delete user deletes all reminders)

4. **User → RecurrenceRules**
   - One user has many recurrence rules
   - Foreign key: `recurrence_rules.user_id` → `users.id`
   - Cascade: DELETE CASCADE (delete user deletes all rules)

5. **Task → Reminders**
   - One task has many reminders (max 5)
   - Foreign key: `reminders.task_id` → `tasks.id`
   - Cascade: DELETE CASCADE (delete task deletes all reminders)

6. **Task → RecurringInstances**
   - One parent task has many recurring instances
   - Foreign key: `tasks.parent_task_id` → `tasks.id`
   - Cascade: SET NULL (delete parent keeps instances)

7. **RecurrenceRule → Tasks**
   - One recurrence rule has many tasks
   - Foreign key: `tasks.recurrence_rule_id` → `recurrence_rules.id`
   - Cascade: SET NULL (delete rule keeps tasks but stops recurrence)

### Many-to-Many Relationships

1. **Tasks ↔ Tags**
   - Many tasks can have many tags
   - Join table: `task_tags`
   - Foreign keys:
     - `task_tags.task_id` → `tasks.id` (DELETE CASCADE)
     - `task_tags.tag_id` → `tags.id` (DELETE CASCADE)
   - Constraint: Maximum 10 tags per task

---

## Data Constraints

### Application-Level Constraints

| Constraint | Enforcement | Validation |
|------------|-------------|------------|
| Max 10 tags per task | Application | Check count before insert |
| Max 5 reminders per task | Application | Check count before insert |
| Max 100 unique tags per user | Application | Check count before insert |
| Max 10,000 tasks per user | Application | Check count before insert |
| Tag name case-insensitive uniqueness | Database | UNIQUE INDEX on LOWER(name) |
| Priority must be Low/Medium/High | Database | CHECK constraint |
| Reminder type must be valid | Database | CHECK constraint |
| Recurrence type must be valid | Database | CHECK constraint |

### Database-Level Constraints

```sql
-- Priority constraint
ALTER TABLE tasks.tasks
ADD CONSTRAINT check_priority
CHECK (priority IN ('Low', 'Medium', 'High'));

-- Reminder type constraint
ALTER TABLE tasks.reminders
ADD CONSTRAINT check_reminder_type
CHECK (reminder_type IN ('15min', '1hr', '1day', '1week', 'custom'));

-- Reminder status constraint
ALTER TABLE tasks.reminders
ADD CONSTRAINT check_reminder_status
CHECK (status IN ('pending', 'sent', 'failed'));

-- Recurrence type constraint
ALTER TABLE tasks.recurrence_rules
ADD CONSTRAINT check_recurrence_type
CHECK (recurrence_type IN ('daily', 'weekly', 'monthly', 'yearly', 'custom'));

-- Recurrence interval constraint
ALTER TABLE tasks.recurrence_rules
ADD CONSTRAINT check_interval_positive
CHECK (interval >= 1);

-- Notification status constraint
ALTER TABLE notifications.notification_log
ADD CONSTRAINT check_notification_status
CHECK (status IN ('sent', 'failed', 'retrying'));

-- Notification attempt constraint
ALTER TABLE notifications.notification_log
ADD CONSTRAINT check_attempt_number
CHECK (attempt_number BETWEEN 1 AND 3);
```

---

## Migration Strategy

### Phase 1: Schema Creation
1. Create service-specific schemas: `tasks`, `notifications`, `audit`
2. Grant appropriate permissions to service users

### Phase 2: Table Creation
1. Create tables in dependency order (users → tasks → tags → task_tags → reminders → recurrence_rules)
2. Create indexes for performance
3. Add foreign key constraints
4. Add check constraints

### Phase 3: Data Migration (if applicable)
1. Migrate existing tasks from monolithic schema
2. Add default priority ('Low') to existing tasks
3. Create audit entries for existing tasks

### Phase 4: Validation
1. Verify all constraints are enforced
2. Test cascade deletes
3. Validate index performance with sample data

---

## Query Patterns

### Common Queries

**1. Get user's tasks with filters**
```sql
SELECT t.*, array_agg(tg.name) as tags
FROM tasks.tasks t
LEFT JOIN tasks.task_tags tt ON t.id = tt.task_id
LEFT JOIN tasks.tags tg ON tt.tag_id = tg.id
WHERE t.user_id = $1
  AND t.completed = $2  -- optional filter
  AND t.priority = $3   -- optional filter
  AND t.due_date BETWEEN $4 AND $5  -- optional filter
GROUP BY t.id
ORDER BY t.created_at DESC
LIMIT $6 OFFSET $7;
```

**2. Full-text search**
```sql
SELECT t.*, ts_rank(to_tsvector('english', t.title || ' ' || COALESCE(t.description, '')), query) as rank
FROM tasks.tasks t,
     to_tsquery('english', $2) query
WHERE t.user_id = $1
  AND to_tsvector('english', t.title || ' ' || COALESCE(t.description, '')) @@ query
ORDER BY rank DESC
LIMIT 50;
```

**3. Get tasks with specific tags (AND logic)**
```sql
SELECT t.*
FROM tasks.tasks t
WHERE t.user_id = $1
  AND t.id IN (
    SELECT tt.task_id
    FROM tasks.task_tags tt
    JOIN tasks.tags tg ON tt.tag_id = tg.id
    WHERE tg.user_id = $1 AND tg.name = ANY($2)
    GROUP BY tt.task_id
    HAVING COUNT(DISTINCT tg.id) = $3  -- number of tags
  );
```

**4. Get upcoming reminders**
```sql
SELECT r.*, t.title as task_title
FROM tasks.reminders r
JOIN tasks.tasks t ON r.task_id = t.id
WHERE r.user_id = $1
  AND r.status = 'pending'
  AND r.scheduled_time BETWEEN NOW() AND NOW() + INTERVAL '7 days'
ORDER BY r.scheduled_time ASC;
```

**5. Get recurring task series**
```sql
SELECT t.*
FROM tasks.tasks t
WHERE t.parent_task_id = $1
ORDER BY t.created_at DESC;
```

---

## Performance Considerations

### Index Strategy
- All foreign keys have indexes for join performance
- Composite indexes for common filter combinations (user_id + status, user_id + priority)
- GIN index for full-text search on task title and description
- GIN index for JSONB queries on audit event_data

### Query Optimization
- Use EXPLAIN ANALYZE to validate query plans
- Limit result sets with pagination (LIMIT/OFFSET)
- Use connection pooling to reduce connection overhead
- Cache frequently accessed data (tags, user preferences)

### Scaling Strategy
- Horizontal scaling via read replicas for read-heavy workloads
- Partition large tables by user_id if needed (10,000+ users)
- Archive old audit logs to separate table (retention policy)

---

**Data Model Complete**: 2026-02-14
**Next Step**: Generate API contracts in contracts/ directory
