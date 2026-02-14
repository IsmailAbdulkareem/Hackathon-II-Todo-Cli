"""
FastAPI route handlers for tag management.

Provides CRUD operations for tags including autocomplete functionality.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from src.core.auth import get_current_user_id, validate_user_ownership
from src.core.database import get_session
from src.models.tag import Tag, TagCreate, TagRead, TagUpdate
from src.services.tag_service import TagService

logger = logging.getLogger(__name__)

# Create router for tag endpoints
router = APIRouter(prefix="/api", tags=["tags"])


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

    user_id = user_id.strip()

    if len(user_id) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID must be at most 255 characters"
        )

    return user_id


@router.get(
    "/{user_id}/tags",
    response_model=List[TagRead],
    status_code=status.HTTP_200_OK
)
async def get_all_tags(
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    sort_by: str = Query("name", description="Sort field (name, usage_count, created_at)"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of tags"),
    session: Session = Depends(get_session)
) -> List[Tag]:
    """
    Retrieve all tags for a user.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        sort_by: Sort field (name, usage_count, created_at)
        limit: Maximum number of tags to return
        session: Database session (injected)

    Returns:
        List of tags (empty array if user has no tags)

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tags
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        tag_service = TagService(session)
        tags = await tag_service.get_all_tags(
            user_id=jwt_user_id,
            sort_by=sort_by,
            limit=limit
        )
        return tags
    except Exception as e:
        logger.error(f"Failed to get tags for user {jwt_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tags"
        )


@router.get(
    "/{user_id}/tags/autocomplete",
    response_model=List[TagRead],
    status_code=status.HTTP_200_OK
)
async def autocomplete_tags(
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    query: str = Query("", description="Partial tag name to search"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    session: Session = Depends(get_session)
) -> List[Tag]:
    """
    Autocomplete tag names based on partial query.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        query: Partial tag name to search
        limit: Maximum number of suggestions (default: 10)
        session: Database session (injected)

    Returns:
        List of matching tags sorted by usage count

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tags
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        tag_service = TagService(session)
        tags = await tag_service.autocomplete_tags(
            user_id=jwt_user_id,
            query=query,
            limit=limit
        )
        return tags
    except Exception as e:
        logger.error(f"Failed to autocomplete tags for user {jwt_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to autocomplete tags"
        )


@router.get(
    "/{user_id}/tags/{tag_id}",
    response_model=TagRead,
    status_code=status.HTTP_200_OK
)
async def get_tag_by_id(
    tag_id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Tag:
    """
    Retrieve a single tag by ID.

    Args:
        tag_id: Tag identifier
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session (injected)

    Returns:
        Tag object

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tags
        HTTPException: 404 if tag not found
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        tag_service = TagService(session)
        tag = await tag_service.get_tag_by_id(jwt_user_id, tag_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        return tag
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tag {tag_id} for user {jwt_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tag"
        )


@router.post(
    "/{user_id}/tags",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED
)
async def create_tag(
    tag_data: TagCreate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Tag:
    """
    Create a new tag.

    Args:
        tag_data: Tag creation data (name, color)
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session (injected)

    Returns:
        Created tag with generated ID

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tags
        HTTPException: 409 if tag name already exists (case-insensitive)
        HTTPException: 422 if validation fails
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        tag_service = TagService(session)
        tag = await tag_service.create_tag(jwt_user_id, tag_data)
        return tag
    except ValueError as e:
        # Tag name already exists
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create tag for user {jwt_user_id}: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tag"
        )


@router.put(
    "/{user_id}/tags/{tag_id}",
    response_model=TagRead,
    status_code=status.HTTP_200_OK
)
async def update_tag(
    tag_id: str,
    tag_data: TagUpdate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> Tag:
    """
    Update an existing tag.

    Args:
        tag_id: Tag identifier
        tag_data: Tag update data (name, color)
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session (injected)

    Returns:
        Updated tag

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tags
        HTTPException: 404 if tag not found
        HTTPException: 409 if new name conflicts with existing tag
        HTTPException: 422 if validation fails
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        tag_service = TagService(session)
        tag = await tag_service.update_tag(jwt_user_id, tag_id, tag_data)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        return tag
    except ValueError as e:
        # Tag name conflict
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update tag {tag_id} for user {jwt_user_id}: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tag"
        )


@router.delete(
    "/{user_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_tag(
    tag_id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a tag permanently.

    Note: This will remove the tag from all tasks via CASCADE delete.

    Args:
        tag_id: Tag identifier
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tags
        HTTPException: 404 if tag not found
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        tag_service = TagService(session)
        deleted = await tag_service.delete_tag(jwt_user_id, tag_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete tag {tag_id} for user {jwt_user_id}: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tag"
        )
