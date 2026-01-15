# Data Model - AI-Powered Todo Chatbot

**Date**: 2026-01-15
**Feature**: 001-ai-chatbot
**Purpose**: Define database entities and relationships

## Entity Definitions

### Conversation

Represents a chat session between user and assistant.

**Fields**:
- `id` (UUID, primary key): Unique conversation identifier
- `user_id` (UUID, foreign key → users.id, indexed): Owner of the conversation
- `created_at` (timestamp with timezone): When conversation was created
- `updated_at` (timestamp with timezone): Last message timestamp

**Relationships**:
- One-to-many with Message (one conversation has many messages)
- Many-to-one with User (many conversations belong to one user)

**Validation Rules**:
- user_id must reference existing user
- created_at defaults to current UTC timestamp
- updated_at defaults to current UTC timestamp, updated on new messages

**State Transitions**:
- Created: When user sends first message without conversation_id
- Updated: When new message is added to conversation
- No explicit "closed" state - conversations remain open indefinitely

**Indexes**:
- Primary key on id
- Index on user_id for efficient user conversation lookup
- Index on updated_at for sorting by recent activity

---

### Message

Represents a single message in a conversation.

**Fields**:
- `id` (UUID, primary key): Unique message identifier
- `conversation_id` (UUID, foreign key → conversations.id, indexed): Parent conversation
- `user_id` (UUID, foreign key → users.id, indexed): Message owner (for authorization)
- `role` (enum: "user" | "assistant"): Who sent the message
- `content` (text, max 5000 characters): Message text content
- `created_at` (timestamp with timezone): When message was sent

**Relationships**:
- Many-to-one with Conversation (many messages belong to one conversation)
- Many-to-one with User (many messages belong to one user)

**Validation Rules**:
- conversation_id must reference existing conversation
- user_id must reference existing user
- user_id must match conversation.user_id (authorization check)
- role must be either "user" or "assistant"
- content must not exceed 5000 characters
- content must not be empty or whitespace-only
- created_at defaults to current UTC timestamp

**State Transitions**:
- Created: When message is persisted to database
- Immutable: Messages cannot be edited or deleted (audit trail)

**Indexes**:
- Primary key on id
- Index on conversation_id for efficient message retrieval
- Composite index on (conversation_id, created_at) for pagination queries
- Index on user_id for authorization checks

---

### Task (Existing from Phase 2)

Represents a todo task. **No schema changes required** - existing entity is reused.

**Fields** (for reference):
- `id` (UUID, primary key): Unique task identifier
- `user_id` (string, max 255 characters, indexed): Task owner
- `title` (string, max 200 characters): Task title
- `description` (string, max 2000 characters, nullable): Task description
- `completed` (boolean, default false): Completion status
- `created_at` (timestamp with timezone): When task was created
- `updated_at` (timestamp with timezone): Last modification timestamp

**Note**: Character limits updated from Phase 2 (title: 500→200, description: 2000→2000)

**Relationships**:
- Many-to-one with User (many tasks belong to one user)
- No direct relationship with Conversation or Message (tasks are managed through MCP tools)

---

## Database Schema (PostgreSQL)

```sql
-- Conversations table (new)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- Messages table (new)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (LENGTH(content) <= 5000 AND LENGTH(TRIM(content)) > 0),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_user_id ON messages(user_id);

-- Tasks table (existing from Phase 2, no changes)
-- Reference only - already exists in database
```

## SQLModel Definitions (Python)

```python
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship

class Conversation(SQLModel, table=True):
    """Conversation entity for chat sessions."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Message entity for chat messages."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(max_length=5000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("user", "assistant"):
            raise ValueError("Role must be 'user' or 'assistant'")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        if len(v) > 5000:
            raise ValueError("Content exceeds 5000 character limit")
        return v.strip()
```

## Data Volume Estimates

Based on spec assumptions:
- **Users**: Existing Phase 2 users
- **Conversations per user**: 1-5 active (typical)
- **Messages per conversation**: 10-20 (average), up to 50 loaded at once
- **Tasks per user**: Existing Phase 2 data

**Storage estimates** (per user):
- Conversations: 5 × ~100 bytes = 500 bytes
- Messages: 100 × ~1KB (avg) = 100KB
- Total new storage: ~100KB per active user

**Query patterns**:
- Most frequent: Load last 50 messages for conversation (indexed query)
- Second most: List user conversations ordered by updated_at (indexed query)
- Infrequent: Create new conversation, create new message

## Migration Strategy

1. **Create new tables** (conversations, messages)
2. **No data migration needed** - fresh start for chat feature
3. **Existing tasks table unchanged** - no migration required
4. **Rollback plan**: Drop conversations and messages tables if needed

## Data Retention Policy

Per spec assumptions:
- Conversations retained indefinitely (no automatic deletion)
- Messages retained indefinitely (audit trail)
- Future consideration: Add archival policy for old conversations
