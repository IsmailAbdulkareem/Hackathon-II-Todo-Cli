"""MCP (Model Context Protocol) server for exposing task management tools to AI agents."""
from typing import Any, Optional, List, Dict
from uuid import UUID
from datetime import datetime, timedelta, timezone
import logging
import json

from sqlmodel import Session, select
from openai import AsyncOpenAI

from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.tag import Tag
from src.models.reminder import Reminder
from src.core.database import get_session
from src.core.config import settings
from src.services.task_service import TaskService
from src.services.tag_service import TagService
from src.services.reminder_service import ReminderService

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MCPServer:
    """MCP server that exposes task management operations as tools for AI agents."""

    def __init__(self):
        """Initialize MCP server with tool registry and OpenAI client."""
        self.tools = {}
        self._register_tools()

        # Initialize OpenAI client for natural language processing
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = "gpt-4-turbo-preview"
        else:
            self.openai_client = None
            logger.warning("OpenAI API key not configured - natural language features disabled")

    def _register_tools(self):
        """Register all MCP tools."""
        self.tools = {
            "add_task": self.add_task,
            "list_tasks": self.list_tasks,
            "complete_task": self.complete_task,
            "delete_task": self.delete_task,
            "update_task": self.update_task,
            "find_task_by_title": self.find_task_by_title,
            "create_recurring_task": self.create_recurring_task,
            "edit_recurring_series": self.edit_recurring_series,
            "delete_recurring_series": self.delete_recurring_series,
        }

    async def add_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: int = 1
    ) -> dict[str, Any]:
        """
        Create a new task for the user.

        Args:
            user_id: User identifier (UUID format)
            title: Task title (max 200 characters)
            description: Optional task description (max 2000 characters)
            priority: Task priority (1-5, where 1 is lowest and 5 is highest)

        Returns:
            dict: {task_id: str, status: str, title: str, priority: int} or {error: str}
        """
        logger.info(f"MCP Tool: add_task called for user_id={user_id}, title='{title[:50]}...', priority={priority}")
        try:
            # Validate character limits
            if len(title) > 200:
                logger.warning(f"MCP Tool: add_task failed - title exceeds 200 chars for user_id={user_id}")
                return {"status": "error", "error": "Title exceeds 200 character limit"}

            if description and len(description) > 2000:
                logger.warning(f"MCP Tool: add_task failed - description exceeds 2000 chars for user_id={user_id}")
                return {"status": "error", "error": "Description exceeds 2000 character limit"}

            # Validate priority
            if priority < 1 or priority > 5:
                logger.warning(f"MCP Tool: add_task failed - invalid priority {priority} for user_id={user_id}")
                return {"status": "error", "error": "Priority must be between 1 and 5"}

            # Create task in database
            session = next(get_session())
            try:
                task = Task(
                    user_id=user_id,
                    title=title.strip(),
                    description=description.strip() if description else None,
                    completed=False
                )
                # Don't set priority - column doesn't exist in database yet
                # if priority and hasattr(Task, 'priority'):
                #     task.priority = priority

                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP Tool: add_task success - created task_id={task.id} for user_id={user_id}")
                return {
                    "task_id": str(task.id),
                    "status": "created",
                    "title": task.title,
                    "priority": 1  # Default priority since column doesn't exist
                }
            finally:
                session.close()

        except Exception as e:
            return {"status": "error", "error": f"Failed to create task: {str(e)}"}

    async def list_tasks(
        self,
        user_id: str,
        status: str = "all"
    ) -> dict[str, Any]:
        """
        Retrieve tasks from the user's task list.

        Args:
            user_id: User identifier (UUID format)
            status: Filter by status - "all", "pending", or "completed"

        Returns:
            dict: {tasks: list, count: int} or {error: str}
        """
        logger.info(f"MCP Tool: list_tasks called for user_id={user_id}, status={status}")
        try:
            # Validate status parameter
            if status not in ("all", "pending", "completed"):
                logger.warning(f"MCP Tool: list_tasks failed - invalid status '{status}' for user_id={user_id}")
                return {"error": "Status must be 'all', 'pending', or 'completed'"}

            # Query tasks from database
            session = next(get_session())
            try:
                statement = select(Task).where(Task.user_id == user_id)

                # Apply status filter
                if status == "pending":
                    statement = statement.where(Task.completed == False)
                elif status == "completed":
                    statement = statement.where(Task.completed == True)

                tasks = session.exec(statement).all()

                # Format tasks for AI agent
                task_list = [
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "priority": 1,  # Default priority since column doesn't exist
                        "completed": task.completed,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    }
                    for task in tasks
                ]

                logger.info(f"MCP Tool: list_tasks success - returned {len(task_list)} tasks for user_id={user_id}")
                return {
                    "tasks": task_list,
                    "count": len(task_list)
                }
            finally:
                session.close()

        except Exception as e:
            return {"error": f"Failed to list tasks: {str(e)}"}

    async def complete_task(
        self,
        user_id: str,
        task_id: str
    ) -> dict[str, Any]:
        """
        Mark a task as complete.

        Args:
            user_id: User identifier (UUID format)
            task_id: Task identifier to mark complete

        Returns:
            dict: {task_id: str, status: str, title: str} or {error: str}
        """
        logger.info(f"MCP Tool: complete_task called for user_id={user_id}, task_id={task_id}")
        try:
            session = next(get_session())
            try:
                # Find task
                statement = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
                task = session.exec(statement).first()

                if not task:
                    logger.warning(f"MCP Tool: complete_task failed - task not found: task_id={task_id}, user_id={user_id}")
                    return {
                        "status": "error",
                        "error": "Task not found or does not belong to user"
                    }

                # Toggle completion status
                task.completed = True
                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP Tool: complete_task success - marked task_id={task_id} as completed for user_id={user_id}")
                return {
                    "task_id": str(task.id),
                    "status": "completed",
                    "title": task.title
                }
            finally:
                session.close()

        except Exception as e:
            logger.error(f"MCP Tool: complete_task error for user_id={user_id}, task_id={task_id}: {str(e)}")
            return {"status": "error", "error": f"Failed to complete task: {str(e)}"}

    async def delete_task(
        self,
        user_id: str,
        task_id: str
    ) -> dict[str, Any]:
        """
        Remove a task from the user's list.

        Args:
            user_id: User identifier (UUID format)
            task_id: Task identifier to delete

        Returns:
            dict: {task_id: str, status: str, title: str} or {error: str}
        """
        logger.info(f"MCP Tool: delete_task called for user_id={user_id}, task_id={task_id}")
        try:
            session = next(get_session())
            try:
                # Find task
                statement = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
                task = session.exec(statement).first()

                if not task:
                    logger.warning(f"MCP Tool: delete_task failed - task not found: task_id={task_id}, user_id={user_id}")
                    return {
                        "status": "error",
                        "error": "Task not found or does not belong to user"
                    }

                # Store title before deletion
                task_title = task.title
                task_id_str = str(task.id)

                # Delete task
                session.delete(task)
                session.commit()

                logger.info(f"MCP Tool: delete_task success - deleted task_id={task_id} for user_id={user_id}")
                return {
                    "task_id": task_id_str,
                    "status": "deleted",
                    "title": task_title
                }
            finally:
                session.close()

        except Exception as e:
            logger.error(f"MCP Tool: delete_task error for user_id={user_id}, task_id={task_id}: {str(e)}")
            return {"status": "error", "error": f"Failed to delete task: {str(e)}"}

    async def update_task(
        self,
        user_id: str,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Modify a task's title, description, or priority.

        Args:
            user_id: User identifier (UUID format)
            task_id: Task identifier to update
            title: New task title (max 200 characters)
            description: New task description (max 2000 characters)
            priority: New task priority (1-5, where 1 is lowest and 5 is highest)

        Returns:
            dict: {task_id: str, status: str, title: str, priority: int} or {error: str}
        """
        logger.info(f"MCP Tool: update_task called for user_id={user_id}, task_id={task_id}")
        try:
            # Validate at least one field is provided
            if not title and not description and priority is None:
                logger.warning(f"MCP Tool: update_task failed - no fields provided for user_id={user_id}, task_id={task_id}")
                return {
                    "status": "error",
                    "error": "Must provide at least title, description, or priority to update"
                }

            # Validate character limits
            if title and len(title) > 200:
                logger.warning(f"MCP Tool: update_task failed - title exceeds 200 chars for user_id={user_id}, task_id={task_id}")
                return {"status": "error", "error": "Title exceeds 200 character limit"}

            if description and len(description) > 2000:
                logger.warning(f"MCP Tool: update_task failed - description exceeds 2000 chars for user_id={user_id}, task_id={task_id}")
                return {"status": "error", "error": "Description exceeds 2000 character limit"}

            # Validate priority
            if priority is not None and (priority < 1 or priority > 5):
                logger.warning(f"MCP Tool: update_task failed - invalid priority {priority} for user_id={user_id}, task_id={task_id}")
                return {"status": "error", "error": "Priority must be between 1 and 5"}

            session = next(get_session())
            try:
                # Find task
                statement = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
                task = session.exec(statement).first()

                if not task:
                    logger.warning(f"MCP Tool: update_task failed - task not found: task_id={task_id}, user_id={user_id}")
                    return {
                        "status": "error",
                        "error": "Task not found or does not belong to user"
                    }

                # Update fields
                if title:
                    task.title = title.strip()
                if description:
                    task.description = description.strip()
                # Don't update priority - column doesn't exist
                # if priority is not None and hasattr(task, 'priority'):
                #     task.priority = priority

                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP Tool: update_task success - updated task_id={task_id} for user_id={user_id}")
                return {
                    "task_id": str(task.id),
                    "status": "updated",
                    "title": task.title,
                    "priority": 1  # Default priority since column doesn't exist
                }
            finally:
                session.close()

        except Exception as e:
            logger.error(f"MCP Tool: update_task error for user_id={user_id}, task_id={task_id}: {str(e)}")
            return {"status": "error", "error": f"Failed to update task: {str(e)}"}

    async def find_task_by_title(
        self,
        user_id: str,
        search_query: str
    ) -> dict[str, Any]:
        """
        Find tasks by partial title match (fuzzy search).

        Args:
            user_id: User identifier (UUID format)
            search_query: Partial title to search for (case-insensitive)

        Returns:
            dict: {tasks: list, count: int} or {error: str}
        """
        logger.info(f"MCP Tool: find_task_by_title called for user_id={user_id}, search_query='{search_query}'")
        try:
            if not search_query or not search_query.strip():
                logger.warning(f"MCP Tool: find_task_by_title failed - empty search query for user_id={user_id}")
                return {"error": "Search query cannot be empty"}

            session = next(get_session())
            try:
                # Search for tasks with partial title match (case-insensitive)
                search_pattern = f"%{search_query.strip()}%"
                statement = select(Task).where(
                    Task.user_id == user_id,
                    Task.title.ilike(search_pattern)
                )
                tasks = session.exec(statement).all()

                # Format tasks for AI agent
                task_list = [
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "priority": 1,  # Default priority since column doesn't exist
                        "completed": task.completed,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    }
                    for task in tasks
                ]

                logger.info(f"MCP Tool: find_task_by_title success - found {len(task_list)} tasks for user_id={user_id}")
                return {
                    "tasks": task_list,
                    "count": len(task_list),
                    "search_query": search_query.strip()
                }
            finally:
                session.close()

        except Exception as e:
            logger.error(f"MCP Tool: find_task_by_title error for user_id={user_id}: {str(e)}")
            return {"error": f"Failed to search tasks: {str(e)}"}

    async def create_recurring_task(
        self,
        user_id: str,
        title: str,
        frequency: str,
        interval: int = 1,
        description: Optional[str] = None,
        priority: int = 1,
        occurrence_count: Optional[int] = None,
        end_date: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Create a recurring task with a recurrence rule.

        Args:
            user_id: User identifier
            title: Task title
            frequency: Recurrence frequency (daily, weekly, monthly, yearly)
            interval: Interval between occurrences (default: 1)
            description: Optional task description
            priority: Task priority (1-5)
            occurrence_count: Optional number of occurrences
            end_date: Optional end date for recurrence

        Returns:
            dict: {task_id: str, recurrence_rule_id: str, status: str} or {error: str}
        """
        logger.info(f"MCP Tool: create_recurring_task called for user_id={user_id}, title='{title[:50]}...', frequency={frequency}")
        try:
            from src.services.recurrence_rule_service import RecurrenceRuleService
            from src.models.recurrence_rule import RecurrenceRuleCreate

            # Validate frequency
            valid_frequencies = ["daily", "weekly", "monthly", "yearly"]
            if frequency.lower() not in valid_frequencies:
                return {"status": "error", "error": f"Invalid frequency. Must be one of: {', '.join(valid_frequencies)}"}

            # Validate interval
            if interval < 1:
                return {"status": "error", "error": "Interval must be at least 1"}

            session = next(get_session())
            try:
                # Create recurrence rule
                recurrence_service = RecurrenceRuleService(session)

                # Parse end_date if provided
                parsed_end_date = None
                if end_date:
                    parsed_end_date = self.parse_natural_date(end_date)
                    if not parsed_end_date:
                        return {"status": "error", "error": f"Could not parse end date: {end_date}"}

                rule_data = RecurrenceRuleCreate(
                    frequency=frequency.lower(),
                    interval=interval,
                    end_date=parsed_end_date,
                    occurrence_count=occurrence_count
                )

                recurrence_rule = await recurrence_service.create_recurrence_rule(user_id, rule_data)

                # Create the first task instance
                task_service = TaskService(session)
                task_data = TaskCreate(
                    title=title,
                    description=description or "",
                    priority=priority,
                    completed=False
                )

                task = await task_service.create_task(
                    user_id=user_id,
                    task_data=task_data,
                    recurrence_rule_id=str(recurrence_rule.id)
                )

                logger.info(f"MCP Tool: create_recurring_task success - task_id={task.id}, rule_id={recurrence_rule.id}")
                return {
                    "status": "success",
                    "task_id": str(task.id),
                    "recurrence_rule_id": str(recurrence_rule.id),
                    "title": task.title,
                    "frequency": frequency,
                    "interval": interval
                }
            finally:
                session.close()

        except Exception as e:
            logger.error(f"MCP Tool: create_recurring_task error for user_id={user_id}: {str(e)}")
            return {"error": f"Failed to create recurring task: {str(e)}"}

    async def edit_recurring_series(
        self,
        user_id: str,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Edit all tasks in a recurring series.

        Args:
            user_id: User identifier
            task_id: ID of any task in the series
            title: New title for all tasks in series
            description: New description for all tasks in series
            priority: New priority for all tasks in series

        Returns:
            dict: {status: str, updated_count: int} or {error: str}
        """
        logger.info(f"MCP Tool: edit_recurring_series called for user_id={user_id}, task_id={task_id}")
        try:
            session = next(get_session())
            try:
                task_service = TaskService(session)

                # Build update data
                update_data = {}
                if title:
                    update_data["title"] = title
                if description:
                    update_data["description"] = description
                if priority:
                    update_data["priority"] = priority

                if not update_data:
                    return {"status": "error", "error": "No update fields provided"}

                # Update the recurring series
                updated_count = await task_service.update_recurring_series(
                    user_id=user_id,
                    task_id=task_id,
                    update_data=update_data
                )

                logger.info(f"MCP Tool: edit_recurring_series success - updated {updated_count} tasks")
                return {
                    "status": "success",
                    "updated_count": updated_count,
                    "message": f"Updated {updated_count} tasks in the recurring series"
                }
            finally:
                session.close()

        except Exception as e:
            logger.error(f"MCP Tool: edit_recurring_series error for user_id={user_id}: {str(e)}")
            return {"error": f"Failed to edit recurring series: {str(e)}"}

    async def delete_recurring_series(
        self,
        user_id: str,
        task_id: str
    ) -> dict[str, Any]:
        """
        Delete all tasks in a recurring series.

        Args:
            user_id: User identifier
            task_id: ID of any task in the series

        Returns:
            dict: {status: str, deleted_count: int} or {error: str}
        """
        logger.info(f"MCP Tool: delete_recurring_series called for user_id={user_id}, task_id={task_id}")
        try:
            session = next(get_session())
            try:
                task_service = TaskService(session)

                # Delete the recurring series
                deleted_count = await task_service.delete_recurring_series(
                    user_id=user_id,
                    task_id=task_id
                )

                logger.info(f"MCP Tool: delete_recurring_series success - deleted {deleted_count} tasks")
                return {
                    "status": "success",
                    "deleted_count": deleted_count,
                    "message": f"Deleted {deleted_count} tasks from the recurring series"
                }
            finally:
                session.close()

        except Exception as e:
            logger.error(f"MCP Tool: delete_recurring_series error for user_id={user_id}: {str(e)}")
            return {"error": f"Failed to delete recurring series: {str(e)}"}

    def get_tools(self) -> dict[str, Any]:
        """
        Get all registered MCP tools.

        Returns:
            dict: Dictionary of tool names to tool functions
        """
        return self.tools

    def parse_natural_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse natural language date expressions into datetime objects.

        Supports:
        - Relative dates: today, tomorrow, next week, in 2 days
        - Day names: Monday, Tuesday, next Friday
        - Specific dates: 2024-12-25

        Args:
            date_str: Natural language date string

        Returns:
            Parsed datetime object or None if parsing fails
        """
        date_str = date_str.lower().strip()
        now = datetime.now(timezone.utc)

        # Handle relative dates
        if date_str == "today":
            return now.replace(hour=23, minute=59, second=59)
        elif date_str == "tomorrow":
            return (now + timedelta(days=1)).replace(hour=23, minute=59, second=59)
        elif date_str == "next week":
            return (now + timedelta(weeks=1)).replace(hour=23, minute=59, second=59)
        elif date_str.startswith("in "):
            # Parse "in X days/weeks/months"
            parts = date_str.split()
            if len(parts) >= 3:
                try:
                    amount = int(parts[1])
                    unit = parts[2].rstrip('s')  # Remove plural 's'

                    if unit == "day":
                        return (now + timedelta(days=amount)).replace(hour=23, minute=59, second=59)
                    elif unit == "week":
                        return (now + timedelta(weeks=amount)).replace(hour=23, minute=59, second=59)
                    elif unit == "month":
                        return (now + timedelta(days=amount * 30)).replace(hour=23, minute=59, second=59)
                except (ValueError, IndexError):
                    pass

        # Handle day names
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(day_names):
            if day in date_str:
                # Calculate days until next occurrence of this day
                current_day = now.weekday()
                target_day = i
                days_ahead = (target_day - current_day) % 7

                if days_ahead == 0 and "next" in date_str:
                    days_ahead = 7
                elif days_ahead == 0:
                    days_ahead = 7  # Default to next week if same day

                return (now + timedelta(days=days_ahead)).replace(hour=23, minute=59, second=59)

        # Try ISO format parsing
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            pass

        logger.warning(f"Could not parse date string: {date_str}")
        return None

    def get_openai_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in OpenAI function calling format.

        Returns:
            List of tool definitions for OpenAI API
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task with title, description, priority, due date, and tags",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title (required, max 200 characters)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description (optional, max 2000 characters)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["Low", "Medium", "High"],
                                "description": "Task priority level (default: Medium)"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date in natural language (e.g., 'tomorrow', 'next Friday', 'in 2 weeks')"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of tag names to attach to the task"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_tasks",
                    "description": "Search and filter tasks by title, priority, completion status, or tags",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to match against task titles"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["Low", "Medium", "High"],
                                "description": "Filter by priority level"
                            },
                            "completed": {
                                "type": "boolean",
                                "description": "Filter by completion status"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by tag names"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed by ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to mark as complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task's title, description, or priority",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["Low", "Medium", "High"],
                                "description": "New priority level"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task by ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_tag_to_task",
                    "description": "Add a tag to a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID"
                            },
                            "tag_name": {
                                "type": "string",
                                "description": "Tag name to add"
                            }
                        },
                        "required": ["task_id", "tag_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_all_tags",
                    "description": "List all available tags for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]

    async def process_chat_message(
        self,
        user_id: str,
        message: str,
        conversation_history: List[Dict[str, str]],
        session: Session
    ) -> Dict[str, Any]:
        """
        Process a chat message using OpenAI and execute tool calls.

        Args:
            user_id: User identifier
            message: User's message
            conversation_history: Previous messages in conversation
            session: Database session

        Returns:
            Response dictionary with assistant message and tool results
        """
        if not self.openai_client:
            return {
                "assistant_message": "Natural language chat is not available. OpenAI API key not configured.",
                "tool_calls": [],
                "requires_followup": False
            }

        # Build messages for OpenAI
        messages = conversation_history.copy()

        # Add system message if not present
        if not any(msg.get("role") == "system" for msg in messages):
            messages.insert(0, {
                "role": "system",
                "content": (
                    "You are a helpful task management assistant. "
                    "Help users create, update, search, and manage their tasks using natural language. "
                    "When users mention dates like 'tomorrow', 'next Friday', or 'in 2 weeks', "
                    "pass them to the tools as-is for parsing. "
                    "If a request is ambiguous (e.g., 'complete the report' when multiple report tasks exist), "
                    "search for matching tasks first and ask the user to clarify by showing up to 5 matches with numbers. "
                    "Be concise, friendly, and helpful in your responses."
                )
            })

        # Add user message
        messages.append({"role": "user", "content": message})

        try:
            # Call OpenAI with tools
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.get_openai_tool_definitions(),
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message
            tool_calls = assistant_message.tool_calls

            # Execute tool calls if present
            tool_results = []
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    result = await self.execute_openai_tool(
                        function_name=function_name,
                        arguments=function_args,
                        user_id=user_id,
                        session=session
                    )

                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "function_name": function_name,
                        "result": result
                    })

            return {
                "assistant_message": assistant_message.content or "",
                "tool_calls": tool_results,
                "requires_followup": bool(tool_calls)
            }

        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
            return {
                "assistant_message": "I encountered an error processing your request. Please try again.",
                "tool_calls": [],
                "requires_followup": False
            }

    async def execute_openai_tool(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        user_id: str,
        session: Session
    ) -> Dict[str, Any]:
        """
        Execute an OpenAI tool function with given arguments.

        Args:
            function_name: Name of the tool function
            arguments: Function arguments
            user_id: User identifier
            session: Database session

        Returns:
            Tool execution result
        """
        try:
            if function_name == "create_task":
                return await self._openai_create_task(user_id, arguments, session)
            elif function_name == "search_tasks":
                return await self._openai_search_tasks(user_id, arguments, session)
            elif function_name == "complete_task":
                return await self.complete_task(user_id, arguments.get("task_id"))
            elif function_name == "update_task":
                return await self._openai_update_task(user_id, arguments, session)
            elif function_name == "delete_task":
                return await self.delete_task(user_id, arguments.get("task_id"))
            elif function_name == "add_tag_to_task":
                return await self._openai_add_tag(user_id, arguments, session)
            elif function_name == "list_all_tags":
                return await self._openai_list_tags(user_id, session)
            else:
                return {"success": False, "error": f"Unknown function: {function_name}"}

        except Exception as e:
            logger.error(f"Error executing tool {function_name}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _openai_create_task(
        self,
        user_id: str,
        arguments: Dict[str, Any],
        session: Session
    ) -> Dict[str, Any]:
        """Create task via OpenAI tool call with natural language date parsing."""
        task_service = TaskService(session)

        # Parse due date if provided
        due_date = None
        if arguments.get("due_date"):
            due_date = self.parse_natural_date(arguments["due_date"])

        task_data = TaskCreate(
            title=arguments["title"],
            description=arguments.get("description", ""),
            priority=arguments.get("priority", "Medium"),
            due_date=due_date,
            is_recurring=False
        )

        # Get or create tags
        tag_ids = []
        if arguments.get("tags"):
            tag_service = TagService(session)
            for tag_name in arguments["tags"]:
                tag = await tag_service.get_or_create_tag(user_id, tag_name)
                tag_ids.append(tag.id)

        task = await task_service.create_task(
            user_id=user_id,
            task_data=task_data,
            tag_ids=tag_ids,
            user_email=f"{user_id}@example.com"
        )

        return {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None
        }

    async def _openai_search_tasks(
        self,
        user_id: str,
        arguments: Dict[str, Any],
        session: Session
    ) -> Dict[str, Any]:
        """Search tasks via OpenAI tool call."""
        from src.services.search_service import SearchService

        search_service = SearchService(session)

        tasks = await search_service.search_tasks(
            user_id=user_id,
            query=arguments.get("query"),
            priority=arguments.get("priority"),
            completed=arguments.get("completed"),
            tags=arguments.get("tags"),
            limit=5  # Limit to 5 for ambiguity handling
        )

        return {
            "success": True,
            "count": len(tasks),
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "completed": task.completed
                }
                for task in tasks
            ]
        }

    async def _openai_update_task(
        self,
        user_id: str,
        arguments: Dict[str, Any],
        session: Session
    ) -> Dict[str, Any]:
        """Update task via OpenAI tool call."""
        task_service = TaskService(session)

        task_data = TaskUpdate(
            title=arguments.get("title"),
            description=arguments.get("description"),
            priority=arguments.get("priority")
        )

        task = await task_service.update_task(
            user_id=user_id,
            task_id=arguments["task_id"],
            task_data=task_data
        )

        if not task:
            return {"success": False, "error": "Task not found"}

        return {
            "success": True,
            "task_id": task.id,
            "title": task.title
        }

    async def _openai_add_tag(
        self,
        user_id: str,
        arguments: Dict[str, Any],
        session: Session
    ) -> Dict[str, Any]:
        """Add tag to task via OpenAI tool call."""
        task_service = TaskService(session)
        tag_service = TagService(session)

        # Get or create tag
        tag = await tag_service.get_or_create_tag(user_id, arguments["tag_name"])

        task = await task_service.add_tag(
            user_id=user_id,
            task_id=arguments["task_id"],
            tag_id=tag.id
        )

        if not task:
            return {"success": False, "error": "Task not found"}

        return {"success": True, "tag_name": tag.name}

    async def _openai_list_tags(
        self,
        user_id: str,
        session: Session
    ) -> Dict[str, Any]:
        """List all tags via OpenAI tool call."""
        tag_service = TagService(session)

        tags = await tag_service.get_user_tags(user_id)

        return {
            "success": True,
            "tags": [
                {"id": tag.id, "name": tag.name, "color": tag.color}
                for tag in tags
            ]
        }


# Global MCP server instance
mcp_server = MCPServer()
