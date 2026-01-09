// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  ENDPOINTS: {
    TASKS: (userId: string) => `/api/${userId}/tasks`,
    TASK: (userId: string, taskId: string) => `/api/${userId}/tasks/${taskId}`,
    TOGGLE_COMPLETE: (userId: string, taskId: string) => `/api/${userId}/tasks/${taskId}/complete`,
  },
  DEFAULT_USER_ID: 'user123', // For Phase 2 (no auth yet)
};

// API Response Types
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string | null;
}

export interface UpdateTaskRequest {
  title: string;
  description?: string | null;
}

export interface ApiError {
  detail: string;
}
