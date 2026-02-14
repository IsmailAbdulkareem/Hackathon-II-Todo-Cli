"""
Dapr subscriber for task events.

Listens to TaskCompleted events and creates next recurring task instances.
"""

import logging
from typing import Dict, Any

from src.config import settings
from src.dapr_client import get_dapr_client
from src.recurrence_engine import get_recurrence_engine

logger = logging.getLogger(__name__)


class TaskEventSubscriber:
    """
    Subscriber for task events from Kafka via Dapr Pub/Sub.

    Processes TaskCompleted events to create recurring task instances.
    """

    def __init__(self):
        """Initialize subscriber with Dapr client and recurrence engine."""
        self.dapr_client = get_dapr_client()
        self.recurrence_engine = get_recurrence_engine()

    def get_subscription_config(self) -> list:
        """
        Get Dapr subscription configuration.

        Returns:
            List of subscription configurations
        """
        return [
            {
                "pubsubname": settings.PUBSUB_NAME,
                "topic": settings.TASK_EVENTS_TOPIC,
                "route": "/task-events"
            }
        ]

    async def handle_task_completed(self, event_data: Dict[str, Any]) -> bool:
        """
        Handle TaskCompleted event.

        Creates the next recurring task instance if applicable.

        Args:
            event_data: Event data from Kafka

        Returns:
            True if processed successfully, False otherwise
        """
        try:
            event_type = event_data.get("event_type")

            # Only process TaskCompleted events
            if event_type != "task.completed":
                logger.debug(f"Ignoring event type: {event_type}")
                return True

            task_data = event_data.get("task", {})
            user_id = event_data.get("user_id")

            if not task_data or not user_id:
                logger.error("Missing task data or user_id in event")
                return False

            # Check if task is recurring
            is_recurring = task_data.get("is_recurring", False)
            if not is_recurring:
                logger.debug(f"Task {task_data.get('id')} is not recurring, skipping")
                return True

            # Get recurrence rule
            recurrence_rule_id = task_data.get("recurrence_rule_id")
            if not recurrence_rule_id:
                logger.warning(
                    f"Recurring task {task_data.get('id')} has no recurrence_rule_id"
                )
                return False

            # Fetch recurrence rule from backend API
            recurrence_rule = await self._get_recurrence_rule(user_id, recurrence_rule_id)
            if not recurrence_rule:
                logger.error(
                    f"Failed to fetch recurrence rule {recurrence_rule_id} for user {user_id}"
                )
                return False

            # Calculate next occurrence
            next_task_data = self.recurrence_engine.calculate_next_occurrence(
                completed_task=task_data,
                recurrence_rule=recurrence_rule
            )

            if not next_task_data:
                logger.info(
                    f"No next occurrence for task {task_data.get('id')} - series complete"
                )
                return True

            # Create next task instance via backend API
            created_task = await self.dapr_client.create_recurring_task_instance(
                user_id=user_id,
                task_data=next_task_data
            )

            if created_task:
                logger.info(
                    f"Successfully created next recurring task instance: {created_task.get('id')}"
                )

                # Update recurrence rule occurrence count
                await self._update_recurrence_rule_count(
                    user_id=user_id,
                    recurrence_rule_id=recurrence_rule_id,
                    current_count=recurrence_rule.get("current_count", 0) + 1
                )

                return True
            else:
                logger.error(
                    f"Failed to create next recurring task instance for user {user_id}"
                )
                return False

        except Exception as e:
            logger.error(f"Error handling TaskCompleted event: {str(e)}", exc_info=True)
            return False

    async def _get_recurrence_rule(
        self,
        user_id: str,
        recurrence_rule_id: str
    ) -> Dict[str, Any] | None:
        """
        Fetch recurrence rule from backend API.

        Args:
            user_id: User identifier
            recurrence_rule_id: Recurrence rule identifier

        Returns:
            Recurrence rule data, or None if not found
        """
        endpoint = f"/api/{user_id}/recurrence-rules/{recurrence_rule_id}"

        try:
            result = await self.dapr_client.invoke_backend_api("GET", endpoint)
            return result
        except Exception as e:
            logger.error(
                f"Error fetching recurrence rule {recurrence_rule_id}: {str(e)}"
            )
            return None

    async def _update_recurrence_rule_count(
        self,
        user_id: str,
        recurrence_rule_id: str,
        current_count: int
    ) -> bool:
        """
        Update recurrence rule occurrence count.

        Args:
            user_id: User identifier
            recurrence_rule_id: Recurrence rule identifier
            current_count: New occurrence count

        Returns:
            True if updated successfully, False otherwise
        """
        endpoint = f"/api/{user_id}/recurrence-rules/{recurrence_rule_id}"
        data = {"current_count": current_count}

        try:
            result = await self.dapr_client.invoke_backend_api("PUT", endpoint, data)
            return result is not None
        except Exception as e:
            logger.error(
                f"Error updating recurrence rule count: {str(e)}"
            )
            return False


# Global subscriber instance
_subscriber: TaskEventSubscriber | None = None


def get_subscriber() -> TaskEventSubscriber:
    """
    Get or create the global subscriber instance.

    Returns:
        TaskEventSubscriber instance
    """
    global _subscriber
    if _subscriber is None:
        _subscriber = TaskEventSubscriber()
    return _subscriber
