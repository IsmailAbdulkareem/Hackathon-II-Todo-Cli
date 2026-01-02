'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Task } from '@/types/todo';
import { cn } from '@/lib/utils';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Trash2, Edit2, Clock } from 'lucide-react';

interface TodoItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (task: Task) => void;
}

const priorityColors = {
  1: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  2: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  3: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  4: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  5: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
};

export function TodoItem({ task, onToggle, onDelete, onEdit }: TodoItemProps) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "group flex items-start gap-4 p-4 rounded-xl border bg-card transition-all hover:shadow-md",
        task.completed && "opacity-60 grayscale-[0.5]"
      )}
    >
      <div className="pt-1">
        <Checkbox
          checked={task.completed}
          onCheckedChange={() => onToggle(task.id)}
        />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h3 className={cn(
            "font-semibold text-lg truncate transition-all",
            task.completed && "line-through text-muted-foreground"
          )}>
            {task.title}
          </h3>
          <span className={cn(
            "text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider",
            priorityColors[task.priority as keyof typeof priorityColors]
          )}>
            P{task.priority}
          </span>
        </div>

        {task.description && (
          <p className={cn(
            "text-sm text-muted-foreground line-clamp-2",
            task.completed && "line-through"
          )}>
            {task.description}
          </p>
        )}

        <div className="flex items-center gap-4 mt-3 text-[10px] text-muted-foreground uppercase font-medium tracking-tight">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {new Date(task.createdAt).toLocaleDateString()}
          </span>
          {task.status === 'completed' && <span className="text-green-600 font-bold">Done</span>}
        </div>
      </div>

      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onEdit(task)}
          className="h-8 w-8"
        >
          <Edit2 className="w-4 h-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onDelete(task.id)}
          className="h-8 w-8 text-destructive hover:text-destructive"
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </motion.div>
  );
}
