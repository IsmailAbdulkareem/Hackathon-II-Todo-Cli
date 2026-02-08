"""FastAPI route handlers for task management with advanced features."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.core.auth import get_current_user_id, validate_user_ownership
from src.core.dependencies import get_repository
from src.core.repository_interface import TaskRepository
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
    repository: TaskRepository = Depends(get_repository)
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
        repository: Task repository (injected)

    Returns:
        List of tasks (empty array if user has no tasks)

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if repository operation fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Support both parameter names for due date range
        start_date = due_date_start or due_from
        end_date = due_date_end or due_to

        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]

        # Use repository search method
        tasks = await repository.search(
            user_id=jwt_user_id,
            query=search,
            completed=completed,
            priority=priority.value if priority else None,
            tags=tag_list,
            due_from=start_date,
            due_to=end_date,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=0,
            limit=1000
        )

        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Repository operation failed"
        )


# US2: Create a new task with advanced features
@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    repository: TaskRepository = Depends(get_repository)
) -> Task:
    """
    Create a new task for a specific user with advanced features (due date, priority, tags, etc.).

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        task_data: Task creation data (title, description, due_date, priority, tags, recurrence, reminder_offset_minutes)
        repository: Task repository (injected)

    Returns:
        Created task with generated ID and timestamps

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 422 if validation fails (handled by FastAPI)
        HTTPException: 500 if repository operation fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Create task using repository
        task = await repository.create(jwt_user_id, task_data)

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

        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Repository operation failed"
        )


# US5: Toggle task completion status
@router.patch("/{user_id}/tasks/{id}/complete", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def toggle_task_completion(
    id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    repository: TaskRepository = Depends(get_repository)
) -> Task:
    """
    Toggle the completion status of a task.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        repository: Task repository (injected)

    Returns:
        Updated task with toggled completion status

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 500 if repository operation fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Get existing task
        task = await repository.get_by_id(jwt_user_id, id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Toggle completion status
        old_completed = task.completed
        update_data = TaskUpdate(completed=not task.completed)

        task = await repository.update(jwt_user_id, id, update_data)

        # Cancel reminder if task is now completed
        if task.completed and task.reminder_offset_minutes and task.reminder_offset_minutes > 0:
            try:
                await reminder_service.cancel_reminder(task.id)
            except Exception as e:
                print(f"Failed to cancel reminder for completed task {task.id}: {e}")

        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Repository operation failed"
        )


# US6: Retrieve a single task by ID
@router.get("/{user_id}/tasks/{id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def get_task_by_id(
    id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    repository: TaskRepository = Depends(get_repository)
) -> Task:
    """
    Retrieve a single task by ID for a specific user.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        repository: Task repository (injected)

    Returns:
        Task object

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 500 if repository operation fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        task = await repository.get_by_id(jwt_user_id, id)

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
            detail="Repository operation failed"
        )


# US3: Update an existing task with advanced features
@router.put("/{user_id}/tasks/{id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def update_task(
    id: str,
    task_data: TaskUpdate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    repository: TaskRepository = Depends(get_repository)
) -> Task:
    """
    Update an existing task with advanced features (title, description, due date, priority, tags, etc.).

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        task_data: Task update data (title, description, due_date, priority, tags, recurrence, reminder_offset_minutes)
        repository: Task repository (injected)

    Returns:
        Updated task

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 422 if validation fails (handled by FastAPI)
        HTTPException: 500 if repository operation fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Get existing task to check reminder/recurrence changes
        existing_task = await repository.get_by_id(jwt_user_id, id)

        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        old_due_date = existing_task.due_date
        old_reminder_offset = existing_task.reminder_offset_minutes
        old_recurrence = existing_task.recurrence

        # Update task using repository
        task = await repository.update(jwt_user_id, id, task_data)

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

        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Repository operation failed"
        )


# US4: Delete a task
@router.delete("/{user_id}/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    repository: TaskRepository = Depends(get_repository)
) -> None:
    """
    Delete a task permanently.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        id: Task identifier (UUID)
        repository: Task repository (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 500 if repository operation fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Get task to check reminder/recurrence before deletion
        task = await repository.get_by_id(jwt_user_id, id)

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

        # Delete task using repository
        result = await repository.delete(jwt_user_id, id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Repository operation failed"
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
    repository: TaskRepository = Depends(get_repository)
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
        repository: Task repository (injected)

    Returns:
        Dictionary with tasks list and pagination info

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if repository operation fails
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Calculate offset for pagination
        skip = (page - 1) * limit

        # Use repository search method
        tasks = await repository.search(
            user_id=jwt_user_id,
            query=q,
            completed=completed,
            priority=priority.value if priority else None,
            tags=tags,
            due_from=due_from,
            due_to=due_to,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )

        # Get total count for pagination
        total_count = await repository.count(jwt_user_id, completed=completed)

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
            detail="Repository operation failed"
        )
