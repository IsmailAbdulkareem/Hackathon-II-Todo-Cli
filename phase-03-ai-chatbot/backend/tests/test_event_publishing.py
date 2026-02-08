"""
Unit Tests for Event Publishing (T090)

Tests the event publisher with mocked Dapr client to verify
correct event structure, error handling, and API calls.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import httpx

from src.core.event_publisher import DaprEventPublisher, EventPublisher


class TestEventPublisherInterface:
    """Tests for EventPublisher abstract interface"""

    def test_event_publisher_is_abstract(self):
        """Test that EventPublisher cannot be instantiated directly"""
        with pytest.raises(TypeError):
            EventPublisher()  # type: ignore


class TestDaprEventPublisher:
    """Tests for DaprEventPublisher implementation"""

    @pytest.fixture
    def publisher(self):
        """Create DaprEventPublisher instance"""
        return DaprEventPublisher(dapr_http_port=3500, pubsub_name="test-pubsub")

    @pytest.mark.asyncio
    async def test_publish_task_created_event(self, publisher):
        """Test publishing TASK_CREATED event"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            await publisher.publish(
                topic="task-events",
                event_type="TASK_CREATED",
                task_id="task-123",
                payload={"title": "Test Task", "user_id": "user-456"}
            )

            # Verify HTTP call was made
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args

            # Verify URL
            assert "localhost:3500" in call_args[0][0]
            assert "test-pubsub" in call_args[0][0]
            assert "task-events" in call_args[0][0]

            # Verify payload structure
            payload = call_args[1]["json"]
            assert payload["type"] == "TASK_CREATED"
            assert payload["task_id"] == "task-123"
            assert "event_id" in payload
            assert "timestamp" in payload
            assert payload["data"]["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_publish_task_updated_event(self, publisher):
        """Test publishing TASK_UPDATED event"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            await publisher.publish(
                topic="task-events",
                event_type="TASK_UPDATED",
                task_id="task-123",
                payload={"title": "Updated Task", "completed": True}
            )

            mock_client.post.assert_called_once()
            payload = mock_client.post.call_args[1]["json"]
            assert payload["type"] == "TASK_UPDATED"
            assert payload["data"]["completed"] is True

    @pytest.mark.asyncio
    async def test_publish_reminder_due_event(self, publisher):
        """Test publishing REMINDER_DUE event"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            await publisher.publish(
                topic="task-reminders",
                event_type="REMINDER_DUE",
                task_id="task-123",
                payload={"message": "Task due in 30 minutes"}
            )

            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert "task-reminders" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_publish_recurring_task_generated_event(self, publisher):
        """Test publishing RECURRING_TASK_GENERATED event"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            await publisher.publish(
                topic="task-recurring",
                event_type="RECURRING_TASK_GENERATED",
                task_id="task-new-123",
                payload={
                    "original_task_id": "task-123",
                    "new_task_id": "task-new-123",
                    "recurrence": "daily"
                }
            )

            mock_client.post.assert_called_once()
            payload = mock_client.post.call_args[1]["json"]
            assert payload["data"]["original_task_id"] == "task-123"

    @pytest.mark.asyncio
    async def test_publish_with_http_error(self, publisher):
        """Test error handling when Dapr returns HTTP error"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server Error", request=MagicMock(), response=mock_response
            )
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await publisher.publish(
                    topic="task-events",
                    event_type="TASK_CREATED",
                    task_id="task-123",
                    payload={"title": "Test"}
                )

    @pytest.mark.asyncio
    async def test_publish_with_network_error(self, publisher):
        """Test error handling when network error occurs"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with pytest.raises(httpx.ConnectError):
                await publisher.publish(
                    topic="task-events",
                    event_type="TASK_CREATED",
                    task_id="task-123",
                    payload={"title": "Test"}
                )

    @pytest.mark.asyncio
    async def test_event_id_is_unique(self, publisher):
        """Test that each event gets a unique event_id"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Publish two events
            await publisher.publish(
                topic="task-events",
                event_type="TASK_CREATED",
                task_id="task-1",
                payload={"title": "Task 1"}
            )

            await publisher.publish(
                topic="task-events",
                event_type="TASK_CREATED",
                task_id="task-2",
                payload={"title": "Task 2"}
            )

            # Get event IDs from both calls
            call1_payload = mock_client.post.call_args_list[0][1]["json"]
            call2_payload = mock_client.post.call_args_list[1][1]["json"]

            assert call1_payload["event_id"] != call2_payload["event_id"]

    @pytest.mark.asyncio
    async def test_timestamp_format(self, publisher):
        """Test that timestamp is in ISO format"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            await publisher.publish(
                topic="task-events",
                event_type="TASK_CREATED",
                task_id="task-123",
                payload={"title": "Test"}
            )

            payload = mock_client.post.call_args[1]["json"]
            timestamp = payload["timestamp"]

            # Verify ISO format by parsing
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

    @pytest.mark.asyncio
    async def test_custom_dapr_port(self):
        """Test using custom Dapr HTTP port"""
        publisher = DaprEventPublisher(dapr_http_port=4500)

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            await publisher.publish(
                topic="task-events",
                event_type="TASK_CREATED",
                task_id="task-123",
                payload={"title": "Test"}
            )

            call_url = mock_client.post.call_args[0][0]
            assert "localhost:4500" in call_url

    @pytest.mark.asyncio
    async def test_custom_pubsub_name(self):
        """Test using custom pub/sub component name"""
        publisher = DaprEventPublisher(pubsub_name="custom-pubsub")

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            await publisher.publish(
                topic="task-events",
                event_type="TASK_CREATED",
                task_id="task-123",
                payload={"title": "Test"}
            )

            call_url = mock_client.post.call_args[0][0]
            assert "custom-pubsub" in call_url
