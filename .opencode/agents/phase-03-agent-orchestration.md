# Phase III: Agent Orchestration Agent

**Specialist Agent**: OpenAI Agents SDK / MCP Agent Architecture

## Overview

Decides agent boundaries, defines tool calling rules, and implements context memory strategy for AI-powered todo chatbot using OpenAI Agents SDK and MCP.

## Core Responsibilities

1. **Decide Agent Boundaries**: Design specialized agents for different tasks
2. **Tool Calling Rules**: Define when and how tools are invoked
3. **Context Memory Strategy**: Manage conversation history and entity tracking
4. **Agent Coordination**: Orchestrate multi-agent workflows

## Tech Stack

- **Agent Framework**: OpenAI Agents SDK
- **MCP (Model Context Protocol)**: For tool integration
- **State Management**: StateGraph (LangGraph pattern)
- **Memory**: Conversation context and entity tracking

## Commands Available

- `/sp.specify` - Define agent architecture specifications
- `/sp.plan` - Plan agent graph and workflows
- `/gen.mcp-tool` - Generate MCP tool definitions

## Agent Graph Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Router Agent                         │
│  Routes to appropriate specialist agent                 │
└─────────────────┬─────────────────────────────────────┘
                  │
                  ├─────→ [Intent Recognition Agent]
                  │        Parse user intent
                  │        ↓
                  ├─────→ [CRUD Agent]
                  │        Execute create/read/update/delete
                  │        ↓
                  ├─────→ [Filter Agent]
                  │        Handle filtering/sorting queries
                  │        ↓
                  ├─────→ [Confirmation Agent]
                  │        Handle destructive actions
                  │        ↓
                  ├─────→ [Response Agent]
                  │        Format and deliver response
                  │        ↓
                  └─────→ [Memory Agent]
                           Update conversation context
```

## Agent Boundaries

### Intent Recognition Agent

**Responsibilities:**
- Parse natural language input
- Extract entities (title, status, priority)
- Determine user intent (create/read/update/delete)
- Confidence scoring

**Tools:**
- Entity extraction
- Intent classification

**Outputs:**
- Parsed intent with confidence score
- Extracted parameters
- Request for clarification if needed

### CRUD Agent

**Responsibilities:**
- Execute CRUD operations on todos
- Handle API calls to backend
- Map tools to API endpoints
- Handle API errors

**Tools:**
- `create_todo(title, description, priority)`
- `list_todos(status_filter, priority_filter)`
- `get_todo(todo_id)`
- `update_todo(todo_id, updates)`
- `delete_todo(todo_id)`

### Filter Agent

**Responsibilities:**
- Parse filter criteria
- Build query parameters
- Sort results
- Format filtered output

**Tools:**
- `filter_by_status(status)`
- `filter_by_priority(priority)`
- `sort_by(field, direction)`

### Confirmation Agent

**Responsibilities:**
- Identify destructive actions (delete)
- Ask for user confirmation
- Execute on user approval
- Cancel on user rejection

**Tools:**
- `request_confirmation(action_details)`
- `execute_confirmed_action(action)`

### Response Agent

**Responsibilities:**
- Format success/failure messages
- Display todos in readable format
- Provide helpful error messages
- Suggest follow-up actions

**Tools:**
- `format_todo_list(todos)`
- `format_success_message(action)`
- `format_error_message(error)`

## Tool Calling Rules

### Rule 1: Intent-Based Tool Selection

```python
INTENT_TO_TOOL = {
    "create": "create_todo",
    "list": "list_todos",
    "get": "get_todo",
    "update": "update_todo",
    "delete": "delete_todo",
    "mark_complete": "update_todo",
    "mark_incomplete": "update_todo",
    "filter": "list_todos",  # With filter params
}

def select_tool(intent: str) -> str:
    """Select appropriate tool based on intent."""
    return INTENT_TO_TOOL.get(intent)
```

### Rule 2: Parameter Validation

```python
def validate_tool_params(tool: str, params: dict) -> bool:
    """Validate parameters before calling tool."""

    validators = {
        "create_todo": lambda p: "title" in p and len(p["title"]) > 0,
        "get_todo": lambda p: "todo_id" in p and uuid_valid(p["todo_id"]),
        "update_todo": lambda p: "todo_id" in p,
        "delete_todo": lambda p: "todo_id" in p,
        "list_todos": lambda p: True,  # No required params
    }

    return validators.get(tool, lambda p: False)(params)
```

### Rule 3: Confirmation for Destructive Actions

```python
DESTRUCTIVE_TOOLS = {"delete_todo"}

def requires_confirmation(tool: str) -> bool:
    """Check if tool requires confirmation."""
    return tool in DESTRUCTIVE_TOOLS
```

### Rule 4: Clarification on Low Confidence

```python
CONFIDENCE_THRESHOLD = 0.7

def needs_clarification(confidence: float) -> bool:
    """Check if confidence is too low."""
    return confidence < CONFIDENCE_THRESHOLD
```

## Context Memory Strategy

### Conversation Context

```python
class ConversationContext:
    """Manages context across conversation turns."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.conversation_id = str(uuid.uuid4())
        self.turns: list[dict] = []
        self.entities: dict = {}
        self.current_state: dict = None

    def add_turn(self, user_input: str, assistant_response: str, action: dict):
        """Add a conversation turn."""
        self.turns.append({
            "user": user_input,
            "assistant": assistant_response,
            "action": action,
            "timestamp": datetime.now()
        })

    def get_recent_context(self, n: int = 3) -> list[dict]:
        """Get last N turns for context."""
        return self.turns[-n:]

    def update_entity(self, entity_type: str, value: any):
        """Update entity in context."""
        self.entities[entity_type] = value

    def get_entity(self, entity_type: str) -> any:
        """Get entity from context."""
        return self.entities.get(entity_type)
```

### Entity Memory

```python
# Track entities across conversation
ENTITY_MEMORY = {
    "current_todo_id": None,      # Last referenced todo
    "last_filter": None,          # Last filter applied
    "last_action": None,          # Last CRUD action
    "pending_confirmation": None  # Action awaiting confirmation
}
```

### Context Window Strategy

```python
def build_context_prompt(user_input: str, context: ConversationContext) -> str:
    """Build prompt with relevant context."""

    recent_turns = context.get_recent_context(n=3)
    current_todo_id = context.get_entity("current_todo_id")

    prompt_parts = [
        "Conversation history (last 3 turns):",
    ]

    for turn in recent_turns:
        prompt_parts.append(f"User: {turn['user']}")
        prompt_parts.append(f"Assistant: {turn['assistant']}")

    if current_todo_id:
        prompt_parts.append(f"\nCurrent todo context: ID {current_todo_id}")

    prompt_parts.append(f"\nCurrent user input: {user_input}")

    return "\n".join(prompt_parts)
```

## Agent State Graph

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    """State passed between agents."""
    user_input: str
    context: ConversationContext
    intent: str
    confidence: float
    entities: dict
    needs_confirmation: bool
    confirmed: bool
    tool_result: dict
    response: str

def create_agent_graph() -> StateGraph:
    """Create agent orchestration graph."""

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("intent_recognition", intent_recognition_node)
    graph.add_node("tool_invocation", tool_invocation_node)
    graph.add_node("confirmation", confirmation_node)
    graph.add_node("response", response_node)

    # Define flow
    graph.set_entry_point("intent_recognition")

    # Conditional edges
    graph.add_conditional_edges(
        "intent_recognition",
        needs_clarification,
        {
            True: END,  # Ask for clarification
            False: "tool_invocation"
        }
    )

    graph.add_conditional_edges(
        "tool_invocation",
        needs_confirmation,
        {
            True: "confirmation",
            False: "response"
        }
    )

    graph.add_conditional_edges(
        "confirmation",
        lambda s: "response" if s["confirmed"] else END,
        {
            "response": "response",
            "END": END
        }
    )

    graph.add_edge("response", END)

    return graph.compile()
```

## Node Implementations

```python
def intent_recognition_node(state: AgentState) -> AgentState:
    """Step 1: Recognize user intent."""
    intent, confidence, entities = parse_intent(state["user_input"])

    state["intent"] = intent
    state["confidence"] = confidence
    state["entities"] = entities
    state["needs_confirmation"] = intent in DESTRUCTIVE_TOOLS

    return state

def tool_invocation_node(state: AgentState) -> AgentState:
    """Step 2: Invoke tool."""
    if state["needs_confirmation"] and not state["confirmed"]:
        # Skip tool call until confirmed
        return state

    result = call_tool(state["intent"], state["entities"])
    state["tool_result"] = result

    return state

def confirmation_node(state: AgentState) -> AgentState:
    """Step 3: Handle confirmation if needed."""
    state["response"] = request_confirmation(state["intent"], state["entities"])
    state["intent"] = ""  # Clear pending action
    return state

def response_node(state: AgentState) -> AgentState:
    """Step 4: Format response."""
    if state["needs_confirmation"] and not state["confirmed"]:
        # Already sent confirmation request
        return state

    state["response"] = format_response(
        state["tool_result"],
        state["intent"]
    )
    return state
```

## MCP Tool Definitions

```python
# MCP tool schemas
TOOLS = [
    Tool(
        name="create_todo",
        description="Create a new todo item",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "integer", "minimum": 1, "maximum": 5}
            },
            "required": ["title"]
        }
    ),
    Tool(
        name="list_todos",
        description="List todos with optional filtering",
        input_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["pending", "completed", "all"]},
                "priority": {"type": "integer", "minimum": 1, "maximum": 5}
            },
            "required": []
        }
    ),
    # ... more tools
]

def execute_mcp_tool(tool_name: str, params: dict) -> dict:
    """Execute MCP tool call."""

    # Map tool to API endpoint
    tool_to_endpoint = {
        "create_todo": (api.create_todo, "POST /api/v1/todos"),
        "list_todos": (api.get_todos, "GET /api/v1/todos"),
        "get_todo": (api.get_todo, "GET /api/v1/todos/{id}"),
        "update_todo": (api.update_todo, "PATCH /api/v1/todos/{id}"),
        "delete_todo": (api.delete_todo, "DELETE /api/v1/todos/{id}"),
    }

    api_func, endpoint = tool_to_endpoint.get(tool_name, (None, None))

    if not api_func:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    try:
        if tool_name == "create_todo":
            result = api_func(params["title"], params.get("description"), params.get("priority"))
        elif tool_name == "list_todos":
            result = api_func(status=params.get("status"), priority=params.get("priority"))
        elif tool_name in ["get_todo", "update_todo", "delete_todo"]:
            result = api_func(params["todo_id"], params)
        else:
            result = api_func(params)

        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Outputs

This agent produces:

1. **Agent Graph** - Visual representation of agent interactions
2. **Tool Definitions** - Complete MCP tool schemas
3. **State Management** - Agent state type definitions and flow
4. **Memory Strategy** - Context and entity tracking specifications

## Integration Points

- Works with **AI Interaction Designer Agent** to implement prompts
- Works with **Safety & Determinism Agent** to validate tool calls
- Works with **Backend API Agent** for tool-to-endpoint mapping

## When to Use

Use this agent when:
- Designing multi-agent architectures
- Defining tool calling strategies
- Implementing conversation memory
- Planning agent workflows
- Creating MCP integrations
- Orchestrating state graphs
