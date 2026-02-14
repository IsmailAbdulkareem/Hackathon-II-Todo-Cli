from datetime import datetime, timezone
from typing import Optional, Literal, List
from uuid import uuid4

from pydantic import Field, field_validator
from sqlmodel import Column, Field as SQLField, SQLModel, String, ARRAY, Integer


class RecurrenceRuleBase(SQLModel):
    """Base recurrence rule model with shared fields for create/update operations."""

    recurrence_type: Literal["daily", "weekly", "monthly", "yearly", "custom"] = Field(
        description="Recurrence type: daily, weekly, monthly, yearly, or custom"
    )
    interval: int = Field(
        default=1,
        ge=1,
        description="Interval (e.g., every N days)"
    )
    days_of_week: Optional[List[int]] = Field(
        default=None,
        description="Days of week (0=Sunday, 6=Saturday) for weekly recurrence"
    )
    day_of_month: Optional[int] = Field(
        default=None,
        ge=1,
        le=31,
        description="Day of month (1-31) for monthly recurrence"
    )
    month_of_year: Optional[int] = Field(
        default=None,
        ge=1,
        le=12,
        description="Month (1-12) for yearly recurrence"
    )
    custom_pattern: Optional[str] = Field(
        default=None,
        description="Custom cron-like pattern for custom recurrence"
    )

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Ensure days_of_week values are in valid range (0-6)."""
        if v is not None:
            for day in v:
                if day < 0 or day > 6:
                    raise ValueError("Days of week must be between 0 (Sunday) and 6 (Saturday)")
        return v


class RecurrenceRule(RecurrenceRuleBase, table=True):
    """
    RecurrenceRule entity model for database persistence.

    Represents the pattern for recurring tasks.
    Used by the Recurring Service to calculate next occurrence dates.
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


class RecurrenceRuleRead(RecurrenceRuleBase):
    """Response model for reading recurrence rule data."""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
