"""
Email sender service using Resend API.

Handles email delivery for task reminders with:
- HTML email templates
- Error handling
- Delivery status tracking
"""

import logging
from typing import Optional

import httpx

from .config import settings

logger = logging.getLogger(__name__)


class EmailSender:
    """
    Email sender service using Resend API.

    Sends reminder notifications via email with formatted templates.
    """

    def __init__(self):
        """Initialize email sender with Resend API key."""
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.RESEND_FROM_EMAIL
        self.from_name = settings.RESEND_FROM_NAME
        self.base_url = "https://api.resend.com"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def send_reminder_email(
        self,
        to_email: str,
        task_title: str,
        task_id: str,
        scheduled_time: str,
        reminder_type: str
    ) -> tuple[bool, Optional[str]]:
        """
        Send a reminder email for a task.

        Args:
            to_email: Recipient email address
            task_title: Task title
            task_id: Task identifier
            scheduled_time: Scheduled reminder time (ISO 8601)
            reminder_type: Reminder type (15min, 1hr, 1day, 1week, custom)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Format subject
            subject = settings.REMINDER_EMAIL_SUBJECT.format(task_title=task_title)

            # Generate email body
            html_body = self._generate_html_body(
                task_title=task_title,
                task_id=task_id,
                scheduled_time=scheduled_time,
                reminder_type=reminder_type
            )

            text_body = self._generate_text_body(
                task_title=task_title,
                scheduled_time=scheduled_time,
                reminder_type=reminder_type
            )

            # Send email via Resend API
            response = await self.client.post(
                f"{self.base_url}/emails",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": f"{self.from_name} <{self.from_email}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_body,
                    "text": text_body
                }
            )

            if response.status_code == 200:
                logger.info(f"Reminder email sent successfully to {to_email} for task {task_id}")
                return True, None
            else:
                error_msg = f"Resend API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False, error_msg

        except httpx.HTTPError as e:
            error_msg = f"HTTP error sending email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _generate_html_body(
        self,
        task_title: str,
        task_id: str,
        scheduled_time: str,
        reminder_type: str
    ) -> str:
        """
        Generate HTML email body.

        Args:
            task_title: Task title
            task_id: Task identifier
            scheduled_time: Scheduled reminder time
            reminder_type: Reminder type

        Returns:
            HTML email body
        """
        reminder_label = self._get_reminder_label(reminder_type)

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Reminder</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        h1 {{
            color: #1f2937;
            font-size: 24px;
            margin: 0 0 10px 0;
        }}
        .reminder-type {{
            display: inline-block;
            background: #eff6ff;
            color: #1e40af;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
        }}
        .task-title {{
            background: #f9fafb;
            border-left: 4px solid #3b82f6;
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .task-title h2 {{
            margin: 0;
            font-size: 18px;
            color: #1f2937;
        }}
        .details {{
            margin: 20px 0;
            color: #6b7280;
            font-size: 14px;
        }}
        .button {{
            display: inline-block;
            background: #3b82f6;
            color: #ffffff;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            color: #9ca3af;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">⏰</div>
            <h1>Task Reminder</h1>
            <span class="reminder-type">{reminder_label}</span>
        </div>

        <div class="task-title">
            <h2>{task_title}</h2>
        </div>

        <div class="details">
            <p>This is a reminder for your task scheduled at:</p>
            <p><strong>{scheduled_time}</strong></p>
        </div>

        <div style="text-align: center;">
            <a href="https://taskai.app/tasks/{task_id}" class="button">View Task</a>
        </div>

        <div class="footer">
            <p>You're receiving this email because you set up a reminder for this task.</p>
            <p>&copy; 2024 TaskAI. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

    def _generate_text_body(
        self,
        task_title: str,
        scheduled_time: str,
        reminder_type: str
    ) -> str:
        """
        Generate plain text email body.

        Args:
            task_title: Task title
            scheduled_time: Scheduled reminder time
            reminder_type: Reminder type

        Returns:
            Plain text email body
        """
        reminder_label = self._get_reminder_label(reminder_type)

        return f"""
⏰ Task Reminder ({reminder_label})

{task_title}

This is a reminder for your task scheduled at:
{scheduled_time}

View your task at: https://taskai.app/tasks

---
You're receiving this email because you set up a reminder for this task.
© 2024 TaskAI. All rights reserved.
"""

    def _get_reminder_label(self, reminder_type: str) -> str:
        """
        Get human-readable label for reminder type.

        Args:
            reminder_type: Reminder type code

        Returns:
            Human-readable label
        """
        labels = {
            "15min": "15 minutes before",
            "1hr": "1 hour before",
            "1day": "1 day before",
            "1week": "1 week before",
            "custom": "Custom reminder"
        }
        return labels.get(reminder_type, "Reminder")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global email sender instance
_email_sender: Optional[EmailSender] = None


def get_email_sender() -> EmailSender:
    """
    Get or create the global email sender instance.

    Returns:
        EmailSender instance
    """
    global _email_sender
    if _email_sender is None:
        _email_sender = EmailSender()
    return _email_sender
