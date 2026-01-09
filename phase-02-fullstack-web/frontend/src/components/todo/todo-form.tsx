'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { TaskCreate } from '@/types/todo';
import { Plus, Edit2, Loader2 } from 'lucide-react';

interface TodoFormProps {
  onSubmit: (data: TaskCreate) => void;
  initialData?: TaskCreate;
  isLoading?: boolean;
}

export function TodoForm({ onSubmit, initialData, isLoading = false }: TodoFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [priority, setPriority] = useState(initialData?.priority || 1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || isLoading) return;

    onSubmit({
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
    });

    if (!initialData) {
      setTitle('');
      setDescription('');
      setPriority(1);
    }
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
        <div className="flex items-center gap-2 bg-neutral-100 dark:bg-neutral-800 px-4 py-2 rounded-lg">
          <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300 whitespace-nowrap">Priority:</label>
          <select
            value={priority}
            onChange={(e) => setPriority(Number(e.target.value))}
            disabled={isLoading}
            className="flex h-9 w-16 rounded-md border-2 border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-1 text-sm font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer transition-all duration-300"
          >
            {[1, 2, 3, 4, 5].map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
      </div>
    </form>
  );
}
