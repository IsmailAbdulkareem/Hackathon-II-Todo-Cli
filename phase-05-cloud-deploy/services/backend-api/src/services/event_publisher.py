"""
Event Publisher service for Kafka event publishing.

Publishes domain events to Kafka topics via Dapr Pub/Sub for event-driven architecture.
Events are consumed by Recurring Service and Notification Service.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from src.core.dapr import get_dapr_client

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Event publisher for task-related domain events.

    Publishes events to Kafka topics via Dapr Pub/Sub component.
    Events follow the schema defined in contracts/events.yaml.
    """

    def __init__(self):
        """Initialize event publisher with Dapr client."""
        self.dapr_client = get_dapr_client()
        self.pubsub_name = "kafka-pubsub"

    async def publish_task_created(
        self,
        task_id: str,
        user_id: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """
        Publish TaskCreated event.

        Args:
            task_id: Task identifier
            user_id: User identifier
            task_data: Complete task data

        Returns:
            True if published successfully
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.created",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,
            "task": task_data
        }

        return await self.dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="task-events",
            data=event
        )

    async def publish_task_updated(
        self,
        task_id: str,
        user_id: str,
        changes: Dict[str, Any],
        task_data: Dict[str, Any]
    ) -> bool:
        """
        Publish TaskUpdated event.

        Args:
            task_id: Task identifier
            user_id: User identifier
            changes: Fields that were changed
            task_data: Complete updated task data

        Returns:
            True if published successfully
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.updated",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,
            "task_id": task_id,
            "changes": changes,
            "task": task_data
        }

        return await self.dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="task-events",
            data=event
        )

    async def publish_task_completed(
        self,
        task_id: str,
        user_id: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """
        Publish TaskCompleted event.

        This event triggers the Recurring Service to create the next instance
        if the task is recurring.

        Args:
            task_id: Task identifier
            user_id: User identifier
            task_data: Complete task data including recurrence rule

        Returns:
            True if published successfully
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,
            "task": task_data
        }

        return await self.dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="task-events",
            data=event
        )

    async def publish_task_deleted(
        self,
        task_id: str,
        user_id: str,
        delete_series: bool = False,
        parent_task_id: Optional[str] = None
    ) -> bool:
        """
        Publish TaskDeleted event.

        Args:
            task_id: Task identifier
            user_id: User identifier
            delete_series: Whether to delete entire recurring series
            parent_task_id: Parent task ID if part of recurring series

        Returns:
            True if published successfully
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.deleted",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,
            "task_id": task_id,
            "delete_series": delete_series,
            "parent_task_id": parent_task_id
        }

        return await self.dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="task-events",
            data=event
        )

    async def publish_reminder_scheduled(
        self,
        reminder_id: str,
        user_id: str,
        task_id: str,
        task_title: str,
        scheduled_time: str,
        reminder_type: str,
        user_email: str
    ) -> bool:
        """
        Publish ReminderScheduled event.

        This event is consumed by the Notification Service to send email reminders.

        Args:
            reminder_id: Reminder identifier
            user_id: User identifier
            task_id: Task identifier
            task_title: Task title for notification
            scheduled_time: ISO 8601 scheduled time
            reminder_type: Reminder type (15min, 1hr, 1day, 1week, custom)
            user_email: User email for notification

        Returns:
            True if published successfully
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "reminder.scheduled",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,
            "reminder": {
                "id": reminder_id,
                "task_id": task_id,
                "task_title": task_title,
                "scheduled_time": scheduled_time,
                "reminder_type": reminder_type,
                "user_email": user_email
            }
        }

        return await self.dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="reminders",
            data=event
        )

    async def publish_reminder_delivered(
        self,
        reminder_id: str,
        user_id: str,
        task_id: str,
        delivery_status: str,
        attempt_number: int,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Publish ReminderDelivered event.

        Args:
            reminder_id: Reminder identifier
            user_id: User identifier
            task_id: Task identifier
            delivery_status: Status (sent or failed)
            attempt_number: Retry attempt number (1-3)
            error_message: Error message if failed

        Returns:
            True if published successfully
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "reminder.delivered",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,
            "reminder_id": reminder_id,
            "task_id": task_id,
            "delivery_status": delivery_status,
            "attempt_number": attempt_number,
            "error_message": error_message
        }

        return await self.dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="reminders",
            data=event
        )


# Global event publisher instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """
    Get or create the global event publisher instance.

    Returns:
        EventPublisher instance
    """
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
