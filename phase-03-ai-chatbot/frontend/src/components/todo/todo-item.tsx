'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Task, PriorityLevel } from '@/types/todo';
import { cn } from '@/lib/utils';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Trash2, Edit2, Clock, CheckCircle2, ChevronDown, ChevronUp, Calendar, Tag, Repeat, Bell, AlertCircle } from 'lucide-react';

interface TodoItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (task: Task) => void;
}

const priorityConfig: Record<PriorityLevel, { color: string; label: string }> = {
  low: {
    color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300 border-blue-300 dark:border-blue-700',
    label: 'Low'
  },
  medium: {
    color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300 border-yellow-300 dark:border-yellow-700',
    label: 'Med'
  },
  high: {
    color: 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300 border-red-300 dark:border-red-700',
    label: 'High'
  },
};

const recurrenceLabels: Record<string, string> = {
  daily: 'Daily',
  weekly: 'Weekly',
  monthly: 'Monthly',
};

export function TodoItem({ task, onToggle, onDelete, onEdit }: TodoItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const descriptionLength = task.description?.length || 0;
  const shouldShowToggle = descriptionLength > 150;

  // Check if task is overdue
  const isOverdue = task.due_date && !task.completed && new Date(task.due_date) < new Date();

  // Format due date
  const formatDueDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays === -1) return 'Yesterday';
    if (diffDays < 0) return `${Math.abs(diffDays)} days ago`;
    if (diffDays <= 7) return `In ${diffDays} days`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9, x: -100 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={cn(
        "group relative flex items-start gap-4 p-5 rounded-2xl border-2 bg-white dark:bg-neutral-900 transition-all duration-300 hover:shadow-xl hover:scale-[1.02] hover:border-blue-300 dark:hover:border-blue-700",
        task.completed && "opacity-70 bg-neutral-50 dark:bg-neutral-900/50",
        isOverdue && "border-red-300 dark:border-red-700"
      )}
    >
      {/* Completion indicator */}
      {task.completed && (
        <div className="absolute top-3 right-3">
          <CheckCircle2 className="w-5 h-5 text-green-500 animate-in zoom-in duration-300" />
        </div>
      )}

      {/* Overdue indicator */}
      {isOverdue && (
        <div className="absolute top-3 right-3">
          <AlertCircle className="w-5 h-5 text-red-500 animate-pulse" />
        </div>
      )}

      <div className="pt-1">
        <Checkbox
          checked={task.completed}
          onCheckedChange={() => onToggle(task.id)}
          className="w-5 h-5 cursor-pointer transition-transform duration-200 hover:scale-110"
        />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <h3 className={cn(
            "font-bold text-lg transition-all duration-300",
            task.completed ? "line-through text-neutral-500 dark:text-neutral-600" : "text-neutral-900 dark:text-neutral-100"
          )}>
            {task.title}
          </h3>
          <span className={cn(
            "text-[10px] px-2.5 py-1 rounded-full font-bold uppercase tracking-wider border",
            priorityConfig[task.priority].color
          )}>
            {priorityConfig[task.priority].label}
          </span>
          {task.recurrence && task.recurrence !== 'none' && (
            <span className="flex items-center gap-1 text-[10px] px-2.5 py-1 rounded-full font-bold bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300 border border-purple-300 dark:border-purple-700">
              <Repeat className="w-3 h-3" />
              {recurrenceLabels[task.recurrence]}
            </span>
          )}
          {task.reminder_offset_minutes > 0 && task.due_date && (
            <span className="flex items-center gap-1 text-[10px] px-2.5 py-1 rounded-full font-bold bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300 border border-amber-300 dark:border-amber-700">
              <Bell className="w-3 h-3" />
              {task.reminder_offset_minutes}m
            </span>
          )}
        </div>

        {task.description && (
          <div className="mb-3">
            <p className={cn(
              "text-sm transition-all duration-300 whitespace-pre-wrap",
              task.completed ? "line-through text-neutral-400 dark:text-neutral-600" : "text-neutral-600 dark:text-neutral-400",
              !isExpanded && shouldShowToggle && "line-clamp-2"
            )}>
              {task.description}
            </p>
            {shouldShowToggle && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="mt-2 text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center gap-1 transition-colors"
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="w-3.5 h-3.5" />
                    Show less
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3.5 h-3.5" />
                    Show more
                  </>
                )}
              </button>
            )}
          </div>
        )}

        {/* Tags */}
        {task.tags && task.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {task.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 text-[10px] font-medium rounded-md border border-blue-200 dark:border-blue-800"
              >
                <Tag className="w-2.5 h-2.5" />
                {tag}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center gap-4 text-[11px] text-neutral-500 dark:text-neutral-500 font-medium flex-wrap">
          <span className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            {new Date(task.created_at).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            })}
          </span>
          {task.due_date && (
            <span className={cn(
              "flex items-center gap-1.5 font-semibold",
              isOverdue ? "text-red-600 dark:text-red-400" : "text-blue-600 dark:text-blue-400"
            )}>
              <Calendar className="w-3.5 h-3.5" />
              Due: {formatDueDate(task.due_date)}
            </span>
          )}
          {task.completed && (
            <span className="flex items-center gap-1 text-green-600 dark:text-green-400 font-bold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Completed
            </span>
          )}
        </div>
      </div>

      <div className="flex gap-2 transition-all duration-300">
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
