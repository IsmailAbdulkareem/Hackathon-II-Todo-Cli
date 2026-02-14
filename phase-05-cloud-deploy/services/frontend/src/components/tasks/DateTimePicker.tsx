"use client";

import React from "react";

/**
 * DateTimePicker Component
 *
 * Provides a user-friendly interface for selecting date and time for task due dates.
 * Supports both date-only and date+time selection modes.
 *
 * Features:
 * - Native HTML5 datetime-local input with fallback
 * - Clear button to remove due date
 * - Validation for past dates
 * - Accessible labels and error messages
 * - Responsive design
 */

export interface DateTimePickerProps {
  /** Current selected date/time value (ISO 8601 string) */
  value?: string;
  /** Callback when date/time changes */
  onChange: (value: string | null) => void;
  /** Label text for the input */
  label?: string;
  /** Whether the field is required */
  required?: boolean;
  /** Whether to include time selection (default: true) */
  includeTime?: boolean;
  /** Minimum allowed date (ISO 8601 string) */
  minDate?: string;
  /** Error message to display */
  error?: string;
  /** Additional CSS classes */
  className?: string;
}

export const DateTimePicker: React.FC<DateTimePickerProps> = ({
  value,
  onChange,
  label = "Due Date",
  required = false,
  includeTime = true,
  minDate,
  error,
  className = "",
}) => {
  // Format value for datetime-local input (YYYY-MM-DDTHH:mm)
  const formatForInput = (isoString: string | undefined): string => {
    if (!isoString) return "";

    try {
      const date = new Date(isoString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const day = String(date.getDate()).padStart(2, "0");
      const hours = String(date.getHours()).padStart(2, "0");
      const minutes = String(date.getMinutes()).padStart(2, "0");

      if (includeTime) {
        return `${year}-${month}-${day}T${hours}:${minutes}`;
      } else {
        return `${year}-${month}-${day}`;
      }
    } catch (e) {
      return "";
    }
  };

  // Format minimum date for input
  const formattedMinDate = minDate ? formatForInput(minDate) : undefined;

  // Handle input change
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;

    if (!inputValue) {
      onChange(null);
      return;
    }

    try {
      // Convert to ISO 8601 string
      const date = new Date(inputValue);
      onChange(date.toISOString());
    } catch (e) {
      // Invalid date, ignore
      console.error("Invalid date format:", e);
    }
  };

  // Handle clear button
  const handleClear = () => {
    onChange(null);
  };

  const inputType = includeTime ? "datetime-local" : "date";
  const formattedValue = formatForInput(value);

  return (
    <div className={`date-time-picker ${className}`}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="flex items-center gap-2">
        <input
          type={inputType}
          value={formattedValue}
          onChange={handleChange}
          min={formattedMinDate}
          required={required}
          className={`
            flex-1 px-3 py-2 border rounded-md shadow-sm
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            ${error ? "border-red-500" : "border-gray-300"}
            disabled:bg-gray-100 disabled:cursor-not-allowed
          `}
        />

        {value && (
          <button
            type="button"
            onClick={handleClear}
            className="
              px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300
              rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500
            "
            aria-label="Clear due date"
          >
            Clear
          </button>
        )}
      </div>

      {error && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {!error && value && (
        <p className="mt-1 text-xs text-gray-500">
          {includeTime ? "Date and time selected" : "Date selected"}
        </p>
      )}
    </div>
  );
};

/**
 * Quick date preset buttons for common due date selections
 */
export interface QuickDatePresetsProps {
  /** Callback when a preset is selected */
  onSelect: (date: Date) => void;
  /** Additional CSS classes */
  className?: string;
}

export const QuickDatePresets: React.FC<QuickDatePresetsProps> = ({
  onSelect,
  className = "",
}) => {
  const presets = [
    { label: "Today", hours: 0 },
    { label: "Tomorrow", hours: 24 },
    { label: "In 3 days", hours: 72 },
    { label: "Next week", hours: 168 },
  ];

  const handlePresetClick = (hours: number) => {
    const date = new Date();
    date.setHours(date.getHours() + hours);
    onSelect(date);
  };

  return (
    <div className={`quick-date-presets ${className}`}>
      <p className="text-xs font-medium text-gray-700 mb-2">Quick select:</p>
      <div className="flex flex-wrap gap-2">
        {presets.map((preset) => (
          <button
            key={preset.label}
            type="button"
            onClick={() => handlePresetClick(preset.hours)}
            className="
              px-2 py-1 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200
              rounded hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500
            "
          >
            {preset.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default DateTimePicker;
