# Phase III: AI Interaction Designer Agent

**Specialist Agent**: Conversation Design for AI-Powered Chatbot

## Overview

Focuses on conversation design, defining user intents, mapping intents to CRUD actions, and designing system prompts for the AI-powered todo chatbot.

## Core Responsibilities

1. **Define User Intents**: Identify and classify user intentions in natural language
2. **Map Intents to Actions**: Connect intents to CRUD operations on todos
3. **Design System Prompts**: Create effective prompts for LLM behavior
4. **Conversation Flow**: Design intuitive multi-turn interactions

## Tech Stack

- **LLM**: OpenAI GPT-4 or similar
- **Agent SDK**: OpenAI Agents SDK
- **Function Calling**: Tool-based execution
- **Memory**: Conversation context management

## Commands Available

- `/sp.specify` - Define chat interaction specifications
- `/sp.plan` - Plan conversation flows
- `/sp.checklist` - Generate conversation design checklist

## User Intents

### Intent Classification

```
CREATE intents:
- "Add a todo to buy groceries"
- "Create a new task: finish report"
- "I need to do laundry"
- "Remind me to call mom"

READ intents:
- "Show me my todos"
- "What's on my list?"
- "List all active tasks"
- "What do I have to do today?"

UPDATE intents:
- "Mark groceries as completed"
- "I finished the report"
- "Change priority of laundry to high"
- "Update todo title to 'Buy milk'"

DELETE intents:
- "Remove the grocery task"
- "Delete the laundry todo"
- "I don't need to call mom anymore"

FILTER intents:
- "Show only completed todos"
- "What's pending?"
- "Filter by high priority"
- "Show tasks due today"
```

### Intent Detection Patterns

```python
# Intents mapped to actions
INTENT_TO_ACTION = {
    "create_todo": ("POST", "/api/v1/todos"),
    "list_todos": ("GET", "/api/v1/todos"),
    "get_todo": ("GET", "/api/v1/todos/{id}"),
    "update_todo": ("PATCH", "/api/v1/todos/{id}"),
    "delete_todo": ("DELETE", "/api/v1/todos/{id}"),
    "mark_complete": ("PATCH", "/api/v1/todos/{id}"),
    "mark_incomplete": ("PATCH", "/api/v1/todos/{id}"),
    "filter_todos": ("GET", "/api/v1/todos"),
}
```

## Intent to CRUD Mapping

### CREATE Operations

**User Says**: "Add a todo to buy groceries"

**Extracted Data**:
- title: "Buy groceries"
- description: None
- priority: 1 (default)

**Action**:
```json
{
  "intent": "create_todo",
  "action": "POST /api/v1/todos",
  "params": {
    "title": "Buy groceries",
    "status": "pending",
    "priority": 1
  }
}
```

### READ Operations

**User Says**: "Show me all my pending todos"

**Extracted Data**:
- status: "pending"

**Action**:
```json
{
  "intent": "filter_todos",
  "action": "GET /api/v1/todos?status=pending",
  "params": {
    "status": "pending"
  }
}
```

### UPDATE Operations

**User Says**: "Mark the groceries todo as completed"

**Extracted Data**:
- identifier: "groceries"
- status: "completed"

**Action**:
```json
{
  "intent": "mark_complete",
  "action": "PATCH /api/v1/todos/{id}",
  "params": {
    "id": "<searched from title>",
    "status": "completed"
  }
}
```

### DELETE Operations

**User Says**: "Delete the laundry task"

**Extracted Data**:
- identifier: "laundry"

**Action**:
```json
{
  "intent": "delete_todo",
  "action": "DELETE /api/v1/todos/{id}",
  "params": {
    "id": "<searched from title>"
  }
}
```

## System Prompt Design

### Base System Prompt

```python
SYSTEM_PROMPT = """
You are a helpful AI assistant for managing todo lists. Your role is to help users
create, read, update, and delete their todos through natural conversation.

Your Capabilities:
1. Create new todos with title, description, and priority
2. List todos with filtering (by status, priority, date)
3. Update existing todos (title, description, status, priority)
4. Mark todos as complete or incomplete
5. Delete todos

Your Behavior:
- Be concise and friendly
- Ask clarifying questions when intent is ambiguous
- Confirm destructive actions (delete) before executing
- Provide clear feedback after each action
- Handle errors gracefully with helpful messages

When users mention a todo by description (e.g., "the grocery task"), search
their todos by title to find the correct ID.

Example interactions:
User: "Add a todo to buy groceries"
Assistant: "I'll add 'Buy groceries' to your todo list. ✓ Added!"

User: "Show me my pending todos"
Assistant: "Here are your pending todos: [list]"

User: "Mark groceries as done"
Assistant: "I've marked 'Buy groceries' as completed. ✓ Done!"
"""
```

### Action-Oriented Prompt

```python
ACTION_PROMPT = """
Analyze the user's request and determine the appropriate CRUD action.

Return a JSON object with:
{
  "intent": "create_todo | read_todo | update_todo | delete_todo",
  "action": "HTTP method and endpoint",
  "confidence": 0-1 score,
  "extracted_params": {...},
  "clarification_needed": boolean,
  "clarification_question": "What to ask if needed"
}

Examples:
Input: "Add a todo to buy milk"
Output: {
  "intent": "create_todo",
  "action": "POST /api/v1/todos",
  "confidence": 0.95,
  "extracted_params": {"title": "buy milk"},
  "clarification_needed": false
}

Input: "Mark the task about groceries as completed"
Output: {
  "intent": "update_todo",
  "action": "PATCH /api/v1/todos/{id}",
  "confidence": 0.90,
  "extracted_params": {"title_contains": "groceries", "status": "completed"},
  "clarification_needed": false
}

Input: "Do that thing"
Output: {
  "intent": null,
  "action": null,
  "confidence": 0.2,
  "extracted_params": {},
  "clarification_needed": true,
  "clarification_question": "Which todo would you like me to help with?"
}
"""
```

## Conversation Flow Design

### 1. Todo Creation Flow

```
User: Add a todo to buy groceries
Assistant: I'll add 'Buy groceries' to your todo list. ✓ Added!

User: Make it high priority
Assistant: I've updated 'Buy groceries' to high priority. ✓ Updated!

User: Add eggs to the description
Assistant: Updated description for 'Buy groceries': "Add eggs". ✓ Updated!
```

### 2. Todo List Flow

```
User: Show me all my todos
Assistant: Here are your todos:
  - [ ] Buy groceries (pending, priority 1)
  - [ ] Finish report (pending, priority 3)
  - [x] Call mom (completed, priority 2)

User: Only show pending ones
Assistant: Here are your pending todos:
  - [ ] Buy groceries (pending, priority 1)
  - [ ] Finish report (pending, priority 3)
```

### 3. Todo Completion Flow

```
User: Mark groceries as done
Assistant: I've marked 'Buy groceries' as completed. ✓ Done!

User: Actually, undo that
Assistant: I've marked 'Buy groceries' as pending again. ✓ Restored!
```

### 4. Todo Deletion Flow (with Confirmation)

```
User: Delete the grocery task
Assistant: Are you sure you want to delete 'Buy groceries'? This action cannot be undone.
(Yes/No)

User: Yes
Assistant: Deleted 'Buy groceries'. ✓ Removed!
```

## Tool Definitions

```python
# Tools for the AI agent
TOOLS = [
    {
        "name": "create_todo",
        "description": "Create a new todo item",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Todo title"},
                "description": {"type": "string", "description": "Optional description"},
                "priority": {"type": "integer", "description": "Priority 1-5", "default": 1}
            },
            "required": ["title"]
        }
    },
    {
        "name": "list_todos",
        "description": "List todos with optional filtering",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["pending", "completed", "all"]},
                "priority": {"type": "integer", "minimum": 1, "maximum": 5}
            },
            "required": []
        }
    },
    {
        "name": "update_todo",
        "description": "Update an existing todo",
        "parameters": {
            "type": "object",
            "properties": {
                "todo_id": {"type": "string", "description": "Todo UUID"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string", "enum": ["pending", "completed"]},
                "priority": {"type": "integer", "minimum": 1, "maximum": 5}
            },
            "required": ["todo_id"]
        }
    },
    {
        "name": "delete_todo",
        "description": "Delete a todo",
        "parameters": {
            "type": "object",
            "properties": {
                "todo_id": {"type": "string", "description": "Todo UUID"}
            },
            "required": ["todo_id"]
        }
    }
]
```

## Conversation Memory Strategy

```python
class ConversationMemory:
    """Manages conversation context across turns."""

    def __init__(self):
        self.history = []
        self.current_todo = None  # Track last mentioned todo
        self.last_action = None   # Track last CRUD operation

    def add_message(self, role: str, content: str):
        """Add message to conversation history."""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })

    def get_context_window(self, limit: int = 10) -> list:
        """Get recent conversation history."""
        return self.history[-limit:]

    def set_current_todo(self, todo: dict):
        """Track the todo currently being discussed."""
        self.current_todo = todo

    def get_current_todo(self) -> Optional[dict]:
        """Get the currently referenced todo."""
        return self.current_todo
```

## Natural Language Processing

### Entity Extraction

```python
def extract_todo_entities(user_input: str) -> dict:
    """Extract entities from natural language."""

    entities = {
        "title": None,
        "description": None,
        "status": None,
        "priority": None,
        "due_date": None
    }

    # Extract title (main task)
    title_patterns = [
        r"(?:add|create|new) (?:a )?todo(?: to)? (.+)",
        r"(?:i need to|i have to|i must) (.+)",
    ]

    for pattern in title_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            entities["title"] = match.group(1).strip().rstrip(".")
            break

    # Extract priority
    priority_keywords = {
        "urgent": 5, "high": 4, "important": 3, "normal": 2, "low": 1
    }

    for keyword, priority in priority_keywords.items():
        if keyword in user_input.lower():
            entities["priority"] = priority
            break

    # Extract status
    if any(word in user_input.lower() for word in ["done", "completed", "finished"]):
        entities["status"] = "completed"
    elif any(word in user_input.lower() for word in ["pending", "todo", "task"]):
        entities["status"] = "pending"

    return entities
```

## Error Handling & Clarification

### Ambiguity Resolution

```python
def resolve_ambiguity(user_input: str, todos: list) -> Optional[str]:
    """Ask clarifying questions when intent is ambiguous."""

    if len(todos) == 0:
        return "You don't have any todos yet. Would you like to create one?"

    # Multiple todos match
    if "that" in user_input.lower() and len(todos) > 1:
        return f"Which todo? Here are your todos: {[t['title'] for t in todos]}"

    # No specific todo mentioned
    if "todo" in user_input.lower() and len(todos) > 1:
        return "Which todo would you like me to help with?"

    return None
```

## Outputs

This agent produces:

1. **Chat Interaction Specification** - Complete intent definitions and mappings
2. **Prompt Templates** - System prompts for different scenarios
3. **Conversation Flow Documents** - Flow diagrams for each interaction type
4. **Tool Definitions** - JSON schemas for function calling

## Integration Points

- Works with **Agent Orchestration Agent** to implement prompt strategies
- Works with **Safety & Determinism Agent** to validate intent detection
- Works with **Backend API Agent** to map intents to endpoints

## When to Use

Use this agent when:
- Designing new chatbot features
- Defining user intents and actions
- Creating system prompts
- Planning conversation flows
- Implementing natural language understanding
- Designing tool/function calling interfaces
