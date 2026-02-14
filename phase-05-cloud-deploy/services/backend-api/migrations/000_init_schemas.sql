-- Phase 5 Part A: Database Schema Initialization
-- Creates service-specific schemas for microservices architecture

-- Create schemas
CREATE SCHEMA IF NOT EXISTS tasks;
CREATE SCHEMA IF NOT EXISTS notifications;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant permissions (adjust user as needed)
GRANT ALL PRIVILEGES ON SCHEMA tasks TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA notifications TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA audit TO postgres;

-- Create Dapr state store table in public schema
CREATE TABLE IF NOT EXISTS public.dapr_state (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    etag TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Dapr metadata table
CREATE TABLE IF NOT EXISTS public.dapr_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Create Dapr jobs table
CREATE TABLE IF NOT EXISTS public.dapr_jobs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    schedule TEXT,
    data JSONB,
    metadata JSONB,
    status TEXT DEFAULT 'pending',
    next_run_time TIMESTAMP WITH TIME ZONE,
    last_run_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for Dapr tables
CREATE INDEX IF NOT EXISTS idx_dapr_jobs_status ON public.dapr_jobs(status);
CREATE INDEX IF NOT EXISTS idx_dapr_jobs_next_run ON public.dapr_jobs(next_run_time);

COMMENT ON SCHEMA tasks IS 'Backend API service - task management, tags, reminders, recurrence rules';
COMMENT ON SCHEMA notifications IS 'Notification Service - notification delivery tracking and retry logic';
COMMENT ON SCHEMA audit IS 'Recurring Service - recurring task audit trail and history';
