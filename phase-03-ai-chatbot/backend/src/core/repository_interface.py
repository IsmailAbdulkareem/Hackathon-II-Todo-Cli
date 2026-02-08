"""
Task Repository Interface (T092)

This module defines the abstract interface for task repository operations,
enabling clean architecture and dependency inversion.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.models.task import Task, TaskCreate, TaskUpdate


class TaskRepository(ABC):
    """
    Abstract interface for task repository operations.

    This interface defines the contract for task persistence,
    allowing different implementations (Dapr, SQL, in-memory, etc.)
    without changing business logic.
    """

    @abstractmethod
    async def create(self, user_id: str, task_data: TaskCreate) -> Task:
        """
        Create a new task.

        Args:
            user_id: User identifier
            task_data: Task creation data

        Returns:
            Created task

        Raises:
            RepositoryError: If creation fails
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            Task if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get all tasks for a user.

        Args:
            user_id: User identifier
            skip: Number of tasks to skip (pagination)
            limit: Maximum number of tasks to return

        Returns:
            List of tasks

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def update(
        self,
        user_id: str,
        task_id: str,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """
        Update a task.

        Args:
            user_id: User identifier
            task_id: Task identifier
            task_data: Task update data

        Returns:
            Updated task if found, None otherwise

        Raises:
            RepositoryError: If update fails
        """
        pass

    @abstractmethod
    async def delete(self, user_id: str, task_id: str) -> bool:
        """
        Delete a task.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            True if deleted, False if not found

        Raises:
            RepositoryError: If deletion fails
        """
        pass

    @abstractmethod
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
        """
        Search and filter tasks.

        Args:
            user_id: User identifier
            query: Text search query
            completed: Filter by completion status
            priority: Filter by priority level
            tags: Filter by tags (OR logic)
            due_from: Filter by due date start
            due_to: Filter by due date end
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            skip: Number of tasks to skip
            limit: Maximum number of tasks to return

        Returns:
            List of matching tasks

        Raises:
            RepositoryError: If search fails
        """
        pass

    @abstractmethod
    async def count(
        self,
        user_id: str,
        completed: Optional[bool] = None
    ) -> int:
        """
        Count tasks for a user.

        Args:
            user_id: User identifier
            completed: Filter by completion status

        Returns:
            Number of tasks

        Raises:
            RepositoryError: If count fails
        """
        pass


class RepositoryError(Exception):
    """Base exception for repository errors"""
    pass


class TaskNotFoundError(RepositoryError):
    """Raised when a task is not found"""
    pass


class TaskAccessDeniedError(RepositoryError):
    """Raised when user doesn't have access to a task"""
    pass


class RepositoryConnectionError(RepositoryError):
    """Raised when repository connection fails"""
    pass
