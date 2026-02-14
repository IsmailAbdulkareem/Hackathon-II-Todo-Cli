/**
 * TagPill component for displaying task tags.
 *
 * Renders a colored pill-shaped tag with optional remove functionality.
 * Supports different sizes and interactive states.
 */

import React from 'react';

export interface Tag {
  id: string;
  name: string;
  color: string;
}

interface TagPillProps {
  tag: Tag;
  size?: 'small' | 'medium' | 'large';
  removable?: boolean;
  onRemove?: (tagId: string) => void;
  onClick?: (tagId: string) => void;
  className?: string;
}

export const TagPill: React.FC<TagPillProps> = ({
  tag,
  size = 'medium',
  removable = false,
  onRemove,
  onClick,
  className = ''
}) => {
  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onRemove) {
      onRemove(tag.id);
    }
  };

  const handleClick = () => {
    if (onClick) {
      onClick(tag.id);
    }
  };

  const isInteractive = onClick !== undefined;

  return (
    <span
      className={`tag-pill ${size} ${isInteractive ? 'interactive' : ''} ${className}`}
      style={{
        backgroundColor: tag.color,
        borderColor: tag.color
      }}
      onClick={isInteractive ? handleClick : undefined}
      role={isInteractive ? 'button' : undefined}
      tabIndex={isInteractive ? 0 : undefined}
      onKeyDown={
        isInteractive
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleClick();
              }
            }
          : undefined
      }
    >
      <span className="tag-name">{tag.name}</span>

      {removable && onRemove && (
        <button
          className="remove-btn"
          onClick={handleRemove}
          aria-label={`Remove ${tag.name} tag`}
          type="button"
        >
          ✕
        </button>
      )}

      <style jsx>{`
        .tag-pill {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          border-radius: 12px;
          border: 1px solid;
          font-weight: 500;
          color: white;
          white-space: nowrap;
          transition: all 0.2s;
        }

        .tag-pill.small {
          padding: 2px 8px;
          font-size: 11px;
          gap: 2px;
        }

        .tag-pill.medium {
          padding: 4px 10px;
          font-size: 13px;
        }

        .tag-pill.large {
          padding: 6px 12px;
          font-size: 14px;
        }

        .tag-pill.interactive {
          cursor: pointer;
        }

        .tag-pill.interactive:hover {
          opacity: 0.9;
          transform: translateY(-1px);
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .tag-pill.interactive:active {
          transform: translateY(0);
        }

        .tag-pill:focus-visible {
          outline: 2px solid #3b82f6;
          outline-offset: 2px;
        }

        .tag-name {
          line-height: 1;
        }

        .remove-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 16px;
          height: 16px;
          padding: 0;
          background: rgba(255, 255, 255, 0.3);
          border: none;
          border-radius: 50%;
          color: white;
          font-size: 10px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .tag-pill.small .remove-btn {
          width: 14px;
          height: 14px;
          font-size: 9px;
        }

        .tag-pill.large .remove-btn {
          width: 18px;
          height: 18px;
          font-size: 11px;
        }

        .remove-btn:hover {
          background: rgba(255, 255, 255, 0.5);
          transform: scale(1.1);
        }

        .remove-btn:active {
          transform: scale(0.95);
        }

        .remove-btn:focus-visible {
          outline: 2px solid white;
          outline-offset: 1px;
        }
      `}</style>
    </span>
  );
};

/**
 * TagList component for displaying multiple tags.
 */
interface TagListProps {
  tags: Tag[];
  size?: 'small' | 'medium' | 'large';
  removable?: boolean;
  onRemove?: (tagId: string) => void;
  onClick?: (tagId: string) => void;
  maxVisible?: number;
  className?: string;
}

export const TagList: React.FC<TagListProps> = ({
  tags,
  size = 'medium',
  removable = false,
  onRemove,
  onClick,
  maxVisible,
  className = ''
}) => {
  const visibleTags = maxVisible ? tags.slice(0, maxVisible) : tags;
  const hiddenCount = maxVisible && tags.length > maxVisible ? tags.length - maxVisible : 0;

  if (tags.length === 0) {
    return null;
  }

  return (
    <div className={`tag-list ${className}`}>
      {visibleTags.map((tag) => (
        <TagPill
          key={tag.id}
          tag={tag}
          size={size}
          removable={removable}
          onRemove={onRemove}
          onClick={onClick}
        />
      ))}

      {hiddenCount > 0 && (
        <span className={`more-tags ${size}`}>+{hiddenCount} more</span>
      )}

      <style jsx>{`
        .tag-list {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          align-items: center;
        }

        .more-tags {
          display: inline-flex;
          align-items: center;
          padding: 4px 10px;
          background: #f3f4f6;
          border: 1px solid #d1d5db;
          border-radius: 12px;
          font-size: 13px;
          font-weight: 500;
          color: #6b7280;
        }

        .more-tags.small {
          padding: 2px 8px;
          font-size: 11px;
        }

        .more-tags.large {
          padding: 6px 12px;
          font-size: 14px;
        }
      `}</style>
    </div>
  );
};

export default TagPill;
