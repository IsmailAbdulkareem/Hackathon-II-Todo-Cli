# Event Schema Generator

**Critical for Phase:** V

Generates Pydantic schemas and event definitions for Kafka event-driven architecture.

## Usage

```
/gen.event-schema "<event-type> "<fields>"

# Examples:
/gen.event-schema "TodoCreated" "id (UUID), title (str), description (str?), user_id (UUID), created_at (datetime)"
/gen.event-schema "TodoCompleted" "id (UUID), completed_by (UUID), completed_at (datetime)"
/gen.event-schema "TodoUpdated" "id (UUID), title (str?), description (str?), updated_at (datetime)"
/gen.event-schema "ReminderTriggered" "todo_id (UUID), reminder_type (str), triggered_at (datetime)"
```

## What It Generates

- Pydantic event models with validation
- Event base classes (BaseEvent, DomainEvent)
- JSON serialization/deserialization
- Event versioning support
- Kafka producer code
- Kafka consumer code
- Event type registry
- Serialization tests

## Output Structure

```
phase-XX/src/events/
  ├── base.py                 # Event base classes
  ├── todo_events.py          # Todo domain events
  ├── reminder_events.py       # Reminder events
  ├── analytics_events.py      # Analytics events
  ├── producer.py             # Kafka producer
  ├── consumer.py             # Kafka consumer
  └── serializers.py         # JSON serializers
```

## Features

- Type-safe event definitions
- Event versioning (v1, v2)
- Automatic JSON serialization
- Validation with Pydantic
- Event ID and timestamp
- Correlation ID for tracing
- Event type constants
- Backward compatibility

## Phase Usage

- **Phase V:** Todo domain events (created, updated, completed, deleted)
- **Phase V:** Reminder events (triggered, snoozed, dismissed)
- **Phase V:** Analytics events (user_activity, task_completion_rate)
- **Phase V:** Audit events (login, logout, permissions)

## Event Types

```
# Domain Events (todos topic)
TodoCreated
TodoUpdated
TodoCompleted
TodoUncompleted
TodoDeleted
TodoPrioritized

# Reminder Events (reminders topic)
ReminderCreated
ReminderTriggered
ReminderSnoozed
ReminderDismissed
ReminderCancelled

# Analytics Events (analytics topic)
UserLogin
UserLogout
TaskCreated
TaskCompleted
TaskOverdue
ProductivityMetric

# Notification Events (notifications topic)
EmailNotificationSent
PushNotificationSent
InAppNotificationCreated
```

## Example Outputs

### base.py
```python
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
import json

class BaseEvent(BaseModel):
    """Base class for all events."""

    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    event_type: str = Field(..., description="Type of the event")
    event_version: str = Field(default="1.0", description="Event schema version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    correlation_id: Optional[UUID] = Field(None, description="Correlation ID for tracing")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump(mode='json')

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> 'BaseEvent':
        """Create event from JSON string."""
        data = json.loads(json_str)
        return cls(**data)
```

### todo_events.py
```python
from .base import BaseEvent
from typing import Optional
from uuid import UUID

class TodoCreated(BaseEvent):
    """Event emitted when a new todo is created."""

    event_type: str = Field(default="TodoCreated", const=True)

    todo_id: UUID = Field(..., description="ID of the created todo")
    user_id: UUID = Field(..., description="ID of the user who created the todo")
    title: str = Field(..., max_length=500, description="Todo title")
    description: Optional[str] = Field(None, max_length=2000, description="Optional description")
    priority: str = Field(default="medium", description="Priority level")
    due_date: Optional[datetime] = Field(None, description="Optional due date")

class TodoUpdated(BaseEvent):
    """Event emitted when a todo is updated."""

    event_type: str = Field(default="TodoUpdated", const=True)

    todo_id: UUID = Field(..., description="ID of the updated todo")
    user_id: UUID = Field(..., description="ID of the user who updated the todo")
    changes: Dict[str, Any] = Field(..., description="Fields that were changed")
    updated_fields: list[str] = Field(..., description="List of updated field names")

class TodoCompleted(BaseEvent):
    """Event emitted when a todo is marked complete."""

    event_type: str = Field(default="TodoCompleted", const=True)

    todo_id: UUID = Field(..., description="ID of the completed todo")
    user_id: UUID = Field(..., description="ID of the user who completed the todo")
    completed_at: datetime = Field(..., description="When the todo was completed")
    time_to_complete: Optional[int] = Field(
        None,
        description="Seconds between creation and completion",
        ge=0
    )

class TodoDeleted(BaseEvent):
    """Event emitted when a todo is deleted."""

    event_type: str = Field(default="TodoDeleted", const=True)

    todo_id: UUID = Field(..., description="ID of the deleted todo")
    user_id: UUID = Field(..., description="ID of the user who deleted the todo")
    deleted_at: datetime = Field(..., description="When the todo was deleted")
    reason: Optional[str] = Field(None, description="Reason for deletion")
```

### reminder_events.py
```python
from .base import BaseEvent
from uuid import UUID

class ReminderTriggered(BaseEvent):
    """Event emitted when a reminder is triggered."""

    event_type: str = Field(default="ReminderTriggered", const=True)

    reminder_id: UUID = Field(..., description="ID of the reminder")
    todo_id: UUID = Field(..., description="ID of the associated todo")
    user_id: UUID = Field(..., description="ID of the user")
    reminder_type: str = Field(..., description="Type of reminder (email, push, in-app)")
    triggered_at: datetime = Field(..., description="When the reminder was triggered")
    due_date: datetime = Field(..., description="Original due date")

class ReminderSnoozed(BaseEvent):
    """Event emitted when a reminder is snoozed."""

    event_type: str = Field(default="ReminderSnoozed", const=True)

    reminder_id: UUID = Field(..., description="ID of the reminder")
    todo_id: UUID = Field(..., description="ID of the associated todo")
    user_id: UUID = Field(..., description="ID of the user")
    new_due_date: datetime = Field(..., description="New due date after snooze")
    snooze_duration: int = Field(..., description="Duration of snooze in minutes")
```

### producer.py
```python
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
import json
import logging
from typing import Union

logger = logging.getLogger(__name__)

class EventProducer:
    """Kafka event producer for publishing domain events."""

    def __init__(self, bootstrap_servers: str):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8') if k else None
        )

    async def publish(
        self,
        event: BaseEvent,
        topic: str,
        key: Optional[str] = None
    ) -> bool:
        """Publish event to Kafka topic."""
        try:
            await self.producer.send_and_wait(
                topic=topic,
                value=event.to_dict(),
                key=key or str(event.event_id)
            )
            logger.info(
                f"Published event {event.event_type} "
                f"(ID: {event.event_id}) to topic {topic}"
            )
            return True

        except KafkaError as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    async def publish_batch(
        self,
        events: list[tuple[BaseEvent, str, Optional[str]]]
    ) -> int:
        """Publish multiple events in a batch."""
        successful = 0
        for event, topic, key in events:
            if await self.publish(event, topic, key):
                successful += 1
        return successful

    async def close(self):
        """Close the producer."""
        await self.producer.stop()
        logger.info("Kafka producer closed")
```

### consumer.py
```python
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
import json
import logging
from typing import Callable, TypeVar

T = TypeVar('T', bound=BaseEvent)
logger = logging.getLogger(__name__)

class EventConsumer:
    """Kafka event consumer for processing domain events."""

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str]
    ):
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.handlers: dict[str, Callable] = {}

    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for a specific event type."""
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")

    async def start(self):
        """Start consuming events."""
        await self.consumer.start()
        logger.info(f"Consumer started, listening on topics: {self.consumer.subscription()}")

        async for msg in self.consumer:
            try:
                event_data = msg.value
                event_type = event_data.get('event_type')

                if event_type in self.handlers:
                    await self.handlers[event_type](event_data, msg)
                else:
                    logger.warning(f"No handler for event type: {event_type}")

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)

    async def stop(self):
        """Stop the consumer."""
        await self.consumer.stop()
        logger.info("Kafka consumer stopped")
```

## Event Flow

```
┌─────────────┐
│   Service   │
└──────┬──────┘
       │
       │ 1. Domain Event Created
       │
       ▼
┌─────────────────┐
│  Event Producer │  Publishes to Kafka
└───────┬───────┘
        │
        │ 2. Event Published
        │
        ▼
┌─────────────────┐
│   Kafka Topic   │  (todos, reminders, analytics)
└───────┬───────┘
        │
        │ 3. Event Delivered
        │
        ▼
┌─────────────────┐
│ Event Consumer │  Subscribed to topic
└───────┬───────┘
        │
        │ 4. Event Processed
        │
        ▼
┌─────────────┐
│  Handlers   │  Update DB, Send notifications, etc.
└─────────────┘
```

## Kafka Topic Configuration

```yaml
# Topic configuration (managed by Kafka operator)
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-events
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days
    segment.ms: 86400000       # 1 day
    cleanup.policy: delete
```

## Best Practices

- **Immutable Events**: Once created, events never change
- **Versioning**: Include event_version for schema evolution
- **Idempotency**: Use event_id to deduplicate
- **Tracing**: Include correlation_id for distributed tracing
- **Timestamps**: Always include UTC timestamp
- **Validation**: Validate events before publishing
- **Dead Letter Queue**: Route unprocessable events to DLT
- **Ordering**: Use partition keys for ordering per entity
- **Retention**: Set appropriate retention period
- **Backward Compatibility**: New fields optional, don't remove old fields

## Event Versioning

```python
# v1.0
class TodoCreated(BaseEvent):
    event_version: str = "1.0"
    title: str

# v2.0 (backward compatible)
class TodoCreated(BaseEvent):
    event_version: str = "2.0"
    title: str
    tags: Optional[list[str]] = None  # New optional field
```

## Testing Events

```python
import pytest
from events.todo_events import TodoCreated

def test_todo_created_event():
    """Test TodoCreated event serialization."""
    event = TodoCreated(
        todo_id=uuid4(),
        user_id=uuid4(),
        title="Test todo",
        description="Test description"
    )

    # Test serialization
    event_dict = event.to_dict()
    assert "event_id" in event_dict
    assert event_dict["event_type"] == "TodoCreated"

    # Test JSON
    json_str = event.to_json()
    reconstructed = TodoCreated.from_json(json_str)

    # Test deserialization
    assert reconstructed.todo_id == event.todo_id
    assert reconstructed.title == event.title
```
