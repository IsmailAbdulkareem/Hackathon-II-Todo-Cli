"""
Fallback Task Repository (T098)

This module implements a fallback repository that uses the existing
database when Dapr is not available, providing graceful degradation.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select, or_, and_

from src.core.repository_interface import (
    TaskRepository,
    RepositoryError,
    TaskNotFoundError
)
from src.core.database import engine
from src.models.task import Task, TaskCreate, TaskUpdate


class FallbackTaskRepository(TaskRepository):
    """
    Fallback implementation using SQLModel/PostgreSQL.

    This repository is used when Dapr is not available,
    ensuring the application continues to function.
    """

    async def create(self, user_id: str, task_data: TaskCreate) -> Task:
        """Create a new task in the database"""
        try:
            with Session(engine) as session:
                # Create task
                task = Task(
                    user_id=user_id,
                    title=task_data.title,
                    description=task_data.description,
                    due_date=task_data.due_date,
                    priority=task_data.priority,
                    tags=task_data.tags or [],
                    recurrence=task_data.recurrence,
                    reminder_offset_minutes=task_data.reminder_offset_minutes or 0
                )

                session.add(task)
                session.commit()
                session.refresh(task)

                return task

        except Exception as e:
            raise RepositoryError(f"Failed to create task: {e}")

    async def get_by_id(self, user_id: str, task_id: str) -> Optional[Task]:
        """Get a task by ID from the database"""
        try:
            with Session(engine) as session:
                statement = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
                task = session.exec(statement).first()
                return task

        except Exception as e:
            raise RepositoryError(f"Failed to get task: {e}")

    async def get_all(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get all tasks for a user from the database"""
        try:
            with Session(engine) as session:
                statement = (
                    select(Task)
                    .where(Task.user_id == user_id)
                    .offset(skip)
                    .limit(limit)
                )
                tasks = session.exec(statement).all()
                return list(tasks)

        except Exception as e:
            raise RepositoryError(f"Failed to get tasks: {e}")

    async def update(
        self,
        user_id: str,
        task_id: str,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """Update a task in the database"""
        try:
            with Session(engine) as session:
                # Get existing task
                statement = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
                task = session.exec(statement).first()

                if not task:
                    return None

                # Update fields
                update_dict = task_data.dict(exclude_unset=True)
                for field, value in update_dict.items():
                    if value is not None:
                        setattr(task, field, value)

                task.updated_at = datetime.utcnow()

                session.add(task)
                session.commit()
                session.refresh(task)

                return task

        except Exception as e:
            raise RepositoryError(f"Failed to update task: {e}")

    async def delete(self, user_id: str, task_id: str) -> bool:
        """Delete a task from the database"""
        try:
            with Session(engine) as session:
                statement = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
                task = session.exec(statement).first()

                if not task:
                    return False

                session.delete(task)
                session.commit()

                return True

        except Exception as e:
            raise RepositoryError(f"Failed to delete task: {e}")

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
        """Search tasks in the database"""
        try:
            with Session(engine) as session:
                statement = select(Task).where(Task.user_id == user_id)

                # Apply filters
                if query:
                    statement = statement.where(
                        or_(
                            Task.title.ilike(f"%{query}%"),
                            Task.description.ilike(f"%{query}%")
                        )
                    )

                if completed is not None:
                    statement = statement.where(Task.completed == completed)

                if priority:
                    statement = statement.where(Task.priority == priority)

                if tags:
                    # Filter by tags (at least one tag matches)
                    tag_filters = [Task.tags.contains([tag]) for tag in tags]
                    statement = statement.where(or_(*tag_filters))

                if due_from:
                    statement = statement.where(Task.due_date >= due_from)

                if due_to:
                    statement = statement.where(Task.due_date <= due_to)

                # Sort
                sort_column = getattr(Task, sort_by)
                if sort_order == "desc":
                    statement = statement.order_by(sort_column.desc())
                else:
                    statement = statement.order_by(sort_column.asc())

                # Paginate
                statement = statement.offset(skip).limit(limit)

                tasks = session.exec(statement).all()
                return list(tasks)

        except Exception as e:
            raise RepositoryError(f"Failed to search tasks: {e}")

    async def count(
        self,
        user_id: str,
        completed: Optional[bool] = None
    ) -> int:
        """Count tasks for a user in the database"""
        try:
            with Session(engine) as session:
                statement = select(Task).where(Task.user_id == user_id)

                if completed is not None:
                    statement = statement.where(Task.completed == completed)

                tasks = session.exec(statement).all()
                return len(list(tasks))

        except Exception as e:
            raise RepositoryError(f"Failed to count tasks: {e}")
