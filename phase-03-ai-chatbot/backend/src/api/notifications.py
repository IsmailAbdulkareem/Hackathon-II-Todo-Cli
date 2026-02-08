"""
Notifications API endpoints for Server-Sent Events (SSE).

Provides real-time notification streaming to clients.
"""

from datetime import datetime, timezone
from typing import AsyncGenerator
import asyncio
import json
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from src.core.auth import get_current_user_id
from src.core.sse_manager import notification_manager

logger = logging.getLogger(__name__)

# Create router for notification endpoints
router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def format_sse_event(event: str, data: dict, id: str = None) -> str:
    """
    Format data as SSE event.

    SSE format:
    event: <event-type>
    id: <event-id>
    data: <json-data>

    (blank line)

    Args:
        event: Event type
        data: Event data (will be JSON serialized)
        id: Optional event ID

    Returns:
        Formatted SSE event string
    """
    lines = []

    if event:
        lines.append(f"event: {event}")

    if id:
        lines.append(f"id: {id}")

    lines.append(f"data: {json.dumps(data)}")
    lines.append("")  # Blank line terminates event

    return "\n".join(lines) + "\n"


@router.get("/stream")
async def notification_stream(
    request: Request,
    user_id: str = Depends(get_current_user_id)
) -> StreamingResponse:
    """
    SSE endpoint for real-time notifications.

    Client connects with:
    ```javascript
    const eventSource = new EventSource('/api/notifications/stream', {
        headers: { 'Authorization': 'Bearer <token>' }
    });
    ```

    Args:
        request: FastAPI request
        user_id: Authenticated user ID from JWT token

    Returns:
        StreamingResponse with SSE events
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        """
        Generate SSE events for user.

        Yields SSE-formatted messages.
        """
        # Register connection
        connection_id = await notification_manager.register(user_id)

        try:
            # Send initial connection event
            yield format_sse_event(
                event="connected",
                data={
                    "user_id": user_id,
                    "connection_id": connection_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

            logger.info(f"SSE stream started for user {user_id}, connection {connection_id}")

            # Keep connection alive and send events
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info(f"Client disconnected: user {user_id}, connection {connection_id}")
                    break

                # Get pending notifications for user
                notifications = await notification_manager.get_pending(user_id)

                for notification in notifications:
                    yield format_sse_event(
                        event=notification.get("type", "notification"),
                        data=notification,
                        id=notification.get("id")
                    )

                # Send heartbeat every 30 seconds
                yield format_sse_event(
                    event="heartbeat",
                    data={"timestamp": datetime.now(timezone.utc).isoformat()}
                )

                # Wait before next check
                await asyncio.sleep(30)

        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for user {user_id}, connection {connection_id}")
        except Exception as e:
            logger.error(f"Error in SSE stream for user {user_id}: {e}", exc_info=True)
        finally:
            # Unregister connection on disconnect
            await notification_manager.unregister(user_id, connection_id)
            logger.info(f"SSE stream ended for user {user_id}, connection {connection_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/status")
async def get_notification_status(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get notification connection status for user.

    Args:
        user_id: Authenticated user ID from JWT token

    Returns:
        Connection status information
    """
    is_connected = notification_manager.is_connected(user_id)
    connection_count = notification_manager.get_connection_count(user_id)

    return {
        "user_id": user_id,
        "connected": is_connected,
        "connection_count": connection_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
