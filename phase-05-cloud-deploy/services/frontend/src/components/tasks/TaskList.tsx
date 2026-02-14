/**
 * TaskList component for displaying and managing tasks.
 *
 * Features:
 * - Priority indicators with color coding
 * - Tag display with TagPill component
 * - Filter and sort controls
 * - Task completion toggle
 * - Task editing and deletion
 * - Empty states
 * - Responsive design
 */

import React, { useState } from 'react';
import { TagList, Tag } from './TagPill';

export interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'Low' | 'Medium' | 'High';
  completed: boolean;
  due_date?: string;
  due_date_status?: 'overdue' | 'due_today' | 'due_soon' | 'upcoming';
  is_recurring: boolean;
  parent_task_id?: string;
  recurrence_rule_id?: string;
  tags?: Tag[];
  created_at: string;
  updated_at: string;
}

interface TaskListProps {
  tasks: Task[];
  onTaskComplete: (taskId: string) => void;
  onTaskEdit: (taskId: string) => void;
  onTaskDelete: (taskId: string) => void;
  onTagClick?: (tagId: string) => void;
  loading?: boolean;
  emptyMessage?: string;
  className?: string;
}

export const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onTaskComplete,
  onTaskEdit,
  onTaskDelete,
  onTagClick,
  loading = false,
  emptyMessage = 'No tasks found',
  className = ''
}) => {
  const [expandedTaskId, setExpandedTaskId] = useState<string | null>(null);

  const toggleExpand = (taskId: string) => {
    setExpandedTaskId(expandedTaskId === taskId ? null : taskId);
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'High':
        return '#ef4444';
      case 'Medium':
        return '#f59e0b';
      case 'Low':
        return '#10b981';
      default:
        return '#6b7280';
    }
  };

  const getPriorityIcon = (priority: string): string => {
    switch (priority) {
      case 'High':
        return '🔴';
      case 'Medium':
        return '🟡';
      case 'Low':
        return '🟢';
      default:
        return '⚪';
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) !== 1 ? 's' : ''}`;
    } else if (diffDays === 0) {
      return 'Due today';
    } else if (diffDays === 1) {
      return 'Due tomorrow';
    } else if (diffDays <= 7) {
      return `Due in ${diffDays} days`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getDueDateClass = (task: Task): string => {
    // Use backend-provided status if available
    if (task.due_date_status) {
      return task.due_date_status.replace('_', '-');
    }

    // Fallback to client-side calculation for backward compatibility
    if (!task.due_date) return '';

    const date = new Date(task.due_date);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return 'overdue';
    if (diffDays === 0) return 'due-today';
    if (diffDays <= 3) return 'due-soon';
    return 'upcoming';
  };

  if (loading) {
    return (
      <div className={`task-list-loading ${className}`}>
        <div className="loading-spinner"></div>
        <p>Loading tasks...</p>
        <style jsx>{`
          .task-list-loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 48px;
            color: #6b7280;
          }

          .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e5e7eb;
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }

          @keyframes spin {
            to {
              transform: rotate(360deg);
            }
          }
        `}</style>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className={`task-list-empty ${className}`}>
        <div className="empty-icon">📝</div>
        <p className="empty-message">{emptyMessage}</p>
        <style jsx>{`
          .task-list-empty {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 48px;
            background: white;
            border: 2px dashed #e5e7eb;
            border-radius: 8px;
          }

          .empty-icon {
            font-size: 48px;
            margin-bottom: 16px;
          }

          .empty-message {
            margin: 0;
            font-size: 16px;
            color: #6b7280;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className={`task-list ${className}`}>
      {tasks.map((task) => {
        const isExpanded = expandedTaskId === task.id;

        return (
          <div
            key={task.id}
            className={`task-item ${task.completed ? 'completed' : ''}`}
          >
            {/* Task Header */}
            <div className="task-header">
              {/* Completion Checkbox */}
              <button
                className="complete-checkbox"
                onClick={() => onTaskComplete(task.id)}
                aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
              >
                {task.completed ? '✓' : ''}
              </button>

              {/* Priority Indicator */}
              <span
                className="priority-indicator"
                style={{ color: getPriorityColor(task.priority) }}
                title={`Priority: ${task.priority}`}
              >
                {getPriorityIcon(task.priority)}
              </span>

              {/* Task Title */}
              <div className="task-content" onClick={() => toggleExpand(task.id)}>
                <h3 className="task-title">{task.title}</h3>

                {/* Task Meta */}
                <div className="task-meta">
                  {task.due_date && (
                    <span className={`due-date ${getDueDateClass(task)}`}>
                      📅 {formatDate(task.due_date)}
                    </span>
                  )}
                  {task.is_recurring && (
                    <span className="recurring-badge" title="Recurring task">
                      🔄 Recurring
                    </span>
                  )}
                  {task.is_recurring && task.due_date && !task.completed && (
                    <span className="next-occurrence" title="Next occurrence">
                      ⏭️ Next: {formatDate(task.due_date)}
                    </span>
                  )}
                </div>
              </div>

              {/* Task Actions */}
              <div className="task-actions">
                <button
                  className="action-btn edit-btn"
                  onClick={() => onTaskEdit(task.id)}
                  aria-label="Edit task"
                  title="Edit task"
                >
                  ✏️
                </button>
                <button
                  className="action-btn delete-btn"
                  onClick={() => onTaskDelete(task.id)}
                  aria-label="Delete task"
                  title="Delete task"
                >
                  🗑️
                </button>
              </div>
            </div>

            {/* Task Tags */}
            {task.tags && task.tags.length > 0 && (
              <div className="task-tags">
                <TagList
                  tags={task.tags}
                  size="small"
                  onClick={onTagClick}
                  maxVisible={5}
                />
              </div>
            )}

            {/* Expanded Description */}
            {isExpanded && task.description && (
              <div className="task-description">
                <p>{task.description}</p>
              </div>
            )}
          </div>
        );
      })}

      <style jsx>{`
        .task-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .task-item {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 16px;
          transition: all 0.2s;
        }

        .task-item:hover {
          border-color: #d1d5db;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .task-item.completed {
          opacity: 0.6;
          background: #f9fafb;
        }

        .task-header {
          display: flex;
          align-items: flex-start;
          gap: 12px;
        }

        .complete-checkbox {
          flex-shrink: 0;
          width: 24px;
          height: 24px;
          border: 2px solid #d1d5db;
          border-radius: 6px;
          background: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          color: white;
          transition: all 0.2s;
        }

        .complete-checkbox:hover {
          border-color: #3b82f6;
        }

        .task-item.completed .complete-checkbox {
          background: #3b82f6;
          border-color: #3b82f6;
        }

        .priority-indicator {
          flex-shrink: 0;
          font-size: 16px;
          margin-top: 2px;
        }

        .task-content {
          flex: 1;
          cursor: pointer;
          min-width: 0;
        }

        .task-title {
          margin: 0 0 4px 0;
          font-size: 16px;
          font-weight: 600;
          color: #1f2937;
          line-height: 1.4;
        }

        .task-item.completed .task-title {
          text-decoration: line-through;
          color: #6b7280;
        }

        .task-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 4px;
        }

        .due-date,
        .recurring-badge {
          display: inline-flex;
          align-items: center;
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
        }

        .due-date.overdue {
          background: #fee2e2;
          color: #991b1b;
        }

        .due-date.due-today {
          background: #fef3c7;
          color: #92400e;
        }

        .due-date.due-soon {
          background: #fed7aa;
          color: #9a3412;
        }

        .due-date.due-later {
          background: #e0e7ff;
          color: #3730a3;
        }

        .recurring-badge {
          background: #dbeafe;
          color: #1e40af;
        }

        .task-actions {
          display: flex;
          gap: 4px;
          flex-shrink: 0;
        }

        .action-btn {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: transparent;
          border: 1px solid transparent;
          border-radius: 6px;
          cursor: pointer;
          font-size: 16px;
          transition: all 0.2s;
        }

        .action-btn:hover {
          background: #f3f4f6;
          border-color: #e5e7eb;
        }

        .delete-btn:hover {
          background: #fee2e2;
          border-color: #fecaca;
        }

        .task-tags {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #f3f4f6;
        }

        .task-description {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #f3f4f6;
        }

        .task-description p {
          margin: 0;
          font-size: 14px;
          color: #6b7280;
          line-height: 1.6;
          white-space: pre-wrap;
        }

        @media (max-width: 640px) {
          .task-item {
            padding: 12px;
          }

          .task-header {
            gap: 8px;
          }

          .task-title {
            font-size: 15px;
          }

          .action-btn {
            width: 28px;
            height: 28px;
            font-size: 14px;
          }
        }
      `}</style>
    </div>
  );
};

export default TaskList;
