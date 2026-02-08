"""
Integration Tests for Event Publishing to Dapr (T091)

Tests the complete event publishing flow with actual Dapr pub/sub
(or mocked Dapr when not available).
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from main import app
from src.core.event_publisher import DaprEventPublisher
from src.services.audit_service import audit_service


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
async def event_publisher():
    """Create event publisher instance"""
    return DaprEventPublisher(dapr_http_port=3500, pubsub_name="redis-pubsub")


@pytest.fixture(autouse=True)
async def cleanup_audit_logs():
    """Clear audit logs before and after each test"""
    await audit_service.clear_logs()
    yield
    await audit_service.clear_logs()


class TestEventPublishingIntegration:
    """Integration tests for event publishing"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_task_created_event_flow(self, client, event_publisher):
        """Test complete flow of TASK_CREATED event"""
        # Publish event
        await event_publisher.publish(
            topic="task-events",
            event_type="TASK_CREATED",
            task_id="test-task-123",
            payload={
                "title": "Integration Test Task",
                "user_id": "test-user-456",
                "completed": False
            }
        )

        # Event should be published (no exception means success)
        # In real Dapr environment, subscriber would receive it

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_task_updated_event_flow(self, client, event_publisher):
        """Test complete flow of TASK_UPDATED event"""
        await event_publisher.publish(
            topic="task-events",
            event_type="TASK_UPDATED",
            task_id="test-task-123",
            payload={
                "title": "Updated Task",
                "completed": True,
                "user_id": "test-user-456"
            }
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_reminder_due_event_flow(self, client, event_publisher):
        """Test complete flow of REMINDER_DUE event"""
        await event_publisher.publish(
            topic="task-reminders",
            event_type="REMINDER_DUE",
            task_id="test-task-123",
            payload={
                "message": "Task due in 30 minutes",
                "user_id": "test-user-456",
                "due_date": datetime.now(timezone.utc).isoformat()
            }
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_recurring_task_generated_event_flow(self, client, event_publisher):
        """Test complete flow of RECURRING_TASK_GENERATED event"""
        await event_publisher.publish(
            topic="task-recurring",
            event_type="RECURRING_TASK_GENERATED",
            task_id="test-task-new-123",
            payload={
                "original_task_id": "test-task-123",
                "new_task_id": "test-task-new-123",
                "recurrence": "daily",
                "user_id": "test-user-456"
            }
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multiple_events_in_sequence(self, client, event_publisher):
        """Test publishing multiple events in sequence"""
        events = [
            ("task-events", "TASK_CREATED", "task-1", {"title": "Task 1"}),
            ("task-events", "TASK_UPDATED", "task-1", {"completed": True}),
            ("task-reminders", "REMINDER_DUE", "task-1", {"message": "Due now"}),
            ("task-events", "TASK_COMPLETED", "task-1", {"completed": True}),
        ]

        for topic, event_type, task_id, payload in events:
            await event_publisher.publish(
                topic=topic,
                event_type=event_type,
                task_id=task_id,
                payload=payload
            )

        # All events should be published successfully


class TestEventSubscriberEndpoints:
    """Integration tests for event subscriber endpoints"""

    @pytest.mark.integration
    def test_dapr_subscribe_endpoint(self, client):
        """Test Dapr subscription configuration endpoint"""
        response = client.get("/events/dapr/subscribe")

        assert response.status_code == 200
        subscriptions = response.json()

        # Verify all three topics are subscribed
        assert len(subscriptions) == 3

        topics = [sub["topic"] for sub in subscriptions]
        assert "task-events" in topics
        assert "task-reminders" in topics
        assert "task-recurring" in topics

        # Verify routes are correct
        for sub in subscriptions:
            assert sub["pubsubname"] == "redis-pubsub"
            assert sub["route"].startswith("/events/")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_task_events_subscriber(self, client):
        """Test task-events subscriber endpoint"""
        # Simulate Dapr CloudEvent
        cloud_event = {
            "specversion": "1.0",
            "type": "TASK_CREATED",
            "source": "test",
            "id": "test-event-123",
            "time": datetime.now(timezone.utc).isoformat(),
            "datacontenttype": "application/json",
            "data": {
                "task_id": "test-task-123",
                "title": "Test Task",
                "user_id": "test-user-456"
            }
        }

        response = client.post("/events/task-events", json=cloud_event)

        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"

        # Verify event was logged to audit service
        logs = await audit_service.get_logs(event_type="TASK_CREATED", limit=10)
        assert len(logs) > 0
        assert logs[0].topic == "task-events"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_task_reminders_subscriber(self, client):
        """Test task-reminders subscriber endpoint"""
        cloud_event = {
            "specversion": "1.0",
            "type": "REMINDER_DUE",
            "source": "test",
            "id": "test-event-456",
            "time": datetime.now(timezone.utc).isoformat(),
            "datacontenttype": "application/json",
            "data": {
                "task_id": "test-task-123",
                "message": "Task due soon",
                "user_id": "test-user-456"
            }
        }

        response = client.post("/events/task-reminders", json=cloud_event)

        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"

        # Verify event was logged
        logs = await audit_service.get_logs(event_type="REMINDER_DUE", limit=10)
        assert len(logs) > 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_task_recurring_subscriber(self, client):
        """Test task-recurring subscriber endpoint"""
        cloud_event = {
            "specversion": "1.0",
            "type": "RECURRING_TASK_GENERATED",
            "source": "test",
            "id": "test-event-789",
            "time": datetime.now(timezone.utc).isoformat(),
            "datacontenttype": "application/json",
            "data": {
                "original_task_id": "test-task-123",
                "new_task_id": "test-task-new-123",
                "recurrence": "daily",
                "user_id": "test-user-456"
            }
        }

        response = client.post("/events/task-recurring", json=cloud_event)

        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"

        # Verify event was logged
        logs = await audit_service.get_logs(event_type="RECURRING_TASK_GENERATED", limit=10)
        assert len(logs) > 0


class TestAuditServiceIntegration:
    """Integration tests for audit service with event system"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_audit_logs_all_events(self, client):
        """Test that all events are logged to audit service"""
        # Simulate multiple events
        events = [
            {"type": "TASK_CREATED", "data": {"task_id": "task-1"}},
            {"type": "TASK_UPDATED", "data": {"task_id": "task-1"}},
            {"type": "REMINDER_DUE", "data": {"task_id": "task-1"}},
        ]

        for event in events:
            cloud_event = {
                "specversion": "1.0",
                "type": event["type"],
                "source": "test",
                "id": f"test-{event['type']}",
                "time": datetime.now(timezone.utc).isoformat(),
                "data": event["data"]
            }

            if "REMINDER" in event["type"]:
                client.post("/events/task-reminders", json=cloud_event)
            else:
                client.post("/events/task-events", json=cloud_event)

        # Verify all events are in audit log
        all_logs = await audit_service.get_logs(limit=100)
        assert len(all_logs) >= 3

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_audit_log_filtering(self, client):
        """Test filtering audit logs by various criteria"""
        # Create events with different types
        await audit_service.log_event(
            event_type="TASK_CREATED",
            topic="task-events",
            data={"task_id": "task-1", "user_id": "user-1"}
        )

        await audit_service.log_event(
            event_type="TASK_UPDATED",
            topic="task-events",
            data={"task_id": "task-2", "user_id": "user-2"}
        )

        await audit_service.log_event(
            event_type="REMINDER_DUE",
            topic="task-reminders",
            data={"task_id": "task-1", "user_id": "user-1"}
        )

        # Filter by event type
        created_logs = await audit_service.get_logs(event_type="TASK_CREATED")
        assert len(created_logs) == 1
        assert created_logs[0].event_type == "TASK_CREATED"

        # Filter by topic
        reminder_logs = await audit_service.get_logs(topic="task-reminders")
        assert len(reminder_logs) == 1
        assert reminder_logs[0].topic == "task-reminders"

        # Filter by user_id
        user1_logs = await audit_service.get_logs(user_id="user-1")
        assert len(user1_logs) == 2

        # Filter by task_id
        task1_logs = await audit_service.get_logs(task_id="task-1")
        assert len(task1_logs) == 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_audit_log_event_count(self, client):
        """Test getting event counts from audit service"""
        # Create multiple events
        for i in range(5):
            await audit_service.log_event(
                event_type="TASK_CREATED",
                topic="task-events",
                data={"task_id": f"task-{i}"}
            )

        for i in range(3):
            await audit_service.log_event(
                event_type="REMINDER_DUE",
                topic="task-reminders",
                data={"task_id": f"task-{i}"}
            )

        # Get counts
        created_count = await audit_service.get_event_count(event_type="TASK_CREATED")
        reminder_count = await audit_service.get_event_count(event_type="REMINDER_DUE")
        total_count = await audit_service.get_event_count()

        assert created_count == 5
        assert reminder_count == 3
        assert total_count >= 8
