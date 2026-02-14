/**
 * RecurringTaskDialog component for confirming operations on recurring tasks.
 *
 * Features:
 * - Confirmation dialog for editing/deleting recurring tasks
 * - Options to apply changes to single instance or entire series
 * - Clear messaging about the impact of each choice
 * - Accessible keyboard navigation
 */

import React from 'react';

export type RecurringAction = 'edit' | 'delete';
export type RecurringScope = 'single' | 'series';

interface RecurringTaskDialogProps {
  isOpen: boolean;
  action: RecurringAction;
  taskTitle: string;
  onConfirm: (scope: RecurringScope) => void;
  onCancel: () => void;
}

export const RecurringTaskDialog: React.FC<RecurringTaskDialogProps> = ({
  isOpen,
  action,
  taskTitle,
  onConfirm,
  onCancel
}) => {
  if (!isOpen) return null;

  const actionText = action === 'edit' ? 'Edit' : 'Delete';
  const actionVerb = action === 'edit' ? 'editing' : 'deleting';

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <div className="dialog-overlay" onClick={onCancel} onKeyDown={handleKeyDown}>
      <div className="dialog-content" onClick={(e) => e.stopPropagation()}>
        {/* Dialog Header */}
        <div className="dialog-header">
          <h2 className="dialog-title">
            {actionText} Recurring Task
          </h2>
          <button
            className="close-btn"
            onClick={onCancel}
            aria-label="Close dialog"
          >
            ✕
          </button>
        </div>

        {/* Dialog Body */}
        <div className="dialog-body">
          <p className="task-name">
            <strong>"{taskTitle}"</strong>
          </p>
          <p className="dialog-message">
            This is a recurring task. Would you like to {actionVerb}:
          </p>

          {/* Action Options */}
          <div className="action-options">
            <button
              className="option-btn single-btn"
              onClick={() => onConfirm('single')}
              autoFocus
            >
              <div className="option-icon">📄</div>
              <div className="option-content">
                <div className="option-title">This task only</div>
                <div className="option-description">
                  {action === 'edit'
                    ? 'Changes will only apply to this specific occurrence'
                    : 'Only this occurrence will be deleted'}
                </div>
              </div>
            </button>

            <button
              className="option-btn series-btn"
              onClick={() => onConfirm('series')}
            >
              <div className="option-icon">📚</div>
              <div className="option-content">
                <div className="option-title">All tasks in series</div>
                <div className="option-description">
                  {action === 'edit'
                    ? 'Changes will apply to all future occurrences'
                    : 'All occurrences (past and future) will be deleted'}
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Dialog Footer */}
        <div className="dialog-footer">
          <button className="cancel-btn" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </div>

      <style jsx>{`
        .dialog-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: fadeIn 0.2s ease-out;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .dialog-content {
          background: white;
          border-radius: 12px;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
            0 10px 10px -5px rgba(0, 0, 0, 0.04);
          max-width: 500px;
          width: 90%;
          max-height: 90vh;
          overflow-y: auto;
          animation: slideUp 0.3s ease-out;
        }

        @keyframes slideUp {
          from {
            transform: translateY(20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        .dialog-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 20px 24px;
          border-bottom: 1px solid #e5e7eb;
        }

        .dialog-title {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
          color: #111827;
        }

        .close-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          background: none;
          border: none;
          border-radius: 6px;
          font-size: 20px;
          color: #6b7280;
          cursor: pointer;
          transition: all 0.2s;
        }

        .close-btn:hover {
          background: #f3f4f6;
          color: #111827;
        }

        .dialog-body {
          padding: 24px;
        }

        .task-name {
          margin: 0 0 16px 0;
          font-size: 16px;
          color: #374151;
        }

        .dialog-message {
          margin: 0 0 20px 0;
          font-size: 14px;
          color: #6b7280;
        }

        .action-options {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .option-btn {
          display: flex;
          align-items: flex-start;
          gap: 16px;
          padding: 16px;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          text-align: left;
          cursor: pointer;
          transition: all 0.2s;
        }

        .option-btn:hover {
          border-color: #3b82f6;
          background: #eff6ff;
        }

        .option-btn:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .option-icon {
          font-size: 32px;
          flex-shrink: 0;
        }

        .option-content {
          flex: 1;
        }

        .option-title {
          font-size: 16px;
          font-weight: 600;
          color: #111827;
          margin-bottom: 4px;
        }

        .option-description {
          font-size: 14px;
          color: #6b7280;
          line-height: 1.5;
        }

        .dialog-footer {
          display: flex;
          justify-content: flex-end;
          padding: 16px 24px;
          border-top: 1px solid #e5e7eb;
        }

        .cancel-btn {
          padding: 10px 20px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          color: #6b7280;
          cursor: pointer;
          transition: all 0.2s;
        }

        .cancel-btn:hover {
          background: #f9fafb;
          border-color: #d1d5db;
        }

        @media (max-width: 640px) {
          .dialog-content {
            width: 95%;
            max-height: 95vh;
          }

          .option-btn {
            flex-direction: column;
            align-items: center;
            text-align: center;
          }

          .option-icon {
            font-size: 40px;
          }
        }
      `}</style>
    </div>
  );
};

export default RecurringTaskDialog;
