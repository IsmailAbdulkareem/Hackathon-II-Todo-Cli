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
        }

    async def add_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Create a new task for the user.

        Args:
            user_id: User identifier (UUID format)
            title: Task title (max 200 characters)
            description: Optional task description (max 2000 characters)

        Returns:
            dict: {task_id: str, status: str, title: str} or {error: str}
        """
        logger.info(f"MCP Tool: add_task called for user_id={user_id}, title='{title[:50]}...'")
        try:
            # Validate character limits
            if len(title) > 200:
                logger.warning(f"MCP Tool: add_task failed - title exceeds 200 chars for user_id={user_id}")
                return {"status": "error", "error": "Title exceeds 200 character limit"}

            if description and len(description) > 2000:
                logger.warning(f"MCP Tool: add_task failed - description exceeds 2000 chars for user_id={user_id}")
                return {"status": "error", "error": "Description exceeds 2000 character limit"}

            # Create task in database
            session = next(get_session())
            try:
                task = Task(
                    user_id=user_id,
                    title=title.strip(),
                    description=description.strip() if description else None,
                    completed=False
                )
                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP Tool: add_task success - created task_id={task.id} for user_id={user_id}")
                return {
                    "task_id": str(task.id),
                    "status": "created",
                    "title": task.title
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
        description: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Modify a task's title or description.

        Args:
            user_id: User identifier (UUID format)
            task_id: Task identifier to update
            title: New task title (max 200 characters)
            description: New task description (max 2000 characters)

        Returns:
            dict: {task_id: str, status: str, title: str} or {error: str}
        """
        logger.info(f"MCP Tool: update_task called for user_id={user_id}, task_id={task_id}")
        try:
            # Validate at least one field is provided
            if not title and not description:
                logger.warning(f"MCP Tool: update_task failed - no fields provided for user_id={user_id}, task_id={task_id}")
                return {
                    "status": "error",
                    "error": "Must provide at least title or description to update"
                }

            # Validate character limits
            if title and len(title) > 200:
                logger.warning(f"MCP Tool: update_task failed - title exceeds 200 chars for user_id={user_id}, task_id={task_id}")
                return {"status": "error", "error": "Title exceeds 200 character limit"}

            if description and len(description) > 2000:
                logger.warning(f"MCP Tool: update_task failed - description exceeds 2000 chars for user_id={user_id}, task_id={task_id}")
                return {"status": "error", "error": "Description exceeds 2000 character limit"}

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

                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP Tool: update_task success - updated task_id={task_id} for user_id={user_id}")
                return {
                    "task_id": str(task.id),
                    "status": "updated",
                    "title": task.title
                }
            finally:
                session.close()

        except Exception as e:
            logger.error(f"MCP Tool: update_task error for user_id={user_id}, task_id={task_id}: {str(e)}")
            return {"status": "error", "error": f"Failed to update task: {str(e)}"}

    def get_tools(self) -> dict[str, Any]:
        """
        Get all registered MCP tools.

        Returns:
            dict: Dictionary of tool names to tool functions
        """
        return self.tools


# Global MCP server instance
mcp_server = MCPServer()
