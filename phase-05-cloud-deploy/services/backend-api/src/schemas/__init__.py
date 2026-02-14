"""
Pydantic schemas for API request/response validation.

This package re-exports schema classes from models for cleaner API imports.
Separates API contracts (schemas) from database models (models).
"""

from .tag import TagCreate, TagRead, TagUpdate
from .reminder import ReminderCreate, ReminderRead
from .recurrence import RecurrenceRuleCreate, RecurrenceRuleRead
from .task import TaskCreate, TaskRead, TaskUpdate

__all__ = [
    # Tag schemas
    "TagCreate",
    "TagRead",
    "TagUpdate",
    # Reminder schemas
    "ReminderCreate",
    "ReminderRead",
    # Recurrence schemas
    "RecurrenceRuleCreate",
    "RecurrenceRuleRead",
    # Task schemas
    "TaskCreate",
    "TaskRead",
    "TaskUpdate",
]
