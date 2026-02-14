"""
FastAPI route handlers for task search and filtering.

Provides advanced search capabilities including full-text search,
multi-criteria filtering, and flexible sorting.
"""

import logging
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from src.core.auth import get_current_user_id, validate_user_ownership
from src.core.database import get_session
from src.models.task import Task, TaskRead
from src.services.search_service import SearchService

logger = logging.getLogger(__name__)

# Create router for search endpoints
router = APIRouter(prefix="/api", tags=["search"])


@router.get(
    "/{user_id}/search",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK
)
async def search_tasks(
    user_id: str,
    jwt_user_id: str = Depends(get_current_user_id),
    query: Optional[str] = Query(None, description="Full-text search query"),
    priority: Optional[Literal["Low", "Medium", "High"]] = Query(
        None,
        description="Filter by priority level"
    ),
    tags: Optional[str] = Query(
        None,
        description="Comma-separated tag names (OR logic)"
    ),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    is_recurring: Optional[bool] = Query(None, description="Filter by recurring status"),
    has_due_date: Optional[bool] = Query(
        None,
        description="Filter tasks with/without due dates"
    ),
    overdue: Optional[bool] = Query(None, description="Filter overdue tasks"),
    sort_by: str = Query(
        "created_at",
        description="Sort field (created_at, updated_at, due_date, priority, title)"
    ),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort direction"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    session: Session = Depends(get_session)
) -> List[Task]:
    """
    Search and filter tasks with multiple criteria.

    Supports:
    - Full-text search across title and description
    - Priority filtering (Low, Medium, High)
    - Tag filtering (OR logic - matches any tag)
    - Completion status filtering
    - Recurring task filtering
    - Due date filtering (has due date, overdue)
    - Flexible sorting (created_at, updated_at, due_date, priority, title)
    - Pagination (limit, offset)

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        query: Full-text search query (searches title and description)
        priority: Filter by priority level
        tags: Comma-separated tag names (OR logic)
        completed: Filter by completion status
        is_recurring: Filter by recurring status
        has_due_date: Filter tasks with/without due dates
        overdue: Filter overdue tasks
        sort_by: Sort field
        sort_order: Sort direction (asc, desc)
        limit: Maximum number of results (1-100)
        offset: Number of results to skip for pagination
        session: Database session (injected)

    Returns:
        List of matching tasks

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if database connection fails

    Examples:
        - Search for "meeting": GET /api/{user_id}/search?query=meeting
        - High priority incomplete tasks: GET /api/{user_id}/search?priority=High&completed=false
        - Tasks with "work" or "urgent" tags: GET /api/{user_id}/search?tags=work,urgent
        - Overdue tasks: GET /api/{user_id}/search?overdue=true
        - Sort by due date: GET /api/{user_id}/search?sort_by=due_date&sort_order=asc
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Parse tags from comma-separated string
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Execute search
        search_service = SearchService(session)
        results = await search_service.search_tasks(
            user_id=jwt_user_id,
            query=query,
            priority=priority,
            tags=tag_list,
            completed=completed,
            is_recurring=is_recurring,
            has_due_date=has_due_date,
            overdue=overdue,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )

        return results

    except Exception as e:
        logger.error(f"Search failed for user {jwt_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed"
        )


@router.get(
    "/{user_id}/search/overdue",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK
)
async def get_overdue_tasks(
    user_id: str,
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> List[Task]:
    """
    Get all overdue incomplete tasks.

    Returns tasks with due dates in the past that are not completed,
    sorted by due date (oldest first).

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session (injected)

    Returns:
        List of overdue tasks

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        search_service = SearchService(session)
        results = await search_service.get_overdue_tasks(jwt_user_id)
        return results

    except Exception as e:
        logger.error(f"Failed to get overdue tasks for user {jwt_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve overdue tasks"
        )


@router.get(
    "/{user_id}/search/due-today",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK
)
async def get_due_today_tasks(
    user_id: str,
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> List[Task]:
    """
    Get all tasks due today.

    Returns incomplete tasks with due dates within today (UTC timezone),
    sorted by due date (earliest first).

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session (injected)

    Returns:
        List of tasks due today

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        search_service = SearchService(session)
        results = await search_service.get_due_today_tasks(jwt_user_id)
        return results

    except Exception as e:
        logger.error(f"Failed to get due today tasks for user {jwt_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve due today tasks"
        )


@router.get(
    "/{user_id}/search/high-priority",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK
)
async def get_high_priority_tasks(
    user_id: str,
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> List[Task]:
    """
    Get all high priority incomplete tasks.

    Returns incomplete tasks with priority set to "High",
    sorted by creation date (newest first).

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session (injected)

    Returns:
        List of high priority tasks

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        search_service = SearchService(session)
        results = await search_service.get_high_priority_tasks(jwt_user_id)
        return results

    except Exception as e:
        logger.error(f"Failed to get high priority tasks for user {jwt_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve high priority tasks"
        )


@router.get(
    "/{user_id}/search/count",
    response_model=dict,
    status_code=status.HTTP_200_OK
)
async def count_tasks(
    user_id: str,
    jwt_user_id: str = Depends(get_current_user_id),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[Literal["Low", "Medium", "High"]] = Query(
        None,
        description="Filter by priority level"
    ),
    session: Session = Depends(get_session)
) -> dict:
    """
    Count tasks matching criteria.

    Useful for dashboard statistics and UI indicators.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        completed: Filter by completion status
        priority: Filter by priority level
        session: Database session (injected)

    Returns:
        Dictionary with count: {"count": 42}

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 500 if database connection fails

    Examples:
        - Total tasks: GET /api/{user_id}/search/count
        - Incomplete tasks: GET /api/{user_id}/search/count?completed=false
        - High priority tasks: GET /api/{user_id}/search/count?priority=High
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        search_service = SearchService(session)
        count = await search_service.count_tasks(
            user_id=jwt_user_id,
            completed=completed,
            priority=priority
        )

        return {"count": count}

    except Exception as e:
        logger.error(f"Failed to count tasks for user {jwt_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count tasks"
        )
