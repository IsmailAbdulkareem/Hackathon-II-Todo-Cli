export type TodoStatus = 'pending' | 'completed';

export type PriorityLevel = 'low' | 'medium' | 'high';

export type RecurrencePattern = 'none' | 'daily' | 'weekly' | 'monthly';

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

export interface TaskCreate {
  title: string;
  description?: string | null;
  due_date?: string | null;
  priority?: PriorityLevel;
  tags?: string[];
  recurrence?: RecurrencePattern;
  reminder_offset_minutes?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  due_date?: string | null;
  priority?: PriorityLevel;
  tags?: string[];
  recurrence?: RecurrencePattern;
  reminder_offset_minutes?: number;
}

export interface TaskFilters {
  priority?: PriorityLevel;
  completed?: boolean;
  due_from?: string;
  due_to?: string;
  tags?: string[];
  sort_by?: 'created_at' | 'updated_at' | 'due_date' | 'priority';
  sort_order?: 'asc' | 'desc';
}

export interface SearchParams extends TaskFilters {
  q?: string;
  page?: number;
  limit?: number;
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
