"""
Recurrence engine for calculating next task occurrences.

Implements recurrence rule logic for:
- Daily recurrence (every N days)
- Weekly recurrence (every N weeks on specific days)
- Monthly recurrence (every N months on specific day)
- Yearly recurrence (every N years on specific date)
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RecurrenceEngine:
    """
    Engine for calculating next recurring task occurrences.

    Supports standard recurrence patterns with interval and frequency.
    """

    def calculate_next_occurrence(
        self,
        completed_task: Dict[str, Any],
        recurrence_rule: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate the next occurrence of a recurring task.

        Args:
            completed_task: The completed task data
            recurrence_rule: Recurrence rule configuration

        Returns:
            Task data for next occurrence, or None if series is complete
        """
        frequency = recurrence_rule.get("frequency")
        interval = recurrence_rule.get("interval", 1)
        end_date = recurrence_rule.get("end_date")
        occurrence_count = recurrence_rule.get("occurrence_count")
        current_count = recurrence_rule.get("current_count", 0)

        # Check if series is complete
        if occurrence_count and current_count >= occurrence_count:
            logger.info(
                f"Recurrence series complete: {current_count}/{occurrence_count} occurrences"
            )
            return None

        # Get the due date from completed task
        due_date_str = completed_task.get("due_date")
        if not due_date_str:
            logger.warning("Completed task has no due date, cannot calculate next occurrence")
            return None

        try:
            due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as e:
            logger.error(f"Invalid due date format: {due_date_str} - {e}")
            return None

        # Calculate next due date based on frequency
        next_due_date = self._calculate_next_due_date(
            due_date=due_date,
            frequency=frequency,
            interval=interval
        )

        if not next_due_date:
            logger.error(f"Failed to calculate next due date for frequency: {frequency}")
            return None

        # Check if next occurrence exceeds end date
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                if next_due_date > end_datetime:
                    logger.info(
                        f"Next occurrence {next_due_date} exceeds end date {end_datetime}"
                    )
                    return None
            except (ValueError, AttributeError) as e:
                logger.warning(f"Invalid end date format: {end_date} - {e}")

        # Create next task instance
        next_task = {
            "title": completed_task.get("title"),
            "description": completed_task.get("description"),
            "priority": completed_task.get("priority", "Medium"),
            "due_date": next_due_date.isoformat(),
            "is_recurring": True,
            "parent_task_id": completed_task.get("parent_task_id") or completed_task.get("id"),
            "recurrence_rule_id": recurrence_rule.get("id")
        }

        logger.info(
            f"Calculated next occurrence: {next_task['title']} due {next_due_date}"
        )

        return next_task

    def _calculate_next_due_date(
        self,
        due_date: datetime,
        frequency: str,
        interval: int
    ) -> Optional[datetime]:
        """
        Calculate the next due date based on frequency and interval.

        Args:
            due_date: Current due date
            frequency: Recurrence frequency (daily, weekly, monthly, yearly)
            interval: Interval between occurrences

        Returns:
            Next due date, or None if calculation fails
        """
        if frequency == "daily":
            return due_date + timedelta(days=interval)

        elif frequency == "weekly":
            return due_date + timedelta(weeks=interval)

        elif frequency == "monthly":
            # Add months by incrementing month and handling year rollover
            month = due_date.month + interval
            year = due_date.year

            while month > 12:
                month -= 12
                year += 1

            # Handle day overflow (e.g., Jan 31 -> Feb 31 doesn't exist)
            day = due_date.day
            while True:
                try:
                    return due_date.replace(year=year, month=month, day=day)
                except ValueError:
                    # Day doesn't exist in target month, try previous day
                    day -= 1
                    if day < 1:
                        logger.error("Failed to calculate valid day for monthly recurrence")
                        return None

        elif frequency == "yearly":
            year = due_date.year + interval

            # Handle leap year edge case (Feb 29)
            day = due_date.day
            month = due_date.month

            if month == 2 and day == 29:
                # Check if target year is leap year
                is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                if not is_leap:
                    day = 28  # Use Feb 28 in non-leap years

            try:
                return due_date.replace(year=year, day=day)
            except ValueError as e:
                logger.error(f"Failed to calculate yearly recurrence: {e}")
                return None

        else:
            logger.error(f"Unsupported recurrence frequency: {frequency}")
            return None


# Global recurrence engine instance
_recurrence_engine: Optional[RecurrenceEngine] = None


def get_recurrence_engine() -> RecurrenceEngine:
    """
    Get or create the global recurrence engine instance.

    Returns:
        RecurrenceEngine instance
    """
    global _recurrence_engine
    if _recurrence_engine is None:
        _recurrence_engine = RecurrenceEngine()
    return _recurrence_engine
