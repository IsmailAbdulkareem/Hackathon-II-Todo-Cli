'use client';

import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Task } from '@/types/todo';
import { TodoItem } from './todo-item';
import { ListTodo } from 'lucide-react';

interface TodoListProps {
  tasks: Task[];
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (task: Task) => void;
}

export function TodoList({ tasks, onToggle, onDelete, onEdit }: TodoListProps) {
  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-muted-foreground border-2 border-dashed rounded-2xl">
        <ListTodo className="w-12 h-12 mb-4 opacity-20" />
        <p className="font-medium">No tasks found</p>
        <p className="text-sm">Add your first task to get started!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <AnimatePresence mode="popLayout">
        {tasks.map((task) => (
          <TodoItem
            key={task.id}
            task={task}
            onToggle={onToggle}
            onDelete={onDelete}
            onEdit={onEdit}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
