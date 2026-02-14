"""Chat service for managing conversations, messages, and OpenAI agent integration."""
from datetime import datetime, timezone
from typing import Optional, Any
from uuid import UUID
import logging
from sqlmodel import Session, select, desc, func
from openai import AsyncOpenAI
from src.models.conversation import Conversation
from src.models.message import Message
from src.core.config import settings
from src.services.mcp_server import mcp_server

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ChatService:
    """Service for managing chat conversations and AI agent interactions."""

    def __init__(self):
        """Initialize ChatService with OpenAI client."""
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.mcp_tools = mcp_server.get_tools()

    async def get_or_create_conversation(
        self,
        session: Session,
        user_id: str,
        conversation_id: Optional[UUID] = None
    ) -> Conversation:
        """
        Get existing conversation or create a new one.

        Args:
            session: Database session
            user_id: User identifier
            conversation_id: Optional existing conversation ID

        Returns:
            Conversation object

        Raises:
            ValueError: If conversation not found or doesn't belong to user
        """
        if conversation_id:
            # Load existing conversation
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = session.exec(statement).first()

            if not conversation:
                raise ValueError("Conversation not found or does not belong to user")

            return conversation
        else:
            # Create new conversation
            conversation = Conversation(user_id=user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation

    async def load_messages(
        self,
        session: Session,
        conversation_id: UUID,
        limit: int = 50
    ) -> list[Message]:
        """
        Load recent messages from a conversation.

        Args:
            session: Database session
            conversation_id: Conversation identifier
            limit: Maximum number of messages to load (default 50)

        Returns:
            List of messages in chronological order
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        messages = session.exec(statement).all()

        # Return in chronological order (oldest first)
        return list(reversed(messages))

    async def save_message(
        self,
        session: Session,
        conversation_id: UUID,
        user_id: str,
        role: str,
        content: str
    ) -> Message:
        """
        Save a message to the database.

        Args:
            session: Database session
            conversation_id: Conversation identifier
            user_id: User identifier
            role: Message role ("user" or "assistant")
            content: Message content

        Returns:
            Created message object
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        session.add(message)

        # Update conversation's updated_at timestamp
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.now(timezone.utc)
            session.add(conversation)

        session.commit()
        session.refresh(message)
        return message

    async def run_agent(
        self,
        user_id: str,
        user_message: str,
        conversation_history: list[Message]
    ) -> dict[str, Any]:
        """
        Run OpenAI agent with conversation context and MCP tools.

        Args:
            user_id: User identifier (for tool invocations)
            user_message: Current user message
            conversation_history: Previous messages in conversation

        Returns:
            dict: {response: str, tool_calls: list}
        """
        try:
            # Convert message history to OpenAI format
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in conversation_history
            ]

            # Get database session for tool execution
            from src.core.database import get_session
            session = next(get_session())

            try:
                # Use enhanced MCP server with OpenAI integration
                result = await mcp_server.process_chat_message(
                    user_id=user_id,
                    message=user_message,
                    conversation_history=messages,
                    session=session
                )

                return {
                    "response": result.get("assistant_message", "I encountered an error processing your request."),
                    "tool_calls": result.get("tool_calls", [])
                }
            finally:
                session.close()

        except Exception as e:
            logger.error(f"ChatService: run_agent error for user_id={user_id}: {str(e)}", exc_info=True)
            return {
                "response": "I encountered an error processing your request. Please try again.",
                "tool_calls": []
            }
                    "- Priority 1: Lowest (blue), Priority 2: Low (green), Priority 3: Medium (yellow)\n"
                    "- Priority 4: High (orange), Priority 5: Highest (red)\n"
                    "- Use update_task with priority parameter to change priority\n"
                    "\n"
                    "REMEMBER: Always USE the tools, don't just talk about using them!"
                )
            })

            # Add conversation history
            for msg in conversation_history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Define tools for OpenAI function calling
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "description": "Create a new task for the user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Task title (max 200 characters)"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Optional task description (max 2000 characters)"
                                },
                                "priority": {
                                    "type": "integer",
                                    "description": "Task priority (1-5, where 1 is lowest and 5 is highest). Default is 1.",
                                    "enum": [1, 2, 3, 4, 5]
                                }
                            },
                            "required": ["title"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "description": "Retrieve tasks from the user's task list",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": ["all", "pending", "completed"],
                                    "description": "Filter tasks by completion status"
                                }
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "complete_task",
                        "description": "Mark a task as complete",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "Task identifier to mark complete"
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
                        "description": "Remove a task from the user's list",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "Task identifier to delete"
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
                        "description": "Modify a task's title, description, or priority",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "Task identifier to update"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "New task title (max 200 characters)"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "New task description (max 2000 characters)"
                                },
                                "priority": {
                                    "type": "integer",
                                    "description": "New task priority (1-5, where 1 is lowest and 5 is highest)",
                                    "enum": [1, 2, 3, 4, 5]
                                }
                            },
                            "required": ["task_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "find_task_by_title",
                        "description": "Search for tasks by partial title match (case-insensitive). Use this when users mention task titles in natural language.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "search_query": {
                                    "type": "string",
                                    "description": "Partial title to search for (e.g., 'groceries', 'buy', etc.)"
                                }
                            },
                            "required": ["search_query"]
                        }
                    }
                }
            ]

            # Call OpenAI API with function calling - Loop until no more tool calls
            tool_calls_made = []  # Initialize before loop
            max_iterations = 5  # Prevent infinite loops
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"OpenAI API call iteration {iteration}")

                response = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )

                assistant_message = response.choices[0].message

                # If no tool calls, we're done - return the response
                if not assistant_message.tool_calls:
                    logger.info(f"No tool calls in iteration {iteration}, returning response")
                    return {
                        "response": assistant_message.content or "I'm here to help! What would you like to do?",
                        "tool_calls": tool_calls_made
                    }

                # Process tool calls
                logger.info(f"Processing {len(assistant_message.tool_calls)} tool calls in iteration {iteration}")

                # Add assistant message with tool calls to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool and add results to messages
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        import json
                        tool_args = json.loads(tool_call.function.arguments)  # Parse JSON arguments safely
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse tool arguments: {e}")
                        tool_result = {"error": f"Invalid JSON arguments: {str(e)}"}
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result)
                        })
                        continue

                    # Add user_id to tool arguments
                    tool_args["user_id"] = user_id

                    # Execute MCP tool
                    if tool_name in self.mcp_tools:
                        try:
                            tool_result = await self.mcp_tools[tool_name](**tool_args)
                            logger.info(f"Tool {tool_name} executed successfully with args: {tool_args}, result: {tool_result}")
                            tool_calls_made.append({
                                "tool": tool_name,
                                "parameters": tool_args,
                                "result": tool_result
                            })

                            # Add tool result to messages
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": str(tool_result)
                            })
                        except Exception as e:
                            logger.error(f"Tool {tool_name} execution failed: {str(e)}", exc_info=True)
                            tool_result = {"error": f"Tool execution failed: {str(e)}"}
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": str(tool_result)
                            })
                    else:
                        logger.warning(f"Tool {tool_name} not found in MCP tools")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": f"Tool {tool_name} not found"})
                        })

                # Loop continues - OpenAI will be called again with tool results

            # If we hit max iterations, return what we have
            logger.warning(f"Hit max iterations ({max_iterations}), returning final response")
            final_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            return {
                "response": final_response.choices[0].message.content or "Task operations completed.",
                "tool_calls": tool_calls_made
            }

        except Exception as e:
            logger.error(f"OpenAI agent error: {type(e).__name__}: {str(e)}", exc_info=True)
            return {
                "response": f"I encountered an error: {type(e).__name__}: {str(e)}. Please try again.",
                "tool_calls": []
            }

    async def get_conversations(
        self,
        session: Session,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> dict[str, Any]:
        """
        Get list of conversations for a user with pagination.

        Args:
            session: Database session
            user_id: User identifier
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            dict: {conversations: list, total: int}
        """
        # Get total count
        count_statement = select(func.count(Conversation.id)).where(
            Conversation.user_id == user_id
        )
        total = session.exec(count_statement).one()

        # Get conversations with pagination
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        conversations = session.exec(statement).all()

        # Format conversations with message counts
        conversation_list = []
        for conv in conversations:
            # Count messages in this conversation
            msg_count_statement = select(func.count(Message.id)).where(
                Message.conversation_id == conv.id
            )
            message_count = session.exec(msg_count_statement).one()

            conversation_list.append({
                "id": conv.id,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": message_count
            })

        return {
            "conversations": conversation_list,
            "total": total
        }

    async def get_conversation_messages(
        self,
        session: Session,
        user_id: str,
        conversation_id: UUID,
        limit: int = 50,
        before: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get messages from a specific conversation with pagination.

        Args:
            session: Database session
            user_id: User identifier
            conversation_id: Conversation identifier
            limit: Maximum number of messages to return
            before: ISO timestamp to get messages before (for pagination)

        Returns:
            dict: {messages: list, total: int}

        Raises:
            ValueError: If conversation not found or doesn't belong to user
        """
        # Verify conversation exists and belongs to user
        conv_statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(conv_statement).first()

        if not conversation:
            raise ValueError("Conversation not found or does not belong to user")

        # Get total message count
        count_statement = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
        total = session.exec(count_statement).one()

        # Build query for messages
        statement = select(Message).where(Message.conversation_id == conversation_id)

        # Apply before filter if provided
        if before:
            try:
                before_dt = datetime.fromisoformat(before.replace('Z', '+00:00'))
                statement = statement.where(Message.created_at < before_dt)
            except ValueError:
                raise ValueError("Invalid timestamp format for 'before' parameter")

        # Order by created_at DESC (most recent first) and apply limit
        statement = statement.order_by(desc(Message.created_at)).limit(limit)
        messages = session.exec(statement).all()

        # Reverse to get chronological order (oldest first)
        messages = list(reversed(messages))

        # Format messages
        message_list = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]

        return {
            "messages": message_list,
            "total": total
        }

    async def delete_conversation(
        self,
        session: Session,
        user_id: str,
        conversation_id: UUID
    ) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            session: Database session
            user_id: User identifier
            conversation_id: Conversation identifier to delete

        Returns:
            bool: True if deleted successfully

        Raises:
            ValueError: If conversation not found or doesn't belong to user
        """
        # Verify conversation exists and belongs to user
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()

        if not conversation:
            raise ValueError("Conversation not found or does not belong to user")

        # Delete all messages in the conversation
        msg_statement = select(Message).where(Message.conversation_id == conversation_id)
        messages = session.exec(msg_statement).all()
        for msg in messages:
            session.delete(msg)

        # Delete the conversation
        session.delete(conversation)
        session.commit()

        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
        return True


# Global chat service instance
chat_service = ChatService()
