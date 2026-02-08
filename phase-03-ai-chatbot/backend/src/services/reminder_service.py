"""
Reminder Service

This module implements the service for handling task reminders.
"""

from datetime import datetime, timedelta
from typing import Optional
import asyncio
import httpx
import uuid

from src.models.task import Task


class ReminderService:
    """
    Service for managing task reminders.

    Implements the logic for scheduling and triggering reminders
    based on task due dates and configured offsets.
    """

    def __init__(self, dapr_http_port: int = 3500):
        self.dapr_http_port = dapr_http_port

    async def schedule_reminder(
        self,
        task_id: str,
        user_id: str,
        reminder_time: datetime,
        dapr_http_port: int = 3500
    ) -> str:
        """
        Schedule a reminder job using Dapr Jobs API.

        Args:
            task_id: Task identifier
            user_id: User identifier (for callback context)
            reminder_time: When to trigger the reminder (UTC)
            dapr_http_port: Dapr sidecar HTTP port

        Returns:
            Job ID for tracking and cancellation
        """
        job_name = f"reminder-{task_id}"

        # Dapr Jobs API: POST /v1.0-alpha1/jobs/{job-name}
        url = f"http://localhost:{dapr_http_port}/v1.0-alpha1/jobs/{job_name}"

        payload = {
            "schedule": reminder_time.isoformat(),  # One-time job at specific time
            "repeats": 1,  # Execute once
            "dueTime": reminder_time.isoformat(),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "reminder_type": "due_date"
            },
            "callback": {
                "method": "POST",
                "endpoint": f"http://localhost:8000/api/internal/reminders/trigger"
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            return result.get("jobId", job_name)

    async def cancel_reminder(
        self,
        task_id: str,
        dapr_http_port: int = 3500
    ) -> None:
        """
        Cancel a scheduled reminder using Dapr Jobs API.

        Args:
            task_id: Task identifier
            dapr_http_port: Dapr sidecar HTTP port
        """
        job_name = f"reminder-{task_id}"

        # Dapr Jobs API: DELETE /v1.0-alpha1/jobs/{job-name}
        url = f"http://localhost:{dapr_http_port}/v1.0-alpha1/jobs/{job_name}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
            response.raise_for_status()

    def calculate_reminder_time(
        self,
        due_date: datetime,
        reminder_offset_minutes: int
    ) -> datetime:
        """
        Calculate the reminder time based on due date and offset.

        Args:
            due_date: Task due date
            reminder_offset_minutes: Minutes before due date to trigger reminder

        Returns:
            Datetime for the reminder
        """
        return due_date - timedelta(minutes=reminder_offset_minutes)

    async def is_reminder_needed(
        self,
        task: Task
    ) -> bool:
        """
        Determine if a reminder is needed for the task.

        Args:
            task: Task to check

        Returns:
            True if reminder is needed and configured
        """
        if task.reminder_offset_minutes is None or task.reminder_offset_minutes <= 0:
            return False

        if task.due_date is None:
            return False

        return True

    async def validate_reminder_configuration(
        self,
        due_date: Optional[datetime],
        reminder_offset_minutes: Optional[int]
    ) -> bool:
        """
        Validate that the reminder configuration is valid.

        Args:
            due_date: Task due date
            reminder_offset_minutes: Minutes before due date to send reminder

        Returns:
            True if configuration is valid
        """
        if reminder_offset_minutes is None or reminder_offset_minutes <= 0:
            return True  # No reminder configured

        if due_date is None:
            return False  # Cannot set reminder without due date

        # Check that reminder time is not after due date
        reminder_time = self.calculate_reminder_time(due_date, reminder_offset_minutes)
        if reminder_time > due_date:
            return False  # Reminder time is after due date

        # Check that reminder time is not in the past (for new tasks)
        if reminder_time < datetime.now(datetime.timezone.utc):
            return False  # Reminder time is in the past

        return True


# Global instance
reminder_service = ReminderService()