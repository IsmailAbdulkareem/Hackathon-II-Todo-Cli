'use client';

import React from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { Button } from '@/components/ui/button';

export type SortField = 'created_at' | 'updated_at' | 'due_date' | 'priority';
export type SortOrder = 'asc' | 'desc';

interface SortSelectorProps {
  sortBy: SortField;
  sortOrder: SortOrder;
  onSortChange: (sortBy: SortField, sortOrder: SortOrder) => void;
  className?: string;
}

const sortOptions: { value: SortField; label: string }[] = [
  { value: 'created_at', label: 'Created Date' },
  { value: 'updated_at', label: 'Updated Date' },
  { value: 'due_date', label: 'Due Date' },
  { value: 'priority', label: 'Priority' },
];

export function SortSelector({ sortBy, sortOrder, onSortChange, className = '' }: SortSelectorProps) {
  const handleSortFieldChange = (field: SortField) => {
    // If clicking the same field, toggle order
    if (field === sortBy) {
      onSortChange(field, sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to descending
      onSortChange(field, 'desc');
    }
  };

  const handleOrderToggle = () => {
    onSortChange(sortBy, sortOrder === 'asc' ? 'desc' : 'asc');
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex items-center gap-2 text-xs font-semibold text-neutral-700 dark:text-neutral-300">
        <ArrowUpDown className="h-3.5 w-3.5" />
        <span>Sort by:</span>
      </div>

      <div className="flex items-center gap-1">
        {sortOptions.map((option) => (
          <Button
            key={option.value}
            variant={sortBy === option.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => handleSortFieldChange(option.value)}
            className="h-8 text-xs"
          >
            {option.label}
          </Button>
        ))}
      </div>

      <Button
        variant="outline"
        size="sm"
        onClick={handleOrderToggle}
        className="h-8 w-8 p-0"
        title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
      >
        {sortOrder === 'asc' ? (
          <ArrowUp className="h-3.5 w-3.5" />
        ) : (
          <ArrowDown className="h-3.5 w-3.5" />
        )}
      </Button>
    </div>
  );
}
