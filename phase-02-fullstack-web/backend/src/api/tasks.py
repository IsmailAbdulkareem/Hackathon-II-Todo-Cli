"""FastAPI route handlers for task management."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session, select

from src.core.database import get_session
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate

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


# US1: Retrieve all tasks for a user
@router.get("/{user_id}/tasks", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
async def get_all_tasks(
    user_id: str = Depends(validate_user_id),
    session: Session = Depends(get_session)
) -> list[Task]:
    """
    Retrieve all tasks for a specific user.

    Args:
        user_id: User identifier
        session: Database session (injected)

    Returns:
        List of tasks (empty array if user has no tasks)

    Raises:
        HTTPException: 500 if database connection fails
    """
    try:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


# US2: Create a new task
@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(validate_user_id),
    session: Session = Depends(get_session)
) -> Task:
    """
    Create a new task for a specific user.

    Args:
        user_id: User identifier
        task_data: Task creation data (title, description)
        session: Database session (injected)

    Returns:
        Created task with generated ID and timestamps

    Raises:
        HTTPException: 422 if validation fails (handled by FastAPI)
        HTTPException: 500 if database connection fails
    """
    try:
        # Create new task with user_id from path parameter
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            completed=False  # Default value
        )

        session.add(task)
        session.commit()
        session.refresh(task)

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
    session: Session = Depends(get_session)
) -> Task:
    """
    Toggle the completion status of a task.

    Args:
        user_id: User identifier
        id: Task identifier (UUID)
        session: Database session (injected)

    Returns:
        Updated task with toggled completion status

    Raises:
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 500 if database connection fails
    """
    try:
        statement = select(Task).where(Task.id == id, Task.user_id == user_id)
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
    session: Session = Depends(get_session)
) -> Task:
    """
    Retrieve a single task by ID for a specific user.

    Args:
        user_id: User identifier
        id: Task identifier (UUID)
        session: Database session (injected)

    Returns:
        Task object

    Raises:
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 500 if database connection fails
    """
    try:
        statement = select(Task).where(Task.id == id, Task.user_id == user_id)
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
    session: Session = Depends(get_session)
) -> Task:
    """
    Update an existing task's title and description.

    Args:
        user_id: User identifier
        id: Task identifier (UUID)
        task_data: Task update data (title, description)
        session: Database session (injected)

    Returns:
        Updated task

    Raises:
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 422 if validation fails (handled by FastAPI)
        HTTPException: 500 if database connection fails
    """
    try:
        statement = select(Task).where(Task.id == id, Task.user_id == user_id)
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
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a task permanently.

    Args:
        user_id: User identifier
        id: Task identifier (UUID)
        session: Database session (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 404 if task not found or belongs to different user
        HTTPException: 500 if database connection fails
    """
    try:
        statement = select(Task).where(Task.id == id, Task.user_id == user_id)
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
