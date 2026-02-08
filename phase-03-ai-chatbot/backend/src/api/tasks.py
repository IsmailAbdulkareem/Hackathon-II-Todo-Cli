"""FastAPI route handlers for task management with advanced features."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session, select
import json

from src.core.auth import get_current_user_id, validate_user_ownership
from src.core.database import get_session
from src.core.event_publisher import event_publisher
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate, PriorityEnum, RecurrenceEnum
from src.services.reminder_service import reminder_service
from src.services.recurring_service import recurring_service

# Create router for task endpoints
router = APIRouter(prefix="/api", tags=["tasks"])


def validate_user_id(
    user_id: str = Path(..., max_length=255, description="User identifier")
) -> str:
    """
    Validate and sanitize user_id path parameter.

    Args:
        user_id: User identifier from path parameter

    Returns:
        Validated user_id

    Raises:
        HTTPException: 400 if user_id is invalid
    """
    if not user_id or not user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID cannot be empty"
        )

    # Strip whitespace and validate length
    user_id = user_id.strip()

    if len(user_id) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID must be at most 255 characters"
        )

    return user_id


# US1: Retrieve all tasks for a user with optional filtering
@router.get("/{user_id}/tasks", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
async def get_all_tasks(
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    priority: Optional[PriorityEnum] = Query(None, description="Filter by priority level"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    tags: Optional[str] = Query(None, description="Filter by tag (comma-separated for multiple)"),
    search: Optional[str] = Query(None, description="Search text in title, description, and tags"),
    due_from: Optional[datetime] = Query(None, description="Filter tasks with due date on or after this date"),
    due_to: Optional[datetime] = Query(None, description="Filter tasks with due date on or before this date"),
    due_date_start: Optional[datetime] = Query(None, description="Alias for due_from"),
    due_date_end: Optional[datetime] = Query(None, description="Alias for due_to"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    session: Session = Depends(get_session)
) -> list[Task]:
    """
    Retrieve all tasks for a specific user with optional filtering and sorting.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        priority: Filter by priority level
        completed: Filter by completion status
        tags: Filter by tag (comma-separated for multiple)
        search: Search text in title, description, and tags
        due_from: Filter tasks with due date on or after this date
        due_to: Filter tasks with due date on or before this date
        due_date_start: Alias for due_from
        due_date_end: Alias for due_to
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        session: Database session (injected)

    Returns:
        List of tasks (empty array if user has no tasks)

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if database connection fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Use jwt_user_id for database query (not url user_id)
        statement = select(Task).where(Task.user_id == jwt_user_id)

        # Apply filters
        if priority is not None:
            statement = statement.where(Task.priority == priority.value)
        if completed is not None:
            statement = statement.where(Task.completed == completed)

        # Support both parameter names for due date range
        start_date = due_date_start or due_from
        end_date = due_date_end or due_to

        if start_date is not None:
            statement = statement.where(Task.due_date >= start_date)
        if end_date is not None:
            statement = statement.where(Task.due_date <= end_date)

        # Execute query to get all matching tasks
        tasks = session.exec(statement).all()

        # Apply tag filtering (in-memory since tags are JSON)
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            tasks = [task for task in tasks if task.tags and any(tag in task.tags for tag in tag_list)]

        # Apply text search (in-memory)
        if search:
            search_lower = search.lower()
            tasks = [
                task for task in tasks
                if (task.title and search_lower in task.title.lower()) or
                   (task.description and search_lower in task.description.lower()) or
                   (task.tags and any(search_lower in tag.lower() for tag in task.tags))
            ]

        # Apply sorting
        if sort_by == "priority":
            priority_order = {"high": 3, "medium": 2, "low": 1}
            tasks = sorted(tasks, key=lambda t: priority_order.get(t.priority.value, 0), reverse=(sort_order == "desc"))
        elif sort_by == "due_date":
            tasks = sorted(tasks, key=lambda t: t.due_date or datetime.max.replace(tzinfo=timezone.utc), reverse=(sort_order == "desc"))
        elif sort_by == "updated_at":
            tasks = sorted(tasks, key=lambda t: t.updated_at, reverse=(sort_order == "desc"))
        else:  # Default to created_at
            tasks = sorted(tasks, key=lambda t: t.created_at, reverse=(sort_order == "desc"))

        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


# US2: Create a new task with advanced features
@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Create a new task for a specific user with advanced features (due date, priority, tags, etc.).

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        task_data: Task creation data (title, description, due_date, priority, tags, recurrence, reminder_offset_minutes)
        session: Database session (injected)

    Returns:
        Created task with generated ID and timestamps

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 422 if validation fails (handled by FastAPI)
        HTTPException: 500 if database connection fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Create new task with jwt_user_id (not url user_id)
        task = Task(
            user_id=jwt_user_id,
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
            priority=task_data.priority,
            tags=task_data.tags,
            recurrence=task_data.recurrence,
            reminder_offset_minutes=task_data.reminder_offset_minutes,
            completed=False  # Default value
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        # Schedule reminder if configured
        if task.reminder_offset_minutes and task.reminder_offset_minutes > 0 and task.due_date:
            try:
                reminder_time = reminder_service.calculate_reminder_time(
                    task.due_date,
                    task.reminder_offset_minutes
                )
                await reminder_service.schedule_reminder(
                    task.id,
                    jwt_user_id,
                    reminder_time
                )
            except Exception as e:
                # Log error but don't fail task creation
                print(f"Failed to schedule reminder for task {task.id}: {e}")

        # Schedule recurring task generation if configured
        if task.recurrence and task.recurrence != RecurrenceEnum.NONE and task.due_date:
            try:
                await recurring_service.schedule_recurring_task_generation(
                    task.id,
                    jwt_user_id,
                    task.recurrence.value,
                    task.due_date
                )
            except Exception as e:
                # Log error but don't fail task creation
                print(f"Failed to schedule recurring task for task {task.id}: {e}")

        # Publish TASK_CREATED event
        try:
            await event_publisher.publish(
                topic="task-events",
                event_type="TASK_CREATED",
                task_id=task.id,
                payload={
                    "user_id": jwt_user_id,
                    "title": task.title,
                    "priority": task.priority.value if task.priority else None,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence": task.recurrence.value if task.recurrence else None
                }
            )
        except Exception as e:
            # Log error but don't fail task creation
            print(f"Failed to publish TASK_CREATED event for task {task.id}: {e}")

        return task
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


# US5: Toggle task completion status
@router.patch("/{user_id}/tasks/{id}/complete", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def toggle_task_completion(
    id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Toggle the completion status of a task.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        session: Database session (injected)

    Returns:
        Updated task with toggled completion status

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 500 if database connection fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Use jwt_user_id for database query
        statement = select(Task).where(Task.id == id, Task.user_id == jwt_user_id)
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Toggle completion status
        old_completed = task.completed
        task.completed = not task.completed
        task.updated_at = datetime.now(timezone.utc)

        session.add(task)
        session.commit()
        session.refresh(task)

        # Cancel reminder if task is now completed
        if task.completed and task.reminder_offset_minutes and task.reminder_offset_minutes > 0:
            try:
                await reminder_service.cancel_reminder(task.id)
            except Exception as e:
                print(f"Failed to cancel reminder for completed task {task.id}: {e}")

        # Publish TASK_COMPLETED event if task was marked as completed
        if task.completed and not old_completed:
            try:
                await event_publisher.publish(
                    topic="task-events",
                    event_type="TASK_COMPLETED",
                    task_id=task.id,
                    payload={
                        "user_id": jwt_user_id,
                        "title": task.title,
                        "completed_at": task.updated_at.isoformat()
                    }
                )
            except Exception as e:
                print(f"Failed to publish TASK_COMPLETED event for task {task.id}: {e}")

        return task
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


# US6: Retrieve a single task by ID
@router.get("/{user_id}/tasks/{id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def get_task_by_id(
    id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Retrieve a single task by ID for a specific user.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        session: Database session (injected)

    Returns:
        Task object

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 500 if database connection fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Use jwt_user_id for database query
        statement = select(Task).where(Task.id == id, Task.user_id == jwt_user_id)
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


# US3: Update an existing task with advanced features
@router.put("/{user_id}/tasks/{id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def update_task(
    id: str,
    task_data: TaskUpdate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Update an existing task with advanced features (title, description, due date, priority, tags, etc.).

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        task_data: Task update data (title, description, due_date, priority, tags, recurrence, reminder_offset_minutes)
        session: Database session (injected)

    Returns:
        Updated task

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 422 if validation fails (handled by FastAPI)
        HTTPException: 500 if database connection fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Use jwt_user_id for database query
        statement = select(Task).where(Task.id == id, Task.user_id == jwt_user_id)
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Track changes for event publishing
        changes = {}
        old_due_date = task.due_date
        old_reminder_offset = task.reminder_offset_minutes
        old_recurrence = task.recurrence

        # Update task fields
        if task_data.title is not None:
            changes["title"] = {"old": task.title, "new": task_data.title}
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.due_date is not None:
            changes["due_date"] = {"old": old_due_date, "new": task_data.due_date}
            task.due_date = task_data.due_date
        if task_data.priority is not None:
            changes["priority"] = {"old": task.priority, "new": task_data.priority}
            task.priority = task_data.priority
        if task_data.tags is not None:
            task.tags = task_data.tags
        if task_data.recurrence is not None:
            changes["recurrence"] = {"old": old_recurrence, "new": task_data.recurrence}
            task.recurrence = task_data.recurrence
        if task_data.reminder_offset_minutes is not None:
            changes["reminder_offset"] = {"old": old_reminder_offset, "new": task_data.reminder_offset_minutes}
            task.reminder_offset_minutes = task_data.reminder_offset_minutes

        task.updated_at = datetime.now(timezone.utc)

        session.add(task)
        session.commit()
        session.refresh(task)

        # Handle reminder updates
        if task.due_date and task.reminder_offset_minutes and task.reminder_offset_minutes > 0:
            # Cancel old reminder and schedule new one
            try:
                await reminder_service.cancel_reminder(task.id)
                reminder_time = reminder_service.calculate_reminder_time(
                    task.due_date,
                    task.reminder_offset_minutes
                )
                await reminder_service.schedule_reminder(
                    task.id,
                    jwt_user_id,
                    reminder_time
                )
            except Exception as e:
                print(f"Failed to update reminder for task {task.id}: {e}")
        elif old_reminder_offset and old_reminder_offset > 0:
            # Reminder was removed, cancel it
            try:
                await reminder_service.cancel_reminder(task.id)
            except Exception as e:
                print(f"Failed to cancel reminder for task {task.id}: {e}")

        # Handle recurring task updates
        if task.recurrence and task.recurrence != RecurrenceEnum.NONE and task.due_date:
            # Cancel old job and schedule new one
            try:
                await recurring_service.cancel_recurring_job(task.id)
                await recurring_service.schedule_recurring_task_generation(
                    task.id,
                    jwt_user_id,
                    task.recurrence.value,
                    task.due_date
                )
            except Exception as e:
                print(f"Failed to update recurring task for task {task.id}: {e}")
        elif old_recurrence and old_recurrence != RecurrenceEnum.NONE:
            # Recurrence was removed, cancel job
            try:
                await recurring_service.cancel_recurring_job(task.id)
            except Exception as e:
                print(f"Failed to cancel recurring job for task {task.id}: {e}")

        # Publish TASK_UPDATED event
        try:
            await event_publisher.publish(
                topic="task-events",
                event_type="TASK_UPDATED",
                task_id=task.id,
                payload={
                    "user_id": jwt_user_id,
                    "changes": changes
                }
            )
        except Exception as e:
            print(f"Failed to publish TASK_UPDATED event for task {task.id}: {e}")

        return task
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


# US4: Delete a task
@router.delete("/{user_id}/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a task permanently.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        session: Database session (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 500 if database connection fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Use jwt_user_id for database query
        statement = select(Task).where(Task.id == id, Task.user_id == jwt_user_id)
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Cancel reminder if exists
        if task.reminder_offset_minutes and task.reminder_offset_minutes > 0:
            try:
                await reminder_service.cancel_reminder(task.id)
            except Exception as e:
                print(f"Failed to cancel reminder for task {task.id}: {e}")

        # Cancel recurring job if exists
        if task.recurrence and task.recurrence != RecurrenceEnum.NONE:
            try:
                await recurring_service.cancel_recurring_job(task.id)
            except Exception as e:
                print(f"Failed to cancel recurring job for task {task.id}: {e}")

        session.delete(task)
        session.commit()

        # Publish TASK_DELETED event
        try:
            await event_publisher.publish(
                topic="task-events",
                event_type="TASK_DELETED",
                task_id=task.id,
                payload={
                    "user_id": jwt_user_id,
                    "title": task.title
                }
            )
        except Exception as e:
            print(f"Failed to publish TASK_DELETED event for task {task.id}: {e}")

        return None
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


# US5: Search and filter tasks with advanced criteria
@router.get("/{user_id}/tasks/search", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def search_tasks(
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    q: Optional[str] = Query(None, description="Text search in title or description"),
    priority: Optional[PriorityEnum] = Query(None, description="Filter by priority level"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags (multiple allowed)"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    due_from: Optional[datetime] = Query(None, description="Filter tasks with due date on or after this date"),
    due_to: Optional[datetime] = Query(None, description="Filter tasks with due date on or before this date"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Advanced search and filter tasks with pagination and sorting.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        q: Text search in title or description
        priority: Filter by priority level
        tags: Filter by tags (multiple allowed)
        completed: Filter by completion status
        due_from: Filter tasks with due date on or after this date
        due_to: Filter tasks with due date on or before this date
        page: Page number for pagination
        limit: Number of items per page
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        session: Database session (injected)

    Returns:
        Dictionary with tasks list and pagination info

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if database connection fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Use jwt_user_id for database query (not url user_id)
        statement = select(Task).where(Task.user_id == jwt_user_id)

        # Apply text search
        if q:
            search_term = f"%{q}%"
            statement = statement.where(
                (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
            )

        # Apply filters
        if priority is not None:
            statement = statement.where(Task.priority == priority.value)
        if tags is not None and len(tags) > 0:
            # Filter by tags - need to match any of the provided tags
            for tag in tags:
                statement = statement.where(Task.tags.op('@>')([tag.lower()]))
        if completed is not None:
            statement = statement.where(Task.completed == completed)
        if due_from is not None:
            statement = statement.where(Task.due_date >= due_from)
        if due_to is not None:
            statement = statement.where(Task.due_date <= due_to)

        # Count total for pagination
        count_statement = select(Task.id).where(Task.user_id == jwt_user_id)
        if q:
            count_statement = count_statement.where(
                (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
            )
        if priority is not None:
            count_statement = count_statement.where(Task.priority == priority.value)
        if tags is not None and len(tags) > 0:
            for tag in tags:
                count_statement = count_statement.where(Task.tags.op('@>')([tag.lower()]))
        if completed is not None:
            count_statement = count_statement.where(Task.completed == completed)
        if due_from is not None:
            count_statement = count_statement.where(Task.due_date >= due_from)
        if due_to is not None:
            count_statement = count_statement.where(Task.due_date <= due_to)

        total_count = session.exec(count_statement).count()

        # Apply sorting
        if sort_by == "priority":
            if sort_order == "asc":
                statement = statement.order_by(Task.priority.asc())
            else:
                statement = statement.order_by(Task.priority.desc())
        elif sort_by == "due_date":
            if sort_order == "asc":
                statement = statement.order_by(Task.due_date.asc())
            else:
                statement = statement.order_by(Task.due_date.desc())
        elif sort_by == "updated_at":
            if sort_order == "asc":
                statement = statement.order_by(Task.updated_at.asc())
            else:
                statement = statement.order_by(Task.updated_at.desc())
        else:  # Default to created_at
            if sort_order == "asc":
                statement = statement.order_by(Task.created_at.asc())
            else:
                statement = statement.order_by(Task.created_at.desc())

        # Apply pagination
        offset = (page - 1) * limit
        statement = statement.offset(offset).limit(limit)

        tasks = session.exec(statement).all()

        return {
            "items": tasks,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "total_pages": (total_count + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )
