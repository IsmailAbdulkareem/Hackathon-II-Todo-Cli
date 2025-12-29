"""TodoService - Business logic for todo operations.

This module contains the TodoService class which manages CRUD operations
for todo tasks. All business rules and validations are enforced here.

Generated via Claude Code following spec-driven development methodology.
"""

from typing import Optional
from src.domain.todo import Todo


class TodoService:
    """Service layer for todo task management.

    Manages in-memory storage of tasks and provides CRUD operations.
    All tasks stored in a dictionary keyed by task ID for O(1) lookups.

    Attributes:
        _tasks: Dictionary storing tasks by ID
        _next_id: Counter for generating unique task IDs (starts at 1)
    """

    def __init__(self) -> None:
        """Initialize TodoService with empty task storage."""
        self._tasks: dict[int, Todo] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Todo:
        """Add a new task to the todo list.

        Args:
            title: Task title (mandatory, max 200 characters)
            description: Task description (optional, max 1000 characters)

        Returns:
            The newly created Todo object

        Raises:
            ValueError: If title is empty or exceeds 200 characters
            ValueError: If description exceeds 1000 characters
        """
        # Validate title (mandatory, non-empty)
        title_stripped = title.strip()
        if not title_stripped:
            raise ValueError("Title cannot be empty")

        if len(title_stripped) > 200:
            raise ValueError("Title too long (max 200 characters)")

        # Validate description (optional)
        if len(description) > 1000:
            raise ValueError("Description too long (max 1000 characters)")

        # Create new task with next available ID
        task = Todo(
            id=self._next_id,
            title=title_stripped,
            description=description
        )

        # Store task and increment ID counter
        self._tasks[self._next_id] = task
        self._next_id += 1

        return task

    def get_all_tasks(self) -> list[Todo]:
        """Retrieve all tasks sorted by ID.

        Returns:
            List of all Todo objects sorted by ID (ascending)
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def get_task_by_id(self, task_id: int) -> Optional[Todo]:
        """Retrieve a specific task by its ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The Todo object if found, None otherwise
        """
        return self._tasks.get(task_id)

    def toggle_complete(self, task_id: int) -> bool:
        """Toggle a task's completion status.

        Args:
            task_id: The unique identifier of the task

        Returns:
            True if task was found and toggled, False if task not found
        """
        task = self.get_task_by_id(task_id)
        if task:
            task.toggle_complete()
            return True
        return False

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """Update a task's title and/or description.

        Args:
            task_id: The unique identifier of the task
            title: New title (optional, if None then title unchanged)
            description: New description (optional, if None then description unchanged)

        Returns:
            True if task was found and updated, False if task not found

        Raises:
            ValueError: If new title is empty or exceeds 200 characters
            ValueError: If new description exceeds 1000 characters
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        # Update title if provided
        if title is not None:
            title_stripped = title.strip()
            if not title_stripped:
                raise ValueError("Title cannot be empty")
            if len(title_stripped) > 200:
                raise ValueError("Title too long (max 200 characters)")
            task.title = title_stripped

        # Update description if provided
        if description is not None:
            if len(description) > 1000:
                raise ValueError("Description too long (max 1000 characters)")
            task.description = description

        return True

    def delete_task(self, task_id: int) -> bool:
        """Delete a task from the todo list.

        Args:
            task_id: The unique identifier of the task to delete

        Returns:
            True if task was found and deleted, False if task not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
