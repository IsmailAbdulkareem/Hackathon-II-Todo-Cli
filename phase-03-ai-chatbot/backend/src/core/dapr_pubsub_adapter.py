"""
Dapr Pub/Sub Adapter (T095)

This module provides an adapter for Dapr Pub/Sub API,
abstracting publish/subscribe operations.
"""

import httpx
from typing import Dict, Any


class DaprPubSubAdapter:
    """
    Adapter for Dapr Pub/Sub API.

    Provides methods for publishing messages to topics
    using Dapr's pub/sub building block.
    """

    def __init__(
        self,
        dapr_http_port: int = 3500,
        pubsub_name: str = "redis-pubsub"
    ):
        """
        Initialize Dapr Pub/Sub adapter.

        Args:
            dapr_http_port: Dapr sidecar HTTP port
            pubsub_name: Name of the pub/sub component
        """
        self.dapr_http_port = dapr_http_port
        self.pubsub_name = pubsub_name
        self.base_url = f"http://localhost:{dapr_http_port}/v1.0/publish/{pubsub_name}"

    async def publish(
        self,
        topic: str,
        data: Dict[str, Any],
        metadata: Dict[str, str] = None
    ) -> None:
        """
        Publish a message to a topic.

        Args:
            topic: Topic name
            data: Message data (will be JSON serialized)
            metadata: Optional metadata for the message

        Raises:
            httpx.HTTPError: If publish operation fails
        """
        url = f"{self.base_url}/{topic}"

        headers = {}
        if metadata:
            for key, value in metadata.items():
                headers[f"metadata.{key}"] = value

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=data,
                headers=headers
            )
            response.raise_for_status()

    async def bulk_publish(
        self,
        topic: str,
        messages: list[Dict[str, Any]]
    ) -> None:
        """
        Publish multiple messages to a topic in a single operation.

        Args:
            topic: Topic name
            messages: List of message data dictionaries

        Raises:
            httpx.HTTPError: If bulk publish operation fails
        """
        url = f"{self.base_url}/{topic}/bulk"

        # Format messages for bulk publish
        entries = [
            {
                "entryId": str(i),
                "event": message
            }
            for i, message in enumerate(messages)
        ]

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=entries)
            response.raise_for_status()
