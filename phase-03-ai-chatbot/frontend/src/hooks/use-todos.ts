import { useState, useCallback, useEffect } from 'react';
import { Task, TaskCreate, TaskUpdate, TodoStatus } from '../types/todo';
import { apiService } from '@/lib/api-service';
import { authService } from '@/lib/auth-service';
import { Task as ApiTask } from '@/lib/api-config';

const LOCAL_STORAGE_KEY = 'local_tasks';

// Adapter: Convert backend API task to frontend Task type
function apiTaskToFrontendTask(apiTask: ApiTask): Task {
  return {
    id: apiTask.id,
    user_id: apiTask.user_id,
    title: apiTask.title,
    description: apiTask.description,
    completed: apiTask.completed,
    created_at: apiTask.created_at,
    updated_at: apiTask.updated_at,
    due_date: apiTask.due_date || null,
    priority: apiTask.priority || 'medium',
    tags: apiTask.tags || [],
    recurrence: apiTask.recurrence || 'none',
    reminder_offset_minutes: apiTask.reminder_offset_minutes || 0,
  };
}

// Local storage helpers
function loadLocalTasks(): Task[] {
  if (typeof window === 'undefined') return [];
  try {
    const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Failed to load local tasks:', error);
    return [];
  }
}

function saveLocalTasks(tasks: Task[]): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(tasks));
  } catch (error) {
    console.error('Failed to save local tasks:', error);
  }
}

function generateId(): string {
  return `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export function useTodos() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Function to reload tasks
  const reloadTasks = useCallback(async () => {
    const authenticated = authService.isAuthenticated();
    if (authenticated) {
      // Load from backend API
      try {
        const apiTasks = await apiService.getTasks();
        const frontendTasks = apiTasks.map(apiTaskToFrontendTask);
        setTasks(frontendTasks);
      } catch (error) {
        console.error('Failed to load tasks from API:', error);
      }
    } else {
      // Load from local storage
      const localTasks = loadLocalTasks();
      setTasks(localTasks);
    }
  }, []);

  // Check authentication and load tasks
  useEffect(() => {
    const authenticated = authService.isAuthenticated();
    setIsAuthenticated(authenticated);

    const loadTasks = async () => {
      if (authenticated) {
        // Load from backend API
        try {
          const apiTasks = await apiService.getTasks();
          const frontendTasks = apiTasks.map(apiTaskToFrontendTask);
          setTasks(frontendTasks);
        } catch (error) {
          console.error('Failed to load tasks from API:', error);
          setTasks([]);
        }
      } else {
        // Load from local storage
        const localTasks = loadLocalTasks();
        setTasks(localTasks);
      }
      setIsInitialized(true);
    };

    loadTasks();

    // Listen for task refresh events from chat
    const handleTaskRefresh = () => {
      reloadTasks();
    };

    window.addEventListener('refreshTasks', handleTaskRefresh);

    // Auto-refresh tasks every 5 seconds when authenticated
    let refreshInterval: NodeJS.Timeout | null = null;
    if (authenticated) {
      refreshInterval = setInterval(() => {
        reloadTasks();
      }, 5000); // Refresh every 5 seconds
    }

    return () => {
      window.removeEventListener('refreshTasks', handleTaskRefresh);
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [reloadTasks]);

  const addTask = useCallback(async (data: TaskCreate) => {
    if (isAuthenticated) {
      // API mode
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
    } else {
      // Local storage mode
      const now = new Date().toISOString();
      const newTask: Task = {
        id: generateId(),
        title: data.title,
        description: data.description || '',
        status: 'pending',
        priority: data.priority || 1,
        completed: false,
        createdAt: now,
        updatedAt: now,
      };
      const updatedTasks = [newTask, ...tasks];
      setTasks(updatedTasks);
      saveLocalTasks(updatedTasks);
      return newTask;
    }
  }, [isAuthenticated, tasks]);

  const updateTask = useCallback(async (id: string, updates: TaskUpdate) => {
    if (isAuthenticated) {
      // API mode
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
    } else {
      // Local storage mode
      const updatedTasks = tasks.map((task) =>
        task.id === id
          ? {
              ...task,
              ...updates,
              updatedAt: new Date().toISOString(),
            }
          : task
      );
      setTasks(updatedTasks);
      saveLocalTasks(updatedTasks);
    }
  }, [isAuthenticated, tasks]);

  const deleteTask = useCallback(async (id: string) => {
    if (isAuthenticated) {
      // API mode
      try {
        await apiService.deleteTask(id);
        setTasks((prev) => prev.filter((task) => task.id !== id));
      } catch (error) {
        console.error('Failed to delete task:', error);
        throw error;
      }
    } else {
      // Local storage mode
      const updatedTasks = tasks.filter((task) => task.id !== id);
      setTasks(updatedTasks);
      saveLocalTasks(updatedTasks);
    }
  }, [isAuthenticated, tasks]);

  const toggleTask = useCallback(async (id: string) => {
    if (isAuthenticated) {
      // API mode
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
    } else {
      // Local storage mode
      const updatedTasks = tasks.map((task) =>
        task.id === id
          ? {
              ...task,
              completed: !task.completed,
              status: (!task.completed ? 'completed' : 'pending') as TodoStatus,
              updatedAt: new Date().toISOString(),
            }
          : task
      );
      setTasks(updatedTasks);
      saveLocalTasks(updatedTasks);
    }
  }, [isAuthenticated, tasks]);

  return {
    tasks,
    addTask,
    updateTask,
    deleteTask,
    toggleTask,
    isInitialized,
  };
}
