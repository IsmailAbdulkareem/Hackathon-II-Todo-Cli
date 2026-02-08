"""
Dapr Task Repository Implementation (T093)

This module implements the TaskRepository interface using Dapr
state store, pub/sub, and jobs APIs.
"""

from typing import List, Optional
from datetime import datetime, timezone
import uuid

from src.core.repository_interface import (
    TaskRepository,
    RepositoryError,
    TaskNotFoundError,
    RepositoryConnectionError
)
from src.core.dapr_state_adapter import DaprStateStoreAdapter
from src.core.dapr_pubsub_adapter import DaprPubSubAdapter
from src.core.dapr_jobs_adapter import DaprJobsAdapter
from src.models.task import Task, TaskCreate, TaskUpdate
import httpx


class DaprTaskRepository(TaskRepository):
    """
    Dapr-based implementation of TaskRepository.

    Uses Dapr state store for persistence, pub/sub for events,
    and jobs API for scheduling.
    """

    def __init__(
        self,
        state_adapter: Optional[DaprStateStoreAdapter] = None,
        pubsub_adapter: Optional[DaprPubSubAdapter] = None,
        jobs_adapter: Optional[DaprJobsAdapter] = None
    ):
        """
        Initialize Dapr task repository.

        Args:
            state_adapter: Dapr state store adapter
            pubsub_adapter: Dapr pub/sub adapter
            jobs_adapter: Dapr jobs adapter
        """
        self.state = state_adapter or DaprStateStoreAdapter()
        self.pubsub = pubsub_adapter or DaprPubSubAdapter()
        self.jobs = jobs_adapter or DaprJobsAdapter()

    def _make_key(self, user_id: str, task_id: str) -> str:
        """Generate state store key for a task"""
        return f"task:{user_id}:{task_id}"

    def _make_index_key(self, user_id: str) -> str:
        """Generate state store key for user's task index"""
        return f"task_index:{user_id}"

    async def create(self, user_id: str, task_data: TaskCreate) -> Task:
        """Create a new task in Dapr state store"""
        try:
            # Generate task ID
            task_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            # Create task object
            task = Task(
                id=task_id,
                user_id=user_id,
                title=task_data.title,
                description=task_data.description,
                completed=False,
                created_at=now,
                updated_at=now,
                due_date=task_data.due_date.isoformat() if task_data.due_date else None,
                priority=task_data.priority,
                tags=task_data.tags or [],
                recurrence=task_data.recurrence,
                reminder_offset_minutes=task_data.reminder_offset_minutes or 0
            )

            # Save to state store
            key = self._make_key(user_id, task_id)
            await self.state.save(key, task.dict())

            # Update task index
            await self._add_to_index(user_id, task_id)

            # Publish event
            await self._publish_event("task-events", "TASK_CREATED", task)

            return task

        except httpx.HTTPError as e:
            raise RepositoryConnectionError(f"Failed to create task: {e}")
        except Exception as e:
            raise RepositoryError(f"Unexpected error creating task: {e}")

    async def get_by_id(self, user_id: str, task_id: str) -> Optional[Task]:
        """Get a task by ID from Dapr state store"""
        try:
            key = self._make_key(user_id, task_id)
            data = await self.state.get(key)

            if data is None:
                return None

            return Task(**data)

        except httpx.HTTPError as e:
            raise RepositoryConnectionError(f"Failed to get task: {e}")
        except Exception as e:
            raise RepositoryError(f"Unexpected error getting task: {e}")

    async def get_all(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get all tasks for a user from Dapr state store"""
        try:
            # Get task IDs from index
            index_key = self._make_index_key(user_id)
            index_data = await self.state.get(index_key)

            if not index_data or "task_ids" not in index_data:
                return []

            task_ids = index_data["task_ids"][skip:skip + limit]

            # Bulk get tasks
            keys = [self._make_key(user_id, tid) for tid in task_ids]
            tasks_data = await self.state.bulk_get(keys)

            # Convert to Task objects
            tasks = []
            for task_data in tasks_data.values():
                if task_data:
                    tasks.append(Task(**task_data))

            return tasks

        except httpx.HTTPError as e:
            raise RepositoryConnectionError(f"Failed to get tasks: {e}")
        except Exception as e:
            raise RepositoryError(f"Unexpected error getting tasks: {e}")

    async def update(
        self,
        user_id: str,
        task_id: str,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """Update a task in Dapr state store"""
        try:
            # Get existing task
            existing = await self.get_by_id(user_id, task_id)
            if not existing:
                return None

            # Update fields (exclude_unset=True means only set fields are included)
            update_dict = task_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(existing, field, value)

            existing.updated_at = datetime.now(timezone.utc).isoformat()

            # Save to state store
            key = self._make_key(user_id, task_id)
            await self.state.save(key, existing.dict())

            # Publish event
            await self._publish_event("task-events", "TASK_UPDATED", existing)

            return existing

        except httpx.HTTPError as e:
            raise RepositoryConnectionError(f"Failed to update task: {e}")
        except Exception as e:
            raise RepositoryError(f"Unexpected error updating task: {e}")

    async def delete(self, user_id: str, task_id: str) -> bool:
        """Delete a task from Dapr state store"""
        try:
            # Check if task exists
            existing = await self.get_by_id(user_id, task_id)
            if not existing:
                return False

            # Delete from state store
            key = self._make_key(user_id, task_id)
            await self.state.delete(key)

            # Remove from index
            await self._remove_from_index(user_id, task_id)

            # Publish event
            await self._publish_event("task-events", "TASK_DELETED", existing)

            return True

        except httpx.HTTPError as e:
            raise RepositoryConnectionError(f"Failed to delete task: {e}")
        except Exception as e:
            raise RepositoryError(f"Unexpected error deleting task: {e}")

    async def search(
        self,
        user_id: str,
        query: Optional[str] = None,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_from: Optional[datetime] = None,
        due_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Search tasks using Dapr state store query"""
        try:
            # Get all tasks and filter in memory
            # (Dapr query API support varies by state store)
            all_tasks = await self.get_all(user_id, skip=0, limit=1000)

            # Apply filters
            filtered = all_tasks

            if query:
                query_lower = query.lower()
                filtered = [
                    t for t in filtered
                    if query_lower in t.title.lower() or
                    (t.description and query_lower in t.description.lower())
                ]

            if completed is not None:
                filtered = [t for t in filtered if t.completed == completed]

            if priority:
                filtered = [t for t in filtered if t.priority == priority]

            if tags:
                filtered = [
                    t for t in filtered
                    if any(tag in t.tags for tag in tags)
                ]

            if due_from:
                filtered = [
                    t for t in filtered
                    if t.due_date and t.due_date >= due_from.isoformat()
                ]

            if due_to:
                filtered = [
                    t for t in filtered
                    if t.due_date and t.due_date <= due_to.isoformat()
                ]

            # Sort
            reverse = sort_order == "desc"
            filtered.sort(key=lambda t: getattr(t, sort_by), reverse=reverse)

            # Paginate
            return filtered[skip:skip + limit]

        except Exception as e:
            raise RepositoryError(f"Unexpected error searching tasks: {e}")

    async def count(
        self,
        user_id: str,
        completed: Optional[bool] = None
    ) -> int:
        """Count tasks for a user"""
        try:
            tasks = await self.get_all(user_id, skip=0, limit=10000)

            if completed is not None:
                tasks = [t for t in tasks if t.completed == completed]

            return len(tasks)

        except Exception as e:
            raise RepositoryError(f"Unexpected error counting tasks: {e}")

    async def _add_to_index(self, user_id: str, task_id: str) -> None:
        """Add task ID to user's task index"""
        index_key = self._make_index_key(user_id)
        index_data = await self.state.get(index_key) or {"task_ids": []}

        if task_id not in index_data["task_ids"]:
            index_data["task_ids"].append(task_id)
            await self.state.save(index_key, index_data)

    async def _remove_from_index(self, user_id: str, task_id: str) -> None:
        """Remove task ID from user's task index"""
        index_key = self._make_index_key(user_id)
        index_data = await self.state.get(index_key)

        if index_data and task_id in index_data["task_ids"]:
            index_data["task_ids"].remove(task_id)
            await self.state.save(index_key, index_data)

    async def _publish_event(
        self,
        topic: str,
        event_type: str,
        task: Task
    ) -> None:
        """Publish task event to Dapr pub/sub"""
        try:
            event_data = {
                "event_id": str(uuid.uuid4()),
                "type": event_type,
                "task_id": task.id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": task.dict()
            }
            await self.pubsub.publish(topic, event_data)
        except Exception:
            # Don't fail the operation if event publishing fails
            pass
