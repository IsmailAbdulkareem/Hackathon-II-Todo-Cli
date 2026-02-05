"""MCP (Model Context Protocol) server for exposing task management tools to AI agents."""
from typing import Any, Optional
from uuid import UUID
import logging
from sqlmodel import Session, select
from src.models.task import Task
from src.core.database import get_session

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MCPServer:
    """MCP server that exposes task management operations as tools for AI agents."""

    def __init__(self):
        """Initialize MCP server with tool registry."""
        self.tools = {}
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools."""
        self.tools = {
            "add_task": self.add_task,
            "list_tasks": self.list_tasks,
            "complete_task": self.complete_task,
            "delete_task": self.delete_task,
            "update_task": self.update_task,
            "find_task_by_title": self.find_task_by_title,
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

    def get_tools(self) -> dict[str, Any]:
        """
        Get all registered MCP tools.

        Returns:
            dict: Dictionary of tool names to tool functions
        """
        return self.tools


# Global MCP server instance
mcp_server = MCPServer()
