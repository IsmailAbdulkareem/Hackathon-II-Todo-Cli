"""
Search service for task filtering and full-text search.

Provides advanced search capabilities including full-text search,
multi-criteria filtering, and flexible sorting options.
"""

import logging
from datetime import datetime, timezone
from typing import List, Literal, Optional

from sqlalchemy import and_, func, or_, text
from sqlmodel import Session, select

from src.models.task import Task

logger = logging.getLogger(__name__)


class SearchService:
    """
    Service layer for task search and filtering operations.

    Supports full-text search, multi-criteria filtering, and sorting.
    All operations are scoped to the authenticated user.
    """

    def __init__(self, session: Session):
        """
        Initialize search service.

        Args:
            session: Database session
        """
        self.session = session

    async def search_tasks(
        self,
        user_id: str,
        query: Optional[str] = None,
        priority: Optional[Literal["Low", "Medium", "High"]] = None,
        tags: Optional[List[str]] = None,
        completed: Optional[bool] = None,
        is_recurring: Optional[bool] = None,
        has_due_date: Optional[bool] = None,
        overdue: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: Literal["asc", "desc"] = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """
        Search and filter tasks with multiple criteria.

        Args:
            user_id: User identifier
            query: Full-text search query (searches title and description)
            priority: Filter by priority level
            tags: Filter by tag names (OR logic - matches any tag)
            completed: Filter by completion status
            is_recurring: Filter by recurring status
            has_due_date: Filter tasks with/without due dates
            overdue: Filter overdue tasks (requires has_due_date=True)
            sort_by: Sort field (created_at, updated_at, due_date, priority, title)
            sort_order: Sort direction (asc, desc)
            limit: Maximum number of results (default: 100)
            offset: Number of results to skip for pagination

        Returns:
            List of matching tasks
        """
        # Start with base query
        statement = select(Task).where(Task.user_id == user_id)

        # Apply full-text search if query provided
        if query and query.strip():
            # Use PostgreSQL full-text search with GIN index
            search_query = query.strip()
            statement = statement.where(
                or_(
                    func.to_tsvector('english', Task.title).op('@@')(
                        func.plainto_tsquery('english', search_query)
                    ),
                    func.to_tsvector('english', Task.description).op('@@')(
                        func.plainto_tsquery('english', search_query)
                    )
                )
            )

        # Apply priority filter
        if priority:
            statement = statement.where(Task.priority == priority)

        # Apply completion status filter
        if completed is not None:
            statement = statement.where(Task.completed == completed)

        # Apply recurring filter
        if is_recurring is not None:
            statement = statement.where(Task.is_recurring == is_recurring)

        # Apply due date filters
        if has_due_date is not None:
            if has_due_date:
                statement = statement.where(Task.due_date.isnot(None))
            else:
                statement = statement.where(Task.due_date.is_(None))

        # Apply overdue filter
        if overdue is not None and overdue:
            now = datetime.now(timezone.utc)
            statement = statement.where(
                and_(
                    Task.due_date.isnot(None),
                    Task.due_date < now,
                    Task.completed == False
                )
            )

        # Apply tag filter (if tags provided)
        if tags and len(tags) > 0:
            # Join with task_tags and tags tables
            statement = statement.join(
                text("tasks.task_tags"),
                text("tasks.tasks.id = tasks.task_tags.task_id")
            ).join(
                text("tasks.tags"),
                text("tasks.task_tags.tag_id = tasks.tags.id")
            ).where(
                func.lower(text("tasks.tags.name")).in_([tag.lower() for tag in tags])
            ).distinct()

        # Apply sorting
        if sort_by == "updated_at":
            order_column = Task.updated_at
        elif sort_by == "due_date":
            # NULL due dates go last
            order_column = Task.due_date.nullslast() if sort_order == "asc" else Task.due_date.nullsfirst()
        elif sort_by == "priority":
            # Custom priority ordering: High > Medium > Low
            priority_order = text(
                "CASE tasks.tasks.priority "
                "WHEN 'High' THEN 1 "
                "WHEN 'Medium' THEN 2 "
                "WHEN 'Low' THEN 3 "
                "ELSE 4 END"
            )
            order_column = priority_order
        elif sort_by == "title":
            order_column = Task.title
        else:  # Default to created_at
            order_column = Task.created_at

        # Apply sort order
        if sort_order == "asc":
            statement = statement.order_by(order_column.asc() if hasattr(order_column, 'asc') else order_column)
        else:
            statement = statement.order_by(order_column.desc() if hasattr(order_column, 'desc') else order_column)

        # Apply pagination
        statement = statement.limit(limit).offset(offset)

        # Execute query
        results = self.session.exec(statement).all()
        return list(results)

    async def search_by_tags(
        self,
        user_id: str,
        tag_names: List[str],
        match_all: bool = False
    ) -> List[Task]:
        """
        Search tasks by tag names.

        Args:
            user_id: User identifier
            tag_names: List of tag names to search
            match_all: If True, task must have ALL tags (AND logic).
                      If False, task must have ANY tag (OR logic).

        Returns:
            List of matching tasks
        """
        if not tag_names or len(tag_names) == 0:
            return []

        if match_all:
            # Task must have ALL specified tags
            statement = select(Task).where(Task.user_id == user_id)

            for tag_name in tag_names:
                statement = statement.join(
                    text("tasks.task_tags"),
                    text("tasks.tasks.id = tasks.task_tags.task_id")
                ).join(
                    text("tasks.tags"),
                    text("tasks.task_tags.tag_id = tasks.tags.id")
                ).where(
                    func.lower(text("tasks.tags.name")) == tag_name.lower()
                )
        else:
            # Task must have ANY of the specified tags (OR logic)
            return await self.search_tasks(
                user_id=user_id,
                tags=tag_names
            )

        results = self.session.exec(statement).all()
        return list(results)

    async def get_overdue_tasks(self, user_id: str) -> List[Task]:
        """
        Get all overdue incomplete tasks for a user.

        Args:
            user_id: User identifier

        Returns:
            List of overdue tasks sorted by due date (oldest first)
        """
        return await self.search_tasks(
            user_id=user_id,
            overdue=True,
            sort_by="due_date",
            sort_order="asc"
        )

    async def get_due_today_tasks(self, user_id: str) -> List[Task]:
        """
        Get all tasks due today for a user.

        Args:
            user_id: User identifier

        Returns:
            List of tasks due today
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        statement = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.due_date >= today_start,
                Task.due_date <= today_end,
                Task.completed == False
            )
        ).order_by(Task.due_date.asc())

        results = self.session.exec(statement).all()
        return list(results)

    async def get_high_priority_tasks(self, user_id: str) -> List[Task]:
        """
        Get all high priority incomplete tasks for a user.

        Args:
            user_id: User identifier

        Returns:
            List of high priority tasks
        """
        return await self.search_tasks(
            user_id=user_id,
            priority="High",
            completed=False,
            sort_by="created_at",
            sort_order="desc"
        )

    async def count_tasks(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        priority: Optional[Literal["Low", "Medium", "High"]] = None
    ) -> int:
        """
        Count tasks matching criteria.

        Args:
            user_id: User identifier
            completed: Filter by completion status
            priority: Filter by priority level

        Returns:
            Number of matching tasks
        """
        statement = select(func.count(Task.id)).where(Task.user_id == user_id)

        if completed is not None:
            statement = statement.where(Task.completed == completed)

        if priority:
            statement = statement.where(Task.priority == priority)

        result = self.session.exec(statement).one()
        return result
