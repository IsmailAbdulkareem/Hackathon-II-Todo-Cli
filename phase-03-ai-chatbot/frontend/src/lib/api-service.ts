import { API_CONFIG, Task, CreateTaskRequest, UpdateTaskRequest, ApiError, SearchParams, PaginatedResponse } from './api-config';
import { authService } from './auth-service';

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
  }

  // Get authentication headers with JWT token
  private getAuthHeaders(): HeadersInit {
    const token = authService.getToken();

    if (!token) {
      throw new Error("Not authenticated");
    }

    return {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    };
  }

  // Helper method for API calls
  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      // Get auth headers for all requests
      const authHeaders = this.getAuthHeaders();

      const response = await fetch(url, {
        ...options,
        headers: {
          ...authHeaders,
          ...options?.headers,
        },
      });

      // Handle 401 Unauthorized - token expired or invalid
      if (response.status === 401) {
        authService.signOut();
        window.location.href = "/login";
        throw new Error("Session expired. Please log in again.");
      }

      // Handle 403 Forbidden - access denied
      if (response.status === 403) {
        throw new Error("Access denied: You can only access your own resources");
      }

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
    const userId = authService.getUserId() || 'unknown';
    return this.request<Task[]>(API_CONFIG.ENDPOINTS.TASKS(userId));
  }

  // Get a single task
  async getTask(taskId: string): Promise<Task> {
    const userId = authService.getUserId() || 'unknown';
    return this.request<Task>(API_CONFIG.ENDPOINTS.TASK(userId, taskId));
  }

  // Create a new task
  async createTask(data: CreateTaskRequest): Promise<Task> {
    const userId = authService.getUserId() || 'unknown';
    return this.request<Task>(API_CONFIG.ENDPOINTS.TASKS(userId), {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Update a task
  async updateTask(taskId: string, data: UpdateTaskRequest): Promise<Task> {
    const userId = authService.getUserId() || 'unknown';
    return this.request<Task>(API_CONFIG.ENDPOINTS.TASK(userId, taskId), {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Delete a task
  async deleteTask(taskId: string): Promise<void> {
    const userId = authService.getUserId() || 'unknown';
    return this.request<void>(API_CONFIG.ENDPOINTS.TASK(userId, taskId), {
      method: 'DELETE',
    });
  }

  // Toggle task completion
  async toggleTaskCompletion(taskId: string): Promise<Task> {
    const userId = authService.getUserId() || 'unknown';
    return this.request<Task>(API_CONFIG.ENDPOINTS.TOGGLE_COMPLETE(userId, taskId), {
      method: 'PATCH',
    });
  }

  // Search and filter tasks
  async searchTasks(params: SearchParams): Promise<PaginatedResponse<Task>> {
    const userId = authService.getUserId() || 'unknown';

    // Build query string from params
    const queryParams = new URLSearchParams();

    if (params.q) queryParams.append('q', params.q);
    if (params.priority) queryParams.append('priority', params.priority);
    if (params.tags && params.tags.length > 0) {
      params.tags.forEach(tag => queryParams.append('tags', tag));
    }
    if (params.completed !== undefined) queryParams.append('completed', String(params.completed));
    if (params.due_from) queryParams.append('due_from', params.due_from);
    if (params.due_to) queryParams.append('due_to', params.due_to);
    if (params.page) queryParams.append('page', String(params.page));
    if (params.limit) queryParams.append('limit', String(params.limit));
    if (params.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params.sort_order) queryParams.append('sort_order', params.sort_order);

    const endpoint = `${API_CONFIG.ENDPOINTS.SEARCH_TASKS(userId)}?${queryParams.toString()}`;
    return this.request<PaginatedResponse<Task>>(endpoint);
  }

  // Get notification status
  async getNotificationStatus(): Promise<{ user_id: string; connected: boolean; connection_count: number }> {
    return this.request<{ user_id: string; connected: boolean; connection_count: number }>(
      API_CONFIG.ENDPOINTS.NOTIFICATIONS_STATUS()
    );
  }
}

// Export singleton instance
export const apiService = new ApiService();
