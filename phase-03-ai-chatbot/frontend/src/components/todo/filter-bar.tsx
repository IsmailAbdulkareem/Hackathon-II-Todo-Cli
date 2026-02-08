'use client';

import React from 'react';
import { Filter, X, Calendar, Tag as TagIcon, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { PriorityLevel } from '@/types/todo';

export interface FilterState {
  priority?: PriorityLevel;
  tags: string[];
  completed?: boolean;
  due_from?: string;
  due_to?: string;
}

interface FilterBarProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  onClear: () => void;
  availableTags?: string[];
}

export function FilterBar({ filters, onChange, onClear, availableTags = [] }: FilterBarProps) {
  const hasActiveFilters =
    filters.priority ||
    filters.tags.length > 0 ||
    filters.completed !== undefined ||
    filters.due_from ||
    filters.due_to;

  const handlePriorityChange = (priority: PriorityLevel | undefined) => {
    onChange({ ...filters, priority });
  };

  const handleTagToggle = (tag: string) => {
    const newTags = filters.tags.includes(tag)
      ? filters.tags.filter(t => t !== tag)
      : [...filters.tags, tag];
    onChange({ ...filters, tags: newTags });
  };

  const handleCompletedChange = (completed: boolean | undefined) => {
    onChange({ ...filters, completed });
  };

  const handleDueDateChange = (field: 'due_from' | 'due_to', value: string) => {
    onChange({ ...filters, [field]: value || undefined });
  };

  return (
    <div className="space-y-4 p-4 bg-neutral-50 dark:bg-neutral-900 rounded-2xl border-2 border-neutral-200 dark:border-neutral-700">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-neutral-600 dark:text-neutral-400" />
          <h3 className="font-semibold text-sm text-neutral-900 dark:text-neutral-100">
            Filters
          </h3>
          {hasActiveFilters && (
            <span className="px-2 py-0.5 text-xs font-bold bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
              Active
            </span>
          )}
        </div>
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClear}
            className="h-7 text-xs"
          >
            <X className="h-3 w-3 mr-1" />
            Clear all
          </Button>
        )}
      </div>

      {/* Priority Filter */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-xs font-semibold text-neutral-700 dark:text-neutral-300">
          <AlertCircle className="h-3.5 w-3.5" />
          Priority
        </label>
        <div className="flex gap-2">
          <Button
            variant={filters.priority === undefined ? "default" : "outline"}
            size="sm"
            onClick={() => handlePriorityChange(undefined)}
            className="h-8 text-xs"
          >
            All
          </Button>
          <Button
            variant={filters.priority === 'low' ? "default" : "outline"}
            size="sm"
            onClick={() => handlePriorityChange('low')}
            className="h-8 text-xs"
          >
            Low
          </Button>
          <Button
            variant={filters.priority === 'medium' ? "default" : "outline"}
            size="sm"
            onClick={() => handlePriorityChange('medium')}
            className="h-8 text-xs"
          >
            Medium
          </Button>
          <Button
            variant={filters.priority === 'high' ? "default" : "outline"}
            size="sm"
            onClick={() => handlePriorityChange('high')}
            className="h-8 text-xs"
          >
            High
          </Button>
        </div>
      </div>

      {/* Completion Status Filter */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-xs font-semibold text-neutral-700 dark:text-neutral-300">
          <CheckCircle className="h-3.5 w-3.5" />
          Status
        </label>
        <div className="flex gap-2">
          <Button
            variant={filters.completed === undefined ? "default" : "outline"}
            size="sm"
            onClick={() => handleCompletedChange(undefined)}
            className="h-8 text-xs"
          >
            All
          </Button>
          <Button
            variant={filters.completed === false ? "default" : "outline"}
            size="sm"
            onClick={() => handleCompletedChange(false)}
            className="h-8 text-xs"
          >
            Active
          </Button>
          <Button
            variant={filters.completed === true ? "default" : "outline"}
            size="sm"
            onClick={() => handleCompletedChange(true)}
            className="h-8 text-xs"
          >
            Completed
          </Button>
        </div>
      </div>

      {/* Tags Filter */}
      {availableTags.length > 0 && (
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-xs font-semibold text-neutral-700 dark:text-neutral-300">
            <TagIcon className="h-3.5 w-3.5" />
            Tags
          </label>
          <div className="flex flex-wrap gap-2">
            {availableTags.map((tag) => (
              <button
                key={tag}
                onClick={() => handleTagToggle(tag)}
                className={`px-3 py-1 text-xs font-medium rounded-full border-2 transition-all duration-200 ${
                  filters.tags.includes(tag)
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 border-neutral-300 dark:border-neutral-600 hover:border-blue-400'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Due Date Range Filter */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-xs font-semibold text-neutral-700 dark:text-neutral-300">
          <Calendar className="h-3.5 w-3.5" />
          Due Date Range
        </label>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-[10px] text-neutral-500 dark:text-neutral-400 mb-1 block">
              From
            </label>
            <input
              type="date"
              value={filters.due_from || ''}
              onChange={(e) => handleDueDateChange('due_from', e.target.value)}
              className="w-full h-9 px-3 text-xs rounded-md border-2 border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="text-[10px] text-neutral-500 dark:text-neutral-400 mb-1 block">
              To
            </label>
            <input
              type="date"
              value={filters.due_to || ''}
              onChange={(e) => handleDueDateChange('due_to', e.target.value)}
              className="w-full h-9 px-3 text-xs rounded-md border-2 border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
