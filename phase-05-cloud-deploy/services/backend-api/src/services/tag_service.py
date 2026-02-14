"""
Tag service for managing task tags.

Provides CRUD operations, autocomplete, and usage tracking for tags.
Tags are case-insensitive and scoped to individual users.
"""

import logging
from typing import List, Optional

from sqlalchemy import func
from sqlmodel import Session, select

from src.models.tag import Tag, TagCreate, TagUpdate

logger = logging.getLogger(__name__)


class TagService:
    """
    Service layer for tag management operations.

    Handles tag CRUD, autocomplete, usage tracking, and validation.
    All operations are scoped to the authenticated user.
    """

    def __init__(self, session: Session):
        """
        Initialize tag service.

        Args:
            session: Database session
        """
        self.session = session

    async def create_tag(self, user_id: str, tag_data: TagCreate) -> Tag:
        """
        Create a new tag for a user.

        Args:
            user_id: User identifier
            tag_data: Tag creation data (name, color)

        Returns:
            Created tag with generated ID

        Raises:
            ValueError: If tag name already exists for user (case-insensitive)
        """
        # Check for duplicate tag name (case-insensitive)
        existing_tag = await self.get_tag_by_name(user_id, tag_data.name)
        if existing_tag:
            raise ValueError(
                f"Tag '{tag_data.name}' already exists. Tag names are case-insensitive."
            )

        # Create new tag
        tag = Tag(
            user_id=user_id,
            name=tag_data.name.strip(),
            color=tag_data.color,
            usage_count=0
        )

        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)

        logger.info(f"Created tag '{tag.name}' for user {user_id}")
        return tag

    async def get_tag_by_id(self, user_id: str, tag_id: str) -> Optional[Tag]:
        """
        Get a tag by ID.

        Args:
            user_id: User identifier
            tag_id: Tag identifier

        Returns:
            Tag if found, None otherwise
        """
        statement = select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id
        )
        return self.session.exec(statement).first()

    async def get_tag_by_name(self, user_id: str, name: str) -> Optional[Tag]:
        """
        Get a tag by name (case-insensitive).

        Args:
            user_id: User identifier
            name: Tag name

        Returns:
            Tag if found, None otherwise
        """
        statement = select(Tag).where(
            func.lower(Tag.name) == name.lower().strip(),
            Tag.user_id == user_id
        )
        return self.session.exec(statement).first()

    async def get_all_tags(
        self,
        user_id: str,
        sort_by: str = "name",
        limit: Optional[int] = None
    ) -> List[Tag]:
        """
        Get all tags for a user.

        Args:
            user_id: User identifier
            sort_by: Sort field (name, usage_count, created_at)
            limit: Maximum number of tags to return

        Returns:
            List of tags
        """
        statement = select(Tag).where(Tag.user_id == user_id)

        # Apply sorting
        if sort_by == "usage_count":
            statement = statement.order_by(Tag.usage_count.desc())
        elif sort_by == "created_at":
            statement = statement.order_by(Tag.created_at.desc())
        else:  # Default to name
            statement = statement.order_by(Tag.name)

        # Apply limit
        if limit:
            statement = statement.limit(limit)

        return list(self.session.exec(statement).all())

    async def autocomplete_tags(
        self,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Tag]:
        """
        Autocomplete tag names based on partial query.

        Args:
            user_id: User identifier
            query: Partial tag name to search
            limit: Maximum number of suggestions (default: 10)

        Returns:
            List of matching tags sorted by usage count
        """
        if not query or not query.strip():
            # Return most used tags if no query
            return await self.get_all_tags(
                user_id,
                sort_by="usage_count",
                limit=limit
            )

        # Case-insensitive prefix search
        statement = select(Tag).where(
            Tag.user_id == user_id,
            func.lower(Tag.name).like(f"{query.lower().strip()}%")
        ).order_by(
            Tag.usage_count.desc()
        ).limit(limit)

        return list(self.session.exec(statement).all())

    async def update_tag(
        self,
        user_id: str,
        tag_id: str,
        tag_data: TagUpdate
    ) -> Optional[Tag]:
        """
        Update an existing tag.

        Args:
            user_id: User identifier
            tag_id: Tag identifier
            tag_data: Tag update data (name, color)

        Returns:
            Updated tag if found, None otherwise

        Raises:
            ValueError: If new name conflicts with existing tag
        """
        tag = await self.get_tag_by_id(user_id, tag_id)
        if not tag:
            return None

        # Check for name conflict if name is being updated
        if tag_data.name and tag_data.name.strip().lower() != tag.name.lower():
            existing_tag = await self.get_tag_by_name(user_id, tag_data.name)
            if existing_tag:
                raise ValueError(
                    f"Tag '{tag_data.name}' already exists. Tag names are case-insensitive."
                )

        # Update fields
        if tag_data.name:
            tag.name = tag_data.name.strip()
        if tag_data.color:
            tag.color = tag_data.color

        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)

        logger.info(f"Updated tag {tag_id} for user {user_id}")
        return tag

    async def delete_tag(self, user_id: str, tag_id: str) -> bool:
        """
        Delete a tag.

        Note: This will remove the tag from all tasks via CASCADE delete
        on the task_tags join table.

        Args:
            user_id: User identifier
            tag_id: Tag identifier

        Returns:
            True if deleted, False if not found
        """
        tag = await self.get_tag_by_id(user_id, tag_id)
        if not tag:
            return False

        self.session.delete(tag)
        self.session.commit()

        logger.info(f"Deleted tag {tag_id} for user {user_id}")
        return True

    async def increment_usage_count(self, tag_id: str) -> None:
        """
        Increment the usage count for a tag.

        Called when a tag is added to a task.

        Args:
            tag_id: Tag identifier
        """
        statement = select(Tag).where(Tag.id == tag_id)
        tag = self.session.exec(statement).first()

        if tag:
            tag.usage_count += 1
            self.session.add(tag)
            self.session.commit()

    async def decrement_usage_count(self, tag_id: str) -> None:
        """
        Decrement the usage count for a tag.

        Called when a tag is removed from a task.

        Args:
            tag_id: Tag identifier
        """
        statement = select(Tag).where(Tag.id == tag_id)
        tag = self.session.exec(statement).first()

        if tag and tag.usage_count > 0:
            tag.usage_count -= 1
            self.session.add(tag)
            self.session.commit()

    async def get_popular_tags(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Tag]:
        """
        Get most frequently used tags for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of tags to return

        Returns:
            List of tags sorted by usage count (descending)
        """
        return await self.get_all_tags(
            user_id,
            sort_by="usage_count",
            limit=limit
        )
