/**
 * React hooks for real-time task synchronization.
 *
 * Provides hooks for:
 * - Real-time sync connection management
 * - Task list with automatic updates
 * - Sync state monitoring
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { getSyncService, stopSyncService, SyncEvent, TaskUpdateEvent } from '../services/realtime';
import { Task } from '../lib/types';

/**
 * Hook for managing real-time sync connection.
 */
export function useRealtimeSync(userId: string, enabled: boolean = true) {
  const [connected, setConnected] = useState(false);
  const [mode, setMode] = useState<'websocket' | 'polling' | 'disconnected'>('disconnected');
  const [lastSync, setLastSync] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const syncServiceRef = useRef(getSyncService(userId));

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const syncService = syncServiceRef.current;

    // Subscribe to connection events
    const unsubscribeConnected = syncService.on('connected', (event: SyncEvent) => {
      setConnected(true);
      setMode(syncService.getConnectionMode());
      setError(null);
      console.log('Sync connected:', event);
    });

    const unsubscribeDisconnected = syncService.on('disconnected', (event: SyncEvent) => {
      setConnected(false);
      setMode('disconnected');
      console.log('Sync disconnected:', event);
    });

    const unsubscribeError = syncService.on('error', (event: SyncEvent) => {
      setError(event.data?.error || 'Sync error occurred');
      console.error('Sync error:', event);
    });

    // Start sync
    syncService.start();

    // Cleanup on unmount
    return () => {
      unsubscribeConnected();
      unsubscribeDisconnected();
      unsubscribeError();
      syncService.stop();
    };
  }, [userId, enabled]);

  const start = useCallback(async () => {
    await syncServiceRef.current.start();
  }, []);

  const stop = useCallback(() => {
    syncServiceRef.current.stop();
  }, []);

  return {
    connected,
    mode,
    lastSync,
    error,
    start,
    stop,
  };
}

/**
 * Hook for managing tasks with real-time updates.
 */
export function useTasksWithSync(
  userId: string,
  initialTasks: Task[] = [],
  enableSync: boolean = true
) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const syncServiceRef = useRef(getSyncService(userId));

  // Update tasks when initial tasks change
  useEffect(() => {
    setTasks(initialTasks);
  }, [initialTasks]);

  // Handle task updates from sync
  useEffect(() => {
    if (!enableSync) {
      return;
    }

    const syncService = syncServiceRef.current;

    const unsubscribe = syncService.on('task_update', (event: SyncEvent) => {
      const updateEvent = event.data as TaskUpdateEvent;

      if (!updateEvent || !updateEvent.task) {
        return;
      }

      const { event: eventType, task } = updateEvent;

      setTasks((prevTasks) => {
        switch (eventType) {
          case 'created':
            // Add new task if not already present
            if (!prevTasks.find((t) => t.id === task.id)) {
              return [...prevTasks, task];
            }
            return prevTasks;

          case 'updated':
          case 'completed':
            // Update existing task
            return prevTasks.map((t) => (t.id === task.id ? task : t));

          case 'deleted':
            // Remove deleted task
            return prevTasks.filter((t) => t.id !== task.id);

          default:
            return prevTasks;
        }
      });
    });

    return () => {
      unsubscribe();
    };
  }, [userId, enableSync]);

  // Optimistic update helpers
  const optimisticUpdate = useCallback((taskId: string, updates: Partial<Task>) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.id === taskId ? { ...task, ...updates } : task
      )
    );
  }, []);

  const optimisticAdd = useCallback((task: Task) => {
    setTasks((prevTasks) => [...prevTasks, task]);
  }, []);

  const optimisticRemove = useCallback((taskId: string) => {
    setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
  }, []);

  return {
    tasks,
    setTasks,
    optimisticUpdate,
    optimisticAdd,
    optimisticRemove,
  };
}

/**
 * Hook for monitoring sync status.
 */
export function useSyncStatus(userId: string) {
  const [status, setStatus] = useState<{
    connected: boolean;
    mode: 'websocket' | 'polling' | 'disconnected';
    reconnecting: boolean;
  }>({
    connected: false,
    mode: 'disconnected',
    reconnecting: false,
  });

  const syncServiceRef = useRef(getSyncService(userId));

  useEffect(() => {
    const syncService = syncServiceRef.current;

    const unsubscribeConnected = syncService.on('connected', () => {
      setStatus({
        connected: true,
        mode: syncService.getConnectionMode(),
        reconnecting: false,
      });
    });

    const unsubscribeDisconnected = syncService.on('disconnected', () => {
      setStatus({
        connected: false,
        mode: 'disconnected',
        reconnecting: true,
      });
    });

    // Check initial status
    setStatus({
      connected: syncService.isConnected(),
      mode: syncService.getConnectionMode(),
      reconnecting: false,
    });

    return () => {
      unsubscribeConnected();
      unsubscribeDisconnected();
    };
  }, [userId]);

  return status;
}

/**
 * Hook for task update notifications.
 */
export function useTaskUpdateNotifications(
  userId: string,
  onTaskUpdate?: (event: TaskUpdateEvent) => void
) {
  const syncServiceRef = useRef(getSyncService(userId));

  useEffect(() => {
    if (!onTaskUpdate) {
      return;
    }

    const syncService = syncServiceRef.current;

    const unsubscribe = syncService.on('task_update', (event: SyncEvent) => {
      const updateEvent = event.data as TaskUpdateEvent;
      if (updateEvent) {
        onTaskUpdate(updateEvent);
      }
    });

    return () => {
      unsubscribe();
    };
  }, [userId, onTaskUpdate]);
}

/**
 * Hook for cleanup on unmount.
 */
export function useSyncCleanup() {
  useEffect(() => {
    return () => {
      stopSyncService();
    };
  }, []);
}

export default {
  useRealtimeSync,
  useTasksWithSync,
  useSyncStatus,
  useTaskUpdateNotifications,
  useSyncCleanup,
};
