import { useState, useCallback, useEffect } from 'react';
import { Task, TaskCreate, TaskUpdate, TodoStatus } from '../types/todo';

const STORAGE_KEY = 'todo_app_tasks';

export function useTodos() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        setTasks(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to parse saved tasks', e);
      }
    }
    setIsInitialized(true);
  }, []);

  // Save to localStorage
  useEffect(() => {
    if (isInitialized) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    }
  }, [tasks, isInitialized]);

  const addTask = useCallback((data: TaskCreate) => {
    const newTask: Task = {
      id: crypto.randomUUID(),
      title: data.title,
      description: data.description || null,
      status: 'pending',
      priority: data.priority || 1,
      completed: false,
      createdAt: new Date().toISOString(),
      updatedAt: null,
    };
    setTasks((prev) => [newTask, ...prev]);
    return newTask;
  }, []);

  const updateTask = useCallback((id: string, updates: TaskUpdate) => {
    setTasks((prev) =>
      prev.map((task) => {
        if (task.id === id) {
          const status = updates.completed !== undefined
            ? (updates.completed ? 'completed' : 'pending')
            : (updates.status || task.status);

          return {
            ...task,
            ...updates,
            status: status as TodoStatus,
            completed: status === 'completed',
            updatedAt: new Date().toISOString(),
          };
        }
        return task;
      })
    );
  }, []);

  const deleteTask = useCallback((id: string) => {
    setTasks((prev) => prev.filter((task) => task.id !== id));
  }, []);

  const toggleTask = useCallback((id: string) => {
    setTasks((prev) =>
      prev.map((task) => {
        if (task.id === id) {
          const completed = !task.completed;
          return {
            ...task,
            completed,
            status: completed ? 'completed' : 'pending',
            updatedAt: new Date().toISOString(),
          };
        }
        return task;
      })
    );
  }, []);

  return {
    tasks,
    addTask,
    updateTask,
    deleteTask,
    toggleTask,
    isInitialized,
  };
}
