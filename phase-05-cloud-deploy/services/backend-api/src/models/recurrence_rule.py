"""
RecurrenceRule model for defining recurring task patterns.

Supports standard recurrence patterns:
- Daily: Every N days
- Weekly: Every N weeks on specific days
- Monthly: Every N months on specific day
- Yearly: Every N years on specific date
"""

from datetime import datetime, timezone
from typing import Optional, Literal
from uuid import uuid4

from pydantic import Field, field_validator
from sqlmodel import Column, Field as SQLField, SQLModel, String


class RecurrenceRuleBase(SQLModel):
    """Base recurrence rule model with shared fields."""

    frequency: Literal["daily", "weekly", "monthly", "yearly"] = Field(
        description="Recurrence frequency"
    )
    interval: int = Field(
        default=1,
        ge=1,
        le=365,
        description="Interval between occurrences (e.g., every 2 weeks)"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="Optional end date for recurrence series"
    )
    occurrence_count: Optional[int] = Field(
        default=None,
        ge=1,
        le=1000,
        description="Optional maximum number of occurrences"
    )


class RecurrenceRule(RecurrenceRuleBase, table=True):
    """
    RecurrenceRule entity model for database persistence.

    Defines the pattern for recurring task instances.
    """

    __tablename__ = "recurrence_rules"
    __table_args__ = {"schema": "tasks"}

    id: str = SQLField(
        sa_column=Column(String(36), primary_key=True),
        description="Unique recurrence rule identifier (UUID)"
    )
    user_id: str = SQLField(
        max_length=255,
        index=True,
        description="User identifier for rule ownership"
    )
    current_count: int = Field(
        default=0,
        description="Current number of occurrences created"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Rule creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Rule last update timestamp (UTC)"
    )

    def __init__(self, **data):
        """Initialize recurrence rule with auto-generated UUID if not provided."""
        if "id" not in data:
            data["id"] = str(uuid4())
        super().__init__(**data)


class RecurrenceRuleCreate(RecurrenceRuleBase):
    """Request model for creating a new recurrence rule."""
    pass


class RecurrenceRuleUpdate(SQLModel):
    """Request model for updating an existing recurrence rule."""

    current_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Update occurrence count"
    )


class RecurrenceRuleRead(RecurrenceRuleBase):
    """Response model for reading recurrence rule data."""

    id: str
    user_id: str
    current_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
