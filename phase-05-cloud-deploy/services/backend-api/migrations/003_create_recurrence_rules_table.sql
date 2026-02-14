-- Migration: Create recurrence_rules table
-- Description: Creates the recurrence_rules table for defining recurring task patterns
-- Service: backend-api (schema owner)
-- Created: 2024-02-14

-- Create recurrence_rules table in tasks schema
CREATE TABLE IF NOT EXISTS tasks.recurrence_rules (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'yearly')),
    interval INTEGER NOT NULL CHECK (interval >= 1 AND interval <= 365),
    end_date TIMESTAMP WITH TIME ZONE,
    occurrence_count INTEGER CHECK (occurrence_count >= 1 AND occurrence_count <= 1000),
    current_count INTEGER NOT NULL DEFAULT 0 CHECK (current_count >= 0),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient querying
CREATE INDEX idx_recurrence_rules_user_id ON tasks.recurrence_rules(user_id);
CREATE INDEX idx_recurrence_rules_frequency ON tasks.recurrence_rules(frequency);
CREATE INDEX idx_recurrence_rules_created_at ON tasks.recurrence_rules(created_at DESC);

-- Add comments for documentation
COMMENT ON TABLE tasks.recurrence_rules IS 'Recurrence rules for defining recurring task patterns';
COMMENT ON COLUMN tasks.recurrence_rules.id IS 'Unique recurrence rule identifier (UUID)';
COMMENT ON COLUMN tasks.recurrence_rules.user_id IS 'User who owns this recurrence rule';
COMMENT ON COLUMN tasks.recurrence_rules.frequency IS 'Recurrence frequency: daily, weekly, monthly, yearly';
COMMENT ON COLUMN tasks.recurrence_rules.interval IS 'Interval between occurrences (e.g., every 2 weeks)';
COMMENT ON COLUMN tasks.recurrence_rules.end_date IS 'Optional end date for recurrence series';
COMMENT ON COLUMN tasks.recurrence_rules.occurrence_count IS 'Optional maximum number of occurrences';
COMMENT ON COLUMN tasks.recurrence_rules.current_count IS 'Current number of occurrences created';
COMMENT ON COLUMN tasks.recurrence_rules.created_at IS 'Rule creation timestamp';
COMMENT ON COLUMN tasks.recurrence_rules.updated_at IS 'Rule last update timestamp';
