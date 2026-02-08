# Research: Phase V Advanced Features

**Date**: 2026-02-06
**Feature**: Phase V - Advanced Features with Dapr-First Architecture
**Status**: Complete

## Table of Contents

1. [Dapr Jobs API Patterns](#1-dapr-jobs-api-patterns)
2. [Server-Sent Events in FastAPI](#2-server-sent-events-in-fastapi)
3. [Redis Streams for Dapr Pub/Sub](#3-redis-streams-for-dapr-pubsub)
4. [Graceful Degradation Strategies](#4-graceful-degradation-strategies)
5. [Recurring Task Scheduling Patterns](#5-recurring-task-scheduling-patterns)
6. [Multi-User Task Isolation](#6-multi-user-task-isolation)

---

## 1. Dapr Jobs API Patterns

### Overview

Dapr Jobs API (introduced in v1.12) provides a unified interface for scheduling and managing jobs across different schedulers. This research addresses how to use Dapr Jobs API for reminder scheduling and recurring task generation.

### Decision: Dapr Jobs API with HTTP Callbacks

**Chosen Approach**: Use Dapr Jobs API for scheduling with HTTP callback endpoints for job execution

**Rationale**:
1. Dapr Jobs API provides unified interface across different job schedulers (cron, Kubernetes CronJob, etc.)
2. HTTP callbacks integrate naturally with FastAPI backend
3. Jobs are persisted and survive application restarts
4. Built-in retry and failure handling
5. No need for separate cron daemon or scheduler service

**Alternatives Considered**:
- **Option A**: Dapr Bindings with Cron - Rejected because bindings are for external systems, not internal scheduling
- **Option B**: Kubernetes CronJobs - Rejected because it requires separate pod deployments and doesn't work in Phase III
- **Option C**: Python APScheduler - Rejected because it violates Dapr-first mandate and doesn't persist across restarts

### Implementation Patterns

#### 1. Schedule Reminder Job

```python
import httpx
from datetime import datetime
from typing import Dict, Any

async def schedule_reminder(
    task_id: str,
    user_id: str,
    reminder_time: datetime,
    dapr_http_port: int = 3500
) -> str:
    """
    Schedule a reminder job using Dapr Jobs API.

    Args:
        task_id: Task identifier
        user_id: User identifier (for callback context)
        reminder_time: When to trigger the reminder (UTC)
        dapr_http_port: Dapr sidecar HTTP port

    Returns:
        Job ID for tracking and cancellation
    """
    job_name = f"reminder-{task_id}"

    # Dapr Jobs API: POST /v1.0-alpha1/jobs/{job-name}
    url = f"http://localhost:{dapr_http_port}/v1.0-alpha1/jobs/{job_name}"

    payload = {
        "schedule": reminder_time.isoformat(),  # One-time job at specific time
        "repeats": 1,  # Execute once
        "dueTime": reminder_time.isoformat(),
        "data": {
            "task_id": task_id,
            "user_id": user_id,
            "reminder_type": "due_date"
        },
        "callback": {
            "method": "POST",
            "endpoint": f"http://localhost:8000/api/internal/reminders/trigger"
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        return result.get("jobId", job_name)
```

#### 2. Schedule Recurring Task Generation Job

```python
async def schedule_recurring_task_generation(
    task_id: str,
    user_id: str,
    recurrence_pattern: str,  # "daily", "weekly", "monthly"
    start_time: datetime,
    dapr_http_port: int = 3500
) -> str:
    """
    Schedule recurring task generation using Dapr Jobs API.

    Args:
        task_id: Parent task identifier
        user_id: User identifier
        recurrence_pattern: Recurrence frequency
        start_time: When to start generating instances
        dapr_http_port: Dapr sidecar HTTP port

    Returns:
        Job ID for tracking and cancellation
    """
    job_name = f"recurring-{task_id}"

    # Convert recurrence pattern to cron expression
    cron_schedule = {
        "daily": "0 0 * * *",      # Midnight UTC daily
        "weekly": "0 0 * * 0",     # Midnight UTC every Sunday
        "monthly": "0 0 1 * *"     # Midnight UTC on 1st of month
    }.get(recurrence_pattern, "0 0 * * *")

    url = f"http://localhost:{dapr_http_port}/v1.0-alpha1/jobs/{job_name}"

    payload = {
        "schedule": cron_schedule,  # Cron expression
        "repeats": 0,  # Infinite repeats (0 = forever)
        "dueTime": start_time.isoformat(),
        "data": {
            "task_id": task_id,
            "user_id": user_id,
            "recurrence_pattern": recurrence_pattern
        },
        "callback": {
            "method": "POST",
            "endpoint": f"http://localhost:8000/api/internal/recurring/generate"
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        return result.get("jobId", job_name)
```

#### 3. Cancel Job

```python
async def cancel_job(
    job_name: str,
    dapr_http_port: int = 3500
) -> None:
    """
    Cancel a scheduled job using Dapr Jobs API.

    Args:
        job_name: Job identifier
        dapr_http_port: Dapr sidecar HTTP port
    """
    # Dapr Jobs API: DELETE /v1.0-alpha1/jobs/{job-name}
    url = f"http://localhost:{dapr_http_port}/v1.0-alpha1/jobs/{job_name}"

    async with httpx.AsyncClient() as client:
        response = await client.delete(url)
        response.raise_for_status()
```

#### 4. Job Callback Endpoints

```python
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone

router = APIRouter(prefix="/api/internal")

@router.post("/reminders/trigger")
async def trigger_reminder(request: Request):
    """
    Callback endpoint for reminder jobs.

    Called by Dapr Jobs API when reminder time arrives.
    """
    payload = await request.json()

    task_id = payload.get("task_id")
    user_id = payload.get("user_id")

    # Publish reminder event to SSE stream
    await publish_reminder_event(user_id, task_id)

    # Publish to Dapr pub/sub for audit
    await publish_event(
        topic="task-reminders",
        event_type="REMINDER_DUE",
        task_id=task_id,
        payload={"user_id": user_id, "timestamp": datetime.now(timezone.utc).isoformat()}
    )

    return {"status": "success"}


@router.post("/recurring/generate")
async def generate_recurring_instance(request: Request):
    """
    Callback endpoint for recurring task generation jobs.

    Called by Dapr Jobs API on schedule (daily/weekly/monthly).
    """
    payload = await request.json()

    task_id = payload.get("task_id")
    user_id = payload.get("user_id")
    recurrence_pattern = payload.get("recurrence_pattern")

    # Get parent task
    parent_task = await task_repository.get(user_id, task_id)

    if parent_task is None:
        # Parent task deleted, cancel job
        await cancel_job(f"recurring-{task_id}")
        return {"status": "cancelled", "reason": "parent_task_deleted"}

    # Generate new task instance
    new_task = Task(
        user_id=user_id,
        title=parent_task.title,
        description=parent_task.description,
        priority=parent_task.priority,
        tags=parent_task.tags,
        due_date=calculate_next_due_date(parent_task.due_date, recurrence_pattern),
        completed=False
    )

    await task_repository.create(user_id, new_task)

    # Publish event
    await publish_event(
        topic="task-recurring",
        event_type="TASK_CREATED",
        task_id=new_task.id,
        payload={
            "parent_task_id": task_id,
            "recurrence_pattern": recurrence_pattern
        }
    )

    return {"status": "success", "new_task_id": new_task.id}
```

### Implementation Notes

**Dapr Jobs Component Configuration**:

```yaml
# dapr/components/jobs.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: jobs-scheduler
  namespace: default
spec:
  type: jobs.scheduler
  version: v1
  metadata:
  - name: storeName
    value: "redis-state"  # Use same Redis for job persistence
```

**Job Persistence**: Jobs are persisted in the state store, so they survive application restarts.

**Failure Handling**: Dapr Jobs API automatically retries failed callbacks with exponential backoff.

**Monitoring**: Use Dapr dashboard to view scheduled jobs and execution history.

---

## 2. Server-Sent Events in FastAPI

### Overview

Server-Sent Events (SSE) provide unidirectional server-to-client push for real-time notifications. This research addresses SSE implementation in FastAPI for delivering reminder notifications to users.

### Decision: FastAPI StreamingResponse with Per-User Connection Management

**Chosen Approach**: Use FastAPI `StreamingResponse` with async generators for SSE, maintain per-user connection registry

**Rationale**:
1. SSE is simpler than WebSockets for unidirectional push (no client-to-server messages needed)
2. FastAPI has built-in support for streaming responses
3. SSE automatically reconnects on connection loss
4. Works through HTTP/HTTPS without special proxy configuration
5. Browser EventSource API provides native client support

**Alternatives Considered**:
- **Option A**: WebSockets - Rejected because bidirectional communication is unnecessary overhead
- **Option B**: Long polling - Rejected due to higher latency and server resource usage
- **Option C**: Push notifications - Rejected because in-app notifications are sufficient for MVP

### Implementation Patterns

#### 1. SSE Endpoint

```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json

router = APIRouter(prefix="/api/notifications")

@router.get("/stream")
async def notification_stream(
    request: Request,
    user_id: str = Depends(get_current_user_id)
) -> StreamingResponse:
    """
    SSE endpoint for real-time notifications.

    Client connects with:
    const eventSource = new EventSource('/api/notifications/stream', {
        headers: { 'Authorization': 'Bearer <token>' }
    });
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        """
        Generate SSE events for user.

        Yields SSE-formatted messages.
        """
        # Register connection
        connection_id = await notification_manager.register(user_id)

        try:
            # Send initial connection event
            yield format_sse_event(
                event="connected",
                data={"user_id": user_id, "connection_id": connection_id}
            )

            # Keep connection alive and send events
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                # Get pending notifications for user
                notifications = await notification_manager.get_pending(user_id)

                for notification in notifications:
                    yield format_sse_event(
                        event="reminder",
                        data=notification,
                        id=notification.get("id")
                    )

                # Send heartbeat every 30 seconds
                yield format_sse_event(event="heartbeat", data={"timestamp": datetime.now(timezone.utc).isoformat()})

                # Wait before next check
                await asyncio.sleep(30)

        finally:
            # Unregister connection on disconnect
            await notification_manager.unregister(user_id, connection_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


def format_sse_event(event: str, data: dict, id: str = None) -> str:
    """
    Format data as SSE event.

    SSE format:
    event: <event-type>
    id: <event-id>
    data: <json-data>

    (blank line)
    """
    lines = []

    if event:
        lines.append(f"event: {event}")

    if id:
        lines.append(f"id: {id}")

    lines.append(f"data: {json.dumps(data)}")
    lines.append("")  # Blank line terminates event

    return "\n".join(lines) + "\n"
```

#### 2. Connection Manager

```python
from typing import Dict, List, Set
import asyncio
from collections import defaultdict
import uuid

class NotificationManager:
    """
    Manage SSE connections and notifications per user.

    Thread-safe connection registry with per-user queues.
    """

    def __init__(self):
        self._connections: Dict[str, Set[str]] = defaultdict(set)  # user_id -> connection_ids
        self._queues: Dict[str, asyncio.Queue] = {}  # user_id -> notification queue
        self._lock = asyncio.Lock()

    async def register(self, user_id: str) -> str:
        """
        Register new SSE connection for user.

        Returns:
            Connection ID
        """
        connection_id = str(uuid.uuid4())

        async with self._lock:
            self._connections[user_id].add(connection_id)

            # Create queue if first connection for user
            if user_id not in self._queues:
                self._queues[user_id] = asyncio.Queue()

        return connection_id

    async def unregister(self, user_id: str, connection_id: str) -> None:
        """
        Unregister SSE connection.
        """
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(connection_id)

                # Clean up if no more connections
                if not self._connections[user_id]:
                    del self._connections[user_id]
                    if user_id in self._queues:
                        del self._queues[user_id]

    async def send_notification(self, user_id: str, notification: dict) -> None:
        """
        Send notification to user's SSE stream.

        Args:
            user_id: Target user
            notification: Notification payload
        """
        async with self._lock:
            if user_id in self._queues:
                await self._queues[user_id].put(notification)

    async def get_pending(self, user_id: str) -> List[dict]:
        """
        Get pending notifications for user (non-blocking).

        Returns:
            List of notifications (empty if none pending)
        """
        notifications = []

        if user_id in self._queues:
            queue = self._queues[user_id]

            # Drain queue without blocking
            while not queue.empty():
                try:
                    notification = queue.get_nowait()
                    notifications.append(notification)
                except asyncio.QueueEmpty:
                    break

        return notifications

    def is_connected(self, user_id: str) -> bool:
        """Check if user has active SSE connections."""
        return user_id in self._connections and len(self._connections[user_id]) > 0


# Global instance
notification_manager = NotificationManager()
```

#### 3. Publishing Notifications

```python
async def publish_reminder_event(user_id: str, task_id: str) -> None:
    """
    Publish reminder notification to user's SSE stream.

    Called by Dapr Jobs callback when reminder is due.
    """
    # Get task details
    task = await task_repository.get(user_id, task_id)

    if task is None:
        return

    # Create notification payload
    notification = {
        "id": str(uuid.uuid4()),
        "type": "reminder",
        "task_id": task_id,
        "title": task.title,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "message": f"Reminder: {task.title} is due soon",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Send to SSE stream
    await notification_manager.send_notification(user_id, notification)
```

#### 4. Frontend Client

```typescript
// src/services/sse/notificationClient.ts
export class NotificationClient {
  private eventSource: EventSource | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(token: string, onNotification: (notification: any) => void) {
    const url = `/api/notifications/stream`;

    // EventSource doesn't support custom headers, use query param for auth
    this.eventSource = new EventSource(`${url}?token=${token}`);

    this.eventSource.addEventListener('connected', (event) => {
      console.log('SSE connected:', event.data);
      this.reconnectAttempts = 0;
    });

    this.eventSource.addEventListener('reminder', (event) => {
      const notification = JSON.parse(event.data);
      onNotification(notification);
    });

    this.eventSource.addEventListener('heartbeat', (event) => {
      console.log('SSE heartbeat:', event.data);
    });

    this.eventSource.onerror = (error) => {
      console.error('SSE error:', error);

      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => this.connect(token, onNotification), 5000);
      }
    };
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}
```

### Implementation Notes

**Authentication**: Use query parameter for token since EventSource doesn't support custom headers.

**Reconnection**: Browser automatically reconnects on connection loss. Use Last-Event-ID header for resume.

**Heartbeat**: Send heartbeat every 30 seconds to keep connection alive through proxies.

**Scalability**: For >1000 concurrent connections, consider Redis Pub/Sub for cross-instance notification delivery.

---

## 3. Redis Streams for Dapr Pub/Sub

### Overview

Redis Streams provides a log-based message broker suitable for event streaming. This research addresses configuring Redis Streams as the Dapr Pub/Sub component for task events.

### Decision: Redis Streams with Consumer Groups

**Chosen Approach**: Use Redis Streams as Dapr Pub/Sub backend with consumer groups for scalability

**Rationale**:
1. Redis Streams provides persistent message log with consumer groups
2. Supports multiple consumers for horizontal scaling
3. Built-in message acknowledgment and retry
4. Lower operational complexity than Kafka for MVP
5. Same Redis instance can serve both state store and pub/sub

**Alternatives Considered**:
- **Option A**: Kafka - Rejected due to operational complexity and infrastructure overhead for Phase III
- **Option B**: Redis Pub/Sub (classic) - Rejected because it doesn't persist messages or support consumer groups
- **Option C**: RabbitMQ - Rejected due to additional infrastructure dependency

### Implementation Patterns

#### 1. Dapr Pub/Sub Component Configuration

```yaml
# dapr/components/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redis-pubsub
  namespace: default
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: "localhost:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-secret
      key: password
  - name: enableTLS
    value: "false"
  - name: consumerID
    value: "todo-backend-{podName}"  # Unique per instance
  - name: processingTimeout
    value: "60s"
  - name: redeliverInterval
    value: "30s"
  - name: queueDepth
    value: "100"
  - name: concurrency
    value: "10"
```

#### 2. Topic Configuration

```yaml
# Event topics
topics:
  - name: task-events
    description: Task lifecycle events (CREATED, UPDATED, COMPLETED)
    retention: 7d
    consumer_group: task-events-consumers

  - name: task-reminders
    description: Reminder notifications
    retention: 1d
    consumer_group: reminder-consumers

  - name: task-recurring
    description: Recurring task generation events
    retention: 7d
    consumer_group: recurring-consumers

  - name: task-audit
    description: Audit log stream (all events)
    retention: 30d
    consumer_group: audit-consumers
```

#### 3. Publishing Events

```python
import httpx
from datetime import datetime, timezone
from typing import Dict, Any

async def publish_event(
    topic: str,
    event_type: str,
    task_id: str,
    payload: Dict[str, Any],
    dapr_http_port: int = 3500,
    pubsub_name: str = "redis-pubsub"
) -> None:
    """
    Publish event to Dapr Pub/Sub.

    Args:
        topic: Event topic (task-events, task-reminders, etc.)
        event_type: Event type (TASK_CREATED, TASK_UPDATED, etc.)
        task_id: Task identifier
        payload: Event-specific data
        dapr_http_port: Dapr sidecar HTTP port
        pubsub_name: Dapr pub/sub component name
    """
    # Dapr Pub/Sub API: POST /v1.0/publish/{pubsub}/{topic}
    url = f"http://localhost:{dapr_http_port}/v1.0/publish/{pubsub_name}/{topic}"

    event = {
        "task_id": task_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=event)
        response.raise_for_status()


# Usage examples
async def on_task_created(task: Task) -> None:
    """Publish TASK_CREATED event."""
    await publish_event(
        topic="task-events",
        event_type="TASK_CREATED",
        task_id=task.id,
        payload={
            "user_id": task.user_id,
            "title": task.title,
            "priority": task.priority,
            "tags": task.tags
        }
    )

async def on_task_completed(task: Task) -> None:
    """Publish TASK_COMPLETED event."""
    await publish_event(
        topic="task-events",
        event_type="TASK_COMPLETED",
        task_id=task.id,
        payload={
            "user_id": task.user_id,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
    )
```

#### 4. Subscribing to Events

```yaml
# dapr/subscriptions/task-events.yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: redis-pubsub
  topic: task-events
  routes:
    default: /api/events/task-events
  deadLetterTopic: task-events-dlq
  bulkSubscribe:
    enabled: true
    maxMessagesCount: 100
    maxAwaitDurationMs: 1000
```

```python
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/events")

@router.post("/task-events")
async def handle_task_event(request: Request):
    """
    Handle task events from Dapr Pub/Sub.

    Called by Dapr runtime when events are published to task-events topic.
    """
    event = await request.json()

    task_id = event.get("task_id")
    event_type = event.get("event_type")
    timestamp = event.get("timestamp")
    payload = event.get("payload")

    # Process event based on type
    if event_type == "TASK_CREATED":
        await handle_task_created(task_id, payload)
    elif event_type == "TASK_UPDATED":
        await handle_task_updated(task_id, payload)
    elif event_type == "TASK_COMPLETED":
        await handle_task_completed(task_id, payload)

    # Return success to acknowledge message
    return {"status": "SUCCESS"}
```

### Implementation Notes

**Message Retention**: Redis Streams retains messages based on MAXLEN or time-based trimming.

**Consumer Groups**: Each consumer group maintains independent read position, enabling multiple subscribers.

**Dead Letter Queue**: Failed messages are sent to DLQ topic after max retries.

**Ordering**: Messages within same partition key are processed in order.

---

## 4. Graceful Degradation Strategies

### Overview

The system must function (with reduced features) when Dapr is unavailable. This research addresses fallback strategies for Dapr dependencies.

### Decision: Local Fallback with Retry Queue

**Chosen Approach**: Implement local fallback adapters with retry queue for Dapr operations

**Rationale**:
1. System remains operational during Dapr outages
2. Operations are queued and retried when Dapr recovers
3. Critical features (task CRUD) work without Dapr
4. Non-critical features (events, reminders) degrade gracefully
5. Clear degradation matrix for user communication

**Alternatives Considered**:
- **Option A**: Fail fast - Rejected because it makes system completely unavailable
- **Option B**: Dual write to both Dapr and local - Rejected due to consistency issues
- **Option C**: Circuit breaker only - Rejected because it doesn't provide fallback functionality

### Implementation Patterns

#### 1. Degradation Matrix

| Feature | Dapr Available | Dapr Unavailable |
|---------|---------------|------------------|
| Task CRUD | ✅ Redis via Dapr | ✅ In-memory store |
| Task Search/Filter | ✅ Full functionality | ✅ In-memory filtering |
| Event Publishing | ✅ Redis Streams | ⚠️ Local queue (retry later) |
| Reminders | ✅ Dapr Jobs | ⚠️ Disabled (log warning) |
| Recurring Tasks | ✅ Dapr Jobs | ⚠️ Disabled (log warning) |
| SSE Notifications | ✅ Full functionality | ✅ Full functionality |

#### 2. Fallback State Store

```python
from typing import Dict, Optional
import asyncio

class InMemoryStateStore:
    """
    In-memory fallback state store when Dapr is unavailable.

    Warning: Data is lost on application restart.
    """

    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def save(self, key: str, value: Any) -> None:
        """Save state to in-memory store."""
        async with self._lock:
            self._store[key] = value

    async def get(self, key: str) -> Optional[Any]:
        """Get state from in-memory store."""
        async with self._lock:
            return self._store.get(key)

    async def delete(self, key: str) -> None:
        """Delete state from in-memory store."""
        async with self._lock:
            self._store.pop(key, None)

    async def list_keys(self, prefix: str) -> list[str]:
        """List keys with prefix."""
        async with self._lock:
            return [k for k in self._store.keys() if k.startswith(prefix)]


class FallbackStateStoreAdapter:
    """
    State store adapter with Dapr fallback.

    Tries Dapr first, falls back to in-memory on failure.
    """

    def __init__(self, dapr_http_port: int = 3500):
        self.dapr_http_port = dapr_http_port
        self.fallback_store = InMemoryStateStore()
        self.dapr_available = True
        self.retry_queue: asyncio.Queue = asyncio.Queue()

    async def save(self, key: str, value: Any) -> None:
        """Save with fallback."""
        try:
            await self._save_dapr(key, value)
            self.dapr_available = True
        except Exception as e:
            logger.warning(f"Dapr unavailable, using fallback: {e}")
            self.dapr_available = False
            await self.fallback_store.save(key, value)
            await self.retry_queue.put(("save", key, value))

    async def get(self, key: str) -> Optional[Any]:
        """Get with fallback."""
        try:
            result = await self._get_dapr(key)
            self.dapr_available = True
            return result
        except Exception as e:
            logger.warning(f"Dapr unavailable, using fallback: {e}")
            self.dapr_available = False
            return await self.fallback_store.get(key)

    async def _save_dapr(self, key: str, value: Any) -> None:
        """Save to Dapr state store."""
        url = f"http://localhost:{self.dapr_http_port}/v1.0/state/redis-state"
        payload = [{"key": key, "value": value}]

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

    async def _get_dapr(self, key: str) -> Optional[Any]:
        """Get from Dapr state store."""
        url = f"http://localhost:{self.dapr_http_port}/v1.0/state/redis-state/{key}"

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)

            if response.status_code == 204:
                return None

            response.raise_for_status()
            return response.json()
```

#### 3. Event Queue with Retry

```python
class EventQueueAdapter:
    """
    Event publisher with local queue for retry.

    Events are queued locally when Dapr is unavailable and
    published when Dapr recovers.
    """

    def __init__(self, dapr_http_port: int = 3500):
        self.dapr_http_port = dapr_http_port
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.dapr_available = True
        self._retry_task = None

    async def publish(self, topic: str, event: Dict[str, Any]) -> None:
        """Publish event with retry queue."""
        try:
            await self._publish_dapr(topic, event)
            self.dapr_available = True
        except Exception as e:
            logger.warning(f"Dapr unavailable, queueing event: {e}")
            self.dapr_available = False
            await self.event_queue.put((topic, event))

            # Start retry task if not running
            if self._retry_task is None or self._retry_task.done():
                self._retry_task = asyncio.create_task(self._retry_loop())

    async def _publish_dapr(self, topic: str, event: Dict[str, Any]) -> None:
        """Publish to Dapr Pub/Sub."""
        url = f"http://localhost:{self.dapr_http_port}/v1.0/publish/redis-pubsub/{topic}"

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=event)
            response.raise_for_status()

    async def _retry_loop(self) -> None:
        """Retry queued events periodically."""
        while not self.event_queue.empty():
            try:
                # Wait before retry
                await asyncio.sleep(30)

                # Try to publish queued events
                topic, event = await self.event_queue.get()
                await self._publish_dapr(topic, event)

                logger.info(f"Successfully published queued event to {topic}")
                self.dapr_available = True

            except Exception as e:
                # Put back in queue and wait longer
                await self.event_queue.put((topic, event))
                logger.warning(f"Retry failed, will try again: {e}")
                await asyncio.sleep(60)
```

#### 4. Health Check and Status Endpoint

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/health")

@router.get("/status")
async def get_system_status():
    """
    Get system status including Dapr availability.

    Returns degradation status for client awareness.
    """
    dapr_status = await check_dapr_health()

    return {
        "status": "healthy" if dapr_status else "degraded",
        "dapr_available": dapr_status,
        "features": {
            "task_crud": "available",
            "task_search": "available",
            "events": "available" if dapr_status else "queued",
            "reminders": "available" if dapr_status else "disabled",
            "recurring_tasks": "available" if dapr_status else "disabled"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

async def check_dapr_health() -> bool:
    """Check if Dapr sidecar is healthy."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://localhost:3500/v1.0/healthz")
            return response.status_code == 200
    except Exception:
        return False
```

### Implementation Notes

**Monitoring**: Log all fallback activations for operational visibility.

**Data Sync**: When Dapr recovers, sync in-memory data to Redis.

**User Communication**: Display degradation status in UI.

---

## 5. Recurring Task Scheduling Patterns

### Overview

Recurring tasks must generate new instances on schedule (daily, weekly, monthly). This research addresses algorithms for calculating next recurrence dates.

### Decision: Anchor-Based Recurrence with Edge Case Handling

**Chosen Approach**: Calculate next recurrence based on original task creation date with special handling for month-end

**Rationale**:
1. Predictable recurrence dates (same day of week/month)
2. Handles edge cases (month-end, leap years, DST)
3. Simple algorithm with clear semantics
4. Matches user expectations from specification

**Alternatives Considered**:
- **Option A**: Relative recurrence (from completion date) - Rejected because spec requires anchor to creation date
- **Option B**: Cron-style expressions - Rejected due to complexity for simple daily/weekly/monthly patterns
- **Option C**: iCalendar RRULE - Rejected as over-engineered for MVP requirements

### Implementation Patterns

#### 1. Recurrence Calculation Functions

```python
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

def calculate_next_daily(current_date: datetime) -> datetime:
    """
    Calculate next daily recurrence.

    Args:
        current_date: Current instance date

    Returns:
        Next instance date (current_date + 1 day)
    """
    return current_date + timedelta(days=1)


def calculate_next_weekly(current_date: datetime, anchor_date: datetime) -> datetime:
    """
    Calculate next weekly recurrence.

    Maintains same day of week as anchor date.

    Args:
        current_date: Current instance date
        anchor_date: Original task creation date

    Returns:
        Next instance date (same day of week, +7 days)
    """
    # Add 7 days to maintain same day of week
    return current_date + timedelta(days=7)


def calculate_next_monthly(current_date: datetime, anchor_date: datetime) -> datetime:
    """
    Calculate next monthly recurrence.

    Maintains same day of month as anchor date.
    Handles month-end edge cases.

    Args:
        current_date: Current instance date
        anchor_date: Original task creation date

    Returns:
        Next instance date (same day of month, +1 month)

    Edge cases:
    - If anchor is day 31 and next month has 30 days, use day 30
    - If anchor is day 29-31 and next month is February, use last day of February
    """
    anchor_day = anchor_date.day

    # Add one month
    next_month = current_date + relativedelta(months=1)

    # Get last day of next month
    last_day = calendar.monthrange(next_month.year, next_month.month)[1]

    # Use anchor day or last day of month, whichever is smaller
    target_day = min(anchor_day, last_day)

    return next_month.replace(day=target_day)


def calculate_next_recurrence(
    current_date: datetime,
    anchor_date: datetime,
    recurrence_pattern: str
) -> datetime:
    """
    Calculate next recurrence date based on pattern.

    Args:
        current_date: Current instance date
        anchor_date: Original task creation date
        recurrence_pattern: "daily", "weekly", or "monthly"

    Returns:
        Next recurrence date

    Raises:
        ValueError: If recurrence_pattern is invalid
    """
    if recurrence_pattern == "daily":
        return calculate_next_daily(current_date)
    elif recurrence_pattern == "weekly":
        return calculate_next_weekly(current_date, anchor_date)
    elif recurrence_pattern == "monthly":
        return calculate_next_monthly(current_date, anchor_date)
    else:
        raise ValueError(f"Invalid recurrence pattern: {recurrence_pattern}")
```

#### 2. Edge Case Tests

```python
import pytest
from datetime import datetime

def test_monthly_recurrence_month_end():
    """Test monthly recurrence for tasks created on day 31."""
    # Task created on Jan 31
    anchor = datetime(2026, 1, 31, 0, 0, 0)
    current = datetime(2026, 1, 31, 0, 0, 0)

    # Next recurrence should be Feb 28 (2026 is not a leap year)
    next_date = calculate_next_monthly(current, anchor)
    assert next_date == datetime(2026, 2, 28, 0, 0, 0)

    # Following recurrence should be Mar 31
    next_date = calculate_next_monthly(next_date, anchor)
    assert next_date == datetime(2026, 3, 31, 0, 0, 0)


def test_monthly_recurrence_leap_year():
    """Test monthly recurrence in leap year."""
    # Task created on Jan 31, 2024 (leap year)
    anchor = datetime(2024, 1, 31, 0, 0, 0)
    current = datetime(2024, 1, 31, 0, 0, 0)

    # Next recurrence should be Feb 29 (leap year)
    next_date = calculate_next_monthly(current, anchor)
    assert next_date == datetime(2024, 2, 29, 0, 0, 0)


def test_weekly_recurrence_maintains_day_of_week():
    """Test weekly recurrence maintains same day of week."""
    # Task created on Tuesday, Feb 4, 2026
    anchor = datetime(2026, 2, 4, 0, 0, 0)  # Tuesday
    current = datetime(2026, 2, 4, 0, 0, 0)

    # Next recurrence should be Tuesday, Feb 11
    next_date = calculate_next_weekly(current, anchor)
    assert next_date == datetime(2026, 2, 11, 0, 0, 0)
    assert next_date.weekday() == anchor.weekday()  # Both Tuesday
```

#### 3. Recurring Task Service

```python
class RecurringTaskService:
    """
    Service for managing recurring task generation.
    """

    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def generate_next_instance(
        self,
        parent_task_id: str,
        user_id: str
    ) -> Optional[Task]:
        """
        Generate next instance of recurring task.

        Args:
            parent_task_id: Parent task identifier
            user_id: User identifier

        Returns:
            New task instance or None if parent deleted
        """
        # Get parent task
        parent = await self.task_repository.get(user_id, parent_task_id)

        if parent is None:
            logger.warning(f"Parent task {parent_task_id} not found, skipping generation")
            return None

        if parent.recurrence == "none":
            logger.warning(f"Task {parent_task_id} is not recurring, skipping generation")
            return None

        # Calculate next due date
        if parent.due_date is None:
            logger.warning(f"Task {parent_task_id} has no due date, skipping generation")
            return None

        next_due_date = calculate_next_recurrence(
            current_date=parent.due_date,
            anchor_date=parent.created_at,
            recurrence_pattern=parent.recurrence
        )

        # Create new task instance
        new_task = Task(
            user_id=user_id,
            title=parent.title,
            description=parent.description,
            priority=parent.priority,
            tags=parent.tags,
            due_date=next_due_date,
            recurrence=parent.recurrence,
            reminder_offset_minutes=parent.reminder_offset_minutes,
            completed=False
        )

        await self.task_repository.create(user_id, new_task)

        # Schedule reminder if configured
        if new_task.reminder_offset_minutes:
            reminder_time = next_due_date - timedelta(minutes=new_task.reminder_offset_minutes)
            await schedule_reminder(new_task.id, user_id, reminder_time)

        logger.info(f"Generated recurring task instance: {new_task.id} from parent {parent_task_id}")

        return new_task
```

### Implementation Notes

**Timezone**: All calculations use UTC to avoid DST ambiguity.

**Missed Instances**: If system is down, skip missed instances (don't generate backlog).

**Cancellation**: When parent task is deleted, cancel recurring job to stop future generation.

**Performance**: Batch generation for multiple users to reduce overhead.

---

## 6. Multi-User Task Isolation

### Overview

This research addresses patterns for implementing secure, performant multi-user task isolation using Dapr State Store API with Redis as the backing store. The goal is to ensure users can only access their own tasks while maintaining query performance for filtering, searching, and sorting operations.

### Decision: Hierarchical Key Prefixing with Application-Layer Filtering

**Chosen Approach**: Composite key strategy with user_id prefix + application-layer authorization enforcement

**Rationale**:
1. Dapr State Store API does not provide native query filtering by metadata or key patterns
2. Redis (backing store) supports efficient key scanning with SCAN command and pattern matching
3. Application-layer filtering provides defense-in-depth security
4. Key prefixing enables efficient bulk operations and user-specific queries

**Alternatives Considered**:
- **Option A**: Flat keys with metadata filtering - Rejected because Dapr State Store API doesn't support metadata queries
- **Option B**: Separate state stores per user - Rejected due to operational complexity and resource overhead
- **Option C**: Single key with all user tasks as JSON array - Rejected due to poor performance and concurrency issues

### Implementation Patterns

#### 1. Key Prefixing Strategy

**Pattern**: `{user_id}:task:{task_id}`

```python
# Key construction
def build_task_key(user_id: str, task_id: str) -> str:
    """
    Build hierarchical key for task storage.

    Format: {user_id}:task:{task_id}
    Example: user-123:task:abc-def-456
    """
    return f"{user_id}:task:{task_id}"

# Key parsing
def parse_task_key(key: str) -> tuple[str, str]:
    """
    Parse task key to extract user_id and task_id.

    Returns: (user_id, task_id)
    Raises: ValueError if key format is invalid
    """
    parts = key.split(":")
    if len(parts) != 3 or parts[1] != "task":
        raise ValueError(f"Invalid task key format: {key}")
    return parts[0], parts[2]
```

**Benefits**:
- Natural namespace isolation per user
- Efficient bulk retrieval using key prefix scanning
- Clear ownership semantics in key structure
- Supports Redis SCAN with pattern matching: `SCAN 0 MATCH user-123:task:*`

**Security Considerations**:
- User_id MUST be derived from authenticated session (JWT token, session cookie)
- NEVER accept user_id from client request body or query parameters
- Validate user_id format to prevent key injection attacks (e.g., `user:123:task:*:task:456`)

#### 2. Dapr State Store API Usage

**Save Task** (POST /v1.0/state/{store}):

```python
import httpx
from typing import Any, Dict

async def save_task(
    user_id: str,
    task_id: str,
    task_data: Dict[str, Any],
    dapr_http_port: int = 3500,
    state_store_name: str = "redis-state"
) -> None:
    """
    Save task to Dapr state store with user_id prefix.

    Args:
        user_id: Authenticated user identifier (from session)
        task_id: Task identifier (UUID)
        task_data: Task payload (dict)
        dapr_http_port: Dapr sidecar HTTP port
        state_store_name: Dapr state store component name
    """
    key = build_task_key(user_id, task_id)

    # Dapr state store save request
    url = f"http://localhost:{dapr_http_port}/v1.0/state/{state_store_name}"
    payload = [
        {
            "key": key,
            "value": task_data,
            "metadata": {
                "ttlInSeconds": "0"  # No expiration for tasks
            }
        }
    ]

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
```

**Get Task** (GET /v1.0/state/{store}/{key}):

```python
async def get_task(
    user_id: str,
    task_id: str,
    dapr_http_port: int = 3500,
    state_store_name: str = "redis-state"
) -> Dict[str, Any] | None:
    """
    Retrieve task from Dapr state store with authorization check.

    Args:
        user_id: Authenticated user identifier (from session)
        task_id: Task identifier (UUID)
        dapr_http_port: Dapr sidecar HTTP port
        state_store_name: Dapr state store component name

    Returns:
        Task data dict or None if not found

    Security:
        - user_id is embedded in key, preventing cross-user access
        - Even if attacker guesses task_id, they cannot access without correct user_id
    """
    key = build_task_key(user_id, task_id)

    url = f"http://localhost:{dapr_http_port}/v1.0/state/{state_store_name}/{key}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 204:  # No content = key not found
            return None

        response.raise_for_status()
        return response.json()
```

**Delete Task** (DELETE /v1.0/state/{store}):

```python
async def delete_task(
    user_id: str,
    task_id: str,
    dapr_http_port: int = 3500,
    state_store_name: str = "redis-state"
) -> None:
    """
    Delete task from Dapr state store with authorization check.

    Args:
        user_id: Authenticated user identifier (from session)
        task_id: Task identifier (UUID)
        dapr_http_port: Dapr sidecar HTTP port
        state_store_name: Dapr state store component name
    """
    key = build_task_key(user_id, task_id)

    url = f"http://localhost:{dapr_http_port}/v1.0/state/{state_store_name}"
    payload = [
        {
            "key": key,
            "etag": None  # Optional: use ETags for optimistic concurrency
        }
    ]

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, json=payload)
        response.raise_for_status()
```

#### 3. Bulk Query Patterns (List User's Tasks)

**Challenge**: Dapr State Store API does not provide native query/filter capabilities. We need to work around this limitation.

**Solution**: Use Redis-specific query API or implement application-layer scanning.

**Option A: Dapr State Query API** (Recommended for Redis):

```python
async def list_user_tasks(
    user_id: str,
    dapr_http_port: int = 3500,
    state_store_name: str = "redis-state"
) -> list[Dict[str, Any]]:
    """
    List all tasks for a user using Dapr State Query API.

    Note: Dapr State Query API is supported by some state stores (Redis, MongoDB, etc.)
    but not all. Check Dapr documentation for your state store.

    Args:
        user_id: Authenticated user identifier (from session)
        dapr_http_port: Dapr sidecar HTTP port
        state_store_name: Dapr state store component name

    Returns:
        List of task data dicts
    """
    # Dapr State Query API (POST /v1.0-alpha1/state/{store}/query)
    url = f"http://localhost:{dapr_http_port}/v1.0-alpha1/state/{state_store_name}/query"

    # Query by key prefix
    query = {
        "filter": {
            "EQ": {
                "key": f"{user_id}:task:"
            }
        },
        "sort": [
            {
                "key": "created_at",
                "order": "DESC"
            }
        ],
        "page": {
            "limit": 100  # Pagination limit
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=query)
        response.raise_for_status()

        result = response.json()
        return [item["value"] for item in result.get("results", [])]
```

**Option B: Redis SCAN via Dapr Service Invocation** (Fallback):

If Dapr State Query API is not available, use Redis SCAN command through a custom service:

```python
async def list_user_tasks_scan(
    user_id: str,
    dapr_http_port: int = 3500
) -> list[Dict[str, Any]]:
    """
    List all tasks for a user using Redis SCAN pattern.

    This approach requires a custom service that has direct Redis access
    and exposes a query endpoint. The main application invokes this service
    via Dapr Service Invocation.

    Args:
        user_id: Authenticated user identifier (from session)
        dapr_http_port: Dapr sidecar HTTP port

    Returns:
        List of task data dicts
    """
    # Invoke custom query service via Dapr Service Invocation
    url = f"http://localhost:{dapr_http_port}/v1.0/invoke/task-query-service/method/query-tasks"

    payload = {
        "user_id": user_id,
        "pattern": f"{user_id}:task:*"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
```

**Option C: Maintain User Task Index** (Best Performance):

Maintain a separate index key that stores all task IDs for a user:

```python
# Index key format: {user_id}:task-index
# Value: JSON array of task IDs

async def add_task_to_index(
    user_id: str,
    task_id: str,
    dapr_http_port: int = 3500,
    state_store_name: str = "redis-state"
) -> None:
    """
    Add task ID to user's task index.

    This maintains a separate index for efficient bulk queries.
    Trade-off: Additional write overhead, but much faster reads.
    """
    index_key = f"{user_id}:task-index"

    # Get current index
    url = f"http://localhost:{dapr_http_port}/v1.0/state/{state_store_name}/{index_key}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 204:
            task_ids = []
        else:
            task_ids = response.json()

        # Add new task ID
        if task_id not in task_ids:
            task_ids.append(task_id)

        # Save updated index
        save_url = f"http://localhost:{dapr_http_port}/v1.0/state/{state_store_name}"
        save_payload = [
            {
                "key": index_key,
                "value": task_ids
            }
        ]
        await client.post(save_url, json=save_payload)

async def list_user_tasks_indexed(
    user_id: str,
    dapr_http_port: int = 3500,
    state_store_name: str = "redis-state"
) -> list[Dict[str, Any]]:
    """
    List all tasks for a user using task index.

    This is the most efficient approach for bulk queries.
    """
    index_key = f"{user_id}:task-index"

    # Get task IDs from index
    url = f"http://localhost:{dapr_http_port}/v1.0/state/{state_store_name}/{index_key}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 204:
            return []

        task_ids = response.json()

        # Bulk get tasks (Dapr supports bulk get)
        bulk_url = f"http://localhost:{dapr_http_port}/v1.0/state/{state_store_name}/bulk"
        bulk_payload = {
            "keys": [build_task_key(user_id, task_id) for task_id in task_ids]
        }

        bulk_response = await client.post(bulk_url, json=bulk_payload)
        bulk_response.raise_for_status()

        results = bulk_response.json()
        return [item["value"] for item in results if "value" in item]
```

#### 4. Query Performance Optimization

**Redis Configuration for Dapr State Store**:

```yaml
# dapr/components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redis-state
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "localhost:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-secret
      key: password
  - name: enableTLS
    value: "false"
  - name: maxRetries
    value: "3"
  - name: maxRetryBackoff
    value: "2s"
  # Performance tuning
  - name: queryIndexes
    value: |
      {
        "indexes": [
          {
            "name": "user_id",
            "type": "TEXT"
          },
          {
            "name": "created_at",
            "type": "NUMERIC"
          },
          {
            "name": "priority",
            "type": "TEXT"
          },
          {
            "name": "completed",
            "type": "TEXT"
          }
        ]
      }
```

**Note**: Redis does not natively support secondary indexes. The `queryIndexes` metadata is used by Dapr's query API to build indexes using Redis data structures (sorted sets, hashes).

**Performance Characteristics**:

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Get single task | O(1) | Direct key lookup |
| Save single task | O(1) | Direct key write |
| Delete single task | O(1) | Direct key delete |
| List all user tasks (SCAN) | O(N) | N = total keys in Redis |
| List all user tasks (index) | O(M) | M = user's task count |
| Filter by priority | O(M) | Application-layer filtering |
| Search by text | O(M) | Application-layer filtering |

**Recommendation**: Use **Option C (Task Index)** for production deployments with >1000 tasks per user.

#### 5. Authorization Enforcement at Repository Layer

**Repository Pattern Implementation**:

```python
from typing import Protocol, Optional
from datetime import datetime

class TaskRepository(Protocol):
    """
    Task repository interface for Dapr state store.

    All methods enforce user_id authorization at the repository layer.
    """

    async def create(self, user_id: str, task: Task) -> Task:
        """Create new task for user."""
        ...

    async def get(self, user_id: str, task_id: str) -> Optional[Task]:
        """Get task by ID, returns None if not found or unauthorized."""
        ...

    async def list(self, user_id: str) -> list[Task]:
        """List all tasks for user."""
        ...

    async def update(self, user_id: str, task_id: str, task: Task) -> Task:
        """Update task, raises exception if not found or unauthorized."""
        ...

    async def delete(self, user_id: str, task_id: str) -> None:
        """Delete task, raises exception if not found or unauthorized."""
        ...

    async def filter(
        self,
        user_id: str,
        priority: Optional[str] = None,
        tags: Optional[list[str]] = None,
        completed: Optional[bool] = None
    ) -> list[Task]:
        """Filter tasks by criteria."""
        ...


class DaprTaskRepository:
    """
    Dapr State Store implementation of TaskRepository.

    Security guarantees:
    - All operations require user_id from authenticated session
    - Keys are prefixed with user_id, preventing cross-user access
    - No direct key manipulation from client input
    """

    def __init__(
        self,
        dapr_http_port: int = 3500,
        state_store_name: str = "redis-state"
    ):
        self.dapr_http_port = dapr_http_port
        self.state_store_name = state_store_name

    async def create(self, user_id: str, task: Task) -> Task:
        """
        Create new task for user.

        Security: user_id is embedded in key, ensuring task ownership.
        """
        key = build_task_key(user_id, task.id)

        # Add to task index for efficient listing
        await self._add_to_index(user_id, task.id)

        # Save task
        await save_task(user_id, task.id, task.dict(), self.dapr_http_port, self.state_store_name)

        return task

    async def get(self, user_id: str, task_id: str) -> Optional[Task]:
        """
        Get task by ID with authorization check.

        Security: Key includes user_id, so even if attacker knows task_id,
        they cannot access task without correct user_id.
        """
        task_data = await get_task(user_id, task_id, self.dapr_http_port, self.state_store_name)

        if task_data is None:
            return None

        return Task(**task_data)

    async def list(self, user_id: str) -> list[Task]:
        """
        List all tasks for user.

        Security: Only returns tasks with user_id prefix.
        """
        task_data_list = await list_user_tasks_indexed(user_id, self.dapr_http_port, self.state_store_name)
        return [Task(**data) for data in task_data_list]

    async def filter(
        self,
        user_id: str,
        priority: Optional[str] = None,
        tags: Optional[list[str]] = None,
        completed: Optional[bool] = None
    ) -> list[Task]:
        """
        Filter tasks by criteria.

        Implementation: Fetch all user tasks, then filter in application layer.

        Performance: O(M) where M = user's task count.
        For large task lists (>10k), consider Redis secondary indexes or
        separate filtered indexes.
        """
        tasks = await self.list(user_id)

        # Apply filters
        filtered = tasks

        if priority is not None:
            filtered = [t for t in filtered if t.priority == priority]

        if tags is not None:
            filtered = [t for t in filtered if any(tag in t.tags for tag in tags)]

        if completed is not None:
            filtered = [t for t in filtered if t.completed == completed]

        return filtered

    async def _add_to_index(self, user_id: str, task_id: str) -> None:
        """Add task ID to user's task index."""
        await add_task_to_index(user_id, task_id, self.dapr_http_port, self.state_store_name)
```

#### 6. Security Best Practices

**1. User ID Derivation from Authentication**:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract user_id from JWT token.

    Security: user_id is NEVER accepted from client input.
    Always derived from authenticated session.
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


# API endpoint with authorization
@router.get("/api/tasks")
async def list_tasks(
    user_id: str = Depends(get_current_user_id),  # Derived from token
    repository: TaskRepository = Depends(get_task_repository)
):
    """
    List tasks for authenticated user.

    Security: user_id comes from JWT token, not from client input.
    """
    tasks = await repository.list(user_id)
    return tasks
```

**2. Prevent Key Injection Attacks**:

```python
import re

def validate_user_id(user_id: str) -> str:
    """
    Validate user_id format to prevent key injection.

    Security: Prevent attackers from injecting special characters
    that could manipulate key structure.

    Example attack: user_id = "user1:task:*:task" would break key isolation
    """
    # Allow only alphanumeric, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        raise ValueError(f"Invalid user_id format: {user_id}")

    # Limit length to prevent DoS
    if len(user_id) > 255:
        raise ValueError("user_id too long")

    return user_id


def build_task_key(user_id: str, task_id: str) -> str:
    """
    Build task key with validation.

    Security: Validate inputs before constructing key.
    """
    user_id = validate_user_id(user_id)
    task_id = validate_user_id(task_id)  # Same validation for task_id

    return f"{user_id}:task:{task_id}"
```

**3. Defense in Depth**:

```python
async def get_task_with_authorization(
    user_id: str,
    task_id: str,
    repository: TaskRepository
) -> Task:
    """
    Get task with multiple authorization checks.

    Defense in depth:
    1. user_id from authenticated session (JWT)
    2. Key prefixing prevents cross-user access
    3. Application-layer verification of task ownership
    """
    task = await repository.get(user_id, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Additional verification (redundant but safe)
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    return task
```

**4. Audit Logging**:

```python
import logging

logger = logging.getLogger(__name__)

async def audit_log_access(
    user_id: str,
    operation: str,
    task_id: Optional[str] = None,
    success: bool = True
) -> None:
    """
    Log all task access for security auditing.

    Logs include:
    - User ID
    - Operation (create, read, update, delete)
    - Task ID (if applicable)
    - Timestamp
    - Success/failure
    """
    logger.info(
        f"Task access: user={user_id} operation={operation} "
        f"task={task_id} success={success} timestamp={datetime.utcnow().isoformat()}"
    )
```

### Implementation Notes

**Phase III (Local Development)**:
1. Use Dapr self-hosted mode with Redis state store
2. Implement repository pattern with key prefixing
3. Use task index for efficient bulk queries
4. Test with multiple users to verify isolation

**Phase IV (Kubernetes Deployment)**:
1. Deploy Redis as StatefulSet with persistence
2. Configure Dapr state store component with Redis connection
3. Enable Redis AUTH for security
4. Consider Redis Cluster for horizontal scaling (>100k tasks)

**Performance Targets**:
- Single task operations: <10ms (O(1) Redis operations)
- List all user tasks: <100ms for 1000 tasks (using index)
- Filter operations: <500ms for 1000 tasks (application-layer filtering)
- Search operations: <1s for 10,000 tasks (application-layer filtering)

**Scaling Considerations**:
- For >10k tasks per user: Implement Redis secondary indexes using sorted sets
- For >100k total tasks: Use Redis Cluster with hash slot distribution
- For >1M total tasks: Consider sharding by user_id hash

### Risks and Mitigations

**Risk 1: Dapr State Query API Not Available**
- Mitigation: Implement task index pattern (Option C) as fallback

**Risk 2: Application-Layer Filtering Performance**
- Mitigation: Implement Redis secondary indexes for frequently filtered fields (priority, tags, completed)

**Risk 3: Task Index Consistency**
- Mitigation: Use Dapr transactions (if supported) or implement eventual consistency with background reconciliation

**Risk 4: Key Injection Attacks**
- Mitigation: Strict input validation on user_id and task_id

**Risk 5: Unauthorized Access via Key Guessing**
- Mitigation: Key prefixing + JWT authentication + audit logging

### Conclusion

The recommended approach for multi-user task isolation in Dapr State Store is:

1. **Key Prefixing**: Use `{user_id}:task:{task_id}` format
2. **Task Index**: Maintain `{user_id}:task-index` for efficient bulk queries
3. **Repository Pattern**: Enforce authorization at repository layer
4. **JWT Authentication**: Derive user_id from authenticated session
5. **Input Validation**: Prevent key injection attacks
6. **Audit Logging**: Log all access for security monitoring

This approach provides:
- **Security**: Defense-in-depth with multiple authorization layers
- **Performance**: O(1) single operations, O(M) bulk queries where M = user's task count
- **Scalability**: Supports 10k+ tasks per user with proper indexing
- **Maintainability**: Clean separation of concerns with repository pattern

### Next Steps

1. Implement `DaprTaskRepository` with key prefixing and task index
2. Create middleware for JWT authentication and user_id extraction
3. Add input validation for user_id and task_id
4. Implement audit logging for all task operations
5. Write integration tests with multiple users to verify isolation
6. Performance test with 10k tasks per user
7. Document security model in API documentation
