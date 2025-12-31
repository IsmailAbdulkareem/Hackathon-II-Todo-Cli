"""Todo entity - Domain model for todo tasks.

This module defines the Todo dataclass representing a single todo task.
Generated via Claude Code following spec-driven development methodology.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Todo:
    """Represents a single todo task.

    Attributes:
        id: Unique identifier (positive integer)
        title: Short description of the task (mandatory, max 200 chars)
        description: Detailed explanation of the task (optional, max 1000 chars)
        completed: Completion status flag (default: False)
        created_at: Timestamp of task creation (auto-set)
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def toggle_complete(self) -> None:
        """Toggle completion status between True and False.

        This method flips the completed attribute from False to True or vice versa.
        Used by TodoService.toggle_complete() to change task status.
        """
        self.completed = not self.completed

    def __str__(self) -> str:
        """String representation for CLI display.

        Returns formatted string for table display:
        Format: "ID | Status | Title | Description"

        Status indicators:
        - "[x]" for completed tasks
        - "[ ]" for incomplete tasks

        Returns:
            Formatted string with fixed-width columns for alignment
        """
        status = "[x]" if self.completed else "[ ]"

        # Truncate title and description if too long for display
        title_display = self.title[:30] if len(self.title) > 30 else self.title
        desc_display = self.description[:50] if len(self.description) > 50 else self.description

        return f"{self.id:3d} | {status} | {title_display:30s} | {desc_display}"
