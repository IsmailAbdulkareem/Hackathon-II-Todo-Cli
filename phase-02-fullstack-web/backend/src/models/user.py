"""User authentication models."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User model for authentication."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(SQLModel):
    """User registration request."""
    email: str = Field(max_length=255)
    name: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)


class UserLogin(SQLModel):
    """User login request."""
    email: str = Field(max_length=255)
    password: str = Field(max_length=255)


class Token(SQLModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    user_name: str


class UserRead(SQLModel):
    """User response (without password)."""
    id: UUID
    email: str
    name: str
    created_at: datetime
