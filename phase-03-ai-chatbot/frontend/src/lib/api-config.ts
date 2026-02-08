// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  ENDPOINTS: {
    TASKS: (userId: string) => `/api/${userId}/tasks`,
    TASK: (userId: string, taskId: string) => `/api/${userId}/tasks/${taskId}`,
    TOGGLE_COMPLETE: (userId: string, taskId: string) => `/api/${userId}/tasks/${taskId}/complete`,
    SEARCH_TASKS: (userId: string) => `/api/${userId}/tasks/search`,
    NOTIFICATIONS_STREAM: () => `/api/notifications/stream`,
    NOTIFICATIONS_STATUS: () => `/api/notifications/status`,
  },
  DEFAULT_USER_ID: 'user123', // Fallback user ID (JWT authentication extracts actual user_id from token)
};

// Priority levels
export type PriorityLevel = 'low' | 'medium' | 'high';

// Recurrence patterns
export type RecurrencePattern = 'none' | 'daily' | 'weekly' | 'monthly';

// API Response Types
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
  due_date: string | null;
  priority: PriorityLevel;
  tags: string[];
  recurrence: RecurrencePattern;
  reminder_offset_minutes: number;
}

export interface CreateTaskRequest {
  title: string;
  description?: string | null;
  due_date?: string | null;
  priority?: PriorityLevel;
  tags?: string[];
  recurrence?: RecurrencePattern;
  reminder_offset_minutes?: number;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string | null;
  due_date?: string | null;
  priority?: PriorityLevel;
  tags?: string[];
  recurrence?: RecurrencePattern;
  reminder_offset_minutes?: number;
}

export interface SearchParams {
  q?: string;
  priority?: PriorityLevel;
  tags?: string[];
  completed?: boolean;
  due_from?: string;
  due_to?: string;
  page?: number;
  limit?: number;
  sort_by?: 'created_at' | 'updated_at' | 'due_date' | 'priority';
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

export interface ApiError {
  detail: string;
}
