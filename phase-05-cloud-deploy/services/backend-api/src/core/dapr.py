"""
Dapr client wrapper for pub/sub and service invocation.

Provides simplified interface for Dapr operations including:
- Publishing events to Kafka topics via Dapr Pub/Sub
- Invoking other services via Dapr Service Invocation
- State management operations
- Jobs API for scheduled tasks
"""

import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DaprClient:
    """
    Dapr client wrapper for microservices communication.

    Provides methods for pub/sub, service invocation, state management,
    and jobs scheduling via Dapr HTTP API.
    """

    def __init__(self, dapr_http_port: int = 3500, dapr_grpc_port: int = 50001):
        """
        Initialize Dapr client.

        Args:
            dapr_http_port: Dapr HTTP port (default: 3500)
            dapr_grpc_port: Dapr gRPC port (default: 50001)
        """
        self.dapr_http_port = dapr_http_port
        self.dapr_grpc_port = dapr_grpc_port
        self.base_url = f"http://localhost:{dapr_http_port}"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def publish_event(
        self,
        pubsub_name: str,
        topic_name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Publish an event to a Kafka topic via Dapr Pub/Sub.

        Args:
            pubsub_name: Name of the pub/sub component (e.g., "kafka-pubsub")
            topic_name: Name of the topic (e.g., "task-events")
            data: Event data to publish
            metadata: Optional metadata for the event

        Returns:
            True if published successfully, False otherwise
        """
        url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic_name}"

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

    async def invoke_service(
        self,
        app_id: str,
        method_name: str,
        data: Optional[Dict[str, Any]] = None,
        http_verb: str = "POST"
    ) -> Optional[Dict[str, Any]]:
        """
        Invoke another service via Dapr Service Invocation.

        Args:
            app_id: Target service app ID (e.g., "recurring-service")
            method_name: Method/endpoint to invoke (e.g., "create-task")
            data: Optional data to send
            http_verb: HTTP verb (GET, POST, PUT, DELETE)

        Returns:
            Response data if successful, None otherwise
        """
        url = f"{self.base_url}/v1.0/invoke/{app_id}/method/{method_name}"

        try:
            if http_verb.upper() == "GET":
                response = await self.client.get(url)
            elif http_verb.upper() == "POST":
                response = await self.client.post(url, json=data)
            elif http_verb.upper() == "PUT":
                response = await self.client.put(url, json=data)
            elif http_verb.upper() == "DELETE":
                response = await self.client.delete(url)
            else:
                logger.error(f"Unsupported HTTP verb: {http_verb}")
                return None

            response.raise_for_status()
            return response.json() if response.content else None
        except httpx.HTTPError as e:
            logger.error(f"Failed to invoke {app_id}/{method_name}: {e}")
            return None

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Save state to Dapr state store.

        Args:
            store_name: Name of the state store component
            key: State key
            value: State value (will be JSON serialized)
            metadata: Optional metadata

        Returns:
            True if saved successfully, False otherwise
        """
        url = f"{self.base_url}/v1.0/state/{store_name}"

        state_data = [{
            "key": key,
            "value": value,
            "metadata": metadata or {}
        }]

        try:
            response = await self.client.post(url, json=state_data)
            response.raise_for_status()
            logger.info(f"Saved state: {key}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to save state {key}: {e}")
            return False

    async def get_state(
        self,
        store_name: str,
        key: str
    ) -> Optional[Any]:
        """
        Get state from Dapr state store.

        Args:
            store_name: Name of the state store component
            key: State key

        Returns:
            State value if found, None otherwise
        """
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json() if response.content else None
        except httpx.HTTPError as e:
            logger.error(f"Failed to get state {key}: {e}")
            return None

    async def schedule_job(
        self,
        job_name: str,
        schedule: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Schedule a job via Dapr Jobs API.

        Args:
            job_name: Unique job name
            schedule: Cron schedule or ISO 8601 datetime
            data: Job data payload
            metadata: Optional metadata

        Returns:
            Job ID if scheduled successfully, None otherwise
        """
        url = f"{self.base_url}/v1.0-alpha1/jobs/{job_name}"

        job_data = {
            "schedule": schedule,
            "data": data,
            "metadata": metadata or {}
        }

        try:
            response = await self.client.post(url, json=job_data)
            response.raise_for_status()
            logger.info(f"Scheduled job: {job_name}")
            return job_name
        except httpx.HTTPError as e:
            logger.error(f"Failed to schedule job {job_name}: {e}")
            return None

    async def delete_job(self, job_name: str) -> bool:
        """
        Delete a scheduled job.

        Args:
            job_name: Job name to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        url = f"{self.base_url}/v1.0-alpha1/jobs/{job_name}"

        try:
            response = await self.client.delete(url)
            response.raise_for_status()
            logger.info(f"Deleted job: {job_name}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to delete job {job_name}: {e}")
            return False

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
