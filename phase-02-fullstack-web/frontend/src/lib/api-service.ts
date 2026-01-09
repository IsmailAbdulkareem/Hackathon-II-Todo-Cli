import { API_CONFIG, Task, CreateTaskRequest, UpdateTaskRequest, ApiError } from './api-config';

class ApiService {
  private baseUrl: string;
  private userId: string;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.userId = API_CONFIG.DEFAULT_USER_ID;
  }

  // Helper method for API calls
  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      // Handle 204 No Content (DELETE success)
      if (response.status === 204) {
        return null as T;
      }

      const data = await response.json();

      if (!response.ok) {
        const error = data as ApiError;
        throw new Error(error.detail || 'API request failed');
      }

      return data as T;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Get all tasks
  async getTasks(): Promise<Task[]> {
    return this.request<Task[]>(API_CONFIG.ENDPOINTS.TASKS(this.userId));
  }

  // Get a single task
  async getTask(taskId: string): Promise<Task> {
    return this.request<Task>(API_CONFIG.ENDPOINTS.TASK(this.userId, taskId));
  }

  // Create a new task
  async createTask(data: CreateTaskRequest): Promise<Task> {
    return this.request<Task>(API_CONFIG.ENDPOINTS.TASKS(this.userId), {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Update a task
  async updateTask(taskId: string, data: UpdateTaskRequest): Promise<Task> {
    return this.request<Task>(API_CONFIG.ENDPOINTS.TASK(this.userId, taskId), {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Delete a task
  async deleteTask(taskId: string): Promise<void> {
    return this.request<void>(API_CONFIG.ENDPOINTS.TASK(this.userId, taskId), {
      method: 'DELETE',
    });
  }

  // Toggle task completion
  async toggleTaskCompletion(taskId: string): Promise<Task> {
    return this.request<Task>(API_CONFIG.ENDPOINTS.TOGGLE_COMPLETE(this.userId, taskId), {
      method: 'PATCH',
    });
  }
}

// Export singleton instance
export const apiService = new ApiService();
