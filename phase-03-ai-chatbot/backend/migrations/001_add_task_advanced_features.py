"""
Migration: Add advanced features to Task model

This migration adds the following fields to the tasks table:
- due_date: DateTime field for task due dates
- priority: String field for task priority (low, medium, high)
- tags: JSON field for storing task tags as an array
- recurrence: String field for recurrence pattern (none, daily, weekly, monthly)
- reminder_offset_minutes: Integer field for reminder timing
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '001_add_task_advanced_features'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to the tasks table
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('priority', sa.String(20), nullable=True, default='medium'))
    op.add_column('tasks', sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default=list))
    op.add_column('tasks', sa.Column('recurrence', sa.String(20), nullable=True, default='none'))
    op.add_column('tasks', sa.Column('reminder_offset_minutes', sa.Integer(), nullable=True, default=0))

    # Create indices for better query performance
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_recurrence', 'tasks', ['recurrence'])

    # Update existing records with default values
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE tasks
        SET priority = 'medium',
            recurrence = 'none',
            reminder_offset_minutes = 0,
            tags = '[]'
        WHERE priority IS NULL
    """))


def downgrade():
    # Remove the columns added in upgrade
    op.drop_column('tasks', 'reminder_offset_minutes')
    op.drop_column('tasks', 'recurrence')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
    op.drop_column('tasks', 'due_date')

    # Drop indices
    op.drop_index('ix_tasks_due_date')
    op.drop_index('ix_tasks_priority')
    op.drop_index('ix_tasks_recurrence')