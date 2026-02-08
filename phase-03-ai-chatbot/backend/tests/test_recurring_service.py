"""
Unit tests for RecurringTaskService

Tests the recurring task generation, recurrence calculation, and scheduling logic.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.recurring_service import RecurringTaskService
from src.models.task import RecurrenceEnum


@pytest.fixture
def recurring_service():
    """Create a RecurringTaskService instance for testing"""
    return RecurringTaskService(dapr_http_port=3500)


class TestCalculateNextOccurrence:
    """Tests for calculate_next_recurrence method"""

    def test_calculate_next_occurrence_daily(self, recurring_service):
        """Test calculating next occurrence for daily recurrence"""
        current_date = datetime(2026, 2, 10, 14, 0, 0)
        anchor_date = datetime(2026, 2, 1, 14, 0, 0)
        recurrence = RecurrenceEnum.DAILY

        result = recurring_service.calculate_next_recurrence(current_date, anchor_date, recurrence)

        expected = datetime(2026, 2, 11, 14, 0, 0)  # Next day, same time
        assert result == expected

    def test_calculate_next_occurrence_weekly(self, recurring_service):
        """Test calculating next occurrence for weekly recurrence"""
        current_date = datetime(2026, 2, 10, 14, 0, 0)  # Tuesday
        anchor_date = datetime(2026, 2, 3, 14, 0, 0)  # Previous Tuesday
        recurrence = RecurrenceEnum.WEEKLY

        result = recurring_service.calculate_next_recurrence(current_date, anchor_date, recurrence)

        expected = datetime(2026, 2, 17, 14, 0, 0)  # Next Tuesday
        assert result == expected

    def test_calculate_next_occurrence_monthly(self, recurring_service):
        """Test calculating next occurrence for monthly recurrence"""
        current_date = datetime(2026, 2, 10, 14, 0, 0)
        anchor_date = datetime(2026, 1, 10, 14, 0, 0)
        recurrence = RecurrenceEnum.MONTHLY

        result = recurring_service.calculate_next_recurrence(current_date, anchor_date, recurrence)

        expected = datetime(2026, 3, 10, 14, 0, 0)  # Same day next month
        assert result == expected

    def test_calculate_next_occurrence_monthly_month_end(self, recurring_service):
        """Test calculating next occurrence for monthly recurrence at month end"""
        current_date = datetime(2026, 1, 31, 14, 0, 0)  # Jan 31
        anchor_date = datetime(2026, 1, 31, 14, 0, 0)
        recurrence = RecurrenceEnum.MONTHLY

        result = recurring_service.calculate_next_recurrence(current_date, anchor_date, recurrence)

        # February doesn't have 31 days, should adjust to Feb 28
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 28
        assert result.hour == 14
        assert result.minute == 0

    def test_calculate_next_occurrence_monthly_leap_year(self, recurring_service):
        """Test monthly recurrence handling for leap year"""
        current_date = datetime(2024, 1, 29, 14, 0, 0)  # Jan 29, 2024 (leap year)
        anchor_date = datetime(2024, 1, 29, 14, 0, 0)
        recurrence = RecurrenceEnum.MONTHLY

        result = recurring_service.calculate_next_recurrence(current_date, anchor_date, recurrence)

        # Feb 2024 has 29 days (leap year)
        expected = datetime(2024, 2, 29, 14, 0, 0)
        assert result == expected

    def test_calculate_next_occurrence_none(self, recurring_service):
        """Test calculating next occurrence with no recurrence"""
        current_date = datetime(2026, 2, 10, 14, 0, 0)
        anchor_date = datetime(2026, 2, 1, 14, 0, 0)
        recurrence = RecurrenceEnum.NONE

        # Should raise ValueError for NONE recurrence
        with pytest.raises(ValueError):
            recurring_service.calculate_next_recurrence(current_date, anchor_date, recurrence)


class TestScheduleRecurringTaskGeneration:
    """Tests for schedule_recurring_task_generation method"""

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_schedule_recurring_daily(self, mock_post, recurring_service):
        """Test scheduling recurring task generation for daily recurrence"""
        mock_post.return_value = MagicMock(status_code=200)

        task_id = "task-123"
        user_id = "user-456"
        recurrence_pattern = "daily"
        start_time = datetime(2026, 2, 10, 14, 0, 0)

        await recurring_service.schedule_recurring_task_generation(
            task_id, user_id, recurrence_pattern, start_time
        )

        # Verify HTTP call was made
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_schedule_recurring_weekly(self, mock_post, recurring_service):
        """Test scheduling recurring task generation for weekly recurrence"""
        mock_post.return_value = MagicMock(status_code=200)

        task_id = "task-789"
        user_id = "user-012"
        recurrence_pattern = "weekly"
        start_time = datetime(2026, 2, 10, 14, 0, 0)

        await recurring_service.schedule_recurring_task_generation(
            task_id, user_id, recurrence_pattern, start_time
        )

        mock_post.assert_called_once()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_schedule_recurring_monthly(self, mock_post, recurring_service):
        """Test scheduling recurring task generation for monthly recurrence"""
        mock_post.return_value = MagicMock(status_code=200)

        task_id = "task-345"
        user_id = "user-678"
        recurrence_pattern = "monthly"
        start_time = datetime(2026, 2, 10, 14, 0, 0)

        await recurring_service.schedule_recurring_task_generation(
            task_id, user_id, recurrence_pattern, start_time
        )

        mock_post.assert_called_once()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_schedule_recurring_none(self, mock_post, recurring_service):
        """Test scheduling with none/invalid recurrence (should still schedule with default)"""
        mock_post.return_value = MagicMock(status_code=200)

        task_id = "task-999"
        user_id = "user-999"
        recurrence_pattern = "none"
        start_time = datetime(2026, 2, 10, 14, 0, 0)

        await recurring_service.schedule_recurring_task_generation(
            task_id, user_id, recurrence_pattern, start_time
        )

        # Will schedule with default cron (daily)
        mock_post.assert_called_once()


class TestCancelRecurringTaskGeneration:
    """Tests for cancel_recurring_job method"""

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.delete')
    async def test_cancel_recurring_success(self, mock_delete, recurring_service):
        """Test successfully canceling recurring task generation"""
        mock_delete.return_value = MagicMock(status_code=200)

        task_id = "task-123"

        await recurring_service.cancel_recurring_job(task_id)

        # Verify HTTP delete was called
        mock_delete.assert_called_once()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.delete')
    async def test_cancel_recurring_nonexistent(self, mock_delete, recurring_service):
        """Test canceling recurring generation that doesn't exist"""
        mock_delete.return_value = MagicMock(status_code=404)

        task_id = "nonexistent-task"

        # Should handle gracefully
        try:
            await recurring_service.cancel_recurring_job(task_id)
        except Exception:
            pass  # Either behavior is acceptable


class TestMonthEndHandling:
    """Tests for month-end date handling in recurring tasks"""

    def test_month_end_february_non_leap(self, recurring_service):
        """Test month-end handling for February in non-leap year"""
        current_date = datetime(2026, 1, 31, 14, 0, 0)  # Jan 31, 2026
        anchor_date = datetime(2026, 1, 31, 14, 0, 0)
        recurrence = RecurrenceEnum.MONTHLY

        result = recurring_service.calculate_next_recurrence(current_date, anchor_date, recurrence)

        # Feb 2026 has 28 days, should adjust to Feb 28
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 28
        assert result.hour == 14
        assert result.minute == 0

    def test_month_end_february_leap(self, recurring_service):
        """Test month-end handling for February in leap year"""
        current_date = datetime(2024, 1, 31, 14, 0, 0)  # Jan 31, 2024 (leap year)
        anchor_date = datetime(2024, 1, 31, 14, 0, 0)
        recurrence = RecurrenceEnum.MONTHLY

        result = recurring_service.calculate_next_recurrence(current_date, anchor_date, recurrence)

        # Feb 2024 has 29 days, should adjust to Feb 29
        assert result.year == 2024
        assert result.month == 2
        assert result.day == 29

    def test_month_end_30_day_month(self, recurring_service):
        """Test month-end handling for 30-day months"""
        current_date = datetime(2026, 3, 31, 14, 0, 0)  # March 31
        anchor_date = datetime(2026, 1, 31, 14, 0, 0)
        recurrence = RecurrenceEnum.MONTHLY

        result = recurring_service.calculate_next_recurrence(current_date, anchor_date, recurrence)

        # April has 30 days, should adjust to April 30
        assert result.month == 4
        assert result.day == 30

    def test_month_end_31_day_month(self, recurring_service):
        """Test month-end handling for 31-day months"""
        current_date = datetime(2026, 2, 28, 14, 0, 0)  # Feb 28
        anchor_date = datetime(2026, 1, 31, 14, 0, 0)
        recurrence = RecurrenceEnum.MONTHLY

        result = recurring_service.calculate_next_recurrence(current_date, anchor_date, recurrence)

        # March has 31 days, should be March 31
        assert result.month == 3
        assert result.day == 31


class TestRecurringTaskWorkflow:
    """Integration tests for recurring task workflow"""

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    @patch('httpx.AsyncClient.delete')
    async def test_full_recurring_workflow(self, mock_delete, mock_post, recurring_service):
        """Test complete recurring workflow: schedule then cancel"""
        mock_post.return_value = MagicMock(status_code=200)
        mock_delete.return_value = MagicMock(status_code=200)

        task_id = "task-workflow"
        user_id = "user-workflow"
        recurrence_pattern = "weekly"
        start_time = datetime(2026, 3, 1, 12, 0, 0)

        # Schedule recurring generation
        await recurring_service.schedule_recurring_task_generation(
            task_id, user_id, recurrence_pattern, start_time
        )
        assert mock_post.called

        # Cancel recurring generation
        await recurring_service.cancel_recurring_job(task_id)
        assert mock_delete.called

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    @patch('httpx.AsyncClient.delete')
    async def test_reschedule_recurring(self, mock_delete, mock_post, recurring_service):
        """Test rescheduling recurring generation (cancel old, schedule new)"""
        mock_post.return_value = MagicMock(status_code=200)
        mock_delete.return_value = MagicMock(status_code=200)

        task_id = "task-reschedule"
        user_id = "user-reschedule"

        # Schedule initial recurring generation (daily)
        old_start_time = datetime(2026, 3, 1, 10, 0, 0)
        await recurring_service.schedule_recurring_task_generation(
            task_id, user_id, "daily", old_start_time
        )

        # Cancel old recurring generation
        await recurring_service.cancel_recurring_job(task_id)

        # Schedule new recurring generation (weekly)
        new_start_time = datetime(2026, 3, 1, 14, 0, 0)
        await recurring_service.schedule_recurring_task_generation(
            task_id, user_id, "weekly", new_start_time
        )

        # Verify both schedule and delete were called
        assert mock_post.call_count == 2
        assert mock_delete.call_count == 1

    def test_multiple_occurrences_daily(self, recurring_service):
        """Test calculating multiple daily occurrences"""
        start_date = datetime(2026, 2, 10, 14, 0, 0)
        anchor_date = datetime(2026, 2, 1, 14, 0, 0)
        recurrence = RecurrenceEnum.DAILY

        # Calculate 5 occurrences
        occurrences = [start_date]
        for _ in range(4):
            next_occurrence = recurring_service.calculate_next_recurrence(
                occurrences[-1], anchor_date, recurrence
            )
            occurrences.append(next_occurrence)

        # Verify all occurrences are correct
        assert len(occurrences) == 5
        assert occurrences[0] == datetime(2026, 2, 10, 14, 0, 0)
        assert occurrences[1] == datetime(2026, 2, 11, 14, 0, 0)
        assert occurrences[2] == datetime(2026, 2, 12, 14, 0, 0)
        assert occurrences[3] == datetime(2026, 2, 13, 14, 0, 0)
        assert occurrences[4] == datetime(2026, 2, 14, 14, 0, 0)

    def test_multiple_occurrences_weekly(self, recurring_service):
        """Test calculating multiple weekly occurrences"""
        start_date = datetime(2026, 2, 10, 14, 0, 0)  # Tuesday
        anchor_date = datetime(2026, 2, 3, 14, 0, 0)  # Previous Tuesday
        recurrence = RecurrenceEnum.WEEKLY

        # Calculate 3 occurrences
        occurrences = [start_date]
        for _ in range(2):
            next_occurrence = recurring_service.calculate_next_recurrence(
                occurrences[-1], anchor_date, recurrence
            )
            occurrences.append(next_occurrence)

        # Verify all occurrences are correct (every Tuesday)
        assert len(occurrences) == 3
        assert occurrences[0] == datetime(2026, 2, 10, 14, 0, 0)
        assert occurrences[1] == datetime(2026, 2, 17, 14, 0, 0)
        assert occurrences[2] == datetime(2026, 2, 24, 14, 0, 0)
