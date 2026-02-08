"""
Dapr State Store Adapter (T094)

This module provides an adapter for Dapr State Store API,
abstracting state management operations.
"""

import httpx
from typing import Dict, Any, Optional, List
import json


class DaprStateStoreAdapter:
    """
    Adapter for Dapr State Store API.

    Provides methods for saving, retrieving, and deleting state
    using Dapr's state management building block.
    """

    def __init__(
        self,
        dapr_http_port: int = 3500,
        store_name: str = "statestore"
    ):
        """
        Initialize Dapr State Store adapter.

        Args:
            dapr_http_port: Dapr sidecar HTTP port
            store_name: Name of the state store component
        """
        self.dapr_http_port = dapr_http_port
        self.store_name = store_name
        self.base_url = f"http://localhost:{dapr_http_port}/v1.0/state/{store_name}"

    async def save(
        self,
        key: str,
        value: Dict[str, Any],
        etag: Optional[str] = None
    ) -> None:
        """
        Save state to Dapr state store.

        Args:
            key: State key
            value: State value (will be JSON serialized)
            etag: Optional ETag for optimistic concurrency

        Raises:
            httpx.HTTPError: If save operation fails
        """
        payload = [
            {
                "key": key,
                "value": value
            }
        ]

        if etag:
            payload[0]["etag"] = etag

        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, json=payload)
            response.raise_for_status()

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get state from Dapr state store.

        Args:
            key: State key

        Returns:
            State value if found, None otherwise

        Raises:
            httpx.HTTPError: If get operation fails
        """
        url = f"{self.base_url}/{key}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            if response.status_code == 204:
                # No content - key doesn't exist
                return None

            response.raise_for_status()
            return response.json()

    async def delete(self, key: str) -> None:
        """
        Delete state from Dapr state store.

        Args:
            key: State key

        Raises:
            httpx.HTTPError: If delete operation fails
        """
        url = f"{self.base_url}/{key}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
            response.raise_for_status()

    async def bulk_get(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple states in a single operation.

        Args:
            keys: List of state keys

        Returns:
            Dictionary mapping keys to values

        Raises:
            httpx.HTTPError: If bulk get operation fails
        """
        url = f"{self.base_url}/bulk"
        payload = {"keys": keys}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            results = {}
            for item in response.json():
                results[item["key"]] = item.get("data")

            return results

    async def query(
        self,
        filter_query: Dict[str, Any],
        sort: Optional[List[Dict[str, str]]] = None,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query state store with filters.

        Args:
            filter_query: Query filter in Dapr query format
            sort: Optional sort specifications
            page_size: Maximum number of results

        Returns:
            List of matching state entries

        Raises:
            httpx.HTTPError: If query operation fails
        """
        url = f"{self.base_url}/query"
        payload = {
            "filter": filter_query,
            "page": {"limit": page_size}
        }

        if sort:
            payload["sort"] = sort

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            return response.json().get("results", [])
