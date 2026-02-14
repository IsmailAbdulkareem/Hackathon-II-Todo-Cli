"""
Dapr client wrapper for notification service.

Provides simplified interface for:
- Publishing reminder delivery events
- Service invocation (if needed)
"""

import json
import logging
from typing import Any, Dict, Optional

import httpx

from .config import settings

logger = logging.getLogger(__name__)


class DaprClient:
    """
    Dapr client wrapper for notification service.

    Handles pub/sub operations for reminder delivery events.
    """

    def __init__(self):
        """Initialize Dapr client."""
        self.base_url = settings.dapr_base_url
        self.pubsub_name = settings.DAPR_PUBSUB_NAME
        self.client = httpx.AsyncClient(timeout=30.0)

    async def publish_event(
        self,
        topic_name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Publish an event to a Kafka topic via Dapr Pub/Sub.

        Args:
            topic_name: Name of the topic (e.g., "reminders")
            data: Event data to publish
            metadata: Optional metadata for the event

        Returns:
            True if published successfully, False otherwise
        """
        url = f"{self.base_url}/v1.0/publish/{self.pubsub_name}/{topic_name}"

        try:
            response = await self.client.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            logger.info(f"Published event to {topic_name}: {data.get('event_type', 'unknown')}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to publish event to {topic_name}: {e}")
            return False

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
        from datetime import datetime, timezone
        from uuid import uuid4

        event = {
            "event_id": str(uuid4()),
            "event_type": "reminder.delivered",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "user_id": user_id,
            "reminder_id": reminder_id,
            "task_id": task_id,
            "delivery_status": delivery_status,
            "attempt_number": attempt_number,
            "error_message": error_message
        }

        return await self.publish_event(
            topic_name=settings.KAFKA_TOPIC_REMINDERS,
            data=event
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global Dapr client instance
_dapr_client: Optional[DaprClient] = None


def get_dapr_client() -> DaprClient:
    """
    Get or create the global Dapr client instance.

    Returns:
        DaprClient instance
    """
    global _dapr_client
    if _dapr_client is None:
        _dapr_client = DaprClient()
    return _dapr_client
