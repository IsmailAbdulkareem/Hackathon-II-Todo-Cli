/**
 * Real-time synchronization service for task updates.
 *
 * Provides two synchronization strategies:
 * 1. WebSocket: Real-time bidirectional communication (preferred)
 * 2. Polling: Fallback for environments without WebSocket support
 *
 * Features:
 * - Automatic reconnection on connection loss
 * - Exponential backoff for reconnection attempts
 * - Event-based API for task updates
 * - Graceful degradation to polling
 */

import { Task } from './api';

export type SyncEventType = 'connected' | 'disconnected' | 'task_update' | 'heartbeat' | 'error';

export interface SyncEvent {
  type: SyncEventType;
  data?: any;
  timestamp: string;
}

export interface TaskUpdateEvent {
  type: 'task_update';
  event: 'created' | 'updated' | 'deleted' | 'completed';
  task: Task;
  timestamp: string;
}

type SyncEventHandler = (event: SyncEvent) => void;

export class RealtimeSyncService {
  private userId: string;
  private ws: WebSocket | null = null;
  private pollingInterval: NodeJS.Timeout | null = null;
  private lastSyncTimestamp: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private eventHandlers: Map<SyncEventType, Set<SyncEventHandler>> = new Map();
  private isConnecting = false;
  private preferWebSocket = true;

  constructor(userId: string, preferWebSocket: boolean = true) {
    this.userId = userId;
    this.preferWebSocket = preferWebSocket;
  }

  /**
   * Start synchronization (WebSocket or polling).
   */
  async start(): Promise<void> {
    if (this.preferWebSocket && typeof WebSocket !== 'undefined') {
      await this.startWebSocket();
    } else {
      this.startPolling();
    }
  }

  /**
   * Stop synchronization and cleanup.
   */
  stop(): void {
    this.stopWebSocket();
    this.stopPolling();
    this.eventHandlers.clear();
  }

  /**
   * Subscribe to sync events.
   */
  on(eventType: SyncEventType, handler: SyncEventHandler): () => void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, new Set());
    }

    this.eventHandlers.get(eventType)!.add(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.eventHandlers.get(eventType);
      if (handlers) {
        handlers.delete(handler);
      }
    };
  }

  /**
   * Emit an event to all subscribers.
   */
  private emit(event: SyncEvent): void {
    const handlers = this.eventHandlers.get(event.type);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(event);
        } catch (error) {
          console.error('Error in sync event handler:', error);
        }
      });
    }
  }

  /**
   * Start WebSocket connection.
   */
  private async startWebSocket(): Promise<void> {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.isConnecting = true;

    try {
      const token = this.getAuthToken();
      const wsUrl = this.getWebSocketUrl();
      const url = `${wsUrl}/api/${this.userId}/sync${token ? `?token=${token}` : ''}`;

      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;

        this.emit({
          type: 'connected',
          timestamp: new Date().toISOString(),
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit({
          type: 'error',
          data: { error: 'WebSocket connection error' },
          timestamp: new Date().toISOString(),
        });
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnecting = false;
        this.ws = null;

        this.emit({
          type: 'disconnected',
          timestamp: new Date().toISOString(),
        });

        // Attempt reconnection
        this.scheduleReconnect();
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.isConnecting = false;
      // Fall back to polling
      this.startPolling();
    }
  }

  /**
   * Stop WebSocket connection.
   */
  private stopWebSocket(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Handle incoming WebSocket messages.
   */
  private handleWebSocketMessage(data: any): void {
    if (data.type === 'task_update') {
      this.emit({
        type: 'task_update',
        data,
        timestamp: data.timestamp || new Date().toISOString(),
      });
    } else if (data.type === 'heartbeat') {
      // Send pong response
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'pong' }));
      }
    } else if (data.type === 'connected') {
      console.log('WebSocket connection confirmed');
    }
  }

  /**
   * Schedule reconnection with exponential backoff.
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached, falling back to polling');
      this.startPolling();
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      this.startWebSocket();
    }, delay);
  }

  /**
   * Start polling for updates.
   */
  private startPolling(): void {
    if (this.pollingInterval) {
      return;
    }

    console.log('Starting polling mode');

    // Initial poll
    this.poll();

    // Poll every 5 seconds
    this.pollingInterval = setInterval(() => {
      this.poll();
    }, 5000);

    this.emit({
      type: 'connected',
      data: { mode: 'polling' },
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Stop polling.
   */
  private stopPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  /**
   * Poll for task updates.
   */
  private async poll(): Promise<void> {
    try {
      const response = await fetch(
        `${this.getApiBaseUrl()}/api/${this.userId}/sync/poll${
          this.lastSyncTimestamp ? `?since=${this.lastSyncTimestamp}` : ''
        }`,
        {
          headers: this.getHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`Polling failed: ${response.status}`);
      }

      const data = await response.json();

      // Update last sync timestamp
      this.lastSyncTimestamp = data.timestamp;

      // Emit task updates
      if (data.tasks && data.tasks.length > 0) {
        data.tasks.forEach((task: Task) => {
          this.emit({
            type: 'task_update',
            data: {
              event: 'updated',
              task,
            },
            timestamp: data.timestamp,
          });
        });
      }
    } catch (error) {
      console.error('Polling error:', error);
      this.emit({
        type: 'error',
        data: { error: 'Polling failed' },
        timestamp: new Date().toISOString(),
      });
    }
  }

  /**
   * Get API base URL.
   */
  private getApiBaseUrl(): string {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  /**
   * Get WebSocket URL from API URL.
   */
  private getWebSocketUrl(): string {
    const apiUrl = this.getApiBaseUrl();
    return apiUrl.replace(/^http/, 'ws');
  }

  /**
   * Get authentication token.
   */
  private getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
  }

  /**
   * Get request headers.
   */
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    const token = this.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * Check if currently connected.
   */
  isConnected(): boolean {
    return (
      (this.ws?.readyState === WebSocket.OPEN) ||
      (this.pollingInterval !== null)
    );
  }

  /**
   * Get current connection mode.
   */
  getConnectionMode(): 'websocket' | 'polling' | 'disconnected' {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return 'websocket';
    } else if (this.pollingInterval !== null) {
      return 'polling';
    } else {
      return 'disconnected';
    }
  }
}

/**
 * Create a singleton instance for the current user.
 */
let syncServiceInstance: RealtimeSyncService | null = null;

export function getSyncService(userId: string): RealtimeSyncService {
  if (!syncServiceInstance || syncServiceInstance['userId'] !== userId) {
    if (syncServiceInstance) {
      syncServiceInstance.stop();
    }
    syncServiceInstance = new RealtimeSyncService(userId);
  }
  return syncServiceInstance;
}

export function stopSyncService(): void {
  if (syncServiceInstance) {
    syncServiceInstance.stop();
    syncServiceInstance = null;
  }
}

export default RealtimeSyncService;
