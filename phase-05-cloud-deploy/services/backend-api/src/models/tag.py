from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import Field, field_validator
from sqlmodel import Column, Field as SQLField, SQLModel, String


class TagBase(SQLModel):
    """Base tag model with shared fields for create/update operations."""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Tag name (required, max 100 characters, case-insensitive)"
    )
    color: str = Field(
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code (e.g., #FF5733)"
    )

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        """Ensure name is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError("Tag name cannot be empty or whitespace only")
        return v.strip()


class Tag(TagBase, table=True):
    """
    Tag entity model for database persistence.

    Represents a category or label that can be applied to tasks.
    Tag names are case-insensitive (stored as-is, compared with LOWER()).
    """

    __tablename__ = "tags"
    __table_args__ = {"schema": "tasks"}

    id: str = SQLField(
        sa_column=Column(String(36), primary_key=True),
        description="Unique tag identifier (UUID)"
    )
    user_id: str = SQLField(
        max_length=255,
        index=True,
        description="User identifier for tag ownership"
    )
    usage_count: int = Field(
        default=0,
        description="Number of tasks using this tag"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Tag creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Tag last update timestamp (UTC)"
    )

    def __init__(self, **data):
        """Initialize tag with auto-generated UUID if not provided."""
        if "id" not in data:
            data["id"] = str(uuid4())
        super().__init__(**data)


class TagCreate(TagBase):
    """Request model for creating a new tag."""
    pass


class TagUpdate(SQLModel):
    """Request model for updating an existing tag."""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Tag name (optional for update)"
    )
    color: Optional[str] = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code (optional for update)"
    )


class TagRead(TagBase):
    """Response model for reading tag data."""

    id: str
    user_id: str
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
