"""
Task service for managing tasks with advanced features.

Provides CRUD operations, priority management, tag operations,
and event publishing for task lifecycle events.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from sqlalchemy import text
from sqlmodel import Session, select

from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.tag import Tag
from src.services.event_publisher import get_event_publisher
from src.services.reminder_service import ReminderService

logger = logging.getLogger(__name__)


class TaskService:
    """
    Service layer for task management operations.

    Handles task CRUD, priority management, tag operations,
    and publishes events for task lifecycle changes.
    """

    def __init__(self, session: Session):
        """
        Initialize task service.

        Args:
            session: Database session
        """
        self.session = session
        self.event_publisher = get_event_publisher()

    async def create_task(
        self,
        user_id: str,
        task_data: TaskCreate,
        tag_ids: Optional[List[str]] = None,
        user_email: Optional[str] = None,
        auto_create_reminders: bool = True,
        recurrence_rule_id: Optional[str] = None,
        parent_task_id: Optional[str] = None
    ) -> Task:
        """
        Create a new task with optional tags, automatic reminders, and recurrence rule.

        Args:
            user_id: User identifier
            task_data: Task creation data
            tag_ids: Optional list of tag IDs to attach
            user_email: User email for reminder notifications
            auto_create_reminders: If True, automatically create default reminders for tasks with due dates
            recurrence_rule_id: Optional recurrence rule ID for recurring tasks
            parent_task_id: Optional parent task ID for recurring task instances

        Returns:
            Created task with tags

        Raises:
            ValueError: If tag IDs are invalid or due date is in the past
        """
        # Validate due date if provided
        if hasattr(task_data, 'due_date') and task_data.due_date:
            self._validate_due_date(task_data.due_date)

        # Create task
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority if hasattr(task_data, 'priority') else "Medium",
            due_date=task_data.due_date if hasattr(task_data, 'due_date') else None,
            is_recurring=task_data.is_recurring if hasattr(task_data, 'is_recurring') else False,
            recurrence_rule_id=recurrence_rule_id,
            parent_task_id=parent_task_id,
            completed=False
        )

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        # Add tags if provided
        if tag_ids and len(tag_ids) > 0:
            await self._add_tags_to_task(task.id, tag_ids)
            self.session.refresh(task)

        # Create default reminders if task has due date
        if auto_create_reminders and task.due_date and user_email:
            await self._create_default_reminders(
                user_id=user_id,
                task_id=task.id,
                due_date=task.due_date,
                user_email=user_email
            )

        # Publish TaskCreated event
        task_dict = self._task_to_dict(task)
        await self.event_publisher.publish_task_created(
            task_id=task.id,
            user_id=user_id,
            task_data=task_dict
        )

        logger.info(f"Created task {task.id} for user {user_id}")
        return task

    async def get_task_by_id(
        self,
        user_id: str,
        task_id: str
    ) -> Optional[Task]:
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

    async def get_all_tasks(self, user_id: str) -> List[Task]:
        """
        Get all tasks for a user.

        Args:
            user_id: User identifier

        Returns:
            List of tasks
        """
        statement = select(Task).where(Task.user_id == user_id)
        return list(self.session.exec(statement).all())

    async def update_task(
        self,
        user_id: str,
        task_id: str,
        task_data: TaskUpdate,
        user_email: Optional[str] = None,
        auto_create_reminders: bool = True
    ) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            user_id: User identifier
            task_id: Task identifier
            task_data: Task update data
            user_email: User email for reminder notifications
            auto_create_reminders: If True, automatically create default reminders when due date is added

        Returns:
            Updated task if found, None otherwise

        Raises:
            ValueError: If due date is in the past
        """
        task = await self.get_task_by_id(user_id, task_id)
        if not task:
            return None

        # Track changes for event
        changes: Dict[str, Any] = {}
        due_date_changed = False
        old_due_date = task.due_date

        # Update fields
        if task_data.title is not None:
            changes["title"] = {"old": task.title, "new": task_data.title}
            task.title = task_data.title

        if task_data.description is not None:
            changes["description"] = {"old": task.description, "new": task_data.description}
            task.description = task_data.description

        if hasattr(task_data, 'priority') and task_data.priority is not None:
            changes["priority"] = {"old": task.priority, "new": task_data.priority}
            task.priority = task_data.priority

        if hasattr(task_data, 'due_date') and task_data.due_date is not None:
            # Validate new due date
            self._validate_due_date(task_data.due_date)

            changes["due_date"] = {"old": task.due_date, "new": task_data.due_date}
            task.due_date = task_data.due_date
            due_date_changed = True

        task.updated_at = datetime.now(timezone.utc)

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        # Handle reminders if due date was added or changed
        if due_date_changed and task.due_date and user_email and auto_create_reminders:
            # Delete existing reminders if due date changed
            if old_due_date:
                reminder_service = ReminderService(self.session)
                await reminder_service.delete_task_reminders(user_id, task_id)

            # Create new default reminders
            await self._create_default_reminders(
                user_id=user_id,
                task_id=task_id,
                due_date=task.due_date,
                user_email=user_email
            )

        # Publish TaskUpdated event if changes were made
        if changes:
            task_dict = self._task_to_dict(task)
            await self.event_publisher.publish_task_updated(
                task_id=task.id,
                user_id=user_id,
                changes=changes,
                task_data=task_dict
            )

        logger.info(f"Updated task {task_id} for user {user_id}")
        return task

    async def delete_task(
        self,
        user_id: str,
        task_id: str,
        delete_series: bool = False
    ) -> bool:
        """
        Delete a task.

        Args:
            user_id: User identifier
            task_id: Task identifier
            delete_series: If True, delete entire recurring series

        Returns:
            True if deleted, False if not found
        """
        task = await self.get_task_by_id(user_id, task_id)
        if not task:
            return False

        parent_task_id = task.parent_task_id

        self.session.delete(task)
        self.session.commit()

        # Publish TaskDeleted event
        await self.event_publisher.publish_task_deleted(
            task_id=task_id,
            user_id=user_id,
            delete_series=delete_series,
            parent_task_id=parent_task_id
        )

        logger.info(f"Deleted task {task_id} for user {user_id}")
        return True

    async def toggle_completion(
        self,
        user_id: str,
        task_id: str
    ) -> Optional[Task]:
        """
        Toggle task completion status.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            Updated task if found, None otherwise
        """
        task = await self.get_task_by_id(user_id, task_id)
        if not task:
            return None

        task.completed = not task.completed
        task.updated_at = datetime.now(timezone.utc)

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        # Publish TaskCompleted event if task was marked complete
        if task.completed:
            task_dict = self._task_to_dict(task)
            await self.event_publisher.publish_task_completed(
                task_id=task.id,
                user_id=user_id,
                task_data=task_dict
            )

        logger.info(f"Toggled completion for task {task_id} to {task.completed}")
        return task

    async def set_priority(
        self,
        user_id: str,
        task_id: str,
        priority: str
    ) -> Optional[Task]:
        """
        Set task priority.

        Args:
            user_id: User identifier
            task_id: Task identifier
            priority: Priority level (Low, Medium, High)

        Returns:
            Updated task if found, None otherwise
        """
        task = await self.get_task_by_id(user_id, task_id)
        if not task:
            return None

        old_priority = task.priority
        task.priority = priority
        task.updated_at = datetime.now(timezone.utc)

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        # Publish TaskUpdated event
        task_dict = self._task_to_dict(task)
        await self.event_publisher.publish_task_updated(
            task_id=task.id,
            user_id=user_id,
            changes={"priority": {"old": old_priority, "new": priority}},
            task_data=task_dict
        )

        logger.info(f"Set priority for task {task_id} to {priority}")
        return task

    async def add_tag(
        self,
        user_id: str,
        task_id: str,
        tag_id: str
    ) -> Optional[Task]:
        """
        Add a tag to a task.

        Args:
            user_id: User identifier
            task_id: Task identifier
            tag_id: Tag identifier

        Returns:
            Updated task if found, None otherwise

        Raises:
            ValueError: If tag doesn't exist or doesn't belong to user
        """
        task = await self.get_task_by_id(user_id, task_id)
        if not task:
            return None

        # Verify tag exists and belongs to user
        tag_statement = select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id
        )
        tag = self.session.exec(tag_statement).first()
        if not tag:
            raise ValueError(f"Tag {tag_id} not found or doesn't belong to user")

        # Add tag to task (via task_tags join table)
        insert_statement = text(
            "INSERT INTO tasks.task_tags (task_id, tag_id) "
            "VALUES (:task_id, :tag_id) "
            "ON CONFLICT DO NOTHING"
        )
        self.session.exec(insert_statement, {"task_id": task_id, "tag_id": tag_id})
        self.session.commit()

        # Increment tag usage count
        tag.usage_count += 1
        self.session.add(tag)
        self.session.commit()

        self.session.refresh(task)

        logger.info(f"Added tag {tag_id} to task {task_id}")
        return task

    async def remove_tag(
        self,
        user_id: str,
        task_id: str,
        tag_id: str
    ) -> Optional[Task]:
        """
        Remove a tag from a task.

        Args:
            user_id: User identifier
            task_id: Task identifier
            tag_id: Tag identifier

        Returns:
            Updated task if found, None otherwise
        """
        task = await self.get_task_by_id(user_id, task_id)
        if not task:
            return None

        # Remove tag from task
        delete_statement = text(
            "DELETE FROM tasks.task_tags "
            "WHERE task_id = :task_id AND tag_id = :tag_id"
        )
        self.session.exec(delete_statement, {"task_id": task_id, "tag_id": tag_id})
        self.session.commit()

        # Decrement tag usage count
        tag_statement = select(Tag).where(Tag.id == tag_id)
        tag = self.session.exec(tag_statement).first()
        if tag and tag.usage_count > 0:
            tag.usage_count -= 1
            self.session.add(tag)
            self.session.commit()

        self.session.refresh(task)

        logger.info(f"Removed tag {tag_id} from task {task_id}")
        return task

    async def get_task_tags(
        self,
        user_id: str,
        task_id: str
    ) -> List[Tag]:
        """
        Get all tags for a task.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            List of tags
        """
        task = await self.get_task_by_id(user_id, task_id)
        if not task:
            return []

        statement = select(Tag).join(
            text("tasks.task_tags"),
            text("tasks.tags.id = tasks.task_tags.tag_id")
        ).where(
            text("tasks.task_tags.task_id = :task_id")
        ).params(task_id=task_id)

        return list(self.session.exec(statement).all())

    async def _add_tags_to_task(
        self,
        task_id: str,
        tag_ids: List[str]
    ) -> None:
        """
        Internal method to add multiple tags to a task.

        Args:
            task_id: Task identifier
            tag_ids: List of tag identifiers
        """
        for tag_id in tag_ids:
            insert_statement = text(
                "INSERT INTO tasks.task_tags (task_id, tag_id) "
                "VALUES (:task_id, :tag_id) "
                "ON CONFLICT DO NOTHING"
            )
            self.session.exec(insert_statement, {"task_id": task_id, "tag_id": tag_id})

            # Increment tag usage count
            tag_statement = select(Tag).where(Tag.id == tag_id)
            tag = self.session.exec(tag_statement).first()
            if tag:
                tag.usage_count += 1
                self.session.add(tag)

        self.session.commit()

    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """
        Convert task to dictionary for event publishing.

        Args:
            task: Task object

        Returns:
            Task data as dictionary
        """
        return {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "is_recurring": task.is_recurring,
            "parent_task_id": task.parent_task_id,
            "recurrence_rule_id": task.recurrence_rule_id,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }

    def _validate_due_date(self, due_date: datetime) -> None:
        """
        Validate that due date is not in the past.

        Args:
            due_date: Due date to validate

        Raises:
            ValueError: If due date is in the past
        """
        now = datetime.now(timezone.utc)

        # Ensure due_date is timezone-aware
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        if due_date <= now:
            raise ValueError("Due date must be in the future")

    async def _create_default_reminders(
        self,
        user_id: str,
        task_id: str,
        due_date: datetime,
        user_email: str
    ) -> None:
        """
        Create default reminders for a task with a due date.

        Creates two reminders:
        - 1 day before due date
        - 1 hour before due date

        Args:
            user_id: User identifier
            task_id: Task identifier
            due_date: Task due date
            user_email: User email for notifications
        """
        reminder_service = ReminderService(self.session)

        # Default reminder types to create
        default_reminder_types = ["1day", "1hr"]

        for reminder_type in default_reminder_types:
            try:
                await reminder_service.create_reminder_from_due_date(
                    user_id=user_id,
                    task_id=task_id,
                    due_date=due_date,
                    reminder_type=reminder_type,
                    user_email=user_email
                )
                logger.info(f"Created {reminder_type} reminder for task {task_id}")
            except Exception as e:
                # Log error but don't fail task creation if reminder creation fails
                logger.warning(
                    f"Failed to create {reminder_type} reminder for task {task_id}: {str(e)}"
                )

    async def update_recurring_series(
        self,
        user_id: str,
        task_id: str,
        task_data: TaskUpdate
    ) -> List[Task]:
        """
        Update all tasks in a recurring series.

        Args:
            user_id: User identifier
            task_id: Task identifier (any task in the series)
            task_data: Task update data to apply to all tasks in series

        Returns:
            List of updated tasks in the series

        Raises:
            ValueError: If task is not part of a recurring series
        """
        task = await self.get_task_by_id(user_id, task_id)
        if not task:
            return []

        if not task.is_recurring:
            raise ValueError("Task is not part of a recurring series")

        # Find the parent task ID (either this task's parent or this task itself)
        parent_id = task.parent_task_id if task.parent_task_id else task.id

        # Get all tasks in the series (parent + all children)
        statement = select(Task).where(
            Task.user_id == user_id,
            (Task.id == parent_id) | (Task.parent_task_id == parent_id)
        )
        series_tasks = list(self.session.exec(statement).all())

        updated_tasks = []
        for series_task in series_tasks:
            # Update each task in the series
            if task_data.title is not None:
                series_task.title = task_data.title
            if task_data.description is not None:
                series_task.description = task_data.description
            if hasattr(task_data, 'priority') and task_data.priority is not None:
                series_task.priority = task_data.priority

            series_task.updated_at = datetime.now(timezone.utc)
            self.session.add(series_task)
            updated_tasks.append(series_task)

        self.session.commit()

        for updated_task in updated_tasks:
            self.session.refresh(updated_task)

        logger.info(f"Updated {len(updated_tasks)} tasks in recurring series for parent {parent_id}")
        return updated_tasks

    async def delete_recurring_series(
        self,
        user_id: str,
        task_id: str
    ) -> int:
        """
        Delete all tasks in a recurring series.

        Args:
            user_id: User identifier
            task_id: Task identifier (any task in the series)

        Returns:
            Number of tasks deleted

        Raises:
            ValueError: If task is not part of a recurring series
        """
        task = await self.get_task_by_id(user_id, task_id)
        if not task:
            return 0

        if not task.is_recurring:
            raise ValueError("Task is not part of a recurring series")

        # Find the parent task ID
        parent_id = task.parent_task_id if task.parent_task_id else task.id

        # Get all tasks in the series
        statement = select(Task).where(
            Task.user_id == user_id,
            (Task.id == parent_id) | (Task.parent_task_id == parent_id)
        )
        series_tasks = list(self.session.exec(statement).all())

        # Delete all tasks in the series
        for series_task in series_tasks:
            self.session.delete(series_task)

        self.session.commit()

        # Publish TaskDeleted event for the series
        await self.event_publisher.publish_task_deleted(
            task_id=parent_id,
            user_id=user_id,
            delete_series=True,
            parent_task_id=parent_id
        )

        deleted_count = len(series_tasks)
        logger.info(f"Deleted {deleted_count} tasks in recurring series for parent {parent_id}")
        return deleted_count

