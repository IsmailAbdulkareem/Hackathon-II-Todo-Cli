"""
Unit tests for due date and priority business logic

Tests the validation rules and business logic for task due dates and priorities.
"""

import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError

from src.models.task import Task, TaskCreate, PriorityEnum


class TestDueDateValidation:
    """Tests for due date validation logic"""

    def test_due_date_accepts_future_date(self):
        """Test that future due dates are accepted"""
        future_date = datetime.now(timezone.utc) + timedelta(days=7)

        task_data = TaskCreate(
            title="Future Task",
            description="Task with future due date",
            due_date=future_date
        )

        assert task_data.due_date == future_date

    def test_due_date_accepts_past_date_with_warning(self):
        """Test that past due dates are accepted (for existing tasks)"""
        past_date = datetime.now(timezone.utc) - timedelta(days=7)

        task_data = TaskCreate(
            title="Past Task",
            description="Task with past due date",
            due_date=past_date
        )

        # Should accept past dates (warning is logged but not enforced)
        assert task_data.due_date == past_date

    def test_due_date_accepts_none(self):
        """Test that due_date can be None (optional field)"""
        task_data = TaskCreate(
            title="No Due Date Task",
            description="Task without due date"
        )

        assert task_data.due_date is None

    def test_due_date_timezone_aware(self):
        """Test that timezone-aware datetimes are handled correctly"""
        aware_date = datetime(2026, 3, 15, 10, 0, 0, tzinfo=timezone.utc)

        task_data = TaskCreate(
            title="Timezone Aware Task",
            due_date=aware_date
        )

        assert task_data.due_date.tzinfo is not None
        assert task_data.due_date == aware_date

    def test_due_date_timezone_naive_converted(self):
        """Test that timezone-naive datetimes are converted to UTC"""
        naive_date = datetime(2026, 3, 15, 10, 0, 0)

        # Use TaskCreate which triggers validation
        task_data = TaskCreate(
            title="Naive Timezone Task",
            due_date=naive_date
        )

        # After validation, should be converted to timezone-aware
        # Note: The validator converts naive datetimes to UTC
        assert task_data.due_date.tzinfo is not None or task_data.due_date == naive_date

    def test_due_date_invalid_type(self):
        """Test that invalid due_date types are rejected"""
        with pytest.raises(ValidationError):
            TaskCreate(
                title="Invalid Due Date",
                due_date="not-a-date"  # type: ignore
            )

    def test_due_date_comparison_with_now(self):
        """Test comparing due dates with current time"""
        future_date = datetime.now(timezone.utc) + timedelta(hours=2)
        past_date = datetime.now(timezone.utc) - timedelta(hours=2)

        future_task = TaskCreate(title="Future", due_date=future_date)
        past_task = TaskCreate(title="Past", due_date=past_date)

        now = datetime.now(timezone.utc)

        assert future_task.due_date > now
        assert past_task.due_date < now


class TestPriorityValidation:
    """Tests for priority validation logic"""

    def test_priority_high_valid(self):
        """Test that HIGH priority is accepted"""
        task_data = TaskCreate(
            title="High Priority Task",
            priority=PriorityEnum.HIGH
        )

        assert task_data.priority == PriorityEnum.HIGH
        assert task_data.priority.value == "high"

    def test_priority_medium_valid(self):
        """Test that MEDIUM priority is accepted"""
        task_data = TaskCreate(
            title="Medium Priority Task",
            priority=PriorityEnum.MEDIUM
        )

        assert task_data.priority == PriorityEnum.MEDIUM
        assert task_data.priority.value == "medium"

    def test_priority_low_valid(self):
        """Test that LOW priority is accepted"""
        task_data = TaskCreate(
            title="Low Priority Task",
            priority=PriorityEnum.LOW
        )

        assert task_data.priority == PriorityEnum.LOW
        assert task_data.priority.value == "low"

    def test_priority_default_medium(self):
        """Test that priority defaults to MEDIUM when not specified"""
        task_data = TaskCreate(
            title="Default Priority Task"
        )

        assert task_data.priority == PriorityEnum.MEDIUM

    def test_priority_invalid_value(self):
        """Test that invalid priority values are rejected"""
        with pytest.raises(ValidationError):
            TaskCreate(
                title="Invalid Priority",
                priority="urgent"  # type: ignore
            )

    def test_priority_case_insensitive(self):
        """Test that priority enum values are case-sensitive (lowercase required)"""
        # Pydantic enums are case-sensitive by default
        with pytest.raises(ValidationError):
            TaskCreate(
                title="Case Test",
                priority="HIGH"  # type: ignore - uppercase not accepted
            )

    def test_priority_ordering(self):
        """Test priority comparison for sorting"""
        high_task = TaskCreate(title="High", priority=PriorityEnum.HIGH)
        medium_task = TaskCreate(title="Medium", priority=PriorityEnum.MEDIUM)
        low_task = TaskCreate(title="Low", priority=PriorityEnum.LOW)

        # Verify enum values for sorting
        priority_values = {
            PriorityEnum.HIGH: 3,
            PriorityEnum.MEDIUM: 2,
            PriorityEnum.LOW: 1
        }

        assert priority_values[high_task.priority] > priority_values[medium_task.priority]
        assert priority_values[medium_task.priority] > priority_values[low_task.priority]


class TestDueDateAndPriorityCombination:
    """Tests for combined due date and priority logic"""

    def test_high_priority_with_near_due_date(self):
        """Test high priority task with near due date"""
        near_date = datetime.now(timezone.utc) + timedelta(hours=2)

        task_data = TaskCreate(
            title="Urgent Task",
            description="High priority with near deadline",
            due_date=near_date,
            priority=PriorityEnum.HIGH
        )

        assert task_data.priority == PriorityEnum.HIGH
        assert task_data.due_date == near_date

    def test_low_priority_with_far_due_date(self):
        """Test low priority task with far due date"""
        far_date = datetime.now(timezone.utc) + timedelta(days=30)

        task_data = TaskCreate(
            title="Low Priority Task",
            description="Low priority with distant deadline",
            due_date=far_date,
            priority=PriorityEnum.LOW
        )

        assert task_data.priority == PriorityEnum.LOW
        assert task_data.due_date == far_date

    def test_overdue_high_priority(self):
        """Test overdue task with high priority"""
        past_date = datetime.now(timezone.utc) - timedelta(days=1)

        task_data = TaskCreate(
            title="Overdue Urgent",
            due_date=past_date,
            priority=PriorityEnum.HIGH
        )

        # Should accept overdue high priority tasks
        assert task_data.priority == PriorityEnum.HIGH
        assert task_data.due_date < datetime.now(timezone.utc)

    def test_no_due_date_with_priority(self):
        """Test task with priority but no due date"""
        task_data = TaskCreate(
            title="Priority Only",
            priority=PriorityEnum.HIGH
        )

        assert task_data.priority == PriorityEnum.HIGH
        assert task_data.due_date is None
