"""
RecurrenceRule service for managing recurrence patterns.

Provides CRUD operations for recurrence rules that define
how recurring tasks should repeat.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Session, select

from src.models.recurrence_rule import (
    RecurrenceRule,
    RecurrenceRuleCreate,
    RecurrenceRuleUpdate
)

logger = logging.getLogger(__name__)


class RecurrenceRuleService:
    """
    Service layer for recurrence rule management operations.

    Handles recurrence rule CRUD and validation.
    """

    def __init__(self, session: Session):
        """
        Initialize recurrence rule service.

        Args:
            session: Database session
        """
        self.session = session

    async def create_recurrence_rule(
        self,
        user_id: str,
        rule_data: RecurrenceRuleCreate
    ) -> RecurrenceRule:
        """
        Create a new recurrence rule.

        Args:
            user_id: User identifier
            rule_data: Recurrence rule creation data

        Returns:
            Created recurrence rule

        Raises:
            ValueError: If validation fails
        """
        # Validate rule data
        self._validate_recurrence_rule(rule_data)

        # Create recurrence rule
        rule = RecurrenceRule(
            user_id=user_id,
            frequency=rule_data.frequency,
            interval=rule_data.interval,
            end_date=rule_data.end_date,
            occurrence_count=rule_data.occurrence_count,
            current_count=0
        )

        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)

        logger.info(f"Created recurrence rule {rule.id} for user {user_id}")
        return rule

    async def get_recurrence_rule_by_id(
        self,
        user_id: str,
        rule_id: str
    ) -> Optional[RecurrenceRule]:
        """
        Get a recurrence rule by ID.

        Args:
            user_id: User identifier
            rule_id: Recurrence rule identifier

        Returns:
            Recurrence rule if found, None otherwise
        """
        statement = select(RecurrenceRule).where(
            RecurrenceRule.id == rule_id,
            RecurrenceRule.user_id == user_id
        )
        return self.session.exec(statement).first()

    async def get_user_recurrence_rules(
        self,
        user_id: str
    ) -> List[RecurrenceRule]:
        """
        Get all recurrence rules for a user.

        Args:
            user_id: User identifier

        Returns:
            List of recurrence rules
        """
        statement = select(RecurrenceRule).where(
            RecurrenceRule.user_id == user_id
        ).order_by(RecurrenceRule.created_at.desc())

        return list(self.session.exec(statement).all())

    async def update_recurrence_rule(
        self,
        user_id: str,
        rule_id: str,
        rule_data: RecurrenceRuleUpdate
    ) -> Optional[RecurrenceRule]:
        """
        Update a recurrence rule.

        Args:
            user_id: User identifier
            rule_id: Recurrence rule identifier
            rule_data: Recurrence rule update data

        Returns:
            Updated recurrence rule if found, None otherwise
        """
        rule = await self.get_recurrence_rule_by_id(user_id, rule_id)
        if not rule:
            return None

        # Update current count if provided
        if rule_data.current_count is not None:
            rule.current_count = rule_data.current_count

        rule.updated_at = datetime.now(timezone.utc)

        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)

        logger.info(f"Updated recurrence rule {rule_id} for user {user_id}")
        return rule

    async def delete_recurrence_rule(
        self,
        user_id: str,
        rule_id: str
    ) -> bool:
        """
        Delete a recurrence rule.

        Args:
            user_id: User identifier
            rule_id: Recurrence rule identifier

        Returns:
            True if deleted, False if not found
        """
        rule = await self.get_recurrence_rule_by_id(user_id, rule_id)
        if not rule:
            return False

        self.session.delete(rule)
        self.session.commit()

        logger.info(f"Deleted recurrence rule {rule_id} for user {user_id}")
        return True

    def _validate_recurrence_rule(self, rule_data: RecurrenceRuleCreate) -> None:
        """
        Validate recurrence rule data.

        Args:
            rule_data: Recurrence rule creation data

        Raises:
            ValueError: If validation fails
        """
        # Validate end_date is in the future if provided
        if rule_data.end_date:
            now = datetime.now(timezone.utc)
            end_date = rule_data.end_date

            # Ensure end_date is timezone-aware
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)

            if end_date <= now:
                raise ValueError("End date must be in the future")

        # Validate that either end_date or occurrence_count is provided
        if not rule_data.end_date and not rule_data.occurrence_count:
            raise ValueError(
                "Either end_date or occurrence_count must be specified for recurrence rule"
            )

        # Validate interval is reasonable for frequency
        if rule_data.frequency == "daily" and rule_data.interval > 365:
            raise ValueError("Daily recurrence interval cannot exceed 365 days")

        if rule_data.frequency == "weekly" and rule_data.interval > 52:
            raise ValueError("Weekly recurrence interval cannot exceed 52 weeks")

        if rule_data.frequency == "monthly" and rule_data.interval > 120:
            raise ValueError("Monthly recurrence interval cannot exceed 120 months")

        if rule_data.frequency == "yearly" and rule_data.interval > 10:
            raise ValueError("Yearly recurrence interval cannot exceed 10 years")
