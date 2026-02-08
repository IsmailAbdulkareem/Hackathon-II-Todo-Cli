'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { TaskCreate, PriorityLevel, RecurrencePattern } from '@/types/todo';
import { Plus, Edit2, Loader2, Calendar, Tag, Repeat, Bell } from 'lucide-react';

interface TodoFormProps {
  onSubmit: (data: TaskCreate) => void;
  initialData?: TaskCreate;
  isLoading?: boolean;
}

export function TodoForm({ onSubmit, initialData, isLoading = false }: TodoFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [priority, setPriority] = useState<PriorityLevel>(initialData?.priority || 'medium');
  const [dueDate, setDueDate] = useState(initialData?.due_date || '');
  const [tags, setTags] = useState<string[]>(initialData?.tags || []);
  const [tagInput, setTagInput] = useState('');
  const [recurrence, setRecurrence] = useState<RecurrencePattern>(initialData?.recurrence || 'none');
  const [reminderOffset, setReminderOffset] = useState(initialData?.reminder_offset_minutes || 0);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || isLoading) return;

    onSubmit({
      title: title.trim(),
      description: description.trim() || null,
      priority,
      due_date: dueDate || null,
      tags: tags.length > 0 ? tags : [],
      recurrence,
      reminder_offset_minutes: reminderOffset,
    });

    if (!initialData) {
      setTitle('');
      setDescription('');
      setPriority('medium');
      setDueDate('');
      setTags([]);
      setRecurrence('none');
      setReminderOffset(0);
      setShowAdvanced(false);
    }
  };

  const handleAddTag = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      const newTag = tagInput.trim().toLowerCase();
      if (!tags.includes(newTag) && tags.length < 20) {
        setTags([...tags, newTag]);
        setTagInput('');
      }
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex gap-3">
        <Input
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={500}
          disabled={isLoading}
          className="flex-1 h-12 text-base border-2 focus:border-blue-500 dark:focus:border-blue-400 transition-all duration-300"
        />
        <Button
          type="submit"
          disabled={!title.trim() || isLoading}
          className="h-12 px-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg shadow-lg shadow-blue-500/50 dark:shadow-blue-500/30 transition-all duration-300 transform hover:scale-105 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              {initialData ? 'Updating...' : 'Adding...'}
            </>
          ) : (
            <>
              {initialData ? <Edit2 className="w-4 h-4 mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
              {initialData ? 'Update Task' : 'Add Task'}
            </>
          )}
        </Button>
      </div>

      <div className="flex gap-4 items-center">
        <Input
          placeholder="Optional description (add more details...)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={2000}
          disabled={isLoading}
          className="text-sm flex-1 border-2 focus:border-purple-500 dark:focus:border-purple-400 transition-all duration-300"
        />
      </div>

      <div className="flex gap-4 items-center flex-wrap">
        <div className="flex items-center gap-2 bg-neutral-100 dark:bg-neutral-800 px-4 py-2 rounded-lg">
          <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300 whitespace-nowrap">Priority:</label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as PriorityLevel)}
            disabled={isLoading}
            className="flex h-9 rounded-md border-2 border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-1 text-sm font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer transition-all duration-300"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div className="flex items-center gap-2 bg-neutral-100 dark:bg-neutral-800 px-4 py-2 rounded-lg">
          <Calendar className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />
          <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300 whitespace-nowrap">Due Date:</label>
          <input
            type="datetime-local"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            disabled={isLoading}
            className="flex h-9 rounded-md border-2 border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-1 text-sm font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer transition-all duration-300"
          />
        </div>

        <Button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          variant="outline"
          className="text-xs"
        >
          {showAdvanced ? 'Hide' : 'Show'} Advanced Options
        </Button>
      </div>

      {showAdvanced && (
        <div className="space-y-3 p-4 bg-neutral-50 dark:bg-neutral-900 rounded-lg border-2 border-neutral-200 dark:border-neutral-700">
          <div className="flex items-center gap-2">
            <Tag className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />
            <label className="text-sm font-semibold text-neutral-700 dark:text-neutral-300">Tags:</label>
            <Input
              placeholder="Type tag and press Enter (max 20)"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleAddTag}
              disabled={isLoading || tags.length >= 20}
              maxLength={50}
              className="flex-1 h-9 text-sm"
            />
          </div>
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs font-medium rounded-full"
                >
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}

          <div className="flex items-center gap-2">
            <Repeat className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />
            <label className="text-sm font-semibold text-neutral-700 dark:text-neutral-300">Recurrence:</label>
            <select
              value={recurrence}
              onChange={(e) => setRecurrence(e.target.value as RecurrencePattern)}
              disabled={isLoading}
              className="flex h-9 rounded-md border-2 border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-1 text-sm font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer transition-all duration-300"
            >
              <option value="none">None</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />
            <label className="text-sm font-semibold text-neutral-700 dark:text-neutral-300">Reminder (minutes before due):</label>
            <input
              type="number"
              value={reminderOffset}
              onChange={(e) => setReminderOffset(Number(e.target.value))}
              disabled={isLoading || !dueDate}
              min="0"
              max="43200"
              className="flex h-9 w-24 rounded-md border-2 border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-1 text-sm font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
            />
            <span className="text-xs text-neutral-500 dark:text-neutral-400">
              {!dueDate && '(Set due date first)'}
            </span>
          </div>
        </div>
      )}
    </form>
  );
}
