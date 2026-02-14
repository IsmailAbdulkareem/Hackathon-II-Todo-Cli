"use client";

import React, { useState } from "react";

/**
 * RecurrenceSelector Component
 *
 * Allows users to configure recurring task patterns.
 * Supports daily, weekly, monthly, and yearly recurrence with intervals.
 *
 * Features:
 * - Frequency selection (daily, weekly, monthly, yearly)
 * - Interval configuration (every N days/weeks/months/years)
 * - End condition (end date or occurrence count)
 * - Visual preview of recurrence pattern
 */

export type RecurrenceFrequency = "daily" | "weekly" | "monthly" | "yearly";

export interface RecurrenceRule {
  frequency: RecurrenceFrequency;
  interval: number;
  endDate?: string;
  occurrenceCount?: number;
}

export interface RecurrenceSelectorProps {
  /** Current recurrence rule */
  value: RecurrenceRule | null;
  /** Callback when recurrence rule changes */
  onChange: (rule: RecurrenceRule | null) => void;
  /** Whether recurring is enabled */
  enabled: boolean;
  /** Callback when enabled state changes */
  onEnabledChange: (enabled: boolean) => void;
  /** Additional CSS classes */
  className?: string;
}

export const RecurrenceSelector: React.FC<RecurrenceSelectorProps> = ({
  value,
  onChange,
  enabled,
  onEnabledChange,
  className = "",
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Default recurrence rule
  const defaultRule: RecurrenceRule = {
    frequency: "daily",
    interval: 1,
    occurrenceCount: 10,
  };

  // Handle enable/disable toggle
  const handleToggle = (checked: boolean) => {
    onEnabledChange(checked);
    if (checked && !value) {
      onChange(defaultRule);
    } else if (!checked) {
      onChange(null);
    }
  };

  // Handle frequency change
  const handleFrequencyChange = (frequency: RecurrenceFrequency) => {
    if (!value) return;
    onChange({ ...value, frequency });
  };

  // Handle interval change
  const handleIntervalChange = (interval: number) => {
    if (!value) return;
    onChange({ ...value, interval: Math.max(1, interval) });
  };

  // Handle end condition change
  const handleEndConditionChange = (
    type: "date" | "count",
    valueStr: string
  ) => {
    if (!value) return;

    if (type === "date") {
      onChange({
        ...value,
        endDate: valueStr || undefined,
        occurrenceCount: undefined,
      });
    } else {
      const count = parseInt(valueStr, 10);
      onChange({
        ...value,
        occurrenceCount: count > 0 ? count : undefined,
        endDate: undefined,
      });
    }
  };

  // Generate human-readable description
  const getRecurrenceDescription = (): string => {
    if (!value) return "";

    const { frequency, interval, endDate, occurrenceCount } = value;

    let desc = `Repeats every ${interval > 1 ? interval : ""} ${frequency}${
      interval > 1 ? "" : ""
    }`;

    if (frequency === "daily") {
      desc = `Repeats every ${interval === 1 ? "day" : `${interval} days`}`;
    } else if (frequency === "weekly") {
      desc = `Repeats every ${interval === 1 ? "week" : `${interval} weeks`}`;
    } else if (frequency === "monthly") {
      desc = `Repeats every ${interval === 1 ? "month" : `${interval} months`}`;
    } else if (frequency === "yearly") {
      desc = `Repeats every ${interval === 1 ? "year" : `${interval} years`}`;
    }

    if (endDate) {
      const date = new Date(endDate);
      desc += ` until ${date.toLocaleDateString()}`;
    } else if (occurrenceCount) {
      desc += ` for ${occurrenceCount} occurrences`;
    }

    return desc;
  };

  return (
    <div className={`recurrence-selector ${className}`}>
      {/* Enable/Disable Toggle */}
      <label className="recurrence-toggle">
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => handleToggle(e.target.checked)}
        />
        <span className="toggle-label">Recurring task</span>
      </label>

      {/* Recurrence Configuration */}
      {enabled && value && (
        <div className="recurrence-config">
          {/* Frequency Selection */}
          <div className="config-section">
            <label className="config-label">Repeat</label>
            <div className="frequency-buttons">
              {(["daily", "weekly", "monthly", "yearly"] as const).map(
                (freq) => (
                  <button
                    key={freq}
                    type="button"
                    onClick={() => handleFrequencyChange(freq)}
                    className={`freq-btn ${
                      value.frequency === freq ? "active" : ""
                    }`}
                  >
                    {freq.charAt(0).toUpperCase() + freq.slice(1)}
                  </button>
                )
              )}
            </div>
          </div>

          {/* Interval Configuration */}
          <div className="config-section">
            <label className="config-label">Every</label>
            <div className="interval-input">
              <input
                type="number"
                min="1"
                max="365"
                value={value.interval}
                onChange={(e) =>
                  handleIntervalChange(parseInt(e.target.value, 10))
                }
                className="interval-number"
              />
              <span className="interval-unit">
                {value.frequency === "daily" && "day(s)"}
                {value.frequency === "weekly" && "week(s)"}
                {value.frequency === "monthly" && "month(s)"}
                {value.frequency === "yearly" && "year(s)"}
              </span>
            </div>
          </div>

          {/* End Condition */}
          <div className="config-section">
            <label className="config-label">Ends</label>
            <div className="end-condition">
              <label className="end-option">
                <input
                  type="radio"
                  name="end-condition"
                  checked={!!value.occurrenceCount}
                  onChange={() => handleEndConditionChange("count", "10")}
                />
                <span>After</span>
                <input
                  type="number"
                  min="1"
                  max="1000"
                  value={value.occurrenceCount || 10}
                  onChange={(e) =>
                    handleEndConditionChange("count", e.target.value)
                  }
                  disabled={!value.occurrenceCount}
                  className="end-input"
                />
                <span>occurrences</span>
              </label>

              <label className="end-option">
                <input
                  type="radio"
                  name="end-condition"
                  checked={!!value.endDate}
                  onChange={() => {
                    const futureDate = new Date();
                    futureDate.setMonth(futureDate.getMonth() + 1);
                    handleEndConditionChange("date", futureDate.toISOString());
                  }}
                />
                <span>On</span>
                <input
                  type="date"
                  value={
                    value.endDate
                      ? new Date(value.endDate).toISOString().split("T")[0]
                      : ""
                  }
                  onChange={(e) =>
                    handleEndConditionChange("date", e.target.value)
                  }
                  disabled={!value.endDate}
                  className="end-input"
                />
              </label>
            </div>
          </div>

          {/* Recurrence Preview */}
          <div className="recurrence-preview">
            <span className="preview-icon">🔄</span>
            <span className="preview-text">{getRecurrenceDescription()}</span>
          </div>
        </div>
      )}

      <style jsx>{`
        .recurrence-selector {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .recurrence-toggle {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
        }

        .recurrence-toggle input[type="checkbox"] {
          width: 18px;
          height: 18px;
          cursor: pointer;
        }

        .toggle-label {
          font-size: 14px;
          font-weight: 500;
          color: #374151;
        }

        .recurrence-config {
          padding: 16px;
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .config-section {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .config-label {
          font-size: 13px;
          font-weight: 600;
          color: #6b7280;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .frequency-buttons {
          display: flex;
          gap: 8px;
        }

        .freq-btn {
          flex: 1;
          padding: 8px 12px;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 500;
          color: #6b7280;
          cursor: pointer;
          transition: all 0.2s;
        }

        .freq-btn:hover {
          border-color: #d1d5db;
          background: #f9fafb;
        }

        .freq-btn.active {
          background: #3b82f6;
          border-color: #3b82f6;
          color: white;
        }

        .interval-input {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .interval-number {
          width: 80px;
          padding: 8px 12px;
          border: 2px solid #e5e7eb;
          border-radius: 6px;
          font-size: 14px;
          color: #1f2937;
        }

        .interval-number:focus {
          outline: none;
          border-color: #3b82f6;
        }

        .interval-unit {
          font-size: 14px;
          color: #6b7280;
        }

        .end-condition {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .end-option {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
        }

        .end-option input[type="radio"] {
          width: 16px;
          height: 16px;
          cursor: pointer;
        }

        .end-option span {
          font-size: 14px;
          color: #374151;
        }

        .end-input {
          padding: 6px 10px;
          border: 2px solid #e5e7eb;
          border-radius: 6px;
          font-size: 14px;
          color: #1f2937;
        }

        .end-input:disabled {
          background: #f3f4f6;
          cursor: not-allowed;
        }

        .end-input:focus:not(:disabled) {
          outline: none;
          border-color: #3b82f6;
        }

        .recurrence-preview {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px;
          background: #dbeafe;
          border: 1px solid #93c5fd;
          border-radius: 6px;
          margin-top: 8px;
        }

        .preview-icon {
          font-size: 18px;
        }

        .preview-text {
          font-size: 14px;
          font-weight: 500;
          color: #1e40af;
        }

        @media (max-width: 640px) {
          .frequency-buttons {
            flex-wrap: wrap;
          }

          .freq-btn {
            flex: 1 1 calc(50% - 4px);
          }
        }
      `}</style>
    </div>
  );
};

export default RecurrenceSelector;
