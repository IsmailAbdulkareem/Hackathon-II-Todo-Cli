import { useState, useCallback, useEffect } from 'react';
import { Task, TaskCreate, TaskUpdate, TodoStatus } from '../types/todo';
import { apiService } from '@/lib/api-service';
import { Task as ApiTask } from '@/lib/api-config';

// Adapter: Convert backend API task to frontend Task type
function apiTaskToFrontendTask(apiTask: ApiTask): Task {
  return {
    id: apiTask.id,
    title: apiTask.title,
    description: apiTask.description,
    status: apiTask.completed ? 'completed' : 'pending',
    priority: 1, // Backend doesn't have priority yet (Phase 2)
    completed: apiTask.completed,
    createdAt: apiTask.created_at,
    updatedAt: apiTask.updated_at,
  };
}

export function useTodos() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load from backend API
  useEffect(() => {
    const loadTasks = async () => {
      try {
        const apiTasks = await apiService.getTasks();
        const frontendTasks = apiTasks.map(apiTaskToFrontendTask);
        setTasks(frontendTasks);
      } catch (error) {
        console.error('Failed to load tasks from API:', error);
        // Fallback to empty array on error
        setTasks([]);
      } finally {
        setIsInitialized(true);
      }
    };

    loadTasks();
  }, []);

  const addTask = useCallback(async (data: TaskCreate) => {
    try {
      const apiTask = await apiService.createTask({
        title: data.title,
        description: data.description || null,
      });
      const newTask = apiTaskToFrontendTask(apiTask);
      setTasks((prev) => [newTask, ...prev]);
      return newTask;
    } catch (error) {
      console.error('Failed to create task:', error);
      throw error;
    }
  }, []);

  const updateTask = useCallback(async (id: string, updates: TaskUpdate) => {
    try {
      const apiTask = await apiService.updateTask(id, {
        title: updates.title || '',
        description: updates.description || null,
      });
      const updatedTask = apiTaskToFrontendTask(apiTask);
      setTasks((prev) =>
        prev.map((task) => (task.id === id ? updatedTask : task))
      );
    } catch (error) {
      console.error('Failed to update task:', error);
      throw error;
    }
  }, []);

  const deleteTask = useCallback(async (id: string) => {
    try {
      await apiService.deleteTask(id);
      setTasks((prev) => prev.filter((task) => task.id !== id));
    } catch (error) {
      console.error('Failed to delete task:', error);
      throw error;
    }
  }, []);

  const toggleTask = useCallback(async (id: string) => {
    try {
      const apiTask = await apiService.toggleTaskCompletion(id);
      const updatedTask = apiTaskToFrontendTask(apiTask);
      setTasks((prev) =>
        prev.map((task) => (task.id === id ? updatedTask : task))
      );
    } catch (error) {
      console.error('Failed to toggle task:', error);
      throw error;
    }
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
