"""
Dapr client for service invocation and pub/sub operations.

Provides methods to:
- Invoke backend API to create recurring task instances
- Publish events for audit logging
"""

import logging
from typing import Dict, Any, Optional

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class DaprClient:
    """
    Dapr client for recurring service operations.

    Handles service invocation to backend API and event publishing.
    """

    def __init__(self):
        """Initialize Dapr client with HTTP endpoint."""
        self.dapr_url = f"http://localhost:{settings.DAPR_HTTP_PORT}"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def invoke_backend_api(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Invoke backend API via Dapr service invocation.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data

        Returns:
            Response data if successful, None otherwise
        """
        url = f"{self.dapr_url}/v1.0/invoke/{settings.BACKEND_API_APP_ID}/method{endpoint}"

        try:
            if method.upper() == "POST":
                response = await self.client.post(url, json=data)
            elif method.upper() == "GET":
                response = await self.client.get(url)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error invoking backend API: {e.response.status_code} - {e.response.text}"
            )
            return None
        except Exception as e:
            logger.error(f"Error invoking backend API: {str(e)}")
            return None

    async def create_recurring_task_instance(
        self,
        user_id: str,
        task_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new recurring task instance via backend API.

        Args:
            user_id: User identifier
            task_data: Task creation data

        Returns:
            Created task data if successful, None otherwise
        """
        endpoint = f"/api/{user_id}/tasks"

        logger.info(
            f"Creating recurring task instance for user {user_id}: {task_data.get('title')}"
        )

        result = await self.invoke_backend_api("POST", endpoint, task_data)

        if result:
            logger.info(f"Successfully created recurring task instance: {result.get('id')}")
        else:
            logger.error(f"Failed to create recurring task instance for user {user_id}")

        return result

    async def publish_event(
        self,
        pubsub_name: str,
        topic_name: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Publish an event to a Dapr pub/sub topic.

        Args:
            pubsub_name: Pub/sub component name
            topic_name: Topic name
            data: Event data

        Returns:
            True if published successfully, False otherwise
        """
        url = f"{self.dapr_url}/v1.0/publish/{pubsub_name}/{topic_name}"

        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            logger.info(f"Published event to {topic_name}")
            return True

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error publishing event: {e.response.status_code} - {e.response.text}"
            )
            return False
        except Exception as e:
            logger.error(f"Error publishing event: {str(e)}")
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
