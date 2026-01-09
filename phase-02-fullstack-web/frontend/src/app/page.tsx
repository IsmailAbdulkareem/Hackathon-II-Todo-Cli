'use client';

import { useTodos } from '@/hooks/use-todos';
import { TodoForm } from '@/components/todo/todo-form';
import { TodoList } from '@/components/todo/todo-list';
import { Layout, AlertCircle, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Task } from '@/types/todo';
import { authService } from '@/lib/auth-service';
import Link from 'next/link';
import { ThemeToggle } from '@/components/theme-toggle';
import { UserProfile } from '@/components/user-profile';
import { MotivationalQuote } from '@/components/motivational-quote';
import { toast } from 'sonner';

export default function Home() {
  const { tasks, addTask, updateTask, toggleTask, deleteTask, isInitialized } = useTodos();
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Check authentication on mount
  useEffect(() => {
    setIsAuthenticated(authService.isAuthenticated());
  }, []);

  const handleLogout = () => {
    setIsAuthenticated(false);
    toast.success('Logged out successfully');
    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-neutral-950 dark:via-neutral-900 dark:to-neutral-950">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 text-blue-600 dark:text-blue-400 animate-spin mx-auto" />
          <p className="text-sm text-neutral-600 dark:text-neutral-400 animate-pulse">Loading your tasks...</p>
        </div>
      </div>
    );
  }

  const handleFormSubmit = async (data: any) => {
    setIsLoading(true);
    try {
      if (editingTask) {
        await updateTask(editingTask.id, data);
        setEditingTask(null);
        toast.success('Task updated successfully!', {
          description: 'Your changes have been saved.',
        });
      } else {
        await addTask(data);
        toast.success('Task created successfully!', {
          description: 'Keep up the great work!',
        });
      }
    } catch (error: any) {
      toast.error('Oops! Something went wrong', {
        description: error.message || 'Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (id: string) => {
    try {
      // Get the task BEFORE toggling to show correct message
      const task = tasks.find(t => t.id === id);
      const wasCompleted = task?.completed || false;

      await toggleTask(id);

      // Show message based on the OLD state (before toggle)
      if (!wasCompleted) {
        toast.success('Task completed! 🎉', {
          description: 'Great job on finishing this task!',
        });
      } else {
        toast.info('Task reopened', {
          description: 'Keep working on it!',
        });
      }
    } catch (error: any) {
      toast.error('Failed to update task', {
        description: error.message || 'Please try again.',
      });
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteTask(id);
      toast.success('Task deleted', {
        description: 'The task has been removed.',
      });
    } catch (error: any) {
      toast.error('Failed to delete task', {
        description: error.message || 'Please try again.',
      });
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-neutral-950 dark:via-neutral-900 dark:to-neutral-950 transition-colors duration-500">
      <div className="max-w-5xl mx-auto p-4 md:p-8 space-y-6">
        {/* Header Section */}
        <header className="space-y-4 animate-in fade-in slide-in-from-top duration-700">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-lg shadow-blue-500/50 dark:shadow-blue-500/30 transform hover:scale-110 transition-transform duration-300">
                <Layout className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Task Manager
                </h1>
                <p className="text-xs sm:text-sm text-neutral-600 dark:text-neutral-400">
                  Organize your life, one task at a time
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 sm:gap-3 w-full sm:w-auto justify-end">
              <ThemeToggle />
              {isAuthenticated ? (
                <UserProfile isAuthenticated={isAuthenticated} onLogout={handleLogout} />
              ) : (
                <Link
                  href="/login"
                  className="px-3 sm:px-4 py-2 text-sm bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium rounded-lg shadow-lg shadow-blue-500/50 dark:shadow-blue-500/30 transition-all duration-300 transform hover:scale-105 cursor-pointer whitespace-nowrap"
                >
                  Login
                </Link>
              )}
            </div>
          </div>

          {/* Motivational Quote */}
          <MotivationalQuote />

          {/* Warning Banner for Unauthenticated Users */}
          {!isAuthenticated && (
            <div className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-950/30 dark:to-orange-950/30 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4 flex items-start gap-3 animate-in fade-in slide-in-from-top duration-700 delay-150">
              <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-500 flex-shrink-0 mt-0.5 animate-pulse" />
              <div className="flex-1">
                <h3 className="font-semibold text-yellow-900 dark:text-yellow-100 mb-1">
                  You're using local storage mode
                </h3>
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  Your tasks are saved locally in your browser. To sync across devices and keep your tasks safe,{' '}
                  <Link href="/login" className="underline font-medium hover:text-yellow-900 dark:hover:text-yellow-100 cursor-pointer">
                    login to your account
                  </Link>
                  {' '}or{' '}
                  <Link href="/register" className="underline font-medium hover:text-yellow-900 dark:hover:text-yellow-100 cursor-pointer">
                    create a new account
                  </Link>
                  .
                </p>
              </div>
            </div>
          )}
        </header>

        {/* Add/Edit Task Section */}
        <section className="bg-white dark:bg-neutral-900 rounded-2xl shadow-xl border border-neutral-200 dark:border-neutral-800 p-6 space-y-4 animate-in fade-in slide-in-from-bottom duration-700 delay-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
              {editingTask ? '✏️ Edit Task' : '➕ Add New Task'}
            </h2>
            {editingTask && (
              <button
                onClick={() => setEditingTask(null)}
                className="text-sm text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100 underline cursor-pointer transition-colors duration-200"
              >
                Cancel Edit
              </button>
            )}
          </div>
          <TodoForm
            onSubmit={handleFormSubmit}
            initialData={editingTask ? {
              title: editingTask.title,
              description: editingTask.description || undefined,
              priority: editingTask.priority
            } : undefined}
            key={editingTask ? `edit-${editingTask.id}` : 'add-new'}
            isLoading={isLoading}
          />
        </section>

        {/* Tasks List Section */}
        <section className="bg-white dark:bg-neutral-900 rounded-2xl shadow-xl border border-neutral-200 dark:border-neutral-800 p-6 space-y-4 animate-in fade-in slide-in-from-bottom duration-700 delay-300">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
              📋 Your Tasks
              <span className="px-3 py-1 bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-950 dark:to-purple-950 text-blue-700 dark:text-blue-300 rounded-full text-sm font-bold">
                {tasks.length}
              </span>
            </h2>
          </div>
          <TodoList
            tasks={tasks}
            onToggle={handleToggle}
            onDelete={handleDelete}
            onEdit={setEditingTask}
          />
        </section>

        {/* Footer */}
        <footer className="text-center py-6 animate-in fade-in duration-700 delay-500">
          <p className="text-sm text-neutral-500 dark:text-neutral-400">
            Made with ❤️ using Spec-Driven Development
          </p>
        </footer>
      </div>
    </main>
  );
}
