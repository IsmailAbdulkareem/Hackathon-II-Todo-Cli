"""FastAPI route handlers for task management."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session, select

from src.core.auth import get_current_user_id, validate_user_ownership
from src.core.database import get_session
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate
from src.models.reminder import Reminder, ReminderCreate, ReminderRead

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


# US1: Retrieve all tasks for a user with filtering and sorting
@router.get("/{user_id}/tasks", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
async def get_all_tasks(
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    priority: str | None = None,
    tags: str | None = None,
    completed: bool | None = None,
    is_recurring: bool | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session)
) -> list[Task]:
    """
    Retrieve all tasks for a specific user with filtering and sorting.

    Supports filtering by:
    - priority: Filter by priority level (Low, Medium, High)
    - tags: Comma-separated tag names (OR logic - matches any tag)
    - completed: Filter by completion status (true/false)
    - is_recurring: Filter by recurring status (true/false)

    Supports sorting by:
    - created_at (default), updated_at, due_date, priority, title
    - sort_order: asc or desc (default: desc)

    Supports pagination:
    - limit: Maximum number of results (default: 100)
    - offset: Number of results to skip (default: 0)

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        priority: Filter by priority level
        tags: Comma-separated tag names
        completed: Filter by completion status
        is_recurring: Filter by recurring status
        sort_by: Sort field
        sort_order: Sort direction (asc, desc)
        limit: Maximum number of results
        offset: Number of results to skip
        session: Database session (injected)

    Returns:
        List of tasks (empty array if user has no tasks)

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if database connection fails
    """
    from src.services.search_service import SearchService

    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Parse tags from comma-separated string
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Validate priority if provided
        priority_value = None
        if priority:
            if priority not in ["Low", "Medium", "High"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Priority must be Low, Medium, or High"
                )
            priority_value = priority

        # Validate sort_order
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"

        # Use SearchService for filtering and sorting
        search_service = SearchService(session)
        tasks = await search_service.search_tasks(
            user_id=jwt_user_id,
            priority=priority_value,
            tags=tag_list,
            completed=completed,
            is_recurring=is_recurring,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        return tasks
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


# US2: Create a new task
@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    recurrence_rule_id: str | None = None,
    tag_ids: list[str] | None = None,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Create a new task for a specific user with optional recurrence rule and tags.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        task_data: Task creation data (title, description, priority, due_date, is_recurring)
        recurrence_rule_id: Optional recurrence rule ID for recurring tasks
        tag_ids: Optional list of tag IDs to attach to the task
        session: Database session (injected)

    Returns:
        Created task with generated ID and timestamps

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 400 if validation fails (due date in past, invalid tags)
        HTTPException: 422 if validation fails (handled by FastAPI)
        HTTPException: 500 if database connection fails
    """
    from src.services.task_service import TaskService

    validate_user_ownership(jwt_user_id, user_id)

    try:
        task_service = TaskService(session)

        # Get user email for reminder notifications (mock for now)
        user_email = f"{jwt_user_id}@example.com"

        task = await task_service.create_task(
            user_id=jwt_user_id,
            task_data=task_data,
            tag_ids=tag_ids,
            user_email=user_email,
            auto_create_reminders=True,
            recurrence_rule_id=recurrence_rule_id,
            parent_task_id=None
        )

        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
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
        task.completed = not task.completed
        task.updated_at = datetime.now(timezone.utc)

        session.add(task)
        session.commit()
        session.refresh(task)

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


# US3: Update an existing task
@router.put("/{user_id}/tasks/{id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def update_task(
    id: str,
    task_data: TaskUpdate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Update an existing task's title and description.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        task_data: Task update data (title, description)
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

        # Update task fields
        task.title = task_data.title
        task.description = task_data.description
        task.updated_at = datetime.now(timezone.utc)

        session.add(task)
        session.commit()
        session.refresh(task)

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

        session.delete(task)
        session.commit()

        return None
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


# US1: Add tag to task
@router.post("/{user_id}/tasks/{id}/tags/{tag_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def add_tag_to_task(
    id: str,
    tag_id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Add a tag to a task.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        tag_id: Tag identifier (UUID)
        session: Database session (injected)

    Returns:
        Updated task with tag added

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task or tag not found
        HTTPException: 409 if tag doesn't belong to user
        HTTPException: 500 if database connection fails
    """
    from src.services.task_service import TaskService

    validate_user_ownership(jwt_user_id, user_id)

    try:
        task_service = TaskService(session)
        task = await task_service.add_tag(jwt_user_id, id, tag_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add tag to task"
        )


# US1: Remove tag from task
@router.delete("/{user_id}/tasks/{id}/tags/{tag_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def remove_tag_from_task(
    id: str,
    tag_id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Remove a tag from a task.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        tag_id: Tag identifier (UUID)
        session: Database session (injected)

    Returns:
        Updated task with tag removed

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found
        HTTPException: 500 if database connection fails
    """
    from src.services.task_service import TaskService

    validate_user_ownership(jwt_user_id, user_id)

    try:
        task_service = TaskService(session)
        task = await task_service.remove_tag(jwt_user_id, id, tag_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return task
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove tag from task"
        )


# US1: Get tags for a task
@router.get("/{user_id}/tasks/{id}/tags", response_model=list, status_code=status.HTTP_200_OK)
async def get_task_tags(
    id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> list:
    """
    Get all tags for a task.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        session: Database session (injected)

    Returns:
        List of tags

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found
        HTTPException: 500 if database connection fails
    """
    from src.services.task_service import TaskService

    validate_user_ownership(jwt_user_id, user_id)

    try:
        task_service = TaskService(session)
        tags = await task_service.get_task_tags(jwt_user_id, id)
        return tags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task tags"
        )


# US1: Set task priority
@router.patch("/{user_id}/tasks/{id}/priority", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def set_task_priority(
    id: str,
    priority: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Set task priority.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        priority: Priority level (Low, Medium, High)
        session: Database session (injected)

    Returns:
        Updated task with new priority

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found
        HTTPException: 422 if invalid priority value
        HTTPException: 500 if database connection fails
    """
    from src.services.task_service import TaskService

    validate_user_ownership(jwt_user_id, user_id)

    # Validate priority value
    if priority not in ["Low", "Medium", "High"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Priority must be Low, Medium, or High"
        )

    try:
        task_service = TaskService(session)
        task = await task_service.set_priority(jwt_user_id, id, priority)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return task
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set task priority"
        )


# US2: Create reminder for task
@router.post("/{user_id}/tasks/{id}/reminders", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
async def create_task_reminder(
    id: str,
    reminder_data: ReminderCreate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Reminder:
    """
    Create a new reminder for a task.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        reminder_data: Reminder creation data (scheduled_time, reminder_type)
        session: Database session (injected)

    Returns:
        Created reminder with scheduled job

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found
        HTTPException: 400 if scheduled time is in the past
        HTTPException: 500 if database connection fails
    """
    from src.services.reminder_service import ReminderService

    validate_user_ownership(jwt_user_id, user_id)

    try:
        reminder_service = ReminderService(session)

        # Get user email from JWT or use placeholder
        # In production, this should come from user profile
        user_email = f"{jwt_user_id}@example.com"

        reminder = await reminder_service.create_reminder(
            user_id=jwt_user_id,
            task_id=id,
            reminder_data=reminder_data,
            user_email=user_email
        )

        return reminder
    except ValueError as e:
        # Handle validation errors (task not found, invalid scheduled time)
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reminder"
        )


# US2: Delete reminder
@router.delete("/{user_id}/tasks/{id}/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_reminder(
    id: str,
    reminder_id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a reminder for a task.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        reminder_id: Reminder identifier (UUID)
        session: Database session (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if reminder not found
        HTTPException: 500 if database connection fails
    """
    from src.services.reminder_service import ReminderService

    validate_user_ownership(jwt_user_id, user_id)

    try:
        reminder_service = ReminderService(session)

        deleted = await reminder_service.delete_reminder(
            user_id=jwt_user_id,
            reminder_id=reminder_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete reminder"
        )


# US2: Get all reminders for a task
@router.get("/{user_id}/tasks/{id}/reminders", response_model=list[ReminderRead], status_code=status.HTTP_200_OK)
async def get_task_reminders(
    id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> list[Reminder]:
    """
    Get all reminders for a task.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        session: Database session (injected)

    Returns:
        List of reminders for the task (empty array if no reminders)

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if database connection fails
    """
    from src.services.reminder_service import ReminderService

    validate_user_ownership(jwt_user_id, user_id)

    try:
        reminder_service = ReminderService(session)

        reminders = await reminder_service.get_task_reminders(
            user_id=jwt_user_id,
            task_id=id
        )

        return reminders
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task reminders"
        )


# US3: Update recurring task series
@router.put("/{user_id}/tasks/{id}/series", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
async def update_recurring_series(
    id: str,
    task_data: TaskUpdate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> list[Task]:
    """
    Update all tasks in a recurring series.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (any task in the series)
        task_data: Task update data to apply to all tasks in series
        session: Database session (injected)

    Returns:
        List of updated tasks in the series

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found
        HTTPException: 400 if task is not part of a recurring series
        HTTPException: 500 if database connection fails
    """
    from src.services.task_service import TaskService

    validate_user_ownership(jwt_user_id, user_id)

    try:
        task_service = TaskService(session)
        updated_tasks = await task_service.update_recurring_series(
            user_id=jwt_user_id,
            task_id=id,
            task_data=task_data
        )

        if not updated_tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return updated_tasks
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recurring series"
        )


# US3: Delete recurring task series
@router.delete("/{user_id}/tasks/{id}/series", status_code=status.HTTP_200_OK)
async def delete_recurring_series(
    id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> dict:
    """
    Delete all tasks in a recurring series.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (any task in the series)
        session: Database session (injected)

    Returns:
        Dictionary with deleted count

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found
        HTTPException: 400 if task is not part of a recurring series
        HTTPException: 500 if database connection fails
    """
    from src.services.task_service import TaskService

    validate_user_ownership(jwt_user_id, user_id)

    try:
        task_service = TaskService(session)
        deleted_count = await task_service.delete_recurring_series(
            user_id=jwt_user_id,
            task_id=id
        )

        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return {"deleted_count": deleted_count, "message": f"Deleted {deleted_count} tasks in recurring series"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recurring series"
        )

