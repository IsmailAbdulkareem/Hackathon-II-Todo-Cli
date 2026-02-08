"""
Event Publisher Interface and Implementation

This module defines the interface for publishing events and provides
an implementation using Dapr's pub/sub API.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import httpx
from datetime import datetime, timezone
import uuid


class EventPublisher(ABC):
    """
    Abstract interface for publishing events to pub/sub systems.
    """

    @abstractmethod
    async def publish(
        self,
        topic: str,
        event_type: str,
        task_id: str,
        payload: Dict[str, Any]
    ) -> None:
        """
        Publish an event to the specified topic.

        Args:
            topic: Event topic name
            event_type: Type of event (TASK_CREATED, TASK_UPDATED, etc.)
            task_id: Associated task ID
            payload: Event-specific data
        """
        pass


class DaprEventPublisher(EventPublisher):
    """
    Dapr-based implementation of EventPublisher.
    """

    def __init__(self, dapr_http_port: int = 3500, pubsub_name: str = "redis-pubsub"):
        self.dapr_http_port = dapr_http_port
        self.pubsub_name = pubsub_name

    async def publish(
        self,
        topic: str,
        event_type: str,
        task_id: str,
        payload: Dict[str, Any]
    ) -> None:
        """
        Publish event to Dapr Pub/Sub.

        Args:
            topic: Event topic (task-events, task-reminders, etc.)
            event_type: Event type (TASK_CREATED, TASK_UPDATED, etc.)
            task_id: Task identifier
            payload: Event-specific data
        """
        # Dapr Pub/Sub API: POST /v1.0/publish/{pubsub}/{topic}
        url = f"http://localhost:{self.dapr_http_port}/v1.0/publish/{self.pubsub_name}/{topic}"

        event = {
            "id": str(uuid.uuid4()),
            "task_id": task_id,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=event)
            response.raise_for_status()


class MockEventPublisher(EventPublisher):
    """
    Mock implementation for testing when Dapr is not available.
    """

    def __init__(self):
        self.published_events = []

    async def publish(
        self,
        topic: str,
        event_type: str,
        task_id: str,
        payload: Dict[str, Any]
    ) -> None:
        """
        Store the event in memory for testing purposes.
        """
        event = {
            "id": str(uuid.uuid4()),
            "topic": topic,
            "task_id": task_id,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload
        }
        self.published_events.append(event)


# Global instance (can be swapped for testing)
event_publisher = DaprEventPublisher()