"""
Reminder service for scheduling task reminders.

Provides reminder management with:
- Dapr Jobs API integration for scheduled delivery
- Multiple reminder types (15min, 1hr, 1day, 1week, custom)
- Event publishing for reminder lifecycle
- Automatic cleanup of expired reminders
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from sqlmodel import Session, select

from src.models.reminder import Reminder, ReminderCreate
from src.models.task import Task
from src.core.dapr import get_dapr_client
from src.services.event_publisher import get_event_publisher

logger = logging.getLogger(__name__)


class ReminderService:
    """
    Service layer for reminder management operations.

    Handles reminder CRUD, scheduling via Dapr Jobs API,
    and event publishing for reminder lifecycle.
    """

    def __init__(self, session: Session):
        """
        Initialize reminder service.

        Args:
            session: Database session
        """
        self.session = session
        self.dapr_client = get_dapr_client()
        self.event_publisher = get_event_publisher()

    async def create_reminder(
        self,
        user_id: str,
        task_id: str,
        reminder_data: ReminderCreate,
        user_email: str
    ) -> Reminder:
        """
        Create a new reminder and schedule it via Dapr Jobs API.

        Args:
            user_id: User identifier
            task_id: Task identifier
            reminder_data: Reminder creation data
            user_email: User email for notification

        Returns:
            Created reminder with scheduled job

        Raises:
            ValueError: If scheduled time is in the past or task not found
        """
        # Validate task exists
        task = await self._get_task(user_id, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Validate scheduled time is in the future
        now = datetime.now(timezone.utc)
        scheduled_time = reminder_data.scheduled_time

        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)

        if scheduled_time <= now:
            raise ValueError("Scheduled time must be in the future")

        # Create reminder
        reminder = Reminder(
            task_id=task_id,
            user_id=user_id,
            scheduled_time=scheduled_time,
            reminder_type=reminder_data.reminder_type,
            status="pending"
        )

        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)

        # Schedule job via Dapr Jobs API
        job_id = await self._schedule_dapr_job(
            reminder=reminder,
            task_title=task.title,
            user_email=user_email
        )

        # Update reminder with job ID
        reminder.dapr_job_id = job_id
        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)

        # Publish ReminderScheduled event
        await self.event_publisher.publish_reminder_scheduled(
            reminder_id=reminder.id,
            user_id=user_id,
            task_id=task_id,
            task_title=task.title,
            scheduled_time=scheduled_time.isoformat(),
            reminder_type=reminder_data.reminder_type,
            user_email=user_email
        )

        logger.info(f"Created reminder {reminder.id} for task {task_id}, scheduled at {scheduled_time}")
        return reminder

    async def create_reminder_from_due_date(
        self,
        user_id: str,
        task_id: str,
        due_date: datetime,
        reminder_type: str,
        user_email: str
    ) -> Optional[Reminder]:
        """
        Create a reminder based on task due date and reminder type.

        Args:
            user_id: User identifier
            task_id: Task identifier
            due_date: Task due date
            reminder_type: Reminder type (15min, 1hr, 1day, 1week)
            user_email: User email for notification

        Returns:
            Created reminder or None if scheduled time is in the past
        """
        # Calculate scheduled time based on reminder type
        scheduled_time = self._calculate_scheduled_time(due_date, reminder_type)

        # Skip if scheduled time is in the past
        now = datetime.now(timezone.utc)
        if scheduled_time <= now:
            logger.warning(
                f"Skipping reminder creation for task {task_id}: "
                f"scheduled time {scheduled_time} is in the past"
            )
            return None

        # Create reminder
        reminder_data = ReminderCreate(
            scheduled_time=scheduled_time,
            reminder_type=reminder_type
        )

        return await self.create_reminder(user_id, task_id, reminder_data, user_email)

    async def get_reminder_by_id(
        self,
        user_id: str,
        reminder_id: str
    ) -> Optional[Reminder]:
        """
        Get a reminder by ID.

        Args:
            user_id: User identifier
            reminder_id: Reminder identifier

        Returns:
            Reminder if found, None otherwise
        """
        statement = select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        )
        return self.session.exec(statement).first()

    async def get_task_reminders(
        self,
        user_id: str,
        task_id: str
    ) -> List[Reminder]:
        """
        Get all reminders for a task.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            List of reminders
        """
        statement = select(Reminder).where(
            Reminder.task_id == task_id,
            Reminder.user_id == user_id
        ).order_by(Reminder.scheduled_time.asc())

        return list(self.session.exec(statement).all())

    async def delete_reminder(
        self,
        user_id: str,
        reminder_id: str
    ) -> bool:
        """
        Delete a reminder and cancel its scheduled job.

        Args:
            user_id: User identifier
            reminder_id: Reminder identifier

        Returns:
            True if deleted, False if not found
        """
        reminder = await self.get_reminder_by_id(user_id, reminder_id)
        if not reminder:
            return False

        # Cancel Dapr job if exists
        if reminder.dapr_job_id:
            await self._cancel_dapr_job(reminder.dapr_job_id)

        # Delete reminder
        self.session.delete(reminder)
        self.session.commit()

        logger.info(f"Deleted reminder {reminder_id}")
        return True

    async def delete_task_reminders(
        self,
        user_id: str,
        task_id: str
    ) -> int:
        """
        Delete all reminders for a task.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            Number of reminders deleted
        """
        reminders = await self.get_task_reminders(user_id, task_id)

        for reminder in reminders:
            await self.delete_reminder(user_id, reminder.id)

        return len(reminders)

    async def _schedule_dapr_job(
        self,
        reminder: Reminder,
        task_title: str,
        user_email: str
    ) -> str:
        """
        Schedule a job via Dapr Jobs API.

        Args:
            reminder: Reminder to schedule
            task_title: Task title for notification
            user_email: User email for notification

        Returns:
            Job ID
        """
        job_name = f"reminder-{reminder.id}"

        # Convert scheduled time to ISO 8601 format
        schedule = reminder.scheduled_time.isoformat()

        # Job data payload
        job_data = {
            "reminder_id": reminder.id,
            "task_id": reminder.task_id,
            "task_title": task_title,
            "user_id": reminder.user_id,
            "user_email": user_email,
            "scheduled_time": schedule,
            "reminder_type": reminder.reminder_type
        }

        # Schedule job
        job_id = await self.dapr_client.schedule_job(
            job_name=job_name,
            schedule=schedule,
            data=job_data
        )

        if not job_id:
            raise RuntimeError(f"Failed to schedule Dapr job for reminder {reminder.id}")

        logger.info(f"Scheduled Dapr job {job_id} for reminder {reminder.id}")
        return job_id

    async def _cancel_dapr_job(self, job_id: str) -> bool:
        """
        Cancel a scheduled Dapr job.

        Args:
            job_id: Job identifier

        Returns:
            True if cancelled successfully
        """
        success = await self.dapr_client.delete_job(job_id)

        if success:
            logger.info(f"Cancelled Dapr job {job_id}")
        else:
            logger.warning(f"Failed to cancel Dapr job {job_id}")

        return success

    def _calculate_scheduled_time(
        self,
        due_date: datetime,
        reminder_type: str
    ) -> datetime:
        """
        Calculate scheduled time based on due date and reminder type.

        Args:
            due_date: Task due date
            reminder_type: Reminder type (15min, 1hr, 1day, 1week)

        Returns:
            Scheduled time for reminder
        """
        if reminder_type == "15min":
            return due_date - timedelta(minutes=15)
        elif reminder_type == "1hr":
            return due_date - timedelta(hours=1)
        elif reminder_type == "1day":
            return due_date - timedelta(days=1)
        elif reminder_type == "1week":
            return due_date - timedelta(weeks=1)
        else:
            # For custom reminders, use the due date as-is
            return due_date

    async def _get_task(self, user_id: str, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            Task if found, None otherwise
        """
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        return self.session.exec(statement).first()
