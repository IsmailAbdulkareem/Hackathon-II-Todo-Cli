# Server-Sent Events (SSE) Protocol for Todo Notifications

## Overview

The Todo application uses Server-Sent Events (SSE) to deliver real-time reminder notifications to authenticated users. This protocol enables push-based communication from the backend to frontend, providing immediate notification when reminders become due.

## Connection Establishment

### Endpoint
```
GET /api/notifications/stream
```

### Authentication
- Method: Bearer token authentication
- Format: Include token in Authorization header or as query parameter
- Header: `Authorization: Bearer <token>`
- Query Parameter: `?token=<token>`

### Request Headers
```
Accept: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

## Event Stream Format

The SSE stream returns content with MIME type `text/event-stream` and uses UTF-8 encoding. Each event follows the SSE specification format:

```
event: <event-type>
id: <event-id>
data: <json-data>
retry: <milliseconds>

event: <event-type>
id: <event-id>
data: <json-data>
```

## Event Types

### reminder Event
Sent when a reminder is due for a task.

**Format:**
```
event: reminder
id: <event-id>
data: {"task_id": "...", "title": "...", "due_date": "...", "priority": "...", "message": "...", "timestamp": "..."}
```

**Example:**
```
event: reminder
id: 1648729350000
data: {"task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef", "title": "Submit quarterly report", "due_date": "2026-02-06T18:00:00Z", "priority": "high", "message": "Reminder: Submit quarterly report is due in 1 hour", "timestamp": "2026-02-06T17:00:00Z"}
```

### heartbeat Event
Sent periodically to maintain connection alive.

**Format:**
```
event: heartbeat
id: <timestamp>
data: {"timestamp": "2026-02-06T17:00:00Z"}
```

**Example:**
```
event: heartbeat
id: 1648729350000
data: {"timestamp": "2026-02-06T17:00:00Z"}
```

### error Event
Sent when an error occurs.

**Format:**
```
event: error
id: <event-id>
data: {"error": "error-message", "timestamp": "..."}
```

**Example:**
```
event: error
id: 1648729350001
data: {"error": "Authentication expired", "timestamp": "2026-02-06T17:00:05Z"}
```

## Data Payload Schema

### Reminder Data
```json
{
  "task_id": "string (UUID)",
  "title": "string (task title)",
  "due_date": "string (ISO 8601 timestamp)",
  "priority": "string (low|medium|high)",
  "message": "string (reminder message)",
  "timestamp": "string (ISO 8601 timestamp of event)"
}
```

### Heartbeat Data
```json
{
  "timestamp": "string (ISO 8601 timestamp of heartbeat)"
}
```

### Error Data
```json
{
  "error": "string (error message)",
  "timestamp": "string (ISO 8601 timestamp of error)"
}
```

## Connection Management

### Heartbeat Interval
- Frequency: Every 30 seconds
- Purpose: Keep connection alive and detect disconnections
- Timeout: Connection closes after 90 seconds without heartbeat

### Event ID
- Format: Unix timestamp in milliseconds
- Purpose: Enable clients to resume from last received event
- Client Responsibility: Store last event ID for reconnection

### Reconnection Strategy
- On disconnect: Client should attempt to reconnect
- Backoff: Use exponential backoff starting at 1 second
- Resume: Include Last-Event-ID header to resume from last received event
- Max Attempts: Try up to 5 times before giving up

## Client Implementation Guidelines

### JavaScript Example
```javascript
const eventSource = new EventSource('/api/notifications/stream', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});

eventSource.addEventListener('reminder', function(event) {
  const reminder = JSON.parse(event.data);
  console.log(`Reminder: ${reminder.message}`);
  // Show notification to user
});

eventSource.addEventListener('heartbeat', function(event) {
  // Connection is alive, no action needed
});

eventSource.addEventListener('error', function(event) {
  const error = JSON.parse(event.data);
  console.error(`SSE Error: ${error.error}`);
});
```

### Error Handling
- Invalid authentication: Close connection immediately
- Server errors: Send error event, then close connection
- Client disconnection: Server should clean up resources

## Security Considerations

### User Isolation
- Each SSE connection delivers notifications only for the authenticated user
- Task data in events contains only information accessible to the user
- No cross-user notification leakage

### Rate Limiting
- Limit events per minute per user to prevent abuse
- Implement throttling for clients receiving too many events
- Monitor for unusual activity patterns

### Token Validation
- Validate authentication token on initial connection
- Re-validate periodically during the connection (every 10 minutes)
- Close connection immediately if token expires

## Performance Guidelines

### Memory Management
- Maintain only one SSE connection per authenticated user
- Clean up connection resources immediately on disconnect
- Limit in-memory queues for pending events

### Event Prioritization
- High priority reminders take precedence over low priority
- Batch multiple events if they occur in rapid succession
- Discard stale events if delivery is delayed beyond relevance

## Server Implementation

### Concurrent Connections
- Support up to 1000 concurrent SSE connections per server instance
- Scale horizontally if more connections needed
- Track active connections for load balancing

### Event Queuing
- Maintain per-user event queues in memory
- Deliver events as they arrive (no batching)
- Clear queues when connection is closed

### Cleanup Procedures
- Remove disconnected users from active connections
- Cancel subscriptions when user session expires
- Log connection events for monitoring