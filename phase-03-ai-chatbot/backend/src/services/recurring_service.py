"""
Recurring Task Service

This module implements the service for handling recurring task generation.
"""

from datetime import datetime, timedelta
from typing import Optional
from dateutil.relativedelta import relativedelta
import calendar
import asyncio
import httpx

from src.models.task import Task, RecurrenceEnum


class RecurringTaskService:
    """
    Service for managing recurring task generation.

    Implements the logic for calculating next recurrence dates and
    generating new task instances based on recurrence patterns.
    """

    def __init__(self, dapr_http_port: int = 3500):
        self.dapr_http_port = dapr_http_port

    def calculate_next_daily(self, current_date: datetime) -> datetime:
        """
        Calculate next daily recurrence.

        Args:
            current_date: Current instance date

        Returns:
            Next instance date (current_date + 1 day)
        """
        return current_date + timedelta(days=1)

    def calculate_next_weekly(self, current_date: datetime, anchor_date: datetime) -> datetime:
        """
        Calculate next weekly recurrence.

        Maintains same day of week as anchor date.

        Args:
            current_date: Current instance date
            anchor_date: Original task creation date

        Returns:
            Next instance date (same day of week, +7 days)
        """
        # Add 7 days to maintain same day of week
        return current_date + timedelta(days=7)

    def calculate_next_monthly(self, current_date: datetime, anchor_date: datetime) -> datetime:
        """
        Calculate next monthly recurrence.

        Maintains same day of month as anchor date.
        Handles month-end edge cases.

        Args:
            current_date: Current instance date
            anchor_date: Original task creation date

        Returns:
            Next instance date (same day of month, +1 month)

        Edge cases:
        - If anchor is day 31 and next month has 30 days, use day 30
        - If anchor is day 29-31 and next month is February, use last day of February
        """
        anchor_day = anchor_date.day

        # Add one month
        next_month = current_date + relativedelta(months=1)

        # Get last day of next month
        last_day = calendar.monthrange(next_month.year, next_month.month)[1]

        # Use anchor day or last day of month, whichever is smaller
        target_day = min(anchor_day, last_day)

        return next_month.replace(day=target_day)

    def calculate_next_recurrence(
        self,
        current_date: datetime,
        anchor_date: datetime,
        recurrence_pattern: RecurrenceEnum
    ) -> datetime:
        """
        Calculate next recurrence date based on pattern.

        Args:
            current_date: Current instance date
            anchor_date: Original task creation date
            recurrence_pattern: "daily", "weekly", or "monthly"

        Returns:
            Next recurrence date

        Raises:
            ValueError: If recurrence_pattern is invalid
        """
        if recurrence_pattern == RecurrenceEnum.DAILY:
            return self.calculate_next_daily(current_date)
        elif recurrence_pattern == RecurrenceEnum.WEEKLY:
            return self.calculate_next_weekly(current_date, anchor_date)
        elif recurrence_pattern == RecurrenceEnum.MONTHLY:
            return self.calculate_next_monthly(current_date, anchor_date)
        else:
            raise ValueError(f"Invalid recurrence pattern: {recurrence_pattern}")

    async def generate_next_instance(
        self,
        parent_task: Task,
        user_id: str
    ) -> Optional[Task]:
        """
        Generate next instance of recurring task.

        Args:
            parent_task: Parent recurring task
            user_id: User identifier

        Returns:
            New task instance or None if parent is invalid
        """
        if parent_task.recurrence == RecurrenceEnum.NONE:
            return None

        if parent_task.due_date is None:
            return None

        # Calculate next due date
        next_due_date = self.calculate_next_recurrence(
            current_date=parent_task.due_date,
            anchor_date=parent_task.created_at,
            recurrence_pattern=parent_task.recurrence
        )

        # Create new task instance
        new_task = Task(
            user_id=user_id,
            title=parent_task.title,
            description=parent_task.description,
            due_date=next_due_date,
            priority=parent_task.priority,
            tags=parent_task.tags,
            recurrence=parent_task.recurrence,
            reminder_offset_minutes=parent_task.reminder_offset_minutes,
            completed=False
        )

        return new_task

    async def schedule_recurring_task_generation(
        self,
        task_id: str,
        user_id: str,
        recurrence_pattern: str,  # "daily", "weekly", "monthly"
        start_time: datetime,
        dapr_http_port: int = 3500
    ) -> str:
        """
        Schedule recurring task generation using Dapr Jobs API.

        Args:
            task_id: Parent task identifier
            user_id: User identifier
            recurrence_pattern: Recurrence frequency
            start_time: When to start generating instances
            dapr_http_port: Dapr sidecar HTTP port

        Returns:
            Job ID for tracking and cancellation
        """
        job_name = f"recurring-{task_id}"

        # Convert recurrence pattern to cron expression
        cron_schedule = {
            "daily": "0 0 * * *",      # Midnight UTC daily
            "weekly": "0 0 * * 0",     # Midnight UTC every Sunday
            "monthly": "0 0 1 * *"     # Midnight UTC on 1st of month
        }.get(recurrence_pattern, "0 0 * * *")

        url = f"http://localhost:{dapr_http_port}/v1.0-alpha1/jobs/{job_name}"

        payload = {
            "schedule": cron_schedule,  # Cron expression
            "repeats": 0,  # Infinite repeats (0 = forever)
            "dueTime": start_time.isoformat(),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "recurrence_pattern": recurrence_pattern
            },
            "callback": {
                "method": "POST",
                "endpoint": f"http://localhost:8000/api/internal/recurring/generate"
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            return result.get("jobId", job_name)

    async def cancel_recurring_job(
        self,
        task_id: str,
        dapr_http_port: int = 3500
    ) -> None:
        """
        Cancel a scheduled recurring task job using Dapr Jobs API.

        Args:
            task_id: Task identifier
            dapr_http_port: Dapr sidecar HTTP port
        """
        job_name = f"recurring-{task_id}"
        url = f"http://localhost:{dapr_http_port}/v1.0-alpha1/jobs/{job_name}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
            response.raise_for_status()


# Global instance
recurring_service = RecurringTaskService()