from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum

from pydantic import Field, field_validator
from sqlmodel import Column, Field as SQLField, SQLModel, String
from sqlalchemy import JSON
import json


class PriorityEnum(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecurrenceEnum(str, Enum):
    """Recurrence patterns for tasks."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TaskBase(SQLModel):
    """Base task model with shared fields for create/update operations."""

    title: str = Field(
        min_length=1,
        max_length=500,
        description="Task title (required, max 500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (optional, max 2000 characters)"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Due date for the task (optional)"
    )
    priority: Optional[PriorityEnum] = Field(
        default=PriorityEnum.MEDIUM,
        description="Priority level of the task (low, medium, high)"
    )
    tags: Optional[List[str]] = Field(
        default=[],
        description="List of tags associated with the task (max 20 items)"
    )
    recurrence: Optional[RecurrenceEnum] = Field(
        default=RecurrenceEnum.NONE,
        description="Recurrence pattern for the task (none, daily, weekly, monthly)"
    )
    reminder_offset_minutes: Optional[int] = Field(
        default=0,
        ge=0,
        le=2147483647,
        description="Minutes before due date to send reminder (0 if no reminder)"
    )

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """Ensure title is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace from description if provided."""
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that due date is in the future if provided."""
        if v is not None:
            # Make timezone-aware if naive (assume UTC)
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)

            if v < datetime.now(timezone.utc):
                # Allow past due dates for existing tasks but warn about it
                print(f"Warning: Due date {v} is in the past")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tags: normalize to lowercase, max 20 items, max 50 chars each."""
        if v is None:
            return []

        # Normalize to lowercase
        normalized_tags = [tag.lower().strip() for tag in v if tag and tag.strip()]

        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in normalized_tags:
            if tag not in seen and len(tag) <= 50:
                seen.add(tag)
                unique_tags.append(tag)

        # Limit to 20 tags maximum
        return unique_tags[:20]


class Task(TaskBase, table=True):
    """
    Task entity model for database persistence.

    Represents a single task with user ownership, completion status, and timestamps.
    """

    __tablename__ = "tasks"

    id: str = SQLField(
        sa_column=Column(String(36), primary_key=True),
        description="Unique task identifier (UUID)"
    )
    user_id: str = SQLField(
        max_length=255,
        index=True,
        description="User identifier for task ownership"
    )
    completed: bool = Field(
        default=False,
        description="Task completion status"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Task creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Task last update timestamp (UTC)"
    )
    # Override tags field to use JSON column type for database storage
    tags: Optional[List[str]] = SQLField(
        default=[],
        sa_column=Column(JSON),
        description="List of tags associated with the task (stored as JSON)"
    )

    def __init__(self, **data):
        """Initialize task with auto-generated UUID if not provided."""
        if "id" not in data:
            data["id"] = str(uuid4())
        super().__init__(**data)

    def __setattr__(self, name, value):
        """Override to handle tags serialization if stored as JSON."""
        if name == "tags" and isinstance(value, str):
            try:
                # If tags comes as JSON string, convert back to list
                value = json.loads(value)
            except json.JSONDecodeError:
                # If it's not JSON, treat as a single tag
                value = [value]
        super().__setattr__(name, value)


class TaskCreate(TaskBase):
    """Request model for creating a new task."""
    pass


class TaskUpdate(TaskBase):
    """Request model for updating an existing task."""
    # Override fields to make them optional for updates
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Task title (required, max 500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (optional, max 2000 characters)"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Due date for the task (optional)"
    )
    priority: Optional[PriorityEnum] = Field(
        default=None,
        description="Priority level of the task (low, medium, high)"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="List of tags associated with the task (max 20 items)"
    )
    recurrence: Optional[RecurrenceEnum] = Field(
        default=None,
        description="Recurrence pattern for the task (none, daily, weekly, monthly)"
    )
    reminder_offset_minutes: Optional[int] = Field(
        default=None,
        ge=0,
        le=2147483647,
        description="Minutes before due date to send reminder (0 if no reminder)"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Completion status of the task"
    )


class TaskRead(TaskBase):
    """Response model for reading task data."""

    id: str
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
