'use client';

import { useTodos } from '@/hooks/use-todos';
import { TodoForm } from '@/components/todo/todo-form';
import { TodoList } from '@/components/todo/todo-list';
import { Layout, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Task } from '@/types/todo';
import { authService } from '@/lib/auth-service';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();
  const { tasks, addTask, updateTask, toggleTask, deleteTask, isInitialized } = useTodos();
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication on mount
  useEffect(() => {
    setIsAuthenticated(authService.isAuthenticated());
  }, []);

  const handleLogout = () => {
    authService.signOut();
    setIsAuthenticated(false);
    window.location.reload(); // Reload to switch to local storage mode
  };

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const handleFormSubmit = (data: any) => {
    if (editingTask) {
      updateTask(editingTask.id, data);
      setEditingTask(null);
    } else {
      addTask(data);
    }
  };

  return (
    <main className="min-h-screen bg-neutral-50 dark:bg-neutral-950 p-4 md:p-8">
      <div className="max-w-3xl mx-auto space-y-8">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary rounded-lg text-primary-foreground shadow-lg">
              <Layout className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Task Manager</h1>
              <p className="text-sm text-muted-foreground">
                Manage your tasks efficiently
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end">
              <span className="text-3xl font-black text-primary/10 select-none">PHASE II</span>
              <div className="px-2 py-0.5 bg-neutral-200 dark:bg-neutral-800 rounded font-mono text-[10px] font-bold">
                v1.0.0-frontend
              </div>
            </div>
            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition"
              >
                Logout
              </button>
            ) : (
              <Link
                href="/login"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
              >
                Login
              </Link>
            )}
          </div>
        </header>

        {!isAuthenticated && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-yellow-900 dark:text-yellow-100 mb-1">
                You're using local storage mode
              </h3>
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                Your tasks are saved locally in your browser. To sync across devices and keep your tasks safe,{' '}
                <Link href="/login" className="underline font-medium hover:text-yellow-900 dark:hover:text-yellow-100">
                  login to your account
                </Link>
                {' '}or{' '}
                <Link href="/register" className="underline font-medium hover:text-yellow-900 dark:hover:text-yellow-100">
                  create a new account
                </Link>
                .
              </p>
            </div>
          </div>
        )}

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              {editingTask ? 'Edit Task' : 'Add New Task'}
            </h2>
            {editingTask && (
              <button
                onClick={() => setEditingTask(null)}
                className="text-xs text-muted-foreground hover:underline"
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
          />
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              Your Tasks
              <span className="px-2 py-0.5 bg-neutral-200 dark:bg-neutral-800 rounded-full text-xs">
                {tasks.length}
              </span>
            </h2>
          </div>
          <TodoList
            tasks={tasks}
            onToggle={toggleTask}
            onDelete={deleteTask}
            onEdit={setEditingTask}
          />
        </section>
      </div>
    </main>
  );
}
