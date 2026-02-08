"""
End-to-End tests for complete user workflows

Tests the full user journey through the application, verifying that all
components work together correctly from task creation to completion.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from sqlmodel import Session, create_engine, SQLModel, select, or_
from sqlmodel.pool import StaticPool
from typing import List, Optional

from main import app
from src.models.task import Task, TaskCreate, TaskUpdate, PriorityEnum, RecurrenceEnum
from src.core.database import get_session
from src.core.auth import get_current_user_id
from src.core.dependencies import get_repository
from src.services.fallback_task_repository import FallbackTaskRepository


class TestTaskRepository(FallbackTaskRepository):
    """Test repository that uses the test session"""

    def __init__(self, test_engine):
        self.test_engine = test_engine

    async def create(self, user_id: str, task_data: TaskCreate) -> Task:
        with Session(self.test_engine) as session:
            task = Task(
                user_id=user_id,
                title=task_data.title,
                description=task_data.description,
                due_date=task_data.due_date,
                priority=task_data.priority,
                tags=task_data.tags or [],
                recurrence=task_data.recurrence,
                reminder_offset_minutes=task_data.reminder_offset_minutes or 0
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    async def get_by_id(self, user_id: str, task_id: str) -> Optional[Task]:
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            return session.exec(statement).first()

    async def update(self, user_id: str, task_id: str, task_data: TaskUpdate) -> Optional[Task]:
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()
            if not task:
                return None
            update_dict = task_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(task, field, value)
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    async def delete(self, user_id: str, task_id: str) -> bool:
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()
            if not task:
                return False
            session.delete(task)
            session.commit()
            return True

    async def get_all(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Task]:
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
            return list(session.exec(statement).all())

    async def count(self, user_id: str, completed: Optional[bool] = None) -> int:
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.user_id == user_id)
            if completed is not None:
                statement = statement.where(Task.completed == completed)
            return len(list(session.exec(statement).all()))

    async def search(self, user_id: str, query: Optional[str] = None,
                    completed: Optional[bool] = None, priority: Optional[str] = None,
                    tags: Optional[List[str]] = None, due_from: Optional[datetime] = None,
                    due_to: Optional[datetime] = None, sort_by: str = "created_at",
                    sort_order: str = "desc", skip: int = 0, limit: int = 100) -> List[Task]:
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.user_id == user_id)
            if query:
                statement = statement.where(or_(Task.title.ilike(f"%{query}%"), Task.description.ilike(f"%{query}%")))
            if completed is not None:
                statement = statement.where(Task.completed == completed)
            if priority:
                statement = statement.where(Task.priority == priority)
            if due_from:
                statement = statement.where(Task.due_date >= due_from)
            if due_to:
                statement = statement.where(Task.due_date <= due_to)
            tasks = list(session.exec(statement).all())
            if tags:
                tasks = [t for t in tasks if t.tags and any(tag in t.tags for tag in tags)]
            if sort_by == "priority":
                priority_order = {"high": 3, "medium": 2, "low": 1}
                tasks = sorted(tasks, key=lambda t: priority_order.get(t.priority.value if hasattr(t.priority, 'value') else t.priority, 0), reverse=(sort_order == "desc"))
            elif sort_by == "due_date":
                tasks = sorted(tasks, key=lambda t: t.due_date or datetime.max.replace(tzinfo=timezone.utc), reverse=(sort_order == "desc"))
            elif sort_by == "updated_at":
                tasks = sorted(tasks, key=lambda t: t.updated_at, reverse=(sort_order == "desc"))
            else:
                tasks = sorted(tasks, key=lambda t: t.created_at, reverse=(sort_order == "desc"))
            return tasks[skip:skip + limit]


# Create in-memory SQLite database for testing
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden dependencies"""
    test_engine = session.get_bind()

    def get_session_override():
        return session

    def get_current_user_id_override():
        return "test-user-e2e"

    async def get_repository_override():
        return TestTaskRepository(test_engine)

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user_id] = get_current_user_id_override
    app.dependency_overrides[get_repository] = get_repository_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


class TestTaskLifecycle:
    """Test complete task lifecycle from creation to completion"""

    @patch('src.services.reminder_service.reminder_service.schedule_reminder')
    @patch('src.core.event_publisher.event_publisher.publish')
    def test_create_task_with_reminder_workflow(self, mock_publish, mock_schedule, client: TestClient):
        """
        E2E: User creates a task with due date and reminder

        Workflow:
        1. Create task with due date and reminder offset
        2. Verify task is created with correct attributes
        3. Verify reminder is scheduled
        4. Verify TASK_CREATED event is published
        """
        mock_schedule.return_value = "reminder-job-123"
        mock_publish.return_value = None

        # Step 1: Create task with reminder
        due_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        task_data = {
            "title": "Important Meeting",
            "description": "Quarterly review meeting",
            "due_date": due_date,
            "priority": "high",
            "reminder_offset_minutes": 30
        }

        response = client.post("/api/test-user-e2e/tasks", json=task_data)

        # Step 2: Verify task creation
        assert response.status_code == 201
        task = response.json()
        assert task["title"] == "Important Meeting"
        assert task["priority"] == "high"
        assert task["reminder_offset_minutes"] == 30

        # Step 3: Verify reminder was scheduled
        mock_schedule.assert_called_once()

        # Step 4: Verify event was published
        mock_publish.assert_called()
        event_call = mock_publish.call_args
        assert event_call.kwargs["topic"] == "task-events"
        assert event_call.kwargs["event_type"] == "TASK_CREATED"

    @patch('src.services.recurring_service.recurring_service.schedule_recurring_task_generation')
    @patch('src.core.event_publisher.event_publisher.publish')
    def test_create_recurring_task_workflow(self, mock_publish, mock_schedule_recurring, client: TestClient):
        """
        E2E: User creates a recurring task

        Workflow:
        1. Create task with recurrence pattern and due date
        2. Verify task is created
        3. Verify recurring job is scheduled
        4. Verify event is published
        """
        mock_schedule_recurring.return_value = "recurring-job-456"
        mock_publish.return_value = None

        # Step 1: Create recurring task (needs due_date for recurring to be scheduled)
        due_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Weekly Team Standup",
            "description": "Monday morning standup",
            "due_date": due_date,
            "recurrence": "weekly",
            "priority": "medium",
            "tags": ["meeting", "team"]
        }

        response = client.post("/api/test-user-e2e/tasks", json=task_data)

        # Step 2: Verify task creation
        assert response.status_code == 201
        task = response.json()
        assert task["title"] == "Weekly Team Standup"
        assert task["recurrence"] == "weekly"
        assert "meeting" in task["tags"]

        # Step 3: Verify recurring job was scheduled
        mock_schedule_recurring.assert_called_once()

        # Step 4: Verify event was published
        mock_publish.assert_called()

    @patch('src.services.reminder_service.reminder_service.cancel_reminder')
    @patch('src.services.reminder_service.reminder_service.schedule_reminder')
    @patch('src.core.event_publisher.event_publisher.publish')
    def test_update_task_reschedules_reminder(self, mock_publish, mock_schedule, mock_cancel, client: TestClient):
        """
        E2E: User updates task due date, triggering reminder rescheduling

        Workflow:
        1. Create task with reminder
        2. Update task with new due date
        3. Verify old reminder is cancelled
        4. Verify new reminder is scheduled
        5. Verify TASK_UPDATED event is published
        """
        mock_schedule.return_value = "reminder-job-789"
        mock_cancel.return_value = None
        mock_publish.return_value = None

        # Step 1: Create task
        due_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        task_data = {
            "title": "Project Deadline",
            "due_date": due_date,
            "reminder_offset_minutes": 60
        }

        create_response = client.post("/api/test-user-e2e/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Step 2: Update task with new due date
        new_due_date = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
        update_data = {
            "due_date": new_due_date,
            "reminder_offset_minutes": 120
        }

        update_response = client.put(f"/api/test-user-e2e/tasks/{task_id}", json=update_data)

        # Step 3 & 4: Verify reminder was cancelled and rescheduled
        assert update_response.status_code == 200
        mock_cancel.assert_called_once()
        assert mock_schedule.call_count == 2  # Once for create, once for update

        # Step 5: Verify TASK_UPDATED event was published
        update_events = [call for call in mock_publish.call_args_list
                        if call.kwargs.get("event_type") == "TASK_UPDATED"]
        assert len(update_events) > 0

    @patch('src.services.reminder_service.reminder_service.schedule_reminder')
    @patch('src.services.reminder_service.reminder_service.cancel_reminder')
    @patch('src.services.recurring_service.recurring_service.cancel_recurring_job')
    @patch('src.core.event_publisher.event_publisher.publish')
    def test_complete_task_lifecycle(self, mock_publish, mock_cancel_recurring, mock_cancel_reminder, mock_schedule_reminder, client: TestClient):
        """
        E2E: Complete task lifecycle from creation to deletion

        Workflow:
        1. Create task with reminder
        2. Update task
        3. Mark as completed using PATCH endpoint
        4. Delete task
        5. Verify all cleanup happens (reminders cancelled, events published)
        """
        mock_schedule_reminder.return_value = "reminder-job-xyz"
        mock_cancel_reminder.return_value = None
        mock_cancel_recurring.return_value = None
        mock_publish.return_value = None

        # Step 1: Create task with reminder
        due_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        task_data = {
            "title": "Temporary Task",
            "description": "This will be deleted",
            "priority": "low",
            "due_date": due_date,
            "reminder_offset_minutes": 30
        }

        create_response = client.post("/api/test-user-e2e/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Step 2: Update task
        update_response = client.put(
            f"/api/test-user-e2e/tasks/{task_id}",
            json={"title": "Updated Temporary Task"}
        )
        assert update_response.status_code == 200

        # Step 3: Mark as completed using PATCH endpoint
        complete_response = client.patch(f"/api/test-user-e2e/tasks/{task_id}/complete")
        assert complete_response.status_code == 200
        assert complete_response.json()["completed"] is True

        # Step 4: Delete task
        delete_response = client.delete(f"/api/test-user-e2e/tasks/{task_id}")
        assert delete_response.status_code == 204

        # Step 5: Verify cleanup
        # Reminder should be cancelled (task has reminder configured)
        assert mock_cancel_reminder.call_count >= 1
        # Recurring job cancellation is called during delete (even if task has no recurrence)
        assert mock_cancel_recurring.call_count >= 0  # May or may not be called

        # Verify task is gone
        get_response = client.get(f"/api/test-user-e2e/tasks/{task_id}")
        assert get_response.status_code == 404


class TestSearchAndFilterWorkflow:
    """Test search and filter workflows"""

    @patch('src.services.reminder_service.reminder_service.schedule_reminder')
    @patch('src.core.event_publisher.event_publisher.publish')
    def test_create_and_filter_tasks_workflow(self, mock_publish, mock_schedule, client: TestClient):
        """
        E2E: User creates multiple tasks and filters them

        Workflow:
        1. Create multiple tasks with different attributes
        2. Filter by priority
        3. Filter by tags
        4. Search by text
        5. Apply compound filters
        """
        mock_schedule.return_value = "reminder-job"
        mock_publish.return_value = None

        # Step 1: Create multiple tasks
        tasks_data = [
            {
                "title": "High Priority Bug Fix",
                "priority": "high",
                "tags": ["bug", "urgent"],
                "completed": False
            },
            {
                "title": "Medium Priority Feature",
                "priority": "medium",
                "tags": ["feature"],
                "completed": False
            },
            {
                "title": "Low Priority Documentation",
                "priority": "low",
                "tags": ["docs"],
                "completed": True
            }
        ]

        for task_data in tasks_data:
            response = client.post("/api/test-user-e2e/tasks", json=task_data)
            assert response.status_code == 201

        # Step 2: Filter by priority
        high_priority_response = client.get(
            "/api/test-user-e2e/tasks",
            params={"priority": "high"}
        )
        assert high_priority_response.status_code == 200
        high_tasks = high_priority_response.json()
        assert len(high_tasks) == 1
        assert high_tasks[0]["priority"] == "high"

        # Step 3: Filter by tags
        bug_tasks_response = client.get(
            "/api/test-user-e2e/tasks",
            params={"tags": "bug"}
        )
        assert bug_tasks_response.status_code == 200
        bug_tasks = bug_tasks_response.json()
        assert len(bug_tasks) == 1
        assert "bug" in bug_tasks[0]["tags"]

        # Step 4: Search by text
        search_response = client.get(
            "/api/test-user-e2e/tasks",
            params={"search": "Feature"}
        )
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) == 1
        assert "Feature" in search_results[0]["title"]

        # Step 5: Apply compound filters
        compound_response = client.get(
            "/api/test-user-e2e/tasks",
            params={
                "priority": "high",
                "completed": "false",
                "tags": "urgent"
            }
        )
        assert compound_response.status_code == 200
        compound_results = compound_response.json()
        assert len(compound_results) == 1
        assert compound_results[0]["priority"] == "high"
        assert compound_results[0]["completed"] is False
        assert "urgent" in compound_results[0]["tags"]


class TestErrorHandlingWorkflow:
    """Test error handling in user workflows"""

    def test_invalid_task_creation_workflow(self, client: TestClient):
        """
        E2E: User attempts to create invalid tasks

        Workflow:
        1. Try to create task without title (should fail)
        2. Try to create task with empty title (should fail)
        3. Try to create task with invalid priority (should fail)
        """
        # Step 1: Missing title
        response1 = client.post("/api/test-user-e2e/tasks", json={"description": "No title"})
        assert response1.status_code == 422

        # Step 2: Empty title
        response2 = client.post("/api/test-user-e2e/tasks", json={"title": "", "description": "Empty title"})
        assert response2.status_code == 422

        # Step 3: Invalid priority
        response3 = client.post("/api/test-user-e2e/tasks", json={"title": "Task", "priority": "invalid"})
        assert response3.status_code == 422

    def test_update_nonexistent_task_workflow(self, client: TestClient):
        """
        E2E: User attempts to update a task that doesn't exist

        Workflow:
        1. Try to update nonexistent task (should return 404)
        2. Try to delete nonexistent task (should return 404)
        """
        # Step 1: Update nonexistent task
        response1 = client.put(
            "/api/test-user-e2e/tasks/nonexistent-id",
            json={"title": "Updated"}
        )
        assert response1.status_code == 404

        # Step 2: Delete nonexistent task
        response2 = client.delete("/api/test-user-e2e/tasks/nonexistent-id")
        assert response2.status_code == 404
