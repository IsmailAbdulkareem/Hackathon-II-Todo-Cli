-- Migration: Add priority field to tasks table
-- Date: 2026-01-16
-- Description: Add priority column (1-5 scale) to tasks table for task prioritization

-- Add priority column with default value 1
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS priority INTEGER NOT NULL DEFAULT 1;

-- Add check constraint to ensure priority is between 1 and 5
ALTER TABLE tasks
ADD CONSTRAINT IF NOT EXISTS tasks_priority_check CHECK (priority >= 1 AND priority <= 5);

-- Create index on priority for faster filtering/sorting
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);

-- Update existing tasks to have default priority 1 (if any exist without it)
UPDATE tasks SET priority = 1 WHERE priority IS NULL;

-- Verify the migration
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'tasks'
        AND column_name = 'priority'
    ) THEN
        RAISE NOTICE 'SUCCESS: priority column added to tasks table';
    ELSE
        RAISE EXCEPTION 'FAILED: priority column not found in tasks table';
    END IF;
END $$;
