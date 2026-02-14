"""
Retry handler for email delivery with exponential backoff.

Implements retry logic with:
- 3 attempts maximum
- Delays: 0s (immediate), 5min, 15min
- Delivery status tracking
- Event publishing for delivery results
"""

import asyncio
import logging
from typing import Optional

from .config import settings
from .dapr_client import get_dapr_client
from .email_sender import get_email_sender

logger = logging.getLogger(__name__)


class RetryHandler:
    """
    Retry handler for email delivery with exponential backoff.

    Attempts email delivery up to 3 times with increasing delays:
    - Attempt 1: Immediate (0s delay)
    - Attempt 2: 5 minutes delay
    - Attempt 3: 15 minutes delay
    """

    def __init__(self):
        """Initialize retry handler."""
        self.email_sender = get_email_sender()
        self.dapr_client = get_dapr_client()
        self.max_attempts = settings.MAX_RETRY_ATTEMPTS
        self.retry_delays = settings.RETRY_DELAYS

    async def send_with_retry(
        self,
        reminder_id: str,
        user_id: str,
        task_id: str,
        task_title: str,
        user_email: str,
        scheduled_time: str,
        reminder_type: str
    ) -> bool:
        """
        Send email with retry logic.

        Args:
            reminder_id: Reminder identifier
            user_id: User identifier
            task_id: Task identifier
            task_title: Task title for email
            user_email: Recipient email address
            scheduled_time: Scheduled reminder time
            reminder_type: Reminder type (15min, 1hr, 1day, 1week, custom)

        Returns:
            True if email sent successfully, False if all attempts failed
        """
        for attempt in range(1, self.max_attempts + 1):
            logger.info(
                f"Attempting to send reminder email (attempt {attempt}/{self.max_attempts}): "
                f"reminder_id={reminder_id}, task_id={task_id}, email={user_email}"
            )

            # Apply delay for retry attempts (not for first attempt)
            if attempt > 1:
                delay = self.retry_delays[attempt - 1]
                logger.info(f"Waiting {delay} seconds before retry attempt {attempt}")
                await asyncio.sleep(delay)

            # Attempt to send email
            success, error_message = await self.email_sender.send_reminder_email(
                to_email=user_email,
                task_title=task_title,
                task_id=task_id,
                scheduled_time=scheduled_time,
                reminder_type=reminder_type
            )

            if success:
                # Email sent successfully
                logger.info(
                    f"Reminder email sent successfully on attempt {attempt}: "
                    f"reminder_id={reminder_id}"
                )

                # Publish ReminderDelivered event with success status
                await self.dapr_client.publish_reminder_delivered(
                    reminder_id=reminder_id,
                    user_id=user_id,
                    task_id=task_id,
                    delivery_status="sent",
                    attempt_number=attempt,
                    error_message=None
                )

                return True
            else:
                # Email failed
                logger.warning(
                    f"Reminder email failed on attempt {attempt}/{self.max_attempts}: "
                    f"reminder_id={reminder_id}, error={error_message}"
                )

                # If this was the last attempt, publish failure event
                if attempt == self.max_attempts:
                    logger.error(
                        f"All retry attempts exhausted for reminder {reminder_id}. "
                        f"Email delivery failed permanently."
                    )

                    # Publish ReminderDelivered event with failed status
                    await self.dapr_client.publish_reminder_delivered(
                        reminder_id=reminder_id,
                        user_id=user_id,
                        task_id=task_id,
                        delivery_status="failed",
                        attempt_number=attempt,
                        error_message=error_message
                    )

                    return False

                # Continue to next retry attempt
                continue

        # Should not reach here, but return False as fallback
        return False

    async def send_immediate(
        self,
        reminder_id: str,
        user_id: str,
        task_id: str,
        task_title: str,
        user_email: str,
        scheduled_time: str,
        reminder_type: str
    ) -> bool:
        """
        Send email immediately without retry logic.

        Useful for testing or when retry is not desired.

        Args:
            reminder_id: Reminder identifier
            user_id: User identifier
            task_id: Task identifier
            task_title: Task title for email
            user_email: Recipient email address
            scheduled_time: Scheduled reminder time
            reminder_type: Reminder type

        Returns:
            True if email sent successfully, False otherwise
        """
        logger.info(f"Sending immediate reminder email: reminder_id={reminder_id}")

        success, error_message = await self.email_sender.send_reminder_email(
            to_email=user_email,
            task_title=task_title,
            task_id=task_id,
            scheduled_time=scheduled_time,
            reminder_type=reminder_type
        )

        # Publish delivery event
        await self.dapr_client.publish_reminder_delivered(
            reminder_id=reminder_id,
            user_id=user_id,
            task_id=task_id,
            delivery_status="sent" if success else "failed",
            attempt_number=1,
            error_message=error_message
        )

        return success


# Global retry handler instance
_retry_handler: Optional[RetryHandler] = None


def get_retry_handler() -> RetryHandler:
    """
    Get or create the global retry handler instance.

    Returns:
        RetryHandler instance
    """
    global _retry_handler
    if _retry_handler is None:
        _retry_handler = RetryHandler()
    return _retry_handler
