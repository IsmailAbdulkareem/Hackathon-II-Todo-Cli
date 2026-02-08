"""
Dapr Jobs Adapter (T096)

This module provides an adapter for Dapr Jobs API,
abstracting job scheduling operations.
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime


class DaprJobsAdapter:
    """
    Adapter for Dapr Jobs API.

    Provides methods for scheduling, retrieving, and deleting jobs
    using Dapr's jobs building block.
    """

    def __init__(self, dapr_http_port: int = 3500):
        """
        Initialize Dapr Jobs adapter.

        Args:
            dapr_http_port: Dapr sidecar HTTP port
        """
        self.dapr_http_port = dapr_http_port
        self.base_url = f"http://localhost:{dapr_http_port}/v1.0-alpha1/jobs"

    async def schedule(
        self,
        job_name: str,
        schedule: str,
        data: Dict[str, Any],
        due_time: Optional[str] = None,
        ttl: Optional[str] = None
    ) -> None:
        """
        Schedule a job.

        Args:
            job_name: Unique job identifier
            schedule: Cron expression or ISO 8601 duration
            data: Job payload data
            due_time: Optional ISO 8601 timestamp for first execution
            ttl: Optional time-to-live for the job

        Raises:
            httpx.HTTPError: If schedule operation fails
        """
        url = f"{self.base_url}/{job_name}"

        payload = {
            "schedule": schedule,
            "data": data
        }

        if due_time:
            payload["dueTime"] = due_time

        if ttl:
            payload["ttl"] = ttl

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

    async def get(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Get job details.

        Args:
            job_name: Job identifier

        Returns:
            Job details if found, None otherwise

        Raises:
            httpx.HTTPError: If get operation fails
        """
        url = f"{self.base_url}/{job_name}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

    async def delete(self, job_name: str) -> None:
        """
        Delete a scheduled job.

        Args:
            job_name: Job identifier

        Raises:
            httpx.HTTPError: If delete operation fails
        """
        url = f"{self.base_url}/{job_name}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
            response.raise_for_status()

    async def list_jobs(self) -> list[Dict[str, Any]]:
        """
        List all scheduled jobs.

        Returns:
            List of job details

        Raises:
            httpx.HTTPError: If list operation fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url)
            response.raise_for_status()
            return response.json().get("jobs", [])
