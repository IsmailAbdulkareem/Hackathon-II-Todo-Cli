'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { TaskCreate } from '@/types/todo';
import { Plus, Edit2 } from 'lucide-react';

interface TodoFormProps {
  onSubmit: (data: TaskCreate) => void;
  initialData?: TaskCreate;
}

export function TodoForm({ onSubmit, initialData }: TodoFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [priority, setPriority] = useState(initialData?.priority || 1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    onSubmit({
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
    });

    setTitle('');
    setDescription('');
    setPriority(1);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-card p-4 rounded-lg border shadow-sm">
      <div className="flex gap-2">
        <Input
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={500}
          className="flex-1"
        />
        <Button type="submit" disabled={!title.trim()}>
          {initialData ? <Edit2 className="w-4 h-4 mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
          {initialData ? 'Update Task' : 'Add Task'}
        </Button>
      </div>

      <div className="flex gap-4 items-center">
        <Input
          placeholder="Optional description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={2000}
          className="text-sm"
        />
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-muted-foreground whitespace-nowrap">Priority:</label>
          <select
            value={priority}
            onChange={(e) => setPriority(Number(e.target.value))}
            className="flex h-9 w-20 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
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
