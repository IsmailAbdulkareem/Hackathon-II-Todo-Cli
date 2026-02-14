-- Migration: Create notifications schema
-- Description: Creates the notifications schema and notification_log table
--              for tracking email notification delivery history
-- Service: notification-service (schema owner)
-- Created: 2024-02-14

-- Create notifications schema
CREATE SCHEMA IF NOT EXISTS notifications;

-- Grant permissions
GRANT USAGE ON SCHEMA notifications TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA notifications TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA notifications TO postgres;

-- Create notification_log table
CREATE TABLE IF NOT EXISTS notifications.notification_log (
    id VARCHAR(36) PRIMARY KEY,
    reminder_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    task_id VARCHAR(36) NOT NULL,
    recipient_email VARCHAR(255) NOT NULL,
    delivery_status VARCHAR(20) NOT NULL CHECK (delivery_status IN ('sent', 'failed')),
    attempt_number INTEGER NOT NULL CHECK (attempt_number >= 1 AND attempt_number <= 3),
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient querying
CREATE INDEX idx_notification_log_reminder_id ON notifications.notification_log(reminder_id);
CREATE INDEX idx_notification_log_user_id ON notifications.notification_log(user_id);
CREATE INDEX idx_notification_log_task_id ON notifications.notification_log(task_id);
CREATE INDEX idx_notification_log_delivery_status ON notifications.notification_log(delivery_status);
CREATE INDEX idx_notification_log_sent_at ON notifications.notification_log(sent_at DESC);

-- Create composite index for common queries
CREATE INDEX idx_notification_log_user_status ON notifications.notification_log(user_id, delivery_status);

-- Add comments for documentation
COMMENT ON SCHEMA notifications IS 'Schema for notification service - tracks email delivery history';
COMMENT ON TABLE notifications.notification_log IS 'Log of all notification delivery attempts with status and error tracking';
COMMENT ON COLUMN notifications.notification_log.id IS 'Unique notification log entry identifier (UUID)';
COMMENT ON COLUMN notifications.notification_log.reminder_id IS 'Reference to the reminder that triggered this notification';
COMMENT ON COLUMN notifications.notification_log.user_id IS 'User who owns the task';
COMMENT ON COLUMN notifications.notification_log.task_id IS 'Task associated with the reminder';
COMMENT ON COLUMN notifications.notification_log.recipient_email IS 'Email address where notification was sent';
COMMENT ON COLUMN notifications.notification_log.delivery_status IS 'Delivery status: sent or failed';
COMMENT ON COLUMN notifications.notification_log.attempt_number IS 'Retry attempt number (1-3)';
COMMENT ON COLUMN notifications.notification_log.error_message IS 'Error message if delivery failed';
COMMENT ON COLUMN notifications.notification_log.sent_at IS 'Timestamp when notification was sent/attempted';
COMMENT ON COLUMN notifications.notification_log.created_at IS 'Record creation timestamp';
