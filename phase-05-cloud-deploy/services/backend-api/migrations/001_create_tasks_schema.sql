-- Phase 5 Part A: Tasks Schema Migration
-- Creates tables for task management with advanced features

-- Create tasks schema tables
CREATE TABLE IF NOT EXISTS tasks.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(10) NOT NULL DEFAULT 'Low' CHECK (priority IN ('Low', 'Medium', 'High')),
    due_date TIMESTAMP WITH TIME ZONE,
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    parent_task_id UUID REFERENCES tasks.tasks(id) ON DELETE SET NULL,
    recurrence_rule_id UUID REFERENCES tasks.recurrence_rules(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create tags table
CREATE TABLE IF NOT EXISTS tasks.tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) NOT NULL,
    usage_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_user_tag UNIQUE (user_id, LOWER(name))
);

-- Create task_tags join table
CREATE TABLE IF NOT EXISTS tasks.task_tags (
    task_id UUID NOT NULL REFERENCES tasks.tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tasks.tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (task_id, tag_id)
);

-- Create reminders table
CREATE TABLE IF NOT EXISTS tasks.reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks.tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    reminder_type VARCHAR(20) NOT NULL CHECK (reminder_type IN ('15min', '1hr', '1day', '1week', 'custom')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    dapr_job_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create recurrence_rules table
CREATE TABLE IF NOT EXISTS tasks.recurrence_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    recurrence_type VARCHAR(20) NOT NULL CHECK (recurrence_type IN ('daily', 'weekly', 'monthly', 'yearly', 'custom')),
    interval INTEGER NOT NULL DEFAULT 1 CHECK (interval >= 1),
    days_of_week INTEGER[],
    day_of_month INTEGER CHECK (day_of_month BETWEEN 1 AND 31),
    month_of_year INTEGER CHECK (month_of_year BETWEEN 1 AND 12),
    custom_pattern TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for tasks table
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks.tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON tasks.tasks(user_id, completed);
CREATE INDEX IF NOT EXISTS idx_tasks_user_priority ON tasks.tasks(user_id, priority);
CREATE INDEX IF NOT EXISTS idx_tasks_user_due_date ON tasks.tasks(user_id, due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_user_recurring ON tasks.tasks(user_id, is_recurring);
CREATE INDEX IF NOT EXISTS idx_tasks_parent_task ON tasks.tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_search ON tasks.tasks USING GIN (to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Create indexes for tags table
CREATE INDEX IF NOT EXISTS idx_tags_user_id ON tasks.tags(user_id);

-- Create indexes for task_tags table
CREATE INDEX IF NOT EXISTS idx_task_tags_tag_id ON tasks.task_tags(tag_id);

-- Create indexes for reminders table
CREATE INDEX IF NOT EXISTS idx_reminders_task_id ON tasks.reminders(task_id);
CREATE INDEX IF NOT EXISTS idx_reminders_user_scheduled ON tasks.reminders(user_id, scheduled_time);
CREATE INDEX IF NOT EXISTS idx_reminders_status_scheduled ON tasks.reminders(status, scheduled_time);
CREATE INDEX IF NOT EXISTS idx_reminders_dapr_job ON tasks.reminders(dapr_job_id);

-- Create indexes for recurrence_rules table
CREATE INDEX IF NOT EXISTS idx_recurrence_rules_user_id ON tasks.recurrence_rules(user_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks.tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tags_updated_at BEFORE UPDATE ON tasks.tags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reminders_updated_at BEFORE UPDATE ON tasks.reminders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recurrence_rules_updated_at BEFORE UPDATE ON tasks.recurrence_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
