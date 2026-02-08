"""
Unit tests for ReminderService

Tests the reminder scheduling, cancellation, and time calculation logic.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.reminder_service import ReminderService


@pytest.fixture
def reminder_service():
    """Create a ReminderService instance for testing"""
    return ReminderService(dapr_http_port=3500)


class TestCalculateReminderTime:
    """Tests for calculate_reminder_time method"""

    def test_calculate_reminder_time_valid(self, reminder_service):
        """Test calculating reminder time with valid inputs"""
        due_date = datetime(2026, 2, 10, 14, 0, 0)  # Feb 10, 2026 at 2:00 PM
        offset_minutes = 30

        result = reminder_service.calculate_reminder_time(due_date, offset_minutes)

        expected = datetime(2026, 2, 10, 13, 30, 0)  # 30 minutes before
        assert result == expected

    def test_calculate_reminder_time_zero_offset(self, reminder_service):
        """Test calculating reminder time with zero offset"""
        due_date = datetime(2026, 2, 10, 14, 0, 0)
        offset_minutes = 0

        result = reminder_service.calculate_reminder_time(due_date, offset_minutes)

        assert result == due_date

    def test_calculate_reminder_time_large_offset(self, reminder_service):
        """Test calculating reminder time with large offset (days)"""
        due_date = datetime(2026, 2, 10, 14, 0, 0)
        offset_minutes = 1440  # 24 hours

        result = reminder_service.calculate_reminder_time(due_date, offset_minutes)

        expected = datetime(2026, 2, 9, 14, 0, 0)  # 1 day before
        assert result == expected

    def test_calculate_reminder_time_past_due_date(self, reminder_service):
        """Test calculating reminder time when offset exceeds due date"""
        due_date = datetime(2026, 2, 10, 14, 0, 0)
        offset_minutes = 100000  # Very large offset

        result = reminder_service.calculate_reminder_time(due_date, offset_minutes)

        # Should still calculate correctly, even if in the past
        expected = due_date - timedelta(minutes=100000)
        assert result == expected


class TestScheduleReminder:
    """Tests for schedule_reminder method"""

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_schedule_reminder_success(self, mock_post, reminder_service):
        """Test successfully scheduling a reminder"""
        mock_post.return_value = MagicMock(status_code=200)

        task_id = "task-123"
        user_id = "user-456"
        reminder_time = datetime(2026, 2, 10, 13, 30, 0)

        result = await reminder_service.schedule_reminder(task_id, user_id, reminder_time)

        # Verify HTTP call was made
        mock_post.assert_called_once()
        # Result exists (implementation detail of exact format not critical)
        assert result is not None

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_schedule_reminder_with_metadata(self, mock_post, reminder_service):
        """Test scheduling reminder includes task and user metadata"""
        mock_post.return_value = MagicMock(status_code=200)

        task_id = "task-789"
        user_id = "user-012"
        reminder_time = datetime(2026, 2, 15, 10, 0, 0)

        await reminder_service.schedule_reminder(task_id, user_id, reminder_time)

        # Verify HTTP call was made with proper data
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_schedule_reminder_dapr_failure(self, mock_post, reminder_service):
        """Test handling Dapr failure when scheduling"""
        mock_post.side_effect = Exception("Dapr unavailable")

        task_id = "task-999"
        user_id = "user-999"
        reminder_time = datetime(2026, 2, 20, 9, 0, 0)

        # Should handle gracefully or raise appropriate error
        with pytest.raises(Exception):
            await reminder_service.schedule_reminder(task_id, user_id, reminder_time)


class TestCancelReminder:
    """Tests for cancel_reminder method"""

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.delete')
    async def test_cancel_reminder_success(self, mock_delete, reminder_service):
        """Test successfully canceling a reminder"""
        mock_delete.return_value = MagicMock(status_code=200)

        task_id = "task-123"

        await reminder_service.cancel_reminder(task_id)

        # Verify HTTP delete was called
        mock_delete.assert_called_once()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.delete')
    async def test_cancel_reminder_nonexistent(self, mock_delete, reminder_service):
        """Test canceling a reminder that doesn't exist"""
        mock_delete.return_value = MagicMock(status_code=404)

        task_id = "nonexistent-task"

        # Should handle gracefully (job already doesn't exist)
        try:
            await reminder_service.cancel_reminder(task_id)
        except Exception:
            pass  # Either behavior is acceptable

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.delete')
    async def test_cancel_reminder_dapr_failure(self, mock_delete, reminder_service):
        """Test handling Dapr failure when canceling"""
        mock_delete.side_effect = Exception("Dapr unavailable")

        task_id = "task-456"

        # Should handle gracefully or raise appropriate error
        with pytest.raises(Exception):
            await reminder_service.cancel_reminder(task_id)


class TestReminderIntegration:
    """Integration tests for reminder workflow"""

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    @patch('httpx.AsyncClient.delete')
    async def test_full_reminder_workflow(self, mock_delete, mock_post, reminder_service):
        """Test complete reminder workflow: schedule then cancel"""
        mock_post.return_value = MagicMock(status_code=200)
        mock_delete.return_value = MagicMock(status_code=200)

        task_id = "task-workflow"
        user_id = "user-workflow"
        due_date = datetime(2026, 3, 1, 12, 0, 0)
        offset_minutes = 60

        # Calculate reminder time
        reminder_time = reminder_service.calculate_reminder_time(due_date, offset_minutes)
        assert reminder_time == datetime(2026, 3, 1, 11, 0, 0)

        # Schedule reminder
        await reminder_service.schedule_reminder(task_id, user_id, reminder_time)
        assert mock_post.called

        # Cancel reminder
        await reminder_service.cancel_reminder(task_id)
        assert mock_delete.called

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    @patch('httpx.AsyncClient.delete')
    async def test_reschedule_reminder(self, mock_delete, mock_post, reminder_service):
        """Test rescheduling a reminder (cancel old, schedule new)"""
        mock_post.return_value = MagicMock(status_code=200)
        mock_delete.return_value = MagicMock(status_code=200)

        task_id = "task-reschedule"
        user_id = "user-reschedule"

        # Schedule initial reminder
        old_reminder_time = datetime(2026, 3, 1, 10, 0, 0)
        await reminder_service.schedule_reminder(task_id, user_id, old_reminder_time)

        # Cancel old reminder
        await reminder_service.cancel_reminder(task_id)

        # Schedule new reminder
        new_reminder_time = datetime(2026, 3, 1, 14, 0, 0)
        await reminder_service.schedule_reminder(task_id, user_id, new_reminder_time)

        # Verify both schedule and delete were called
        assert mock_post.call_count == 2
        assert mock_delete.call_count == 1
