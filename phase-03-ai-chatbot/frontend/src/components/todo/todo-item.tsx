'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Task } from '@/types/todo';
import { cn } from '@/lib/utils';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Trash2, Edit2, Clock, CheckCircle2 } from 'lucide-react';

interface TodoItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (task: Task) => void;
}

const priorityColors = {
  1: 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300 border-blue-300 dark:border-blue-700',
  2: 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300 border-green-300 dark:border-green-700',
  3: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300 border-yellow-300 dark:border-yellow-700',
  4: 'bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300 border-orange-300 dark:border-orange-700',
  5: 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300 border-red-300 dark:border-red-700',
};

export function TodoItem({ task, onToggle, onDelete, onEdit }: TodoItemProps) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9, x: -100 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={cn(
        "group relative flex items-start gap-4 p-5 rounded-2xl border-2 bg-white dark:bg-neutral-900 transition-all duration-300 hover:shadow-xl hover:scale-[1.02] hover:border-blue-300 dark:hover:border-blue-700",
        task.completed && "opacity-70 bg-neutral-50 dark:bg-neutral-900/50"
      )}
    >
      {/* Completion indicator */}
      {task.completed && (
        <div className="absolute top-3 right-3">
          <CheckCircle2 className="w-5 h-5 text-green-500 animate-in zoom-in duration-300" />
        </div>
      )}

      <div className="pt-1 cursor-pointer" onClick={() => onToggle(task.id)}>
        <Checkbox
          checked={task.completed}
          onCheckedChange={() => onToggle(task.id)}
          className="w-5 h-5 cursor-pointer transition-transform duration-200 hover:scale-110"
        />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2">
          <h3 className={cn(
            "font-bold text-lg truncate transition-all duration-300",
            task.completed ? "line-through text-neutral-500 dark:text-neutral-600" : "text-neutral-900 dark:text-neutral-100"
          )}>
            {task.title}
          </h3>
          <span className={cn(
            "text-[10px] px-2.5 py-1 rounded-full font-bold uppercase tracking-wider border",
            priorityColors[task.priority as keyof typeof priorityColors]
          )}>
            P{task.priority}
          </span>
        </div>

        {task.description && (
          <p className={cn(
            "text-sm mb-3 line-clamp-2 transition-all duration-300",
            task.completed ? "line-through text-neutral-400 dark:text-neutral-600" : "text-neutral-600 dark:text-neutral-400"
          )}>
            {task.description}
          </p>
        )}

        <div className="flex items-center gap-4 text-[11px] text-neutral-500 dark:text-neutral-500 font-medium">
          <span className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            {new Date(task.createdAt).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            })}
          </span>
          {task.status === 'completed' && (
            <span className="flex items-center gap-1 text-green-600 dark:text-green-400 font-bold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Completed
            </span>
          )}
        </div>
      </div>

      <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-all duration-300 transform group-hover:translate-x-0 translate-x-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onEdit(task)}
          className="h-9 w-9 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-950 hover:text-blue-600 dark:hover:text-blue-400 transition-all duration-300 cursor-pointer transform hover:scale-110"
        >
          <Edit2 className="w-4 h-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onDelete(task.id)}
          className="h-9 w-9 rounded-lg hover:bg-red-100 dark:hover:bg-red-950 hover:text-red-600 dark:hover:text-red-400 transition-all duration-300 cursor-pointer transform hover:scale-110"
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </motion.div>
  );
}
