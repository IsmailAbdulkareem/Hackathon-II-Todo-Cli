# MCP Tool Generator

**Critical for Phase:** III

Generates MCP (Model Context Protocol) tools following Official MCP SDK patterns for AI agent integration.

## Usage

```
/gen.mcp-tool <tool_name> "<description>"

# Examples:
/gen.mcp-tool add_task "Create new todo with title and optional description"
/gen.mcp-tool list_tasks "Get all todos for user, optionally filter by completion status"
/gen.mcp-tool complete_task "Mark todo as completed by ID"
/gen.mcp-tool delete_task "Delete todo by ID"
/gen.mcp-tool parse_todo "Parse natural language to todo entity (NLP)"
```

## What It Generates

- MCP tool handler class
- Input schema with validation
- Error handling for MCP protocol
- Tool metadata (description, parameters)
- Integration with database layer
- Logging for debugging
- Unit tests

## Output Structure

```
phase-XX/src/mcp/tools/
  ├── base.py              # Base MCP tool class
  ├── add_todo.py          # Add task tool
  ├── list_todos.py        # List tasks tool
  ├── complete_todo.py      # Complete task tool
  ├── delete_todo.py        # Delete task tool
  ├── parse_todo.py         # NLP parsing tool
  └── __init__.py         # Tool registry
```

## Features

- Official MCP SDK compliance
- Type-safe input validation
- Async support for database calls
- Proper error formatting for AI
- Tool discovery metadata
- Permission checks (user isolation)
- Detailed error messages for AI understanding

## Phase Usage

- **Phase III:** All 5 task management tools
- **Phase III:** NLP tools for natural language parsing
- **Phase III:** Scheduling tools for smart date extraction

## Example Output

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Optional
import json

server = Server("todo-server")

class AddTodoTool:
    """MCP tool for adding a new todo item."""

    @staticmethod
    def get_tool_definition() -> Tool:
        return Tool(
            name="add_todo",
            description="Create a new todo task with title and optional description",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description"
                    }
                },
                "required": ["title"]
            }
        )

    @staticmethod
    async def execute(user_id: str, title: str, description: Optional[str] = None):
        """Execute add todo operation."""
        try:
            # Create todo in database
            todo = Todo(
                title=title,
                description=description,
                user_id=user_id,
                completed=False
            )
            session.add(todo)
            session.commit()
            session.refresh(todo)

            return {
                "success": True,
                "todo": {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "created_at": todo.created_at.isoformat()
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create todo: {str(e)}"
            }

# Register tool
server.add_tool(AddTodoTool.get_tool_definition(), AddTodoTool.execute)
```

## MCP Protocol Features

- **Tool Registration:** Auto-discovery for AI agents
- **Input Validation:** JSON schema compliance
- **Error Responses:** MCP error format
- **Async Execution:** Non-blocking operations
- **Context Passing:** User session and permissions
- **Logging:** Structured logs for debugging

## Best Practices

- Clear, descriptive tool names
- Detailed parameter descriptions for AI understanding
- Graceful error handling
- User isolation (prevent cross-user access)
- Consistent response format
- Performance monitoring
- Input sanitization
