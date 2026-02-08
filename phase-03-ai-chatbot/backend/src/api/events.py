"""
Event Subscriber Endpoints (T088)

This module implements Dapr pub/sub subscriber endpoints for consuming
task-related events from various topics.
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime, timezone

from src.services.audit_service import audit_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/task-events")
async def handle_task_events(request: Request):
    """
    Dapr pub/sub subscriber endpoint for task-events topic.

    Handles events: TASK_CREATED, TASK_UPDATED, TASK_COMPLETED, TASK_DELETED

    Args:
        request: FastAPI request containing Dapr CloudEvent

    Returns:
        Success response for Dapr
    """
    try:
        # Parse Dapr CloudEvent
        event_data = await request.json()

        # Extract event details
        event_type = event_data.get("type", "unknown")
        data = event_data.get("data", {})

        logger.info(f"Received task event: {event_type}")

        # Log to audit service
        await audit_service.log_event(
            event_type=event_type,
            topic="task-events",
            data=data,
            timestamp=datetime.now(timezone.utc)
        )

        # Return success to Dapr
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing task event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/task-reminders")
async def handle_task_reminders(request: Request):
    """
    Dapr pub/sub subscriber endpoint for task-reminders topic.

    Handles events: REMINDER_DUE, REMINDER_SCHEDULED, REMINDER_CANCELLED

    Args:
        request: FastAPI request containing Dapr CloudEvent

    Returns:
        Success response for Dapr
    """
    try:
        # Parse Dapr CloudEvent
        event_data = await request.json()

        # Extract event details
        event_type = event_data.get("type", "unknown")
        data = event_data.get("data", {})

        logger.info(f"Received reminder event: {event_type}")

        # Log to audit service
        await audit_service.log_event(
            event_type=event_type,
            topic="task-reminders",
            data=data,
            timestamp=datetime.now(timezone.utc)
        )

        # Additional processing for reminder events
        if event_type == "REMINDER_DUE":
            task_id = data.get("task_id")
            logger.info(f"Reminder due for task: {task_id}")
            # Could trigger additional notifications here

        # Return success to Dapr
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing reminder event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/task-recurring")
async def handle_task_recurring(request: Request):
    """
    Dapr pub/sub subscriber endpoint for task-recurring topic.

    Handles events: RECURRING_TASK_GENERATED, RECURRING_TASK_SCHEDULED

    Args:
        request: FastAPI request containing Dapr CloudEvent

    Returns:
        Success response for Dapr
    """
    try:
        # Parse Dapr CloudEvent
        event_data = await request.json()

        # Extract event details
        event_type = event_data.get("type", "unknown")
        data = event_data.get("data", {})

        logger.info(f"Received recurring task event: {event_type}")

        # Log to audit service
        await audit_service.log_event(
            event_type=event_type,
            topic="task-recurring",
            data=data,
            timestamp=datetime.now(timezone.utc)
        )

        # Additional processing for recurring task events
        if event_type == "RECURRING_TASK_GENERATED":
            original_task_id = data.get("original_task_id")
            new_task_id = data.get("new_task_id")
            logger.info(f"Recurring task generated: {original_task_id} -> {new_task_id}")

        # Return success to Dapr
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing recurring task event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription endpoint.

    Tells Dapr which topics this service subscribes to and which
    endpoints should handle events from each topic.

    Returns:
        List of subscription configurations
    """
    return [
        {
            "pubsubname": "redis-pubsub",
            "topic": "task-events",
            "route": "/events/task-events"
        },
        {
            "pubsubname": "redis-pubsub",
            "topic": "task-reminders",
            "route": "/events/task-reminders"
        },
        {
            "pubsubname": "redis-pubsub",
            "topic": "task-recurring",
            "route": "/events/task-recurring"
        }
    ]
