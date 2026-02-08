"""
Server-Sent Events (SSE) Manager

This module manages SSE connections and notifications for real-time updates.
"""

from typing import Dict, List, Set
import asyncio
from collections import defaultdict
import uuid
import logging

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Manage SSE connections and notifications per user.

    Thread-safe connection registry with per-user queues.
    """

    def __init__(self):
        self._connections: Dict[str, Set[str]] = defaultdict(set)  # user_id -> connection_ids
        self._queues: Dict[str, asyncio.Queue] = {}  # user_id -> notification queue
        self._lock = asyncio.Lock()

    async def register(self, user_id: str) -> str:
        """
        Register new SSE connection for user.

        Args:
            user_id: User identifier

        Returns:
            Connection ID
        """
        connection_id = str(uuid.uuid4())

        async with self._lock:
            self._connections[user_id].add(connection_id)

            # Create queue if first connection for user
            if user_id not in self._queues:
                self._queues[user_id] = asyncio.Queue()

        logger.info(f"Registered SSE connection {connection_id} for user {user_id}")
        return connection_id

    async def unregister(self, user_id: str, connection_id: str) -> None:
        """
        Unregister SSE connection.

        Args:
            user_id: User identifier
            connection_id: Connection identifier
        """
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(connection_id)

                # Clean up if no more connections
                if not self._connections[user_id]:
                    del self._connections[user_id]
                    if user_id in self._queues:
                        del self._queues[user_id]

        logger.info(f"Unregistered SSE connection {connection_id} for user {user_id}")

    async def send_notification(self, user_id: str, notification: dict) -> None:
        """
        Send notification to user's SSE stream.

        Args:
            user_id: Target user
            notification: Notification payload
        """
        async with self._lock:
            if user_id in self._queues:
                await self._queues[user_id].put(notification)
                logger.debug(f"Queued notification for user {user_id}: {notification.get('type')}")

    async def get_pending(self, user_id: str) -> List[dict]:
        """
        Get pending notifications for user (non-blocking).

        Args:
            user_id: User identifier

        Returns:
            List of notifications (empty if none pending)
        """
        notifications = []

        if user_id in self._queues:
            queue = self._queues[user_id]

            # Drain queue without blocking
            while not queue.empty():
                try:
                    notification = queue.get_nowait()
                    notifications.append(notification)
                except asyncio.QueueEmpty:
                    break

        return notifications

    def is_connected(self, user_id: str) -> bool:
        """
        Check if user has active SSE connections.

        Args:
            user_id: User identifier

        Returns:
            True if user has active connections
        """
        return user_id in self._connections and len(self._connections[user_id]) > 0

    def get_connection_count(self, user_id: str) -> int:
        """
        Get number of active connections for user.

        Args:
            user_id: User identifier

        Returns:
            Number of active connections
        """
        return len(self._connections.get(user_id, set()))


# Global instance
notification_manager = NotificationManager()
