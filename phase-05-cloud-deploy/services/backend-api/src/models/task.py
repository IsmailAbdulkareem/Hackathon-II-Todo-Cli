from datetime import datetime, timezone, timedelta
from typing import Optional, Literal
from uuid import UUID, uuid4

from pydantic import Field, field_validator, computed_field
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
    priority: Literal["Low", "Medium", "High"] = Field(
        default="Low",
        description="Task priority level (Low, Medium, High)"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Task due date with optional time (timezone-aware)"
    )
    is_recurring: bool = Field(
        default=False,
        description="Whether task is recurring"
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

    Represents a single task with user ownership, completion status, advanced features
    (priority, tags, due dates, reminders, recurrence), and timestamps.
    """

    __tablename__ = "tasks"
    __table_args__ = {"schema": "tasks"}

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
    parent_task_id: Optional[str] = SQLField(
        default=None,
        max_length=36,
        description="Parent task ID for recurring series"
    )
    recurrence_rule_id: Optional[str] = SQLField(
        default=None,
        max_length=36,
        description="Recurrence rule ID if task is recurring"
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

    @computed_field
    @property
    def due_date_status(self) -> Optional[Literal["overdue", "due_today", "due_soon", "upcoming"]]:
        """
        Calculate due date status indicator.

        Returns:
            - "overdue": Due date is in the past
            - "due_today": Due date is today
            - "due_soon": Due date is within the next 3 days
            - "upcoming": Due date is more than 3 days away
            - None: No due date set or task is completed
        """
        if not self.due_date or self.completed:
            return None

        now = datetime.now(timezone.utc)
        due_date = self.due_date

        # Ensure due_date is timezone-aware
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        # Calculate time difference
        time_diff = due_date - now

        # Overdue: due date is in the past
        if time_diff.total_seconds() < 0:
            return "overdue"

        # Due today: within 24 hours
        if time_diff.total_seconds() < 86400:  # 24 hours in seconds
            return "due_today"

        # Due soon: within 3 days
        if time_diff.total_seconds() < 259200:  # 3 days in seconds
            return "due_soon"

        # Upcoming: more than 3 days away
        return "upcoming"

    class Config:
        from_attributes = True
