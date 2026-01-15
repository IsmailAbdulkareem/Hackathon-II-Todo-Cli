-- Migration: Add messages table for AI chatbot feature
-- Date: 2026-01-15
-- Purpose: Store individual messages in chat conversations

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (LENGTH(content) <= 5000 AND LENGTH(TRIM(content)) > 0),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);

-- Add comments for documentation
COMMENT ON TABLE messages IS 'Individual messages in chat conversations';
COMMENT ON COLUMN messages.id IS 'Unique message identifier';
COMMENT ON COLUMN messages.conversation_id IS 'Parent conversation';
COMMENT ON COLUMN messages.user_id IS 'Message owner (for authorization)';
COMMENT ON COLUMN messages.role IS 'Who sent the message: user or assistant';
COMMENT ON COLUMN messages.content IS 'Message text content (max 5000 characters)';
COMMENT ON COLUMN messages.created_at IS 'When message was sent';
