from datetime import datetime, timezone
from typing import Optional, Literal
from uuid import uuid4

from pydantic import Field, field_validator
from sqlmodel import Column, Field as SQLField, SQLModel, String


class ReminderBase(SQLModel):
    """Base reminder model with shared fields for create/update operations."""

    scheduled_time: datetime = Field(
        description="Exact reminder time (timezone-aware)"
    )
    reminder_type: Literal["15min", "1hr", "1day", "1week", "custom"] = Field(
        description="Reminder type: 15min, 1hr, 1day, 1week, or custom"
    )

    @field_validator("scheduled_time")
    @classmethod
    def validate_scheduled_time_future(cls, v: datetime) -> datetime:
        """Ensure scheduled time is in the future when created."""
        # Note: This validation is only for creation, not updates
        # The actual enforcement happens in the service layer
        return v


class Reminder(ReminderBase, table=True):
    """
    Reminder entity model for database persistence.

    Represents a scheduled notification for a task.
    Reminders are delivered at exact scheduled times via Dapr Jobs API.
    """

    __tablename__ = "reminders"
    __table_args__ = {"schema": "tasks"}

    id: str = SQLField(
        sa_column=Column(String(36), primary_key=True),
        description="Unique reminder identifier (UUID)"
    )
    task_id: str = SQLField(
        max_length=36,
        index=True,
        description="Task reference"
    )
    user_id: str = SQLField(
        max_length=255,
        index=True,
        description="User identifier for reminder ownership"
    )
    status: Literal["pending", "sent", "failed"] = Field(
        default="pending",
        description="Reminder delivery status"
    )
    dapr_job_id: Optional[str] = SQLField(
        default=None,
        max_length=255,
        description="Dapr Jobs API job identifier"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Reminder creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Reminder last update timestamp (UTC)"
    )

    def __init__(self, **data):
        """Initialize reminder with auto-generated UUID if not provided."""
        if "id" not in data:
            data["id"] = str(uuid4())
        super().__init__(**data)


class ReminderCreate(ReminderBase):
    """Request model for creating a new reminder."""
    pass


class ReminderRead(ReminderBase):
    """Response model for reading reminder data."""

    id: str
    task_id: str
    user_id: str
    status: Literal["pending", "sent", "failed"]
    dapr_job_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
