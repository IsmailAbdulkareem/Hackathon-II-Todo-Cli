"""
Integration tests for Task API endpoints

Tests the full HTTP request-response cycle including routing, validation,
service integration, and error handling using FastAPI's dependency injection.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from typing import List, Optional

from main import app
from src.models.task import Task, TaskCreate, TaskUpdate, PriorityEnum, RecurrenceEnum
from src.core.database import get_session
from src.core.auth import get_current_user_id
from src.core.dependencies import get_repository
from src.core.repository_interface import TaskRepository
from src.services.fallback_task_repository import FallbackTaskRepository


class TestTaskRepository(FallbackTaskRepository):
    """Test repository that uses the test session"""

    def __init__(self, test_engine):
        self.test_engine = test_engine

    async def create(self, user_id: str, task_data: TaskCreate) -> Task:
        """Create using test engine"""
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
        """Get by ID using test engine"""
        from sqlmodel import select
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()
            return task

    async def update(self, user_id: str, task_id: str, task_data: TaskUpdate) -> Optional[Task]:
        """Update using test engine"""
        from sqlmodel import select
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
        """Delete using test engine"""
        from sqlmodel import select
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return False

            session.delete(task)
            session.commit()
            return True

    async def get_all(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all using test engine"""
        from sqlmodel import select
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
            tasks = session.exec(statement).all()
            return list(tasks)

    async def count(self, user_id: str, completed: Optional[bool] = None) -> int:
        """Count using test engine"""
        from sqlmodel import select
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.user_id == user_id)

            if completed is not None:
                statement = statement.where(Task.completed == completed)

            tasks = session.exec(statement).all()
            return len(list(tasks))

    async def search(self, user_id: str, query: Optional[str] = None,
                    completed: Optional[bool] = None, priority: Optional[str] = None,
                    tags: Optional[List[str]] = None, due_from: Optional[datetime] = None,
                    due_to: Optional[datetime] = None, sort_by: str = "created_at",
                    sort_order: str = "desc", skip: int = 0, limit: int = 100) -> List[Task]:
        """Search using test engine"""
        from sqlmodel import select, or_
        with Session(self.test_engine) as session:
            statement = select(Task).where(Task.user_id == user_id)

            if query:
                statement = statement.where(
                    or_(
                        Task.title.ilike(f"%{query}%"),
                        Task.description.ilike(f"%{query}%")
                    )
                )

            if completed is not None:
                statement = statement.where(Task.completed == completed)

            if priority:
                statement = statement.where(Task.priority == priority)

            if due_from:
                statement = statement.where(Task.due_date >= due_from)

            if due_to:
                statement = statement.where(Task.due_date <= due_to)

            # Get all matching tasks
            tasks = list(session.exec(statement).all())

            # Apply tag filtering in memory
            if tags:
                tasks = [t for t in tasks if t.tags and any(tag in t.tags for tag in tags)]

            # Sort in memory
            if sort_by == "priority":
                priority_order = {"high": 3, "medium": 2, "low": 1}
                tasks = sorted(tasks, key=lambda t: priority_order.get(t.priority.value if hasattr(t.priority, 'value') else t.priority, 0), reverse=(sort_order == "desc"))
            elif sort_by == "due_date":
                tasks = sorted(tasks, key=lambda t: t.due_date or datetime.max.replace(tzinfo=timezone.utc), reverse=(sort_order == "desc"))
            elif sort_by == "updated_at":
                tasks = sorted(tasks, key=lambda t: t.updated_at, reverse=(sort_order == "desc"))
            else:  # Default to created_at
                tasks = sorted(tasks, key=lambda t: t.created_at, reverse=(sort_order == "desc"))

            # Paginate
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
        return "test-user-456"

    async def get_repository_override():
        """Return a test repository that uses the test database"""
        return TestTaskRepository(test_engine)

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user_id] = get_current_user_id_override
    app.dependency_overrides[get_repository] = get_repository_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_task(session: Session):
    """Create a sample task in the database"""
    task = Task(
        id="test-task-123",
        user_id="test-user-456",
        title="Test Task",
        description="Test Description",
        completed=False,
        due_date=datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc),
        priority=PriorityEnum.MEDIUM,
        tags=["test", "integration"],
        recurrence=RecurrenceEnum.NONE,
        reminder_offset_minutes=30,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


class TestGetTasks:
    """Tests for GET /api/{user_id}/tasks endpoint"""

    def test_get_tasks_success(self, client: TestClient, sample_task: Task):
        """Test successfully retrieving tasks for a user"""
        response = client.get("/api/test-user-456/tasks")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "test-task-123"
        assert data[0]["title"] == "Test Task"

    def test_get_tasks_empty(self, client: TestClient):
        """Test retrieving tasks when user has no tasks"""
        response = client.get("/api/test-user-456/tasks")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_tasks_with_filters(self, client: TestClient, sample_task: Task):
        """Test retrieving tasks with query filters"""
        response = client.get(
            "/api/test-user-456/tasks",
            params={"completed": "false", "priority": "medium"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "medium"


class TestCreateTask:
    """Tests for POST /api/{user_id}/tasks endpoint"""

    @patch('src.services.reminder_service.reminder_service.schedule_reminder')
    @patch('src.core.event_publisher.event_publisher.publish')
    def test_create_task_minimal(self, mock_publish, mock_schedule, client: TestClient):
        """Test creating a task with minimal required fields"""
        mock_schedule.return_value = "reminder-job-id"
        mock_publish.return_value = None

        task_data = {
            "title": "New Task",
            "description": "Task description"
        }

        response = client.post("/api/test-user-456/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["user_id"] == "test-user-456"
        assert "id" in data

    def test_create_task_invalid_title(self, client: TestClient):
        """Test creating a task with invalid title"""
        task_data = {
            "title": "",  # Empty title
            "description": "Description"
        }

        response = client.post("/api/test-user-456/tasks", json=task_data)

        assert response.status_code == 422  # Validation error

    def test_create_task_missing_title(self, client: TestClient):
        """Test creating a task without required title field"""
        task_data = {
            "description": "Description"
        }

        response = client.post("/api/test-user-456/tasks", json=task_data)

        assert response.status_code == 422  # Validation error


class TestUpdateTask:
    """Tests for PUT /api/{user_id}/tasks/{task_id} endpoint"""

    @patch('src.services.reminder_service.reminder_service.cancel_reminder')
    @patch('src.services.reminder_service.reminder_service.schedule_reminder')
    @patch('src.core.event_publisher.event_publisher.publish')
    def test_update_task_success(self, mock_publish, mock_schedule, mock_cancel, client: TestClient, sample_task: Task):
        """Test successfully updating a task"""
        mock_cancel.return_value = None
        mock_schedule.return_value = "reminder-job-id"
        mock_publish.return_value = None

        update_data = {
            "title": "Updated Title",
            "priority": "high"
        }

        response = client.put("/api/test-user-456/tasks/test-task-123", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "high"

    def test_update_task_not_found(self, client: TestClient):
        """Test updating a non-existent task"""
        update_data = {
            "title": "Updated Title"
        }

        response = client.put("/api/test-user-456/tasks/nonexistent-id", json=update_data)

        assert response.status_code == 404


class TestDeleteTask:
    """Tests for DELETE /api/{user_id}/tasks/{task_id} endpoint"""

    @patch('src.services.reminder_service.reminder_service.cancel_reminder')
    @patch('src.services.recurring_service.recurring_service.cancel_recurring_job')
    def test_delete_task_success(self, mock_cancel_recurring, mock_cancel_reminder, client: TestClient, sample_task: Task):
        """Test successfully deleting a task"""
        mock_cancel_reminder.return_value = None
        mock_cancel_recurring.return_value = None

        response = client.delete("/api/test-user-456/tasks/test-task-123")

        assert response.status_code == 204

    def test_delete_task_not_found(self, client: TestClient):
        """Test deleting a non-existent task"""
        response = client.delete("/api/test-user-456/tasks/nonexistent-id")

        assert response.status_code == 404


@pytest.fixture
def multiple_tasks(session: Session):
    """Create multiple tasks with different attributes for filtering tests"""
    tasks = [
        Task(
            id="task-1",
            user_id="test-user-456",
            title="High Priority Bug",
            description="Fix critical bug in authentication",
            completed=False,
            due_date=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            priority=PriorityEnum.HIGH,
            tags=["bug", "urgent", "backend"],
            recurrence=RecurrenceEnum.NONE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        Task(
            id="task-2",
            user_id="test-user-456",
            title="Medium Priority Feature",
            description="Add user profile page",
            completed=False,
            due_date=datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc),
            priority=PriorityEnum.MEDIUM,
            tags=["feature", "frontend"],
            recurrence=RecurrenceEnum.NONE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        Task(
            id="task-3",
            user_id="test-user-456",
            title="Low Priority Documentation",
            description="Update API documentation",
            completed=True,
            due_date=datetime(2026, 2, 10, 12, 0, 0, tzinfo=timezone.utc),
            priority=PriorityEnum.LOW,
            tags=["docs", "backend"],
            recurrence=RecurrenceEnum.NONE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        Task(
            id="task-4",
            user_id="test-user-456",
            title="Urgent Security Patch",
            description="Apply security updates",
            completed=False,
            due_date=datetime(2026, 2, 8, 12, 0, 0, tzinfo=timezone.utc),
            priority=PriorityEnum.HIGH,
            tags=["security", "urgent"],
            recurrence=RecurrenceEnum.NONE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
    ]

    for task in tasks:
        session.add(task)
    session.commit()

    for task in tasks:
        session.refresh(task)

    return tasks


class TestSearchAndFilter:
    """Tests for search and filter functionality"""

    def test_filter_by_priority(self, client: TestClient, multiple_tasks):
        """Test filtering tasks by priority"""
        response = client.get("/api/test-user-456/tasks", params={"priority": "high"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(task["priority"] == "high" for task in data)

    def test_filter_by_completion_status(self, client: TestClient, multiple_tasks):
        """Test filtering tasks by completion status"""
        response = client.get("/api/test-user-456/tasks", params={"completed": "false"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(task["completed"] is False for task in data)

    def test_filter_by_tags(self, client: TestClient, multiple_tasks):
        """Test filtering tasks by tags"""
        response = client.get("/api/test-user-456/tasks", params={"tags": "urgent"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("urgent" in task["tags"] for task in data)

    def test_filter_by_due_date_range(self, client: TestClient, multiple_tasks):
        """Test filtering tasks by due date range"""
        response = client.get(
            "/api/test-user-456/tasks",
            params={
                "due_date_start": "2026-02-01",
                "due_date_end": "2026-02-20"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        for task in data:
            due_date = datetime.fromisoformat(task["due_date"].replace("Z", "+00:00"))
            assert datetime(2026, 2, 1, tzinfo=timezone.utc) <= due_date <= datetime(2026, 2, 20, tzinfo=timezone.utc)

    def test_text_search_in_title(self, client: TestClient, multiple_tasks):
        """Test text search in task titles"""
        response = client.get("/api/test-user-456/tasks", params={"search": "Priority"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("Priority" in task["title"] for task in data)

    def test_text_search_in_description(self, client: TestClient, multiple_tasks):
        """Test text search in task descriptions"""
        response = client.get("/api/test-user-456/tasks", params={"search": "authentication"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "authentication" in data[0]["description"]

    def test_compound_filter(self, client: TestClient, multiple_tasks):
        """Test filtering with multiple criteria"""
        response = client.get(
            "/api/test-user-456/tasks",
            params={
                "priority": "high",
                "completed": "false",
                "tags": "urgent"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for task in data:
            assert task["priority"] == "high"
            assert task["completed"] is False
            assert "urgent" in task["tags"]

    def test_sort_by_due_date(self, client: TestClient, multiple_tasks):
        """Test sorting tasks by due date"""
        response = client.get(
            "/api/test-user-456/tasks",
            params={"sort_by": "due_date", "sort_order": "asc"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

        # Verify tasks are sorted by due date ascending
        due_dates = [datetime.fromisoformat(task["due_date"].replace("Z", "+00:00")) for task in data]
        assert due_dates == sorted(due_dates)

    def test_sort_by_priority(self, client: TestClient, multiple_tasks):
        """Test sorting tasks by priority"""
        response = client.get(
            "/api/test-user-456/tasks",
            params={"sort_by": "priority", "sort_order": "desc"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

        # Verify high priority tasks come first
        priority_order = {"high": 3, "medium": 2, "low": 1}
        priorities = [priority_order[task["priority"]] for task in data]
        assert priorities == sorted(priorities, reverse=True)

    def test_empty_search_results(self, client: TestClient, multiple_tasks):
        """Test search with no matching results"""
        response = client.get("/api/test-user-456/tasks", params={"search": "nonexistent"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestTagFiltering:
    """Tests for tag-based filtering functionality (T046)"""

    def test_filter_by_single_tag(self, client: TestClient, multiple_tasks):
        """Test filtering tasks by a single tag"""
        response = client.get("/api/test-user-456/tasks", params={"tags": "backend"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("backend" in task["tags"] for task in data)

    def test_filter_by_multiple_tags_or_logic(self, client: TestClient, multiple_tasks):
        """Test filtering tasks by multiple tags (OR logic - any match)"""
        response = client.get("/api/test-user-456/tasks", params={"tags": "bug,docs"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Should return tasks with either "bug" or "docs" tag
        for task in data:
            assert "bug" in task["tags"] or "docs" in task["tags"]

    def test_filter_by_multiple_tags_with_spaces(self, client: TestClient, multiple_tasks):
        """Test filtering with comma-separated tags including whitespace"""
        response = client.get("/api/test-user-456/tasks", params={"tags": "urgent, security"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Should handle whitespace and return tasks with either tag
        for task in data:
            assert "urgent" in task["tags"] or "security" in task["tags"]

    def test_filter_by_nonexistent_tag(self, client: TestClient, multiple_tasks):
        """Test filtering by a tag that doesn't exist"""
        response = client.get("/api/test-user-456/tasks", params={"tags": "nonexistent"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_filter_by_empty_tag_parameter(self, client: TestClient, multiple_tasks):
        """Test filtering with empty tag parameter"""
        response = client.get("/api/test-user-456/tasks", params={"tags": ""})

        assert response.status_code == 200
        data = response.json()
        # Empty tag parameter should return all tasks (no filtering)
        assert len(data) == 4

    def test_tag_filter_with_priority_filter(self, client: TestClient, multiple_tasks):
        """Test combining tag filter with priority filter"""
        response = client.get(
            "/api/test-user-456/tasks",
            params={"tags": "urgent", "priority": "high"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for task in data:
            assert "urgent" in task["tags"]
            assert task["priority"] == "high"

    def test_tag_filter_with_completion_status(self, client: TestClient, multiple_tasks):
        """Test combining tag filter with completion status"""
        response = client.get(
            "/api/test-user-456/tasks",
            params={"tags": "backend", "completed": "false"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        for task in data:
            assert "backend" in task["tags"]
            assert task["completed"] is False

    def test_tag_filter_with_text_search(self, client: TestClient, multiple_tasks):
        """Test combining tag filter with text search"""
        response = client.get(
            "/api/test-user-456/tasks",
            params={"tags": "urgent", "search": "Bug"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "urgent" in data[0]["tags"]
        assert "Bug" in data[0]["title"]

    def test_tag_filter_with_sorting(self, client: TestClient, multiple_tasks):
        """Test tag filtering with sorting by priority"""
        response = client.get(
            "/api/test-user-456/tasks",
            params={"tags": "backend,urgent", "sort_by": "priority", "sort_order": "desc"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Verify all tasks have at least one of the tags
        for task in data:
            assert "backend" in task["tags"] or "urgent" in task["tags"]

        # Verify sorting by priority (high to low)
        priority_order = {"high": 3, "medium": 2, "low": 1}
        priorities = [priority_order[task["priority"]] for task in data]
        assert priorities == sorted(priorities, reverse=True)

    def test_tag_filter_case_sensitivity(self, client: TestClient, multiple_tasks):
        """Test that tag filtering is case-sensitive (tags are normalized to lowercase)"""
        # Tags are stored as lowercase, so uppercase search should not match
        response = client.get("/api/test-user-456/tasks", params={"tags": "URGENT"})

        assert response.status_code == 200
        data = response.json()
        # Should return 0 results since tags are lowercase and search is case-sensitive
        assert len(data) == 0

        # Lowercase should work
        response = client.get("/api/test-user-456/tasks", params={"tags": "urgent"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
