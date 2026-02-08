"""
Internal API endpoints for Dapr callbacks.

These endpoints are called by Dapr Jobs API when scheduled jobs trigger.
They should not be exposed publicly.
"""

from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlmodel import Session, select

from src.core.database import get_session
from src.core.event_publisher import event_publisher
from src.models.task import Task
from src.services.recurring_service import recurring_service
from src.services.reminder_service import reminder_service

# Create router for internal endpoints
router = APIRouter(prefix="/api/internal", tags=["internal"])


@router.post("/reminders/trigger")
async def trigger_reminder(request: Request):
    """
    Callback endpoint for reminder jobs.

    Called by Dapr Jobs API when reminder time arrives.

    Args:
        request: FastAPI request containing job data

    Returns:
        Success status
    """
    try:
        payload = await request.json()

        task_id = payload.get("task_id")
        user_id = payload.get("user_id")

        if not task_id or not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing task_id or user_id in payload"
            )

        # Publish reminder event to pub/sub for audit
        await event_publisher.publish(
            topic="task-reminders",
            event_type="REMINDER_DUE",
            task_id=task_id,
            payload={
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

        return {"status": "success", "task_id": task_id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger reminder: {str(e)}"
        )


@router.post("/recurring/generate")
async def generate_recurring_instance(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Callback endpoint for recurring task generation jobs.

    Called by Dapr Jobs API on schedule (daily/weekly/monthly).

    Args:
        request: FastAPI request containing job data
        session: Database session

    Returns:
        Success status with new task ID
    """
    try:
        payload = await request.json()

        task_id = payload.get("task_id")
        user_id = payload.get("user_id")
        recurrence_pattern = payload.get("recurrence_pattern")

        if not task_id or not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing task_id or user_id in payload"
            )

        # Get parent task
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        parent_task = session.exec(statement).first()

        if parent_task is None:
            # Parent task deleted, cancel job
            await recurring_service.cancel_recurring_job(task_id)
            return {
                "status": "cancelled",
                "reason": "parent_task_deleted",
                "task_id": task_id
            }

        # Generate new task instance
        new_task = await recurring_service.generate_next_instance(parent_task, user_id)

        if new_task is None:
            return {
                "status": "skipped",
                "reason": "invalid_configuration",
                "task_id": task_id
            }

        # Save new task to database
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        # Schedule reminder if configured
        if new_task.reminder_offset_minutes and new_task.reminder_offset_minutes > 0 and new_task.due_date:
            reminder_time = reminder_service.calculate_reminder_time(
                new_task.due_date,
                new_task.reminder_offset_minutes
            )
            await reminder_service.schedule_reminder(
                new_task.id,
                user_id,
                reminder_time
            )

        # Publish event
        await event_publisher.publish(
            topic="task-recurring",
            event_type="TASK_CREATED",
            task_id=new_task.id,
            payload={
                "parent_task_id": task_id,
                "recurrence_pattern": recurrence_pattern,
                "user_id": user_id
            }
        )

        return {
            "status": "success",
            "new_task_id": new_task.id,
            "parent_task_id": task_id
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recurring instance: {str(e)}"
        )
