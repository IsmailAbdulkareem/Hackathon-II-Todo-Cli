-- Migration: Add conversations table for AI chatbot feature
-- Date: 2026-01-15
-- Purpose: Store chat sessions between users and AI assistant

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);

-- Add comment for documentation
COMMENT ON TABLE conversations IS 'Chat sessions between users and AI assistant';
COMMENT ON COLUMN conversations.id IS 'Unique conversation identifier';
COMMENT ON COLUMN conversations.user_id IS 'Owner of the conversation';
COMMENT ON COLUMN conversations.created_at IS 'When conversation was created';
COMMENT ON COLUMN conversations.updated_at IS 'Last message timestamp';
