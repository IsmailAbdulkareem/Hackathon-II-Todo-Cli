/**
 * FilterPanel component for task filtering.
 *
 * Provides UI controls for filtering tasks by:
 * - Priority (Low, Medium, High)
 * - Tags (multi-select)
 * - Completion status
 * - Recurring status
 * - Due date status (overdue, due today, has due date)
 */

import React, { useState } from 'react';

export interface FilterOptions {
  priority: string | null;
  tags: string[];
  completed: boolean | null;
  isRecurring: boolean | null;
  overdue: boolean | null;
  dueToday: boolean | null;
  hasDueDate: boolean | null;
}

interface FilterPanelProps {
  filters: FilterOptions;
  onFilterChange: (filters: FilterOptions) => void;
  availableTags: Array<{ id: string; name: string; color: string }>;
  className?: string;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onFilterChange,
  availableTags,
  className = ''
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handlePriorityChange = (priority: string | null) => {
    onFilterChange({ ...filters, priority });
  };

  const handleTagToggle = (tagName: string) => {
    const newTags = filters.tags.includes(tagName)
      ? filters.tags.filter(t => t !== tagName)
      : [...filters.tags, tagName];
    onFilterChange({ ...filters, tags: newTags });
  };

  const handleCompletedChange = (completed: boolean | null) => {
    onFilterChange({ ...filters, completed });
  };

  const handleRecurringChange = (isRecurring: boolean | null) => {
    onFilterChange({ ...filters, isRecurring });
  };

  const handleDueDateFilterChange = (
    filterType: 'overdue' | 'dueToday' | 'hasDueDate',
    value: boolean | null
  ) => {
    onFilterChange({ ...filters, [filterType]: value });
  };

  const clearAllFilters = () => {
    onFilterChange({
      priority: null,
      tags: [],
      completed: null,
      isRecurring: null,
      overdue: null,
      dueToday: null,
      hasDueDate: null
    });
  };

  const hasActiveFilters =
    filters.priority !== null ||
    filters.tags.length > 0 ||
    filters.completed !== null ||
    filters.isRecurring !== null ||
    filters.overdue !== null ||
    filters.dueToday !== null ||
    filters.hasDueDate !== null;

  return (
    <div className={`filter-panel ${className}`}>
      {/* Filter Header */}
      <div className="filter-header">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="filter-toggle"
          aria-expanded={isExpanded}
        >
          <span className="filter-icon">🔍</span>
          <span className="filter-title">Filters</span>
          {hasActiveFilters && (
            <span className="filter-badge">{getActiveFilterCount(filters)}</span>
          )}
          <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>▼</span>
        </button>

        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            className="clear-filters-btn"
            title="Clear all filters"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Filter Content */}
      {isExpanded && (
        <div className="filter-content">
          {/* Priority Filter */}
          <div className="filter-section">
            <h3 className="filter-section-title">Priority</h3>
            <div className="filter-options">
              <button
                onClick={() => handlePriorityChange(null)}
                className={`filter-btn ${filters.priority === null ? 'active' : ''}`}
              >
                All
              </button>
              <button
                onClick={() => handlePriorityChange('High')}
                className={`filter-btn priority-high ${filters.priority === 'High' ? 'active' : ''}`}
              >
                High
              </button>
              <button
                onClick={() => handlePriorityChange('Medium')}
                className={`filter-btn priority-medium ${filters.priority === 'Medium' ? 'active' : ''}`}
              >
                Medium
              </button>
              <button
                onClick={() => handlePriorityChange('Low')}
                className={`filter-btn priority-low ${filters.priority === 'Low' ? 'active' : ''}`}
              >
                Low
              </button>
            </div>
          </div>

          {/* Tags Filter */}
          {availableTags.length > 0 && (
            <div className="filter-section">
              <h3 className="filter-section-title">Tags</h3>
              <div className="filter-tags">
                {availableTags.map(tag => (
                  <button
                    key={tag.id}
                    onClick={() => handleTagToggle(tag.name)}
                    className={`tag-filter-btn ${filters.tags.includes(tag.name) ? 'active' : ''}`}
                    style={{
                      borderColor: tag.color,
                      backgroundColor: filters.tags.includes(tag.name) ? tag.color : 'transparent',
                      color: filters.tags.includes(tag.name) ? '#fff' : tag.color
                    }}
                  >
                    {tag.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Status Filter */}
          <div className="filter-section">
            <h3 className="filter-section-title">Status</h3>
            <div className="filter-options">
              <button
                onClick={() => handleCompletedChange(null)}
                className={`filter-btn ${filters.completed === null ? 'active' : ''}`}
              >
                All
              </button>
              <button
                onClick={() => handleCompletedChange(false)}
                className={`filter-btn ${filters.completed === false ? 'active' : ''}`}
              >
                Active
              </button>
              <button
                onClick={() => handleCompletedChange(true)}
                className={`filter-btn ${filters.completed === true ? 'active' : ''}`}
              >
                Completed
              </button>
            </div>
          </div>

          {/* Due Date Filter */}
          <div className="filter-section">
            <h3 className="filter-section-title">Due Date</h3>
            <div className="filter-options-vertical">
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={filters.overdue === true}
                  onChange={(e) => handleDueDateFilterChange('overdue', e.target.checked ? true : null)}
                />
                <span className="filter-label overdue">Overdue</span>
              </label>
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={filters.dueToday === true}
                  onChange={(e) => handleDueDateFilterChange('dueToday', e.target.checked ? true : null)}
                />
                <span className="filter-label due-today">Due Today</span>
              </label>
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={filters.hasDueDate === true}
                  onChange={(e) => handleDueDateFilterChange('hasDueDate', e.target.checked ? true : null)}
                />
                <span className="filter-label">Has Due Date</span>
              </label>
            </div>
          </div>

          {/* Recurring Filter */}
          <div className="filter-section">
            <h3 className="filter-section-title">Recurring</h3>
            <div className="filter-options">
              <button
                onClick={() => handleRecurringChange(null)}
                className={`filter-btn ${filters.isRecurring === null ? 'active' : ''}`}
              >
                All
              </button>
              <button
                onClick={() => handleRecurringChange(true)}
                className={`filter-btn ${filters.isRecurring === true ? 'active' : ''}`}
              >
                Recurring
              </button>
              <button
                onClick={() => handleRecurringChange(false)}
                className={`filter-btn ${filters.isRecurring === false ? 'active' : ''}`}
              >
                One-time
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .filter-panel {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 16px;
        }

        .filter-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .filter-toggle {
          display: flex;
          align-items: center;
          gap: 8px;
          background: none;
          border: none;
          cursor: pointer;
          font-size: 16px;
          font-weight: 600;
          color: #1f2937;
          padding: 0;
        }

        .filter-icon {
          font-size: 20px;
        }

        .filter-badge {
          background: #3b82f6;
          color: white;
          border-radius: 12px;
          padding: 2px 8px;
          font-size: 12px;
          font-weight: 600;
        }

        .expand-icon {
          font-size: 12px;
          transition: transform 0.2s;
        }

        .expand-icon.expanded {
          transform: rotate(180deg);
        }

        .clear-filters-btn {
          background: none;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          padding: 6px 12px;
          font-size: 14px;
          color: #6b7280;
          cursor: pointer;
          transition: all 0.2s;
        }

        .clear-filters-btn:hover {
          background: #f9fafb;
          color: #1f2937;
        }

        .filter-content {
          margin-top: 16px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .filter-section {
          border-top: 1px solid #e5e7eb;
          padding-top: 12px;
        }

        .filter-section-title {
          font-size: 14px;
          font-weight: 600;
          color: #6b7280;
          margin: 0 0 8px 0;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .filter-options {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .filter-options-vertical {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .filter-btn {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          padding: 8px 16px;
          font-size: 14px;
          color: #6b7280;
          cursor: pointer;
          transition: all 0.2s;
        }

        .filter-btn:hover {
          background: #f9fafb;
          border-color: #d1d5db;
        }

        .filter-btn.active {
          background: #3b82f6;
          border-color: #3b82f6;
          color: white;
        }

        .filter-btn.priority-high.active {
          background: #ef4444;
          border-color: #ef4444;
        }

        .filter-btn.priority-medium.active {
          background: #f59e0b;
          border-color: #f59e0b;
        }

        .filter-btn.priority-low.active {
          background: #10b981;
          border-color: #10b981;
        }

        .filter-tags {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .tag-filter-btn {
          border: 2px solid;
          border-radius: 16px;
          padding: 6px 12px;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .tag-filter-btn:hover {
          opacity: 0.8;
        }

        .filter-checkbox {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
        }

        .filter-checkbox input[type="checkbox"] {
          width: 18px;
          height: 18px;
          cursor: pointer;
        }

        .filter-label {
          font-size: 14px;
          color: #374151;
        }

        .filter-label.overdue {
          color: #ef4444;
          font-weight: 500;
        }

        .filter-label.due-today {
          color: #f59e0b;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
};

/**
 * Helper function to count active filters.
 */
function getActiveFilterCount(filters: FilterOptions): number {
  let count = 0;
  if (filters.priority !== null) count++;
  if (filters.tags.length > 0) count += filters.tags.length;
  if (filters.completed !== null) count++;
  if (filters.isRecurring !== null) count++;
  if (filters.overdue === true) count++;
  if (filters.dueToday === true) count++;
  if (filters.hasDueDate === true) count++;
  return count;
}

export default FilterPanel;
