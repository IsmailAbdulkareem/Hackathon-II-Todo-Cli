"""
Real-time synchronization endpoints for task updates.

Provides WebSocket and polling endpoints for real-time task synchronization
between chat and graphical interfaces.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlmodel import Session

from src.core.auth import get_current_user_id, validate_user_ownership
from src.core.database import get_session

logger = logging.getLogger(__name__)

# Create router for real-time sync endpoints
router = APIRouter(prefix="/api", tags=["realtime"])

# Store active WebSocket connections per user
active_connections: Dict[str, List[WebSocket]] = {}


class ConnectionManager:
    """
    Manages WebSocket connections for real-time task updates.

    Maintains active connections per user and broadcasts updates
    to all connected clients for that user.
    """

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"WebSocket disconnected for user {user_id}. Remaining connections: {len(self.active_connections[user_id])}")

            # Clean up empty user entries
            if len(self.active_connections[user_id]) == 0:
                del self.active_connections[user_id]

    async def broadcast_to_user(self, user_id: str, message: dict):
        """
        Broadcast a message to all connections for a specific user.

        Args:
            user_id: User identifier
            message: Message data to broadcast
        """
        if user_id not in self.active_connections:
            return

        # Send to all active connections for this user
        disconnected = []
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to WebSocket: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, user_id)

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """
        Send a message to a specific WebSocket connection.

        Args:
            websocket: WebSocket connection
            message: Message data to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/{user_id}/sync")
async def websocket_sync_endpoint(
    websocket: WebSocket,
    user_id: str
):
    """
    WebSocket endpoint for real-time task synchronization.

    Maintains a persistent connection and pushes task updates
    to the client in real-time.

    Protocol:
    - Client connects with user_id in path
    - Server sends periodic heartbeat messages: {"type": "heartbeat", "timestamp": "..."}
    - Server sends task updates: {"type": "task_update", "event": "created|updated|deleted", "task": {...}}
    - Client can send ping: {"type": "ping"} -> Server responds with pong: {"type": "pong"}

    Args:
        websocket: WebSocket connection
        user_id: User identifier from path

    Note: Authentication should be handled via query parameter or initial message
    """
    await manager.connect(websocket, user_id)

    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            websocket,
            {
                "type": "connected",
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (with timeout for heartbeat)
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0
                )

                # Handle ping/pong
                if data.get("type") == "ping":
                    await manager.send_personal_message(
                        websocket,
                        {
                            "type": "pong",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    )

            except asyncio.TimeoutError:
                # Send heartbeat if no message received
                await manager.send_personal_message(
                    websocket,
                    {
                        "type": "heartbeat",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)


@router.get("/{user_id}/sync/poll", response_model=dict, status_code=status.HTTP_200_OK)
async def poll_sync_endpoint(
    user_id: str,
    jwt_user_id: str = Depends(get_current_user_id),
    since: Optional[str] = None,
    session: Session = Depends(get_session)
) -> dict:
    """
    Polling endpoint for task synchronization.

    Alternative to WebSocket for clients that prefer polling.
    Returns tasks that have been updated since the provided timestamp.

    Args:
        user_id: User identifier from URL
        jwt_user_id: Authenticated user ID from JWT token
        since: ISO 8601 timestamp of last sync (optional)
        session: Database session (injected)

    Returns:
        Dictionary with:
        - timestamp: Current server timestamp
        - tasks: List of tasks updated since 'since' timestamp
        - has_more: Boolean indicating if there are more updates

    Raises:
        HTTPException: 401 if JWT invalid, 403 if accessing other user's tasks
        HTTPException: 422 if 'since' timestamp is invalid
        HTTPException: 500 if database connection fails

    Example:
        GET /api/{user_id}/sync/poll?since=2024-02-14T10:30:00Z
    """
    from sqlmodel import select
    from src.models.task import Task

    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Parse 'since' timestamp if provided
        since_dt = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid 'since' timestamp format. Use ISO 8601 format."
                )

        # Query tasks updated since timestamp
        statement = select(Task).where(Task.user_id == jwt_user_id)

        if since_dt:
            statement = statement.where(Task.updated_at > since_dt)

        statement = statement.order_by(Task.updated_at.asc()).limit(100)

        tasks = session.exec(statement).all()

        # Convert tasks to dict
        task_list = [
            {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "is_recurring": task.is_recurring,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tasks": task_list,
            "has_more": len(tasks) >= 100
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Polling sync failed for user {jwt_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task updates"
        )


async def broadcast_task_update(user_id: str, event_type: str, task_data: dict):
    """
    Broadcast a task update to all connected clients for a user.

    This function should be called by the TaskService when tasks are
    created, updated, or deleted.

    Args:
        user_id: User identifier
        event_type: Event type (created, updated, deleted, completed)
        task_data: Task data dictionary
    """
    message = {
        "type": "task_update",
        "event": event_type,
        "task": task_data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    await manager.broadcast_to_user(user_id, message)
    logger.info(f"Broadcasted {event_type} event for task {task_data.get('id')} to user {user_id}")
