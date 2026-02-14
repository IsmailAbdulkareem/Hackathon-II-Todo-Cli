/**
 * TaskForm component for creating and editing tasks.
 *
 * Features:
 * - Title and description inputs
 * - Priority selector (Low, Medium, High)
 * - Tag input with autocomplete
 * - Due date picker with optional time
 * - Reminder selector for task notifications
 * - Recurring task toggle
 * - Form validation
 * - Submit and cancel actions
 */

import React, { useState, useEffect, useRef } from 'react';
import { Tag } from './TagPill';
import { DateTimePicker, QuickDatePresets } from './DateTimePicker';
import { ReminderSelector, Reminder } from './ReminderSelector';
import { RecurrenceSelector, RecurrenceRule } from './RecurrenceSelector';

export interface TaskFormData {
  title: string;
  description: string;
  priority: 'Low' | 'Medium' | 'High';
  due_date?: string;
  is_recurring: boolean;
  tag_ids: string[];
  reminders?: Reminder[];
  recurrence_rule?: RecurrenceRule;
}

interface TaskFormProps {
  initialData?: Partial<TaskFormData>;
  availableTags: Tag[];
  onSubmit: (data: TaskFormData) => void;
  onCancel: () => void;
  submitLabel?: string;
  loading?: boolean;
  className?: string;
}

export const TaskForm: React.FC<TaskFormProps> = ({
  initialData,
  availableTags,
  onSubmit,
  onCancel,
  submitLabel = 'Create Task',
  loading = false,
  className = ''
}) => {
  const [formData, setFormData] = useState<TaskFormData>({
    title: initialData?.title || '',
    description: initialData?.description || '',
    priority: initialData?.priority || 'Medium',
    due_date: initialData?.due_date || undefined,
    is_recurring: initialData?.is_recurring || false,
    tag_ids: initialData?.tag_ids || [],
    reminders: initialData?.reminders || [],
    recurrence_rule: initialData?.recurrence_rule || undefined
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [tagSearchQuery, setTagSearchQuery] = useState('');
  const [showTagSuggestions, setShowTagSuggestions] = useState(false);
  const tagInputRef = useRef<HTMLInputElement>(null);

  // Filter tags based on search query
  const filteredTags = availableTags.filter(
    (tag) =>
      tag.name.toLowerCase().includes(tagSearchQuery.toLowerCase()) &&
      !formData.tag_ids.includes(tag.id)
  );

  // Get selected tags
  const selectedTags = availableTags.filter((tag) =>
    formData.tag_ids.includes(tag.id)
  );

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.length > 200) {
      newErrors.title = 'Title must be 200 characters or less';
    }

    if (formData.description.length > 2000) {
      newErrors.description = 'Description must be 2000 characters or less';
    }

    if (formData.due_date) {
      const dueDate = new Date(formData.due_date);
      if (isNaN(dueDate.getTime())) {
        newErrors.due_date = 'Invalid date format';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleAddTag = (tagId: string) => {
    if (!formData.tag_ids.includes(tagId)) {
      setFormData({
        ...formData,
        tag_ids: [...formData.tag_ids, tagId]
      });
    }
    setTagSearchQuery('');
    setShowTagSuggestions(false);
  };

  const handleRemoveTag = (tagId: string) => {
    setFormData({
      ...formData,
      tag_ids: formData.tag_ids.filter((id) => id !== tagId)
    });
  };

  const handleTagInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      setShowTagSuggestions(false);
      setTagSearchQuery('');
    } else if (e.key === 'Enter' && filteredTags.length > 0) {
      e.preventDefault();
      handleAddTag(filteredTags[0].id);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={`task-form ${className}`}>
      {/* Title Input */}
      <div className="form-group">
        <label htmlFor="title" className="form-label required">
          Title
        </label>
        <input
          id="title"
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className={`form-input ${errors.title ? 'error' : ''}`}
          placeholder="Enter task title..."
          maxLength={200}
          disabled={loading}
          autoFocus
        />
        {errors.title && <span className="error-message">{errors.title}</span>}
        <span className="char-count">{formData.title.length}/200</span>
      </div>

      {/* Description Input */}
      <div className="form-group">
        <label htmlFor="description" className="form-label">
          Description
        </label>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className={`form-textarea ${errors.description ? 'error' : ''}`}
          placeholder="Enter task description (optional)..."
          rows={4}
          maxLength={2000}
          disabled={loading}
        />
        {errors.description && <span className="error-message">{errors.description}</span>}
        <span className="char-count">{formData.description.length}/2000</span>
      </div>

      {/* Priority Selector */}
      <div className="form-group">
        <label className="form-label">Priority</label>
        <div className="priority-selector">
          {(['Low', 'Medium', 'High'] as const).map((priority) => (
            <button
              key={priority}
              type="button"
              onClick={() => setFormData({ ...formData, priority })}
              className={`priority-btn priority-${priority.toLowerCase()} ${
                formData.priority === priority ? 'active' : ''
              }`}
              disabled={loading}
            >
              {priority === 'High' && '🔴'}
              {priority === 'Medium' && '🟡'}
              {priority === 'Low' && '🟢'}
              <span>{priority}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tag Input with Autocomplete */}
      <div className="form-group">
        <label htmlFor="tags" className="form-label">
          Tags
        </label>

        {/* Selected Tags */}
        {selectedTags.length > 0 && (
          <div className="selected-tags">
            {selectedTags.map((tag) => (
              <span
                key={tag.id}
                className="selected-tag"
                style={{ backgroundColor: tag.color }}
              >
                {tag.name}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag.id)}
                  className="remove-tag-btn"
                  aria-label={`Remove ${tag.name}`}
                >
                  ✕
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Tag Search Input */}
        <div className="tag-input-wrapper">
          <input
            ref={tagInputRef}
            id="tags"
            type="text"
            value={tagSearchQuery}
            onChange={(e) => {
              setTagSearchQuery(e.target.value);
              setShowTagSuggestions(true);
            }}
            onFocus={() => setShowTagSuggestions(true)}
            onBlur={() => setTimeout(() => setShowTagSuggestions(false), 200)}
            onKeyDown={handleTagInputKeyDown}
            className="form-input"
            placeholder="Search tags..."
            disabled={loading}
          />

          {/* Tag Suggestions */}
          {showTagSuggestions && filteredTags.length > 0 && (
            <div className="tag-suggestions">
              {filteredTags.slice(0, 5).map((tag) => (
                <button
                  key={tag.id}
                  type="button"
                  onClick={() => handleAddTag(tag.id)}
                  className="tag-suggestion"
                >
                  <span
                    className="tag-color-dot"
                    style={{ backgroundColor: tag.color }}
                  />
                  <span>{tag.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Due Date Input */}
      <div className="form-group">
        <DateTimePicker
          value={formData.due_date}
          onChange={(value) => {
            setFormData({ ...formData, due_date: value || undefined });
            // Clear reminders if due date is removed
            if (!value) {
              setFormData({ ...formData, due_date: undefined, reminders: [] });
            }
          }}
          label="Due Date"
          includeTime={true}
          minDate={new Date().toISOString()}
          error={errors.due_date}
        />

        {/* Quick Date Presets */}
        {!formData.due_date && (
          <QuickDatePresets
            onSelect={(date) => setFormData({ ...formData, due_date: date.toISOString() })}
            className="mt-2"
          />
        )}
      </div>

      {/* Reminder Selector */}
      <div className="form-group">
        <ReminderSelector
          value={formData.reminders || []}
          onChange={(reminders) => setFormData({ ...formData, reminders })}
          dueDate={formData.due_date}
          disabled={!formData.due_date}
        />
      </div>

      {/* Recurrence Configuration */}
      <div className="form-group">
        <RecurrenceSelector
          value={formData.recurrence_rule || null}
          onChange={(rule) => {
            setFormData({
              ...formData,
              recurrence_rule: rule || undefined,
              is_recurring: !!rule
            });
          }}
          enabled={formData.is_recurring}
          onEnabledChange={(enabled) => {
            setFormData({
              ...formData,
              is_recurring: enabled,
              recurrence_rule: enabled ? formData.recurrence_rule : undefined
            });
          }}
        />
      </div>

      {/* Form Actions */}
      <div className="form-actions">
        <button
          type="button"
          onClick={onCancel}
          className="btn btn-secondary"
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !formData.title.trim()}
        >
          {loading ? 'Saving...' : submitLabel}
        </button>
      </div>

      <style jsx>{`
        .task-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .form-label {
          font-size: 14px;
          font-weight: 600;
          color: #374151;
        }

        .form-label.required::after {
          content: ' *';
          color: #ef4444;
        }

        .form-input,
        .form-textarea {
          padding: 10px 12px;
          border: 2px solid #e5e7eb;
          border-radius: 6px;
          font-size: 14px;
          color: #1f2937;
          transition: all 0.2s;
        }

        .form-input:focus,
        .form-textarea:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-input.error,
        .form-textarea.error {
          border-color: #ef4444;
        }

        .form-input:disabled,
        .form-textarea:disabled {
          background: #f9fafb;
          cursor: not-allowed;
        }

        .form-textarea {
          resize: vertical;
          min-height: 100px;
        }

        .error-message {
          font-size: 13px;
          color: #ef4444;
        }

        .char-count {
          font-size: 12px;
          color: #9ca3af;
          text-align: right;
        }

        .priority-selector {
          display: flex;
          gap: 8px;
        }

        .priority-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          padding: 10px;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 500;
          color: #6b7280;
          cursor: pointer;
          transition: all 0.2s;
        }

        .priority-btn:hover:not(:disabled) {
          border-color: #d1d5db;
          background: #f9fafb;
        }

        .priority-btn.active {
          border-color: currentColor;
          background: currentColor;
          color: white;
        }

        .priority-btn.priority-high.active {
          border-color: #ef4444;
          background: #ef4444;
        }

        .priority-btn.priority-medium.active {
          border-color: #f59e0b;
          background: #f59e0b;
        }

        .priority-btn.priority-low.active {
          border-color: #10b981;
          background: #10b981;
        }

        .priority-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .selected-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-bottom: 8px;
        }

        .selected-tag {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 4px 10px;
          border-radius: 12px;
          font-size: 13px;
          font-weight: 500;
          color: white;
        }

        .remove-tag-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 16px;
          height: 16px;
          background: rgba(255, 255, 255, 0.3);
          border: none;
          border-radius: 50%;
          color: white;
          font-size: 10px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .remove-tag-btn:hover {
          background: rgba(255, 255, 255, 0.5);
        }

        .tag-input-wrapper {
          position: relative;
        }

        .tag-suggestions {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          margin-top: 4px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          max-height: 200px;
          overflow-y: auto;
          z-index: 10;
        }

        .tag-suggestion {
          display: flex;
          align-items: center;
          gap: 8px;
          width: 100%;
          padding: 10px 12px;
          background: none;
          border: none;
          text-align: left;
          font-size: 14px;
          color: #374151;
          cursor: pointer;
          transition: background 0.2s;
        }

        .tag-suggestion:hover {
          background: #f9fafb;
        }

        .tag-color-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .form-checkbox {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
        }

        .form-checkbox input[type="checkbox"] {
          width: 18px;
          height: 18px;
          cursor: pointer;
        }

        .form-checkbox span {
          font-size: 14px;
          color: #374151;
        }

        .form-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          padding-top: 8px;
          border-top: 1px solid #e5e7eb;
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-secondary {
          background: white;
          border: 1px solid #e5e7eb;
          color: #6b7280;
        }

        .btn-secondary:hover:not(:disabled) {
          background: #f9fafb;
          border-color: #d1d5db;
        }

        .btn-primary {
          background: #3b82f6;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #2563eb;
        }

        @media (max-width: 640px) {
          .priority-selector {
            flex-direction: column;
          }

          .form-actions {
            flex-direction: column-reverse;
          }

          .btn {
            width: 100%;
          }
        }
      `}</style>
    </form>
  );
};

export default TaskForm;
