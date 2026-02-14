-- Migration: Create audit schema for recurring-service
-- Purpose: Track task recurrence events and audit trail
-- Service: recurring-service
-- Created: 2026-02-14

-- Create audit schema
CREATE SCHEMA IF NOT EXISTS audit;

-- Task audit log table
-- Tracks all recurring task events (creation, completion, next instance generation)
CREATE TABLE IF NOT EXISTS audit.task_audit (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    task_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'recurring_instance_created',
        'recurring_task_completed',
        'recurrence_ended',
        'recurrence_error'
    )),
    event_data JSONB NOT NULL,
    parent_task_id VARCHAR(36),
    recurrence_rule_id VARCHAR(36),
    occurrence_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Indexes for common queries
    CONSTRAINT fk_task_audit_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_task_audit_user_id ON audit.task_audit(user_id);
CREATE INDEX IF NOT EXISTS idx_task_audit_task_id ON audit.task_audit(task_id);
CREATE INDEX IF NOT EXISTS idx_task_audit_parent_task_id ON audit.task_audit(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_task_audit_recurrence_rule_id ON audit.task_audit(recurrence_rule_id);
CREATE INDEX IF NOT EXISTS idx_task_audit_event_type ON audit.task_audit(event_type);
CREATE INDEX IF NOT EXISTS idx_task_audit_created_at ON audit.task_audit(created_at DESC);

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_task_audit_user_task ON audit.task_audit(user_id, task_id);
CREATE INDEX IF NOT EXISTS idx_task_audit_user_parent ON audit.task_audit(user_id, parent_task_id);

-- Comments for documentation
COMMENT ON SCHEMA audit IS 'Audit schema for recurring-service task event tracking';
COMMENT ON TABLE audit.task_audit IS 'Audit log for all recurring task events and lifecycle tracking';
COMMENT ON COLUMN audit.task_audit.event_type IS 'Type of recurring task event: recurring_instance_created, recurring_task_completed, recurrence_ended, recurrence_error';
COMMENT ON COLUMN audit.task_audit.event_data IS 'JSON data containing event details, task snapshot, and recurrence rule information';
COMMENT ON COLUMN audit.task_audit.occurrence_number IS 'Sequential number of this occurrence in the recurring series (1, 2, 3, ...)';
