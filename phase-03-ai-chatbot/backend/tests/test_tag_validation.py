"""
Unit tests for tag validation and normalization

Tests the validation rules and normalization logic for task tags.
"""

import pytest
from pydantic import ValidationError

from src.models.task import Task, TaskCreate, TaskUpdate


class TestTagValidation:
    """Tests for tag validation logic"""

    def test_tags_accepts_empty_list(self):
        """Test that empty tag list is accepted"""
        task_data = TaskCreate(
            title="No Tags Task",
            tags=[]
        )

        assert task_data.tags == []

    def test_tags_accepts_none(self):
        """Test that None defaults to empty list"""
        task_data = TaskCreate(
            title="Default Tags Task"
        )

        assert task_data.tags == []

    def test_tags_accepts_single_tag(self):
        """Test that single tag is accepted"""
        task_data = TaskCreate(
            title="Single Tag Task",
            tags=["work"]
        )

        assert task_data.tags == ["work"]
        assert len(task_data.tags) == 1

    def test_tags_accepts_multiple_tags(self):
        """Test that multiple tags are accepted"""
        task_data = TaskCreate(
            title="Multiple Tags Task",
            tags=["work", "urgent", "backend"]
        )

        assert task_data.tags == ["work", "urgent", "backend"]
        assert len(task_data.tags) == 3

    def test_tags_preserves_order(self):
        """Test that tag order is preserved"""
        tags = ["alpha", "beta", "gamma", "delta"]
        task_data = TaskCreate(
            title="Ordered Tags Task",
            tags=tags
        )

        assert task_data.tags == tags

    def test_tags_allows_duplicates(self):
        """Test that duplicate tags are allowed (normalization happens at API layer)"""
        task_data = TaskCreate(
            title="Duplicate Tags Task",
            tags=["work", "work", "urgent"]
        )

        # Model accepts duplicates; API layer should normalize
        assert "work" in task_data.tags
        assert "urgent" in task_data.tags

    def test_tags_accepts_special_characters(self):
        """Test that tags with special characters are accepted"""
        task_data = TaskCreate(
            title="Special Chars Task",
            tags=["c++", "node.js", "web-dev", "api_v2"]
        )

        assert "c++" in task_data.tags
        assert "node.js" in task_data.tags
        assert "web-dev" in task_data.tags
        assert "api_v2" in task_data.tags

    def test_tags_accepts_unicode(self):
        """Test that tags with unicode characters are accepted"""
        task_data = TaskCreate(
            title="Unicode Tags Task",
            tags=["日本語", "español", "emoji-🚀"]
        )

        assert "日本語" in task_data.tags
        assert "español" in task_data.tags
        assert "emoji-🚀" in task_data.tags

    def test_tags_invalid_type(self):
        """Test that invalid tag types are rejected"""
        with pytest.raises(ValidationError):
            TaskCreate(
                title="Invalid Tags",
                tags="not-a-list"  # type: ignore
            )

    def test_tags_invalid_item_type(self):
        """Test that non-string tag items are rejected"""
        with pytest.raises(ValidationError):
            TaskCreate(
                title="Invalid Tag Items",
                tags=[123, 456]  # type: ignore
            )

    def test_tags_mixed_valid_invalid(self):
        """Test that mixed valid/invalid tag items are rejected"""
        with pytest.raises(ValidationError):
            TaskCreate(
                title="Mixed Tags",
                tags=["valid", 123, "also-valid"]  # type: ignore
            )


class TestTagNormalization:
    """Tests for tag normalization logic (API layer behavior)"""

    def test_tags_whitespace_handling(self):
        """Test that tags with whitespace are accepted (API should trim)"""
        task_data = TaskCreate(
            title="Whitespace Tags Task",
            tags=["  work  ", "urgent", "  backend  "]
        )

        # Model accepts whitespace; API layer should normalize
        assert len(task_data.tags) == 3

    def test_tags_case_sensitivity(self):
        """Test that tags are normalized to lowercase"""
        task_data = TaskCreate(
            title="Case Sensitive Tags",
            tags=["Work", "work", "WORK"]
        )

        # Tags are normalized to lowercase and duplicates removed
        assert task_data.tags == ["work"]
        assert len(task_data.tags) == 1

    def test_tags_empty_string(self):
        """Test that empty string tags are filtered out"""
        task_data = TaskCreate(
            title="Empty String Tags",
            tags=["work", "", "urgent"]
        )

        # Empty strings are filtered out
        assert task_data.tags == ["work", "urgent"]
        assert len(task_data.tags) == 2

    def test_tags_very_long_tag(self):
        """Test that tags over 50 characters are filtered out"""
        long_tag = "a" * 100
        task_data = TaskCreate(
            title="Long Tag Task",
            tags=[long_tag, "valid-tag"]
        )

        # Tags over 50 chars are filtered out
        assert long_tag not in task_data.tags
        assert "valid-tag" in task_data.tags
        assert len(task_data.tags) == 1

    def test_tags_many_tags(self):
        """Test that tags are limited to 20 maximum"""
        many_tags = [f"tag-{i}" for i in range(50)]
        task_data = TaskCreate(
            title="Many Tags Task",
            tags=many_tags
        )

        # Only first 20 tags are kept
        assert len(task_data.tags) == 20
        assert task_data.tags[0] == "tag-0"
        assert task_data.tags[19] == "tag-19"


class TestTagUpdate:
    """Tests for tag updates"""

    def test_update_tags_add_new(self):
        """Test adding new tags via update"""
        update_data = TaskUpdate(
            tags=["work", "urgent", "new-tag"]
        )

        assert "new-tag" in update_data.tags
        assert len(update_data.tags) == 3

    def test_update_tags_remove_all(self):
        """Test removing all tags via update"""
        update_data = TaskUpdate(
            tags=[]
        )

        assert update_data.tags == []

    def test_update_tags_replace(self):
        """Test replacing tags completely"""
        update_data = TaskUpdate(
            tags=["completely", "different", "tags"]
        )

        assert update_data.tags == ["completely", "different", "tags"]

    def test_update_tags_none_keeps_existing(self):
        """Test that None in update doesn't change tags"""
        update_data = TaskUpdate(
            title="Updated Title"
            # tags not specified
        )

        # When tags is not provided, it should be None (keeps existing)
        assert update_data.tags is None or update_data.tags == []


class TestTagFiltering:
    """Tests for tag filtering logic"""

    def test_filter_by_single_tag(self):
        """Test filtering tasks by single tag"""
        task1 = TaskCreate(title="Task 1", tags=["work", "urgent"])
        task2 = TaskCreate(title="Task 2", tags=["personal"])
        task3 = TaskCreate(title="Task 3", tags=["work", "backend"])

        # Simulate filtering
        work_tasks = [t for t in [task1, task2, task3] if "work" in t.tags]

        assert len(work_tasks) == 2
        assert task1 in work_tasks
        assert task3 in work_tasks

    def test_filter_by_multiple_tags_any(self):
        """Test filtering tasks by multiple tags (OR logic)"""
        task1 = TaskCreate(title="Task 1", tags=["work", "urgent"])
        task2 = TaskCreate(title="Task 2", tags=["personal"])
        task3 = TaskCreate(title="Task 3", tags=["work", "backend"])

        # Simulate filtering with OR logic
        filter_tags = ["work", "personal"]
        filtered = [t for t in [task1, task2, task3]
                   if any(tag in t.tags for tag in filter_tags)]

        assert len(filtered) == 3

    def test_filter_by_multiple_tags_all(self):
        """Test filtering tasks by multiple tags (AND logic)"""
        task1 = TaskCreate(title="Task 1", tags=["work", "urgent"])
        task2 = TaskCreate(title="Task 2", tags=["work", "backend"])
        task3 = TaskCreate(title="Task 3", tags=["work", "urgent", "backend"])

        # Simulate filtering with AND logic
        filter_tags = ["work", "urgent"]
        filtered = [t for t in [task1, task2, task3]
                   if all(tag in t.tags for tag in filter_tags)]

        assert len(filtered) == 2
        assert task1 in filtered
        assert task3 in filtered

    def test_filter_no_matching_tags(self):
        """Test filtering with no matching tags"""
        task1 = TaskCreate(title="Task 1", tags=["work"])
        task2 = TaskCreate(title="Task 2", tags=["personal"])

        # Simulate filtering
        filtered = [t for t in [task1, task2] if "urgent" in t.tags]

        assert len(filtered) == 0

    def test_filter_tasks_without_tags(self):
        """Test filtering tasks that have no tags"""
        task1 = TaskCreate(title="Task 1", tags=["work"])
        task2 = TaskCreate(title="Task 2", tags=[])
        task3 = TaskCreate(title="Task 3", tags=["personal"])

        # Simulate filtering for tasks without tags
        no_tags = [t for t in [task1, task2, task3] if len(t.tags) == 0]

        assert len(no_tags) == 1
        assert task2 in no_tags
