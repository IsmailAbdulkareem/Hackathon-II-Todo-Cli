from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field, field_validator
from sqlmodel import Column, Field as SQLField, SQLModel, String


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
    priority: Optional[int] = Field(
        default=1,
        ge=1,
        le=5,
        description="Task priority (1-5, where 1 is lowest and 5 is highest)"
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

    def __init__(self, **data):
        """Initialize task with auto-generated UUID if not provided."""
        if "id" not in data:
            data["id"] = str(uuid4())
        super().__init__(**data)


class TaskCreate(TaskBase):
    """Request model for creating a new task."""
    pass


class TaskUpdate(TaskBase):
    """Request model for updating an existing task."""
    pass


class TaskRead(TaskBase):
    """Response model for reading task data."""

    id: str
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
