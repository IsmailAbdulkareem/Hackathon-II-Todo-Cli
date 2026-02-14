"""
FastAPI route handlers for recurrence rule management.

Provides endpoints for:
- Creating recurrence rules
- Getting recurrence rules by ID
- Listing user's recurrence rules
- Updating recurrence rules
- Deleting recurrence rules
"""

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session

from src.core.auth import get_current_user_id, validate_user_ownership
from src.core.database import get_session
from src.models.recurrence_rule import (
    RecurrenceRule,
    RecurrenceRuleCreate,
    RecurrenceRuleRead,
    RecurrenceRuleUpdate
)
from src.services.recurrence_rule_service import RecurrenceRuleService

# Create router for recurrence rule endpoints
router = APIRouter(prefix="/api", tags=["recurrence-rules"])


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


@router.post(
    "/{user_id}/recurrence-rules",
    response_model=RecurrenceRuleRead,
    status_code=status.HTTP_201_CREATED
)
async def create_recurrence_rule(
    rule_data: RecurrenceRuleCreate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> RecurrenceRule:
    """
    Create a new recurrence rule.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        rule_data: Recurrence rule creation data
        session: Database session (injected)

    Returns:
        Created recurrence rule

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's data
        HTTPException: 400 if validation fails
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        rule_service = RecurrenceRuleService(session)
        rule = await rule_service.create_recurrence_rule(jwt_user_id, rule_data)
        return rule

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recurrence rule"
        )


@router.get(
    "/{user_id}/recurrence-rules/{rule_id}",
    response_model=RecurrenceRuleRead,
    status_code=status.HTTP_200_OK
)
async def get_recurrence_rule(
    rule_id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> RecurrenceRule:
    """
    Get a recurrence rule by ID.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        rule_id: Recurrence rule identifier
        session: Database session (injected)

    Returns:
        Recurrence rule

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's data
        HTTPException: 404 if rule not found
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        rule_service = RecurrenceRuleService(session)
        rule = await rule_service.get_recurrence_rule_by_id(jwt_user_id, rule_id)

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurrence rule not found"
            )

        return rule

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recurrence rule"
        )


@router.get(
    "/{user_id}/recurrence-rules",
    response_model=list[RecurrenceRuleRead],
    status_code=status.HTTP_200_OK
)
async def list_recurrence_rules(
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> list[RecurrenceRule]:
    """
    List all recurrence rules for a user.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session (injected)

    Returns:
        List of recurrence rules

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's data
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        rule_service = RecurrenceRuleService(session)
        rules = await rule_service.get_user_recurrence_rules(jwt_user_id)
        return rules

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list recurrence rules"
        )


@router.put(
    "/{user_id}/recurrence-rules/{rule_id}",
    response_model=RecurrenceRuleRead,
    status_code=status.HTTP_200_OK
)
async def update_recurrence_rule(
    rule_id: str,
    rule_data: RecurrenceRuleUpdate,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> RecurrenceRule:
    """
    Update a recurrence rule.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        rule_id: Recurrence rule identifier
        rule_data: Recurrence rule update data
        session: Database session (injected)

    Returns:
        Updated recurrence rule

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's data
        HTTPException: 404 if rule not found
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        rule_service = RecurrenceRuleService(session)
        rule = await rule_service.update_recurrence_rule(jwt_user_id, rule_id, rule_data)

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurrence rule not found"
            )

        return rule

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recurrence rule"
        )


@router.delete(
    "/{user_id}/recurrence-rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_recurrence_rule(
    rule_id: str,
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a recurrence rule.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        rule_id: Recurrence rule identifier
        session: Database session (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's data
        HTTPException: 404 if rule not found
        HTTPException: 500 if database connection fails
    """
    validate_user_ownership(jwt_user_id, user_id)

    try:
        rule_service = RecurrenceRuleService(session)
        deleted = await rule_service.delete_recurrence_rule(jwt_user_id, rule_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurrence rule not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recurrence rule"
        )
