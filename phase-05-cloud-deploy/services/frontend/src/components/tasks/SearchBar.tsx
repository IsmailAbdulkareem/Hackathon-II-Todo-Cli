/**
 * SearchBar component for real-time task search.
 *
 * Provides a search input with debounced real-time search functionality.
 * Searches across task titles and descriptions using full-text search.
 */

import React, { useState, useEffect, useCallback } from 'react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  debounceMs?: number;
  className?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = 'Search tasks...',
  debounceMs = 300,
  className = ''
}) => {
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  // Debounced search effect
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(query);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [query, debounceMs, onSearch]);

  const handleClear = useCallback(() => {
    setQuery('');
    onSearch('');
  }, [onSearch]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      handleClear();
      (e.target as HTMLInputElement).blur();
    }
  }, [handleClear]);

  return (
    <div className={`search-bar ${isFocused ? 'focused' : ''} ${className}`}>
      <div className="search-input-wrapper">
        {/* Search Icon */}
        <span className="search-icon" aria-hidden="true">
          🔍
        </span>

        {/* Search Input */}
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="search-input"
          aria-label="Search tasks"
        />

        {/* Clear Button */}
        {query && (
          <button
            onClick={handleClear}
            className="clear-btn"
            aria-label="Clear search"
            type="button"
          >
            ✕
          </button>
        )}
      </div>

      {/* Search Tips */}
      {isFocused && !query && (
        <div className="search-tips">
          <p className="search-tip">💡 Search across task titles and descriptions</p>
          <p className="search-tip">⌨️ Press <kbd>Esc</kbd> to clear</p>
        </div>
      )}

      {/* Active Search Indicator */}
      {query && (
        <div className="search-status">
          Searching for: <strong>{query}</strong>
        </div>
      )}

      <style jsx>{`
        .search-bar {
          position: relative;
          width: 100%;
          margin-bottom: 16px;
        }

        .search-input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          transition: all 0.2s;
        }

        .search-bar.focused .search-input-wrapper {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .search-icon {
          position: absolute;
          left: 12px;
          font-size: 18px;
          color: #9ca3af;
          pointer-events: none;
        }

        .search-input {
          flex: 1;
          padding: 12px 40px 12px 44px;
          border: none;
          outline: none;
          font-size: 16px;
          color: #1f2937;
          background: transparent;
        }

        .search-input::placeholder {
          color: #9ca3af;
        }

        .clear-btn {
          position: absolute;
          right: 8px;
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f3f4f6;
          border: none;
          border-radius: 50%;
          color: #6b7280;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }

        .clear-btn:hover {
          background: #e5e7eb;
          color: #374151;
        }

        .clear-btn:active {
          transform: scale(0.95);
        }

        .search-tips {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          margin-top: 8px;
          padding: 12px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          z-index: 10;
        }

        .search-tip {
          margin: 0;
          padding: 4px 0;
          font-size: 13px;
          color: #6b7280;
          line-height: 1.5;
        }

        .search-tip kbd {
          display: inline-block;
          padding: 2px 6px;
          background: #f3f4f6;
          border: 1px solid #d1d5db;
          border-radius: 4px;
          font-family: monospace;
          font-size: 12px;
          color: #374151;
        }

        .search-status {
          margin-top: 8px;
          padding: 8px 12px;
          background: #eff6ff;
          border: 1px solid #bfdbfe;
          border-radius: 6px;
          font-size: 14px;
          color: #1e40af;
        }

        .search-status strong {
          font-weight: 600;
        }

        @media (max-width: 640px) {
          .search-input {
            font-size: 16px; /* Prevent zoom on iOS */
          }

          .search-tips {
            font-size: 12px;
          }
        }
      `}</style>
    </div>
  );
};

export default SearchBar;
