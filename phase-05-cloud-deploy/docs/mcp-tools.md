# TaskAI MCP Tools Guide

## Overview

TaskAI integrates with the Model Context Protocol (MCP) to provide AI-powered task management capabilities. This guide covers the available MCP tools, their usage, and integration patterns.

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol for AI assistants to interact with external tools and services. TaskAI exposes several MCP tools that enable AI assistants like Claude to:

- Create and manage tasks using natural language
- Search and filter tasks intelligently
- Set reminders and due dates
- Organize tasks with tags
- Analyze task patterns and provide insights

## Available MCP Tools

### 1. Create Task

**Tool Name**: `taskai_create_task`

**Description**: Create a new task from natural language input

**Parameters**:
```json
{
  "user_id": "string (required)",
  "prompt": "string (required)",
  "context": "object (optional)"
}
```

**Example**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "prompt": "Remind me to call the dentist tomorrow at 2pm",
  "context": {
    "timezone": "America/New_York"
  }
}
```

**Response**:
```json
{
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Call the dentist",
    "due_date": "2026-02-15T14:00:00Z",
    "priority": "medium",
    "tags": ["personal", "health"]
  },
  "interpretation": {
    "action": "create_task",
    "extracted_date": "tomorrow at 2pm",
    "extracted_priority": "medium",
    "suggested_tags": ["personal", "health"]
  }
}
```

**AI Processing**:
- Extracts task title from natural language
- Parses relative dates ("tomorrow", "next week", "in 3 days")
- Infers priority from context ("urgent", "important", "ASAP")
- Suggests relevant tags based on content
- Sets appropriate due dates and reminders

### 2. Search Tasks

**Tool Name**: `taskai_search_tasks`

**Description**: Search tasks using natural language queries

**Parameters**:
```json
{
  "user_id": "string (required)",
  "query": "string (required)",
  "filters": "object (optional)"
}
```

**Example**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "query": "high priority work tasks due this week",
  "filters": {
    "include_completed": false
  }
}
```

**Response**:
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete project documentation",
      "priority": "high",
      "due_date": "2026-02-20T17:00:00Z",
      "tags": ["work", "documentation"],
      "relevance_score": 0.95
    }
  ],
  "total": 1,
  "query_interpretation": {
    "filters_applied": ["priority:high", "tags:work", "due:this_week"],
    "search_terms": ["project", "documentation"]
  }
}
```

**AI Processing**:
- Understands natural language queries
- Extracts filters from context ("high priority", "this week")
- Ranks results by relevance
- Handles fuzzy matching and synonyms

### 3. Update Task

**Tool Name**: `taskai_update_task`

**Description**: Update task properties using natural language

**Parameters**:
```json
{
  "user_id": "string (required)",
  "task_id": "string (required)",
  "instruction": "string (required)"
}
```

**Example**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "instruction": "Move this to next Monday and mark as high priority"
}
```

**Response**:
```json
{
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project documentation",
    "due_date": "2026-02-17T09:00:00Z",
    "priority": "high",
    "updated_at": "2026-02-14T10:00:00Z"
  },
  "changes": {
    "due_date": {
      "old": "2026-02-20T17:00:00Z",
      "new": "2026-02-17T09:00:00Z"
    },
    "priority": {
      "old": "medium",
      "new": "high"
    }
  }
}
```

**AI Processing**:
- Parses update instructions
- Handles multiple changes in one instruction
- Validates changes before applying
- Provides clear change summary

### 4. Analyze Tasks

**Tool Name**: `taskai_analyze_tasks`

**Description**: Analyze task patterns and provide insights

**Parameters**:
```json
{
  "user_id": "string (required)",
  "analysis_type": "string (required)",
  "time_range": "string (optional)"
}
```

**Analysis Types**:
- `productivity`: Task completion patterns
- `workload`: Current and upcoming workload
- `priorities`: Priority distribution and recommendations
- `tags`: Tag usage and organization
- `overdue`: Overdue tasks and patterns

**Example**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "analysis_type": "productivity",
  "time_range": "last_30_days"
}
```

**Response**:
```json
{
  "analysis": {
    "type": "productivity",
    "period": "2026-01-15 to 2026-02-14",
    "metrics": {
      "total_tasks": 45,
      "completed_tasks": 38,
      "completion_rate": 0.84,
      "average_completion_time": "2.3 days",
      "on_time_completion_rate": 0.76
    },
    "insights": [
      "Your completion rate is 84%, which is above average",
      "You tend to complete tasks faster on Mondays and Tuesdays",
      "High priority tasks have a 92% completion rate",
      "Consider breaking down tasks that take more than 5 days"
    ],
    "recommendations": [
      "Schedule complex tasks early in the week",
      "Set more realistic due dates for large tasks",
      "Use tags more consistently for better organization"
    ]
  }
}
```

**AI Processing**:
- Analyzes historical task data
- Identifies patterns and trends
- Provides actionable insights
- Suggests improvements

### 5. Smart Scheduling

**Tool Name**: `taskai_smart_schedule`

**Description**: Intelligently schedule tasks based on workload and priorities

**Parameters**:
```json
{
  "user_id": "string (required)",
  "task_ids": "array (optional)",
  "constraints": "object (optional)"
}
```

**Example**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "task_ids": ["task-1", "task-2", "task-3"],
  "constraints": {
    "working_hours": "9am-5pm",
    "max_tasks_per_day": 5,
    "buffer_time": "30min"
  }
}
```

**Response**:
```json
{
  "schedule": [
    {
      "date": "2026-02-15",
      "tasks": [
        {
          "task_id": "task-1",
          "title": "Complete project documentation",
          "suggested_time": "09:00-11:00",
          "priority": "high",
          "estimated_duration": "2 hours"
        },
        {
          "task_id": "task-2",
          "title": "Review pull requests",
          "suggested_time": "14:00-15:30",
          "priority": "medium",
          "estimated_duration": "1.5 hours"
        }
      ],
      "workload": "moderate"
    }
  ],
  "recommendations": [
    "Start with high priority tasks in the morning",
    "Leave buffer time between tasks for breaks",
    "Consider delegating task-3 if possible"
  ]
}
```

**AI Processing**:
- Considers task priorities and dependencies
- Respects working hours and constraints
- Balances workload across days
- Provides scheduling recommendations

## Integration Patterns

### Claude Desktop Integration

TaskAI can be integrated with Claude Desktop as an MCP server:

**Configuration** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "taskai": {
      "command": "node",
      "args": ["/path/to/taskai-mcp-server/index.js"],
      "env": {
        "TASKAI_API_URL": "http://localhost:8000",
        "TASKAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Usage in Claude**:
```
User: Create a task to review the quarterly report by Friday

Claude: I'll create that task for you using TaskAI.
[Uses taskai_create_task tool]

Task created successfully:
- Title: Review quarterly report
- Due: Friday, February 21, 2026 at 5:00 PM
- Priority: Medium
- Tags: work, reports

Would you like me to set a reminder for this task?
```

### API Integration

For custom integrations, use the TaskAI API with AI-powered endpoints:

```python
import requests

API_URL = "http://localhost:8000/api"
USER_ID = "your-user-id"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create task with AI
response = requests.post(
    f"{API_URL}/{USER_ID}/tasks/ai",
    headers=headers,
    json={
        "prompt": "Schedule a meeting with the team next Tuesday at 10am"
    }
)

task = response.json()
print(f"Created task: {task['title']}")
```

### Webhook Integration

TaskAI can send webhooks for task events:

**Configuration**:
```json
{
  "webhook_url": "https://your-app.com/webhooks/taskai",
  "events": ["task.created", "task.updated", "task.completed"],
  "secret": "your-webhook-secret"
}
```

**Webhook Payload**:
```json
{
  "event": "task.created",
  "timestamp": "2026-02-14T10:00:00Z",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Complete project documentation",
    "priority": "high"
  },
  "signature": "sha256=..."
}
```

## Natural Language Processing

### Supported Date Formats

TaskAI understands various date formats:

- **Relative**: "tomorrow", "next week", "in 3 days", "next Monday"
- **Absolute**: "February 20", "2026-02-20", "Feb 20, 2026"
- **Time**: "at 2pm", "at 14:00", "in the morning", "tonight"
- **Recurring**: "every Monday", "daily", "weekly", "monthly"

### Priority Detection

AI infers priority from context:

- **High**: "urgent", "ASAP", "critical", "important", "high priority"
- **Medium**: "soon", "when you can", "moderate"
- **Low**: "eventually", "low priority", "nice to have"

### Tag Suggestions

AI suggests tags based on:

- Task content and keywords
- Historical tag usage
- Common task categories
- User preferences

## Best Practices

### 1. Provide Context

Include relevant context for better AI understanding:

```json
{
  "prompt": "Schedule dentist appointment",
  "context": {
    "timezone": "America/New_York",
    "preferred_time": "afternoon",
    "recurring": false
  }
}
```

### 2. Use Natural Language

Write prompts as you would speak:

✅ Good: "Remind me to call John tomorrow at 2pm"
❌ Bad: "task: call, date: tomorrow, time: 14:00"

### 3. Be Specific

Provide enough detail for accurate interpretation:

✅ Good: "High priority: Review pull request #123 by end of day"
❌ Bad: "Review PR"

### 4. Leverage AI Analysis

Use analysis tools to gain insights:

```python
# Get productivity insights
analysis = taskai.analyze_tasks(
    user_id=user_id,
    analysis_type="productivity",
    time_range="last_30_days"
)

# Act on recommendations
for recommendation in analysis['recommendations']:
    print(f"💡 {recommendation}")
```

### 5. Handle Errors Gracefully

AI interpretation may not always be perfect:

```python
try:
    task = taskai.create_task(user_id, prompt)
except InterpretationError as e:
    # Ask for clarification
    print(f"Could you clarify: {e.message}")
    # Provide suggestions
    print(f"Did you mean: {e.suggestions}")
```

## Advanced Features

### Multi-Task Operations

Create multiple tasks from a single prompt:

```json
{
  "prompt": "This week I need to: review code, update docs, and fix bugs"
}
```

Response creates 3 separate tasks with appropriate due dates.

### Task Dependencies

AI can understand task relationships:

```json
{
  "prompt": "After finishing the design, implement the feature and then write tests"
}
```

Creates 3 tasks with dependencies: Design → Implementation → Tests

### Smart Reminders

AI sets intelligent reminders based on task importance:

- High priority: Multiple reminders (1 week, 1 day, 1 hour before)
- Medium priority: Standard reminders (1 day, 1 hour before)
- Low priority: Single reminder (1 day before)

## Troubleshooting

### AI Misinterpretation

If AI misinterprets your prompt:

1. **Be more specific**: Add more context and details
2. **Use explicit dates**: "February 20" instead of "next week"
3. **Specify priority**: "high priority" or "low priority"
4. **Review and edit**: Check the created task and update if needed

### Performance Issues

For slow AI responses:

1. **Simplify prompts**: Break complex requests into smaller ones
2. **Use batch operations**: Create multiple tasks in one request
3. **Cache results**: Store frequently used interpretations
4. **Optimize context**: Reduce unnecessary context data

### Integration Errors

Common integration issues:

1. **Authentication**: Ensure valid JWT token
2. **API URL**: Verify correct API endpoint
3. **Rate limits**: Respect API rate limits (100 req/min)
4. **Timeouts**: Increase timeout for AI operations (30s recommended)

## API Reference

For detailed API documentation, see:
- [API Reference](api-reference.md)
- [Architecture Documentation](architecture.md)

## Examples

### Example 1: Daily Planning

```python
# Get today's tasks
tasks = taskai.search_tasks(
    user_id=user_id,
    query="due today"
)

# Analyze workload
analysis = taskai.analyze_tasks(
    user_id=user_id,
    analysis_type="workload",
    time_range="today"
)

# Smart schedule
schedule = taskai.smart_schedule(
    user_id=user_id,
    task_ids=[t['id'] for t in tasks],
    constraints={
        "working_hours": "9am-5pm",
        "max_tasks_per_day": 5
    }
)

print(f"Today's schedule: {schedule}")
```

### Example 2: Weekly Review

```python
# Get completed tasks
completed = taskai.search_tasks(
    user_id=user_id,
    query="completed this week"
)

# Analyze productivity
analysis = taskai.analyze_tasks(
    user_id=user_id,
    analysis_type="productivity",
    time_range="this_week"
)

print(f"Completed {len(completed)} tasks this week")
print(f"Insights: {analysis['insights']}")
```

### Example 3: Bulk Task Creation

```python
# Create multiple tasks from meeting notes
notes = """
Action items from today's meeting:
- John will update the documentation by Friday
- Sarah needs to review the design by tomorrow
- Team should test the new feature next week
"""

tasks = taskai.create_task(
    user_id=user_id,
    prompt=notes
)

print(f"Created {len(tasks)} tasks from meeting notes")
```

## Future Enhancements

Planned MCP tool improvements:

- **Voice input**: Create tasks via voice commands
- **Email integration**: Create tasks from emails
- **Calendar sync**: Sync tasks with Google Calendar/Outlook
- **Collaboration**: Share tasks and assign to team members
- **Templates**: Create tasks from predefined templates
- **Automation**: Trigger actions based on task events

## Support

For MCP integration support:
- Documentation: https://docs.taskai.local/mcp
- GitHub Issues: https://github.com/your-org/taskai/issues
- Discord: https://discord.gg/taskai
- Email: mcp-support@taskai.local

---

**Last Updated**: 2026-02-14
**Version**: 1.0.0
