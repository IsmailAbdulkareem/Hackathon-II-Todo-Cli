"""
Audit Logging Service (T089)

This module implements an audit logging service that consumes and stores
all events published through the event system for compliance and debugging.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AuditLogEntry:
    """
    Represents a single audit log entry.
    """
    id: str
    event_type: str
    topic: str
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[str] = None
    task_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class AuditService:
    """
    Service for logging and querying audit events.

    Stores all events received from pub/sub topics for audit trail,
    compliance, and debugging purposes.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize audit service.

        Args:
            log_file: Optional file path for persistent audit logs
        """
        self.log_file = log_file
        self._in_memory_logs: List[AuditLogEntry] = []
        self._log_counter = 0

        if log_file:
            self._ensure_log_file_exists()

    def _ensure_log_file_exists(self):
        """Ensure audit log file and directory exist"""
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            if not log_path.exists():
                log_path.touch()

    async def log_event(
        self,
        event_type: str,
        topic: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
        user_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Log an event to the audit trail.

        Args:
            event_type: Type of event (e.g., TASK_CREATED)
            topic: Pub/sub topic the event came from
            data: Event payload data
            timestamp: Event timestamp (defaults to now)
            user_id: Optional user ID associated with event
            task_id: Optional task ID associated with event

        Returns:
            Created audit log entry
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        # Generate unique ID
        self._log_counter += 1
        entry_id = f"audit-{self._log_counter}-{int(timestamp.timestamp())}"

        # Extract user_id and task_id from data if not provided
        if user_id is None and "user_id" in data:
            user_id = data["user_id"]
        if task_id is None and "task_id" in data:
            task_id = data["task_id"]

        # Create audit log entry
        entry = AuditLogEntry(
            id=entry_id,
            event_type=event_type,
            topic=topic,
            timestamp=timestamp,
            data=data,
            user_id=user_id,
            task_id=task_id
        )

        # Store in memory
        self._in_memory_logs.append(entry)

        # Write to file if configured
        if self.log_file:
            await self._write_to_file(entry)

        logger.info(f"Audit log created: {entry_id} - {event_type}")

        return entry

    async def _write_to_file(self, entry: AuditLogEntry):
        """Write audit log entry to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log to file: {e}")

    async def get_logs(
        self,
        event_type: Optional[str] = None,
        topic: Optional[str] = None,
        user_id: Optional[str] = None,
        task_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """
        Query audit logs with filters.

        Args:
            event_type: Filter by event type
            topic: Filter by topic
            user_id: Filter by user ID
            task_id: Filter by task ID
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            limit: Maximum number of entries to return

        Returns:
            List of matching audit log entries
        """
        results = self._in_memory_logs.copy()

        # Apply filters
        if event_type:
            results = [e for e in results if e.event_type == event_type]

        if topic:
            results = [e for e in results if e.topic == topic]

        if user_id:
            results = [e for e in results if e.user_id == user_id]

        if task_id:
            results = [e for e in results if e.task_id == task_id]

        if start_time:
            results = [e for e in results if e.timestamp >= start_time]

        if end_time:
            results = [e for e in results if e.timestamp <= end_time]

        # Sort by timestamp (newest first) and limit
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]

    async def get_event_count(
        self,
        event_type: Optional[str] = None,
        topic: Optional[str] = None
    ) -> int:
        """
        Get count of events matching filters.

        Args:
            event_type: Filter by event type
            topic: Filter by topic

        Returns:
            Count of matching events
        """
        logs = await self.get_logs(
            event_type=event_type,
            topic=topic,
            limit=999999  # Get all for counting
        )
        return len(logs)

    async def get_recent_events(self, limit: int = 10) -> List[AuditLogEntry]:
        """
        Get most recent audit log entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent audit log entries
        """
        return await self.get_logs(limit=limit)

    async def clear_logs(self):
        """
        Clear all in-memory audit logs.

        WARNING: This does not clear the log file if configured.
        """
        self._in_memory_logs.clear()
        self._log_counter = 0
        logger.warning("Audit logs cleared from memory")


# Global audit service instance
audit_service = AuditService(log_file="logs/audit.log")
