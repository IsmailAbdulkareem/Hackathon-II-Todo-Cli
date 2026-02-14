"use client";

import React, { useState } from "react";

/**
 * ReminderSelector Component
 *
 * Allows users to select when they want to be reminded about a task.
 * Supports preset reminder times (15min, 1hr, 1day, 1week) and custom times.
 *
 * Features:
 * - Multiple reminder selection
 * - Preset reminder options
 * - Custom reminder time input
 * - Visual feedback for selected reminders
 * - Accessible keyboard navigation
 */

export type ReminderType = "15min" | "1hr" | "1day" | "1week" | "custom";

export interface Reminder {
  id?: string;
  type: ReminderType;
  scheduledTime?: string; // ISO 8601 string for custom reminders
}

export interface ReminderSelectorProps {
  /** Currently selected reminders */
  value: Reminder[];
  /** Callback when reminders change */
  onChange: (reminders: Reminder[]) => void;
  /** Task due date (required for calculating reminder times) */
  dueDate?: string;
  /** Whether reminders are disabled (e.g., no due date set) */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
}

const REMINDER_OPTIONS: Array<{
  type: ReminderType;
  label: string;
  description: string;
}> = [
  {
    type: "15min",
    label: "15 minutes before",
    description: "Get reminded 15 minutes before the due date",
  },
  {
    type: "1hr",
    label: "1 hour before",
    description: "Get reminded 1 hour before the due date",
  },
  {
    type: "1day",
    label: "1 day before",
    description: "Get reminded 1 day before the due date",
  },
  {
    type: "1week",
    label: "1 week before",
    description: "Get reminded 1 week before the due date",
  },
];

export const ReminderSelector: React.FC<ReminderSelectorProps> = ({
  value,
  onChange,
  dueDate,
  disabled = false,
  className = "",
}) => {
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [customTime, setCustomTime] = useState("");

  // Check if a reminder type is selected
  const isSelected = (type: ReminderType): boolean => {
    return value.some((r) => r.type === type);
  };

  // Toggle a preset reminder
  const toggleReminder = (type: ReminderType) => {
    if (disabled) return;

    if (isSelected(type)) {
      // Remove reminder
      onChange(value.filter((r) => r.type !== type));
    } else {
      // Add reminder
      onChange([...value, { type }]);
    }
  };

  // Add custom reminder
  const addCustomReminder = () => {
    if (!customTime || disabled) return;

    try {
      const date = new Date(customTime);
      onChange([
        ...value,
        {
          type: "custom",
          scheduledTime: date.toISOString(),
        },
      ]);

      // Reset custom input
      setCustomTime("");
      setShowCustomInput(false);
    } catch (e) {
      console.error("Invalid custom reminder time:", e);
    }
  };

  // Remove a specific reminder
  const removeReminder = (index: number) => {
    if (disabled) return;
    onChange(value.filter((_, i) => i !== index));
  };

  // Format custom reminder time for display
  const formatCustomTime = (isoString: string): string => {
    try {
      const date = new Date(isoString);
      return date.toLocaleString(undefined, {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
    } catch (e) {
      return "Invalid date";
    }
  };

  return (
    <div className={`reminder-selector ${className}`}>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Reminders
      </label>

      {!dueDate && (
        <p className="text-sm text-gray-500 mb-3">
          Set a due date to enable reminders
        </p>
      )}

      {/* Preset reminder options */}
      <div className="space-y-2 mb-4">
        {REMINDER_OPTIONS.map((option) => (
          <button
            key={option.type}
            type="button"
            onClick={() => toggleReminder(option.type)}
            disabled={disabled || !dueDate}
            className={`
              w-full text-left px-4 py-3 border rounded-lg transition-colors
              ${
                isSelected(option.type)
                  ? "bg-blue-50 border-blue-500 text-blue-900"
                  : "bg-white border-gray-300 text-gray-700 hover:bg-gray-50"
              }
              ${
                disabled || !dueDate
                  ? "opacity-50 cursor-not-allowed"
                  : "cursor-pointer"
              }
              focus:outline-none focus:ring-2 focus:ring-blue-500
            `}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="font-medium">{option.label}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {option.description}
                </div>
              </div>
              {isSelected(option.type) && (
                <svg
                  className="w-5 h-5 text-blue-600"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Custom reminder option */}
      {!showCustomInput && (
        <button
          type="button"
          onClick={() => setShowCustomInput(true)}
          disabled={disabled || !dueDate}
          className={`
            w-full px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200
            rounded-lg hover:bg-blue-100 transition-colors
            ${
              disabled || !dueDate
                ? "opacity-50 cursor-not-allowed"
                : "cursor-pointer"
            }
            focus:outline-none focus:ring-2 focus:ring-blue-500
          `}
        >
          + Add custom reminder
        </button>
      )}

      {/* Custom reminder input */}
      {showCustomInput && (
        <div className="mt-3 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom reminder time
          </label>
          <div className="flex gap-2">
            <input
              type="datetime-local"
              value={customTime}
              onChange={(e) => setCustomTime(e.target.value)}
              className="
                flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
              "
            />
            <button
              type="button"
              onClick={addCustomReminder}
              disabled={!customTime}
              className="
                px-4 py-2 text-sm font-medium text-white bg-blue-600
                rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
                focus:outline-none focus:ring-2 focus:ring-blue-500
              "
            >
              Add
            </button>
            <button
              type="button"
              onClick={() => {
                setShowCustomInput(false);
                setCustomTime("");
              }}
              className="
                px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300
                rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500
              "
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Selected reminders summary */}
      {value.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium text-gray-700 mb-2">
            Active reminders ({value.length}):
          </p>
          <div className="space-y-1">
            {value.map((reminder, index) => (
              <div
                key={index}
                className="flex items-center justify-between px-3 py-2 bg-blue-50 border border-blue-200 rounded-md"
              >
                <span className="text-sm text-blue-900">
                  {reminder.type === "custom" && reminder.scheduledTime
                    ? formatCustomTime(reminder.scheduledTime)
                    : REMINDER_OPTIONS.find((o) => o.type === reminder.type)
                        ?.label}
                </span>
                <button
                  type="button"
                  onClick={() => removeReminder(index)}
                  disabled={disabled}
                  className="
                    text-blue-600 hover:text-blue-800 focus:outline-none
                    disabled:opacity-50 disabled:cursor-not-allowed
                  "
                  aria-label="Remove reminder"
                >
                  <svg
                    className="w-4 h-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ReminderSelector;
