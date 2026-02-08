'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { API_CONFIG } from '@/lib/api-config';
import { authService } from '@/lib/auth-service';

export interface NotificationEvent {
  type: 'reminder' | 'heartbeat' | 'connected';
  data: {
    task_id?: string;
    title?: string;
    message?: string;
    timestamp: string;
    user_id?: string;
    connection_id?: string;
  };
}

export interface UseNotificationsReturn {
  notifications: NotificationEvent[];
  isConnected: boolean;
  error: string | null;
  clearNotifications: () => void;
  removeNotification: (index: number) => void;
}

export function useNotifications(): UseNotificationsReturn {
  const [notifications, setNotifications] = useState<NotificationEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    try {
      const token = authService.getToken();
      if (!token) {
        setError('Not authenticated');
        return;
      }

      // Close existing connection if any
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Create SSE connection with auth token
      const baseUrl = API_CONFIG.BASE_URL;
      const endpoint = API_CONFIG.ENDPOINTS.NOTIFICATIONS_STREAM();
      const url = `${baseUrl}${endpoint}`;

      // EventSource doesn't support custom headers, so we pass token as query param
      const urlWithAuth = `${url}?token=${encodeURIComponent(token)}`;

      const eventSource = new EventSource(urlWithAuth);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('SSE connection opened');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      eventSource.addEventListener('connected', (event) => {
        const data = JSON.parse(event.data);
        console.log('SSE connected:', data);
      });

      eventSource.addEventListener('reminder', (event) => {
        const data = JSON.parse(event.data);
        console.log('Reminder received:', data);

        const notification: NotificationEvent = {
          type: 'reminder',
          data: {
            task_id: data.task_id,
            title: data.title,
            message: data.message,
            timestamp: data.timestamp || new Date().toISOString(),
          },
        };

        setNotifications((prev) => [...prev, notification]);
      });

      eventSource.addEventListener('heartbeat', (event) => {
        // Heartbeat received, connection is alive
        console.log('Heartbeat received');
      });

      eventSource.onerror = (event) => {
        console.error('SSE error:', event);
        setIsConnected(false);

        // Close the connection
        eventSource.close();

        // Attempt to reconnect with exponential backoff
        const maxAttempts = 5;
        const baseDelay = 1000;
        const maxDelay = 30000;

        if (reconnectAttemptsRef.current < maxAttempts) {
          const delay = Math.min(
            baseDelay * Math.pow(2, reconnectAttemptsRef.current),
            maxDelay
          );

          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxAttempts})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, delay);
        } else {
          setError('Failed to connect to notification service. Please refresh the page.');
        }
      };
    } catch (err) {
      console.error('Failed to establish SSE connection:', err);
      setError('Failed to connect to notification service');
      setIsConnected(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    setIsConnected(false);
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const removeNotification = useCallback((index: number) => {
    setNotifications((prev) => prev.filter((_, i) => i !== index));
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    notifications,
    isConnected,
    error,
    clearNotifications,
    removeNotification,
  };
}
