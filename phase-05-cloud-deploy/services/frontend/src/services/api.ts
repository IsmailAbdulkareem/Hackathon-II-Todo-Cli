/**
 * API client for TaskAI backend.
 *
 * Provides methods for:
 * - Task CRUD operations
 * - Tag management
 * - Search and filtering
 * - Real-time synchronization
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string;
  priority: 'Low' | 'Medium' | 'High';
  due_date?: string;
  is_recurring: boolean;
  parent_task_id?: string;
  recurrence_rule_id?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: string;
  user_id: string;
  name: string;
  color: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface SearchParams {
  query?: string;
  priority?: 'Low' | 'Medium' | 'High';
  tags?: string;
  completed?: boolean;
  is_recurring?: boolean;
  has_due_date?: boolean;
  overdue?: boolean;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

export interface SyncResponse {
  timestamp: string;
  tasks: Task[];
  has_more: boolean;
}

// Helper function to get auth token
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

// Helper function to build headers
function getHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

// Helper function to handle API errors
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP ${response.status}: ${response.statusText}`
    }));
    throw new Error(error.detail || 'An error occurred');
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// Task API methods
export const taskApi = {
  /**
   * Get all tasks for a user with optional filtering and sorting.
   */
  async getTasks(
    userId: string,
    params?: {
      priority?: string;
      tags?: string;
      completed?: boolean;
      is_recurring?: boolean;
      sort_by?: string;
      sort_order?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<Task[]> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });
    }

    const url = `${API_BASE_URL}/api/${userId}/tasks${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<Task[]>(response);
  },

  /**
   * Get a single task by ID.
   */
  async getTask(userId: string, taskId: string): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}`, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<Task>(response);
  },

  /**
   * Create a new task.
   */
  async createTask(
    userId: string,
    data: {
      title: string;
      description: string;
      priority?: 'Low' | 'Medium' | 'High';
      due_date?: string;
      is_recurring?: boolean;
    }
  ): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse<Task>(response);
  },

  /**
   * Update an existing task.
   */
  async updateTask(
    userId: string,
    taskId: string,
    data: {
      title?: string;
      description?: string;
      priority?: 'Low' | 'Medium' | 'High';
      due_date?: string;
    }
  ): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse<Task>(response);
  },

  /**
   * Delete a task.
   */
  async deleteTask(userId: string, taskId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });

    return handleResponse<void>(response);
  },

  /**
   * Toggle task completion status.
   */
  async toggleComplete(userId: string, taskId: string): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
      headers: getHeaders(),
    });

    return handleResponse<Task>(response);
  },

  /**
   * Set task priority.
   */
  async setPriority(
    userId: string,
    taskId: string,
    priority: 'Low' | 'Medium' | 'High'
  ): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}/priority?priority=${priority}`, {
      method: 'PATCH',
      headers: getHeaders(),
    });

    return handleResponse<Task>(response);
  },

  /**
   * Add a tag to a task.
   */
  async addTag(userId: string, taskId: string, tagId: string): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}/tags/${tagId}`, {
      method: 'POST',
      headers: getHeaders(),
    });

    return handleResponse<Task>(response);
  },

  /**
   * Remove a tag from a task.
   */
  async removeTag(userId: string, taskId: string, tagId: string): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}/tags/${tagId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });

    return handleResponse<Task>(response);
  },

  /**
   * Get tags for a task.
   */
  async getTaskTags(userId: string, taskId: string): Promise<Tag[]> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}/tags`, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<Tag[]>(response);
  },

  /**
   * Create a reminder for a task.
   */
  async createReminder(
    userId: string,
    taskId: string,
    data: {
      scheduled_time: string;
      reminder_type: '15min' | '1hr' | '1day' | '1week' | 'custom';
    }
  ): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}/reminders`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse<any>(response);
  },

  /**
   * Delete a reminder from a task.
   */
  async deleteReminder(userId: string, taskId: string, reminderId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}/reminders/${reminderId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });

    return handleResponse<void>(response);
  },

  /**
   * Get reminders for a task.
   */
  async getTaskReminders(userId: string, taskId: string): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}/reminders`, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<any[]>(response);
  },
};

// Tag API methods
export const tagApi = {
  /**
   * Get all tags for a user.
   */
  async getTags(
    userId: string,
    params?: {
      sort_by?: string;
      limit?: number;
    }
  ): Promise<Tag[]> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });
    }

    const url = `${API_BASE_URL}/api/${userId}/tags${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<Tag[]>(response);
  },

  /**
   * Get tag autocomplete suggestions.
   */
  async autocomplete(userId: string, query: string, limit: number = 10): Promise<Tag[]> {
    const queryParams = new URLSearchParams({
      query,
      limit: String(limit),
    });

    const response = await fetch(`${API_BASE_URL}/api/${userId}/tags/autocomplete?${queryParams}`, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<Tag[]>(response);
  },

  /**
   * Get a single tag by ID.
   */
  async getTag(userId: string, tagId: string): Promise<Tag> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tags/${tagId}`, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<Tag>(response);
  },

  /**
   * Create a new tag.
   */
  async createTag(
    userId: string,
    data: {
      name: string;
      color: string;
    }
  ): Promise<Tag> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tags`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse<Tag>(response);
  },

  /**
   * Update an existing tag.
   */
  async updateTag(
    userId: string,
    tagId: string,
    data: {
      name?: string;
      color?: string;
    }
  ): Promise<Tag> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tags/${tagId}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse<Tag>(response);
  },

  /**
   * Delete a tag.
   */
  async deleteTag(userId: string, tagId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tags/${tagId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });

    return handleResponse<void>(response);
  },
};

// Search API methods
export const searchApi = {
  /**
   * Search tasks with multiple criteria.
   */
  async searchTasks(userId: string, params: SearchParams): Promise<Task[]> {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, String(value));
      }
    });

    const response = await fetch(`${API_BASE_URL}/api/${userId}/search?${queryParams}`, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<Task[]>(response);
  },

  /**
   * Get overdue tasks.
   */
  async getOverdueTasks(userId: string): Promise<Task[]> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/search/overdue`, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<Task[]>(response);
  },

  /**
   * Get tasks due today.
   */
  async getDueTodayTasks(userId: string): Promise<Task[]> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/search/due-today`, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<Task[]>(response);
  },

  /**
   * Get high priority tasks.
   */
  async getHighPriorityTasks(userId: string): Promise<Task[]> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/search/high-priority`, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<Task[]>(response);
  },

  /**
   * Count tasks matching criteria.
   */
  async countTasks(
    userId: string,
    params?: {
      completed?: boolean;
      priority?: 'Low' | 'Medium' | 'High';
    }
  ): Promise<{ count: number }> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });
    }

    const url = `${API_BASE_URL}/api/${userId}/search/count${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<{ count: number }>(response);
  },
};

// Real-time sync API methods
export const syncApi = {
  /**
   * Poll for task updates since a timestamp.
   */
  async poll(userId: string, since?: string): Promise<SyncResponse> {
    const queryParams = new URLSearchParams();
    if (since) {
      queryParams.append('since', since);
    }

    const response = await fetch(`${API_BASE_URL}/api/${userId}/sync/poll?${queryParams}`, {
      method: 'GET',
      headers: getHeaders(),
    });

    return handleResponse<SyncResponse>(response);
  },

  /**
   * Create a WebSocket connection for real-time updates.
   */
  createWebSocket(userId: string): WebSocket {
    const token = getAuthToken();
    const wsUrl = API_BASE_URL.replace('http', 'ws');
    const url = `${wsUrl}/api/${userId}/sync${token ? `?token=${token}` : ''}`;

    return new WebSocket(url);
  },
};

export default {
  task: taskApi,
  tag: tagApi,
  search: searchApi,
  sync: syncApi,
};
