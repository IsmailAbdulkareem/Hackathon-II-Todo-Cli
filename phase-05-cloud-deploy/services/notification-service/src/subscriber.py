"""
Dapr subscriber for reminder events.

Subscribes to the 'reminders' Kafka topic via Dapr Pub/Sub and
processes ReminderScheduled events by sending email notifications.
"""

import logging
from typing import Dict, Any

from .config import settings
from .retry_handler import get_retry_handler

logger = logging.getLogger(__name__)


class ReminderSubscriber:
    """
    Dapr subscriber for reminder events.

    Processes ReminderScheduled events from the reminders topic
    and triggers email delivery with retry logic.
    """

    def __init__(self):
        """Initialize reminder subscriber."""
        self.retry_handler = get_retry_handler()

    async def handle_reminder_scheduled(self, event: Dict[str, Any]) -> bool:
        """
        Handle ReminderScheduled event.

        Args:
            event: Event data containing reminder details

        Returns:
            True if handled successfully, False otherwise
        """
        try:
            # Extract event data
            event_type = event.get("event_type")
            if event_type != "reminder.scheduled":
                logger.warning(f"Unexpected event type: {event_type}")
                return False

            # Extract reminder data
            reminder_data = event.get("reminder", {})
            reminder_id = reminder_data.get("id")
            task_id = reminder_data.get("task_id")
            task_title = reminder_data.get("task_title")
            scheduled_time = reminder_data.get("scheduled_time")
            reminder_type = reminder_data.get("reminder_type")
            user_email = reminder_data.get("user_email")
            user_id = event.get("user_id")

            # Validate required fields
            if not all([reminder_id, task_id, task_title, scheduled_time,
                       reminder_type, user_email, user_id]):
                logger.error(f"Missing required fields in reminder event: {event}")
                return False

            logger.info(
                f"Processing ReminderScheduled event: "
                f"reminder_id={reminder_id}, task_id={task_id}, "
                f"user_email={user_email}, scheduled_time={scheduled_time}"
            )

            # Send email with retry logic
            success = await self.retry_handler.send_with_retry(
                reminder_id=reminder_id,
                user_id=user_id,
                task_id=task_id,
                task_title=task_title,
                user_email=user_email,
                scheduled_time=scheduled_time,
                reminder_type=reminder_type
            )

            if success:
                logger.info(f"Successfully processed reminder {reminder_id}")
            else:
                logger.error(f"Failed to process reminder {reminder_id} after all retries")

            return success

        except Exception as e:
            logger.error(f"Error handling ReminderScheduled event: {e}", exc_info=True)
            return False

    def get_subscription_config(self) -> list[Dict[str, str]]:
        """
        Get Dapr subscription configuration.

        Returns:
            List of subscription configurations for Dapr
        """
        return [
            {
                "pubsubname": settings.DAPR_PUBSUB_NAME,
                "topic": settings.KAFKA_TOPIC_REMINDERS,
                "route": "/reminders"
            }
        ]


# Global subscriber instance
_subscriber: ReminderSubscriber | None = None


def get_subscriber() -> ReminderSubscriber:
    """
    Get or create the global subscriber instance.

    Returns:
        ReminderSubscriber instance
    """
    global _subscriber
    if _subscriber is None:
        _subscriber = ReminderSubscriber()
    return _subscriber
