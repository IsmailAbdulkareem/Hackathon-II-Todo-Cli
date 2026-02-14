"""Message model for AI chatbot feature."""
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """Message entity for individual chat messages."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(max_length=5000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role is either 'user' or 'assistant'."""
        if v not in ("user", "assistant"):
            raise ValueError("Role must be 'user' or 'assistant'")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty and within character limit."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        if len(v) > 5000:
            raise ValueError("Content exceeds 5000 character limit")
        return v.strip()

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440002",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2026-01-15T14:45:00Z"
            }
        }
