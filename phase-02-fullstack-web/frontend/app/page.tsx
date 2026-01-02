'use client';

import { useTodos } from '@/hooks/use-todos';
import { TodoForm } from '@/components/todo/todo-form';
import { TodoList } from '@/components/todo/todo-list';
import { Layout } from 'lucide-react';

export default function Home() {
  const { tasks, addTask, toggleTask, deleteTask, isInitialized } = useTodos();

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

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
              <p className="text-sm text-muted-foreground">Manage your tasks with Spec-Driven precision</p>
            </div>
          </div>

          <div className="flex flex-col items-end">
            <span className="text-3xl font-black text-primary/10 select-none">PHASE II</span>
            <div className="px-2 py-0.5 bg-neutral-200 dark:bg-neutral-800 rounded font-mono text-[10px] font-bold">
              v1.0.0-frontend
            </div>
          </div>
        </header>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              Add New Task
            </h2>
          </div>
          <TodoForm onSubmit={addTask} />
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
            onEdit={(task) => console.log('Edit', task)}
          />
        </section>
      </div>
    </main>
  );
}
