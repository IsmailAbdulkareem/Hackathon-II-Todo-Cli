'use client';

import React, { useState } from 'react';
import { Search, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface SearchBoxProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  placeholder?: string;
  className?: string;
}

export function SearchBox({
  value,
  onChange,
  onSearch,
  placeholder = "Search tasks...",
  className = ""
}: SearchBoxProps) {
  const [isFocused, setIsFocused] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  const handleClear = () => {
    onChange('');
    onSearch();
  };

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" />
        <Input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          className={`pl-10 pr-20 h-11 border-2 transition-all duration-300 ${
            isFocused
              ? 'border-blue-500 dark:border-blue-400 ring-2 ring-blue-500/20'
              : 'border-neutral-300 dark:border-neutral-600'
          }`}
        />
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {value && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleClear}
              className="h-7 w-7 p-0 hover:bg-neutral-100 dark:hover:bg-neutral-800"
            >
              <X className="h-3.5 w-3.5" />
            </Button>
          )}
          <Button
            type="button"
            onClick={onSearch}
            size="sm"
            className="h-7 px-3 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold"
          >
            Search
          </Button>
        </div>
      </div>
    </div>
  );
}
