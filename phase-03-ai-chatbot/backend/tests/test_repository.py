"""
Unit Tests for Repository Implementations (T100)

Tests the repository interface and implementations with various scenarios.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.repository_interface import (
    TaskRepository,
    RepositoryError,
    TaskNotFoundError
)
from src.services.dapr_task_repository import DaprTaskRepository
from src.services.fallback_task_repository import FallbackTaskRepository
from src.models.task import Task, TaskCreate, TaskUpdate, PriorityEnum


class TestRepositoryInterface:
    """Tests for TaskRepository interface"""

    def test_repository_is_abstract(self):
        """Test that TaskRepository cannot be instantiated directly"""
        with pytest.raises(TypeError):
            TaskRepository()  # type: ignore


class TestDaprTaskRepository:
    """Tests for DaprTaskRepository implementation"""

    @pytest.fixture
    def mock_state_adapter(self):
        """Create mock state adapter"""
        adapter = AsyncMock()
        adapter.save = AsyncMock()
        adapter.get = AsyncMock()
        adapter.delete = AsyncMock()
        adapter.bulk_get = AsyncMock()
        return adapter

    @pytest.fixture
    def mock_pubsub_adapter(self):
        """Create mock pub/sub adapter"""
        adapter = AsyncMock()
        adapter.publish = AsyncMock()
        return adapter

    @pytest.fixture
    def mock_jobs_adapter(self):
        """Create mock jobs adapter"""
        adapter = AsyncMock()
        adapter.schedule = AsyncMock()
        adapter.delete = AsyncMock()
        return adapter

    @pytest.fixture
    def repository(self, mock_state_adapter, mock_pubsub_adapter, mock_jobs_adapter):
        """Create DaprTaskRepository with mocked adapters"""
        return DaprTaskRepository(
            state_adapter=mock_state_adapter,
            pubsub_adapter=mock_pubsub_adapter,
            jobs_adapter=mock_jobs_adapter
        )

    @pytest.mark.asyncio
    async def test_create_task(self, repository, mock_state_adapter, mock_pubsub_adapter):
        """Test creating a task"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            priority=PriorityEnum.HIGH
        )

        task = await repository.create("user-123", task_data)

        assert task.title == "Test Task"
        assert task.user_id == "user-123"
        assert task.priority == PriorityEnum.HIGH
        assert task.id is not None

        # Verify state was saved (task + index = 2 calls)
        assert mock_state_adapter.save.call_count == 2

        # Verify event was published
        mock_pubsub_adapter.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_by_id(self, repository, mock_state_adapter):
        """Test getting a task by ID"""
        mock_task_data = {
            "id": "task-123",
            "user_id": "user-123",
            "title": "Test Task",
            "description": None,
            "completed": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "due_date": None,
            "priority": "medium",
            "tags": [],
            "recurrence": "none",
            "reminder_offset_minutes": 0
        }
        mock_state_adapter.get.return_value = mock_task_data

        task = await repository.get_by_id("user-123", "task-123")

        assert task is not None
        assert task.id == "task-123"
        assert task.title == "Test Task"

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, repository, mock_state_adapter):
        """Test getting a non-existent task"""
        mock_state_adapter.get.return_value = None

        task = await repository.get_by_id("user-123", "nonexistent")

        assert task is None

    @pytest.mark.asyncio
    async def test_update_task(self, repository, mock_state_adapter, mock_pubsub_adapter):
        """Test updating a task"""
        # Mock existing task
        existing_task_data = {
            "id": "task-123",
            "user_id": "user-123",
            "title": "Old Title",
            "description": None,
            "completed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "due_date": None,
            "priority": "medium",
            "tags": [],
            "recurrence": "none",
            "reminder_offset_minutes": 0
        }
        mock_state_adapter.get.return_value = existing_task_data

        update_data = TaskUpdate(title="New Title", completed=True)

        task = await repository.update("user-123", "task-123", update_data)

        assert task is not None
        assert task.title == "New Title"
        assert task.completed is True

        # Verify state was saved
        mock_state_adapter.save.assert_called()

        # Verify event was published
        mock_pubsub_adapter.publish.assert_called()

    @pytest.mark.asyncio
    async def test_delete_task(self, repository, mock_state_adapter, mock_pubsub_adapter):
        """Test deleting a task"""
        # Mock existing task
        existing_task_data = {
            "id": "task-123",
            "user_id": "user-123",
            "title": "Test Task",
            "description": None,
            "completed": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "due_date": None,
            "priority": "medium",
            "tags": [],
            "recurrence": "none",
            "reminder_offset_minutes": 0
        }
        mock_state_adapter.get.return_value = existing_task_data

        # Mock index
        mock_state_adapter.get.side_effect = [
            existing_task_data,  # First call for get_by_id
            {"task_ids": ["task-123"]}  # Second call for index
        ]

        result = await repository.delete("user-123", "task-123")

        assert result is True

        # Verify state was deleted
        mock_state_adapter.delete.assert_called_once()

        # Verify event was published
        mock_pubsub_adapter.publish.assert_called()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task(self, repository, mock_state_adapter):
        """Test deleting a non-existent task"""
        mock_state_adapter.get.return_value = None

        result = await repository.delete("user-123", "nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_get_all_tasks(self, repository, mock_state_adapter):
        """Test getting all tasks for a user"""
        # Mock index
        mock_state_adapter.get.side_effect = [
            {"task_ids": ["task-1", "task-2"]},  # Index
        ]

        # Mock bulk get
        mock_state_adapter.bulk_get.return_value = {
            "task:user-123:task-1": {
                "id": "task-1",
                "user_id": "user-123",
                "title": "Task 1",
                "description": None,
                "completed": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "due_date": None,
                "priority": "medium",
                "tags": [],
                "recurrence": "none",
                "reminder_offset_minutes": 0
            },
            "task:user-123:task-2": {
                "id": "task-2",
                "user_id": "user-123",
                "title": "Task 2",
                "description": None,
                "completed": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "due_date": None,
                "priority": "high",
                "tags": [],
                "recurrence": "none",
                "reminder_offset_minutes": 0
            }
        }

        tasks = await repository.get_all("user-123")

        assert len(tasks) == 2
        assert tasks[0].id == "task-1"
        assert tasks[1].id == "task-2"

    @pytest.mark.asyncio
    async def test_search_tasks_by_query(self, repository, mock_state_adapter):
        """Test searching tasks by text query"""
        # Mock get_all to return tasks
        mock_state_adapter.get.return_value = {"task_ids": ["task-1", "task-2"]}
        mock_state_adapter.bulk_get.return_value = {
            "task:user-123:task-1": {
                "id": "task-1",
                "user_id": "user-123",
                "title": "Important Meeting",
                "description": None,
                "completed": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "due_date": None,
                "priority": "high",
                "tags": [],
                "recurrence": "none",
                "reminder_offset_minutes": 0
            },
            "task:user-123:task-2": {
                "id": "task-2",
                "user_id": "user-123",
                "title": "Buy Groceries",
                "description": None,
                "completed": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "due_date": None,
                "priority": "low",
                "tags": [],
                "recurrence": "none",
                "reminder_offset_minutes": 0
            }
        }

        tasks = await repository.search("user-123", query="meeting")

        assert len(tasks) == 1
        assert tasks[0].title == "Important Meeting"

    @pytest.mark.asyncio
    async def test_count_tasks(self, repository, mock_state_adapter):
        """Test counting tasks"""
        mock_state_adapter.get.return_value = {"task_ids": ["task-1", "task-2", "task-3"]}
        mock_state_adapter.bulk_get.return_value = {
            f"task:user-123:task-{i}": {
                "id": f"task-{i}",
                "user_id": "user-123",
                "title": f"Task {i}",
                "description": None,
                "completed": i == 1,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "due_date": None,
                "priority": "medium",
                "tags": [],
                "recurrence": "none",
                "reminder_offset_minutes": 0
            }
            for i in range(1, 4)
        }

        total_count = await repository.count("user-123")
        completed_count = await repository.count("user-123", completed=True)

        assert total_count == 3
        assert completed_count == 1


class TestFallbackTaskRepository:
    """Tests for FallbackTaskRepository implementation"""

    @pytest.mark.asyncio
    async def test_repository_interface_compliance(self):
        """Test that FallbackTaskRepository implements TaskRepository"""
        repo = FallbackTaskRepository()
        assert isinstance(repo, TaskRepository)

    # Additional tests would require database setup
    # These are integration tests that should be run with a test database
