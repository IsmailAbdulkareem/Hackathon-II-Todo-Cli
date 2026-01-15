# Phase 0: Research - AI-Powered Todo Chatbot

**Date**: 2026-01-15
**Feature**: 001-ai-chatbot
**Purpose**: Resolve technical unknowns identified in Technical Context

## Research Topics

### 1. MCP SDK Python Implementation Patterns and Best Practices

**Decision**: Use official MCP Python SDK with FastAPI integration

**Rationale**:
- MCP (Model Context Protocol) is designed for exposing application functionality as tools that AI agents can invoke
- Python SDK provides server implementation with tool registration patterns
- FastAPI integration allows MCP server to run alongside existing backend
- Tools are defined as Python functions with type hints and docstrings for automatic schema generation

**Implementation Pattern**:
```python
from mcp import Server, Tool

# Define MCP server
mcp_server = Server("todo-mcp-server")

# Register tools with type hints
@mcp_server.tool()
async def add_task(user_id: str, title: str, description: str = None) -> dict:
    """Create a new task for the user."""
    # Implementation calls existing task service
    pass

@mcp_server.tool()
async def list_tasks(user_id: str, status: str = "all") -> list:
    """List tasks filtered by status (all, pending, completed)."""
    pass
```

**Best Practices**:
- Keep tools stateless - accept user_id as parameter
- Use existing service layer (don't duplicate task logic)
- Return structured data (dicts/lists) for AI agent consumption
- Include comprehensive docstrings for tool discovery
- Handle errors gracefully with descriptive messages

**Alternatives Considered**:
- Custom tool protocol: Rejected - MCP is standardized and well-supported
- REST API only: Rejected - MCP provides better AI agent integration

---

### 2. OpenAI Agents SDK Integration with FastAPI

**Decision**: Use OpenAI Agents SDK with async FastAPI endpoint

**Rationale**:
- OpenAI Agents SDK provides natural language interpretation and tool orchestration
- Supports MCP tool integration out of the box
- Async/await pattern compatible with FastAPI
- Handles conversation context management internally

**Implementation Pattern**:
```python
from fastapi import APIRouter, Depends
from openai import AsyncOpenAI
from openai.agents import Agent

router = APIRouter()

# Initialize agent with MCP tools
agent = Agent(
    name="todo-assistant",
    instructions="You help users manage their todo tasks through natural language.",
    tools=mcp_server.get_tools(),  # MCP tools
    model="gpt-4"
)

@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    # Load conversation history from database
    conversation = get_or_create_conversation(user_id, request.conversation_id)
    messages = load_messages(conversation.id, limit=50)

    # Run agent with context
    response = await agent.run(
        messages=messages + [{"role": "user", "content": request.message}]
    )

    # Persist messages
    save_message(conversation.id, "user", request.message)
    save_message(conversation.id, "assistant", response.content)

    return {
        "conversation_id": conversation.id,
        "response": response.content,
        "tool_calls": response.tool_calls
    }
```

**Best Practices**:
- Load conversation history before each request (stateless endpoint)
- Limit history to last 50 messages for performance
- Persist both user and assistant messages immediately
- Return conversation_id for client-side tracking
- Handle OpenAI API errors with user-friendly messages

**Alternatives Considered**:
- LangChain: Rejected - more complex, OpenAI SDK is simpler for this use case
- Custom NLP: Rejected - requires significant ML expertise and training data

---

### 3. Hosted ChatKit Domain Allowlisting and Configuration Workflow

**Decision**: Use OpenAI's hosted ChatKit with domain allowlisting

**Rationale**:
- Hackathon requirement mandates hosted ChatKit (not self-hosted)
- Domain allowlisting is security requirement for production deployment
- Provides pre-built chat UI components with minimal configuration

**Configuration Workflow**:

1. **Deploy Frontend First**:
   - Deploy Next.js app to Vercel
   - Obtain production URL (e.g., `https://todo-chatbot.vercel.app`)

2. **Configure Domain Allowlist**:
   - Navigate to OpenAI Platform → Organization → Security → Domain Allowlist
   - Add production URL (without trailing slash)
   - Save configuration

3. **Obtain Domain Key**:
   - OpenAI provides domain key after allowlisting
   - Add to environment variables: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<key>`

4. **Initialize ChatKit**:
```typescript
import { ChatKit } from '@openai/chatkit';

export default function ChatPage() {
  return (
    <ChatKit
      domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
      apiEndpoint="/api/chat"
      onMessage={handleMessage}
    />
  );
}
```

**Best Practices**:
- Test locally first (localhost typically works without allowlisting)
- Add domain key to environment variables (never commit to git)
- Document deployment order in quickstart.md
- Handle ChatKit initialization errors gracefully

**Alternatives Considered**:
- Self-hosted ChatKit: Rejected - violates hackathon requirements
- Custom chat UI: Rejected - more development time, hosted ChatKit is required

---

### 4. Stateless Chat Endpoint Architecture with Conversation State Persistence

**Decision**: Stateless FastAPI endpoint with PostgreSQL conversation persistence

**Rationale**:
- Stateless design enables horizontal scaling
- Database persistence ensures conversation continuity across sessions
- Each request is independent and reproducible
- Aligns with Phase 2 architecture (FastAPI + PostgreSQL)

**Architecture Pattern**:

```
Request Flow:
1. Client sends message + optional conversation_id
2. Backend loads conversation from database (or creates new)
3. Backend loads last 50 messages from database
4. Backend runs AI agent with full context
5. Backend persists user message and assistant response
6. Backend returns response + conversation_id
7. Server holds NO state (ready for next request)
```

**Database Schema**:
- Conversation: id, user_id, created_at, updated_at
- Message: id, conversation_id, user_id, role, content, created_at

**Implementation Pattern**:
```python
def get_or_create_conversation(user_id: str, conversation_id: int = None):
    if conversation_id:
        # Load existing conversation
        conv = session.get(Conversation, conversation_id)
        if not conv or conv.user_id != user_id:
            raise HTTPException(404, "Conversation not found")
        return conv
    else:
        # Create new conversation
        conv = Conversation(user_id=user_id)
        session.add(conv)
        session.commit()
        return conv

def load_messages(conversation_id: int, limit: int = 50):
    # Load last N messages ordered by created_at DESC
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()
    return list(reversed(messages))  # Return chronological order
```

**Best Practices**:
- Always validate user owns conversation before loading
- Use pagination for message history (50 messages default)
- Index conversation_id and created_at for query performance
- Transaction boundaries: persist messages atomically
- Return conversation_id in every response for client tracking

**Alternatives Considered**:
- In-memory session state: Rejected - doesn't scale, loses state on restart
- Redis cache: Rejected - adds complexity, database is sufficient for this scale

---

### 5. MCP Tool Definition Patterns for Task Operations

**Decision**: Define 5 MCP tools matching CRUD operations

**Rationale**:
- Each tool maps to a specific task operation
- Tools accept user_id to enforce ownership
- Return structured data for AI agent interpretation
- Reuse existing Phase 2 task service logic

**Tool Definitions**:

1. **add_task**
   - Parameters: user_id (str), title (str), description (str, optional)
   - Returns: {task_id, status, title}
   - Maps to: POST /api/{user_id}/tasks

2. **list_tasks**
   - Parameters: user_id (str), status (str = "all" | "pending" | "completed")
   - Returns: [{id, title, description, completed, created_at}, ...]
   - Maps to: GET /api/{user_id}/tasks

3. **complete_task**
   - Parameters: user_id (str), task_id (int)
   - Returns: {task_id, status, title}
   - Maps to: PATCH /api/{user_id}/tasks/{id}/complete

4. **delete_task**
   - Parameters: user_id (str), task_id (int)
   - Returns: {task_id, status, title}
   - Maps to: DELETE /api/{user_id}/tasks/{id}

5. **update_task**
   - Parameters: user_id (str), task_id (int), title (str, optional), description (str, optional)
   - Returns: {task_id, status, title}
   - Maps to: PUT /api/{user_id}/tasks/{id}

**Implementation Pattern**:
```python
@mcp_server.tool()
async def add_task(user_id: str, title: str, description: str = None) -> dict:
    """
    Create a new task for the user.

    Args:
        user_id: User identifier
        title: Task title (max 200 characters)
        description: Optional task description (max 2000 characters)

    Returns:
        dict: {task_id: int, status: str, title: str}
    """
    # Validate character limits
    if len(title) > 200:
        return {"error": "Title exceeds 200 character limit"}
    if description and len(description) > 2000:
        return {"error": "Description exceeds 2000 character limit"}

    # Call existing task service
    task = await task_service.create_task(user_id, title, description)

    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }
```

**Best Practices**:
- Include comprehensive docstrings (AI agent uses these)
- Validate inputs before calling service layer
- Return consistent response format
- Handle errors gracefully with descriptive messages
- Log tool invocations for debugging

**Alternatives Considered**:
- Single "manage_task" tool: Rejected - too complex, harder for AI to use correctly
- Direct database access: Rejected - bypasses existing validation and business logic

---

## Summary

All technical unknowns have been resolved:

1. ✅ MCP SDK Python patterns identified - use official SDK with FastAPI
2. ✅ OpenAI Agents SDK integration designed - async endpoint with conversation context
3. ✅ Hosted ChatKit workflow documented - deploy → allowlist → configure
4. ✅ Stateless architecture defined - database-persisted conversations
5. ✅ MCP tool patterns established - 5 tools mapping to task operations

**Next Phase**: Phase 1 - Design & Contracts (data-model.md, contracts/, quickstart.md)
