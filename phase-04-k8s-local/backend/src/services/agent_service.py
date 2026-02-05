"""OpenAI Agents SDK implementation for task management chatbot."""
from datetime import datetime, timezone
from typing import Optional, Any
from uuid import UUID
from sqlmodel import Session, select, desc
from agents import Agent, function_tool, Runner
from src.models.conversation import Conversation
from src.models.message import Message
from src.core.config import settings
from src.services.mcp_server import mcp_server


class TaskAgent:
    """Task management agent using OpenAI Agents SDK."""

    def __init__(self):
        """Initialize TaskAgent with OpenAI Agents SDK."""
        self.mcp_server = mcp_server

        # Define tools using function_tool decorator
        @function_tool
        async def add_task(title: str, description: str = "") -> dict:
            """
            Create a new task in the user's task list.

            Args:
                title: Task title (max 200 characters)
                description: Optional task description (max 2000 characters)

            Returns:
                dict with task details
            """
            # Get user_id from context (will be set during run)
            user_id = self._current_user_id
            return await self.mcp_server.add_task(user_id, title, description)

        @function_tool
        async def list_tasks(status: str = "all") -> dict:
            """
            Retrieve tasks from the user's task list.

            Args:
                status: Filter tasks by completion status (all, pending, completed)

            Returns:
                dict with list of tasks
            """
            user_id = self._current_user_id
            return await self.mcp_server.list_tasks(user_id, status)

        @function_tool
        async def complete_task(task_id: str) -> dict:
            """
            Mark a task as complete.

            Args:
                task_id: Task identifier to mark complete

            Returns:
                dict with updated task details
            """
            user_id = self._current_user_id
            return await self.mcp_server.complete_task(user_id, task_id)

        @function_tool
        async def delete_task(task_id: str) -> dict:
            """
            Remove a task from the user's list.

            Args:
                task_id: Task identifier to delete

            Returns:
                dict with deletion confirmation
            """
            user_id = self._current_user_id
            return await self.mcp_server.delete_task(user_id, task_id)

        @function_tool
        async def update_task(task_id: str, title: str = None, description: str = None) -> dict:
            """
            Modify a task's title or description.

            Args:
                task_id: Task identifier to update
                title: New task title (max 200 characters)
                description: New task description (max 2000 characters)

            Returns:
                dict with updated task details
            """
            user_id = self._current_user_id
            return await self.mcp_server.update_task(user_id, task_id, title, description)

        @function_tool
        async def find_task_by_title(search_query: str) -> dict:
            """
            Search for tasks by partial title match (case-insensitive).
            Use this when users mention task titles in natural language.

            Args:
                search_query: Partial title to search for (e.g., 'groceries', 'buy', etc.)

            Returns:
                dict with matching tasks
            """
            user_id = self._current_user_id
            return await self.mcp_server.find_task_by_title(user_id, search_query)

        # Store tools
        self.tools = [
            add_task,
            list_tasks,
            complete_task,
            delete_task,
            update_task,
            find_task_by_title
        ]

        # Create agent
        self.agent = Agent(
            name="Task Assistant",
            model=settings.OPENAI_MODEL,
            instructions="""You are a helpful AI assistant that helps users manage their todo tasks.
You can create, view, update, complete, and delete tasks through natural language.

When users ask to add tasks, use the add_task tool.
When users ask to see tasks, use the list_tasks tool.
When users mark tasks complete, use the complete_task tool.
When users want to update tasks, use the update_task tool.
When users want to delete tasks, use the delete_task tool.
When users mention task titles in natural language (e.g., 'I finished buying groceries'),
use find_task_by_title to search for matching tasks first.

Always confirm actions with friendly messages.
If a command is ambiguous and matches multiple tasks, present a numbered list and ask the user to select.""",
            tools=self.tools
        )

        # Store current user_id for tool access
        self._current_user_id = None

    async def process_message(
        self,
        session: Session,
        user_id: str,
        message: str,
        conversation_id: Optional[UUID] = None
    ) -> dict[str, Any]:
        """
        Process a user message using the OpenAI Agent.

        Args:
            session: Database session
            user_id: User identifier
            message: User's message
            conversation_id: Optional existing conversation ID

        Returns:
            dict: {response: str, conversation_id: UUID, tool_calls: list}
        """
        try:
            # Set current user_id for tools to access
            self._current_user_id = user_id

            # Get or create conversation
            conversation = await self._get_or_create_conversation(
                session, user_id, conversation_id
            )

            # Load conversation history
            history = await self._load_conversation_history(session, conversation.id)

            # Run agent with message using Runner (must await!)
            result = await Runner.run(
                starting_agent=self.agent,
                input=message,
                context={"user_id": user_id, "history": history}
            )

            # Extract response
            response_text = result.output if hasattr(result, 'output') else str(result)

            # Save user message
            user_msg = Message(
                conversation_id=conversation.id,
                user_id=user_id,
                role="user",
                content=message
            )
            session.add(user_msg)

            # Save assistant response
            assistant_msg = Message(
                conversation_id=conversation.id,
                user_id=user_id,
                role="assistant",
                content=response_text
            )
            session.add(assistant_msg)

            # Update conversation timestamp
            conversation.updated_at = datetime.now(timezone.utc)
            session.add(conversation)
            session.commit()

            return {
                "response": response_text,
                "conversation_id": str(conversation.id),
                "tool_calls": []  # Agents SDK handles this internally
            }

        except Exception as e:
            session.rollback()
            return {
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "conversation_id": str(conversation_id) if conversation_id else None,
                "tool_calls": []
            }
        finally:
            # Clear current user_id
            self._current_user_id = None

    async def _get_or_create_conversation(
        self,
        session: Session,
        user_id: str,
        conversation_id: Optional[UUID] = None
    ) -> Conversation:
        """Get existing conversation or create a new one."""
        if conversation_id:
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = session.exec(statement).first()
            if not conversation:
                raise ValueError("Conversation not found or access denied")
            return conversation
        else:
            conversation = Conversation(user_id=user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation

    async def _load_conversation_history(
        self,
        session: Session,
        conversation_id: UUID,
        limit: int = 50
    ) -> list[dict]:
        """Load conversation history for context."""
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        messages = session.exec(statement).all()

        # Reverse to chronological order and format for agent
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]


# Singleton instance
task_agent = TaskAgent()
