"""FastAPI route handlers for chat functionality."""
from typing import Optional
from uuid import UUID
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from src.core.auth import get_current_user_id, validate_user_ownership
from src.core.database import get_session
from src.core.rate_limiter import chat_rate_limiter
from src.services.chat_service import chat_service
# from src.services.agent_service import task_agent  # Disabled for now

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Create router for chat endpoints
router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID (optional)")
    message: str = Field(..., max_length=5000, description="User's message")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: UUID = Field(..., description="Conversation ID")
    response: str = Field(..., description="AI assistant's response")
    tool_calls: list = Field(default_factory=list, description="Tools invoked during processing")


class ConversationItem(BaseModel):
    """Model for conversation list item."""
    id: UUID = Field(..., description="Conversation ID")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    updated_at: str = Field(..., description="Last update timestamp (ISO format)")
    message_count: int = Field(..., description="Number of messages in conversation")


class ConversationsResponse(BaseModel):
    """Response model for conversations list endpoint."""
    conversations: list[ConversationItem] = Field(..., description="List of conversations")
    total: int = Field(..., description="Total number of conversations")
    limit: int = Field(..., description="Limit used for pagination")
    offset: int = Field(..., description="Offset used for pagination")


class MessageItem(BaseModel):
    """Model for message item."""
    id: UUID = Field(..., description="Message ID")
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")


class MessagesResponse(BaseModel):
    """Response model for messages list endpoint."""
    messages: list[MessageItem] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages in conversation")
    limit: int = Field(..., description="Limit used for pagination")
    before: Optional[str] = Field(None, description="Timestamp used for pagination")


@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(
    request: ChatRequest,
    user_id: str,
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Send chat message and get AI response.

    This endpoint:
    1. Validates user authentication and ownership
    2. Gets or creates conversation
    3. Loads conversation history (last 50 messages)
    4. Runs OpenAI agent with MCP tools
    5. Persists user and assistant messages
    6. Returns AI response

    Args:
        request: Chat request with message and optional conversation_id
        user_id: User identifier from URL path
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        ChatResponse with conversation_id, response, and tool_calls

    Raises:
        HTTPException: 400 if message exceeds limit
        HTTPException: 401 if JWT invalid
        HTTPException: 403 if accessing other user's conversation
        HTTPException: 404 if conversation not found
        HTTPException: 500 if internal error
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    # Check rate limit
    chat_rate_limiter.check_rate_limit(jwt_user_id)

    logger.info(f"Chat endpoint: send_chat_message called for user_id={user_id}, conversation_id={request.conversation_id}")

    try:
        # Validate message length (5000 character limit)
        if len(request.message) > 5000:
            logger.warning(f"Chat endpoint: Message exceeds 5000 chars for user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message exceeds 5000 character limit"
            )

        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        # Get or create conversation
        try:
            conversation = await chat_service.get_or_create_conversation(
                session=session,
                user_id=jwt_user_id,
                conversation_id=request.conversation_id
            )
            logger.info(f"Chat endpoint: Conversation retrieved/created - conversation_id={conversation.id}, user_id={user_id}")
        except ValueError as e:
            logger.warning(f"Chat endpoint: Conversation not found for user_id={user_id}, conversation_id={request.conversation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

        # Load message history (last 50 messages)
        message_history = await chat_service.load_messages(
            session=session,
            conversation_id=conversation.id,
            limit=50
        )
        logger.info(f"Chat endpoint: Loaded {len(message_history)} messages for conversation_id={conversation.id}")

        # Run OpenAI agent with conversation context
        agent_result = await chat_service.run_agent(
            user_id=jwt_user_id,
            user_message=request.message,
            conversation_history=message_history
        )
        logger.info(f"Chat endpoint: OpenAI agent executed - {len(agent_result.get('tool_calls', []))} tool calls made")

        # Persist user message
        await chat_service.save_message(
            session=session,
            conversation_id=conversation.id,
            user_id=jwt_user_id,
            role="user",
            content=request.message
        )

        # Persist assistant response
        await chat_service.save_message(
            session=session,
            conversation_id=conversation.id,
            user_id=jwt_user_id,
            role="assistant",
            content=agent_result["response"]
        )
        logger.info(f"Chat endpoint: Messages persisted for conversation_id={conversation.id}")

        logger.info(f"Chat endpoint: send_chat_message success for user_id={user_id}, conversation_id={conversation.id}")
        return ChatResponse(
            conversation_id=conversation.id,
            response=agent_result["response"],
            tool_calls=agent_result["tool_calls"]
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error and return generic error message
        logger.error(f"Chat endpoint: send_chat_message error for user_id={user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{user_id}/conversations", response_model=ConversationsResponse, status_code=status.HTTP_200_OK)
async def get_conversations(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ConversationsResponse:
    """
    Get list of conversations for a user.

    This endpoint:
    1. Validates user authentication and ownership
    2. Retrieves conversations with pagination
    3. Includes message count for each conversation
    4. Orders by updated_at DESC (most recent first)

    Args:
        user_id: User identifier from URL path
        limit: Maximum number of conversations to return (default 20, max 100)
        offset: Number of conversations to skip (default 0)
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        ConversationsResponse with list of conversations and pagination info

    Raises:
        HTTPException: 401 if JWT invalid
        HTTPException: 403 if accessing other user's conversations
        HTTPException: 500 if internal error
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Validate pagination parameters
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )
        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative"
            )

        # Get conversations with pagination
        conversations_data = await chat_service.get_conversations(
            session=session,
            user_id=jwt_user_id,
            limit=limit,
            offset=offset
        )

        return ConversationsResponse(
            conversations=conversations_data["conversations"],
            total=conversations_data["total"],
            limit=limit,
            offset=offset
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{user_id}/conversations/{conversation_id}/messages", response_model=MessagesResponse, status_code=status.HTTP_200_OK)
async def get_conversation_messages(
    user_id: str,
    conversation_id: UUID,
    limit: int = 50,
    before: Optional[str] = None,
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> MessagesResponse:
    """
    Get messages from a specific conversation.

    This endpoint:
    1. Validates user authentication and ownership
    2. Validates conversation belongs to user
    3. Retrieves messages with pagination
    4. Orders by created_at ASC (chronological order)

    Args:
        user_id: User identifier from URL path
        conversation_id: Conversation identifier
        limit: Maximum number of messages to return (default 50, max 100)
        before: ISO timestamp to get messages before (for pagination)
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        MessagesResponse with list of messages and pagination info

    Raises:
        HTTPException: 401 if JWT invalid
        HTTPException: 403 if accessing other user's conversation
        HTTPException: 404 if conversation not found
        HTTPException: 500 if internal error
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Validate pagination parameters
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )

        # Get messages with pagination
        messages_data = await chat_service.get_conversation_messages(
            session=session,
            user_id=jwt_user_id,
            conversation_id=conversation_id,
            limit=limit,
            before=before
        )

        return MessagesResponse(
            messages=messages_data["messages"],
            total=messages_data["total"],
            limit=limit,
            before=before
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{user_id}/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    user_id: str,
    conversation_id: UUID,
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a conversation and all its messages.

    This endpoint:
    1. Validates user authentication and ownership
    2. Validates conversation belongs to user
    3. Deletes all messages in the conversation
    4. Deletes the conversation

    Args:
        user_id: User identifier from URL path
        conversation_id: Conversation identifier to delete
        jwt_user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 401 if JWT invalid
        HTTPException: 403 if accessing other user's conversation
        HTTPException: 404 if conversation not found
        HTTPException: 500 if internal error
    """
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    try:
        # Delete conversation
        await chat_service.delete_conversation(
            session=session,
            user_id=jwt_user_id,
            conversation_id=conversation_id
        )

        logger.info(f"Chat endpoint: delete_conversation success for user_id={user_id}, conversation_id={conversation_id}")

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint: delete_conversation error for user_id={user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
