/**
 * TypeScript type definitions for TaskAI application.
 *
 * Defines all data models, API request/response types, and UI state types.
 */

// ============================================================================
// Core Domain Models
// ============================================================================

export interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string;
  priority: Priority;
  due_date?: string;
  is_recurring: boolean;
  parent_task_id?: string;
  recurrence_rule_id?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  tags?: Tag[];
  reminders?: Reminder[];
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

export interface Reminder {
  id: string;
  task_id: string;
  user_id: string;
  scheduled_time: string;
  reminder_type: ReminderType;
  status: ReminderStatus;
  dapr_job_id?: string;
  created_at: string;
  updated_at: string;
}

export interface RecurrenceRule {
  id: string;
  user_id: string;
  recurrence_type: RecurrenceType;
  interval: number;
  days_of_week?: number[];
  day_of_month?: number;
  month_of_year?: number;
  custom_pattern?: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Enums and Literal Types
// ============================================================================

export type Priority = 'Low' | 'Medium' | 'High';

export type ReminderType = '15min' | '1hr' | '1day' | '1week' | 'custom';

export type ReminderStatus = 'pending' | 'sent' | 'failed';

export type RecurrenceType = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';

export type SortField = 'created_at' | 'updated_at' | 'due_date' | 'priority' | 'title';

export type SortOrder = 'asc' | 'desc';

// ============================================================================
// API Request Types
// ============================================================================

export interface CreateTaskRequest {
  title: string;
  description: string;
  priority?: Priority;
  due_date?: string;
  is_recurring?: boolean;
  tag_ids?: string[];
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  priority?: Priority;
  due_date?: string;
}

export interface CreateTagRequest {
  name: string;
  color: string;
}

export interface UpdateTagRequest {
  name?: string;
  color?: string;
}

export interface CreateReminderRequest {
  scheduled_time: string;
  reminder_type: ReminderType;
}

export interface CreateRecurrenceRuleRequest {
  recurrence_type: RecurrenceType;
  interval: number;
  days_of_week?: number[];
  day_of_month?: number;
  month_of_year?: number;
  custom_pattern?: string;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface TaskResponse extends Task {}

export interface TagResponse extends Tag {}

export interface ReminderResponse extends Reminder {}

export interface RecurrenceRuleResponse extends RecurrenceRule {}

export interface SyncResponse {
  timestamp: string;
  tasks: Task[];
  has_more: boolean;
}

export interface CountResponse {
  count: number;
}

// ============================================================================
// Search and Filter Types
// ============================================================================

export interface SearchParams {
  query?: string;
  priority?: Priority;
  tags?: string;
  completed?: boolean;
  is_recurring?: boolean;
  has_due_date?: boolean;
  overdue?: boolean;
  sort_by?: SortField;
  sort_order?: SortOrder;
  limit?: number;
  offset?: number;
}

export interface FilterOptions {
  priority: Priority | null;
  tags: string[];
  completed: boolean | null;
  isRecurring: boolean | null;
  overdue: boolean | null;
  dueToday: boolean | null;
  hasDueDate: boolean | null;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface TaskFormData {
  title: string;
  description: string;
  priority: Priority;
  due_date?: string;
  is_recurring: boolean;
  tag_ids: string[];
}

export interface TaskListState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  filters: FilterOptions;
  searchQuery: string;
  sortBy: SortField;
  sortOrder: SortOrder;
}

export interface TagState {
  tags: Tag[];
  loading: boolean;
  error: string | null;
}

export interface SyncState {
  connected: boolean;
  mode: 'websocket' | 'polling' | 'disconnected';
  lastSync: string | null;
  error: string | null;
}

// ============================================================================
// Real-time Event Types
// ============================================================================

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

// ============================================================================
// Utility Types
// ============================================================================

export interface PaginationParams {
  limit: number;
  offset: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface ApiError {
  detail: string;
  status?: number;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface TaskListProps {
  tasks: Task[];
  onTaskComplete: (taskId: string) => void;
  onTaskEdit: (taskId: string) => void;
  onTaskDelete: (taskId: string) => void;
  onTagClick?: (tagId: string) => void;
  loading?: boolean;
  emptyMessage?: string;
  className?: string;
}

export interface TaskFormProps {
  initialData?: Partial<TaskFormData>;
  availableTags: Tag[];
  onSubmit: (data: TaskFormData) => void;
  onCancel: () => void;
  submitLabel?: string;
  loading?: boolean;
  className?: string;
}

export interface FilterPanelProps {
  filters: FilterOptions;
  onFilterChange: (filters: FilterOptions) => void;
  availableTags: Tag[];
  className?: string;
}

export interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  debounceMs?: number;
  className?: string;
}

export interface TagPillProps {
  tag: Tag;
  size?: 'small' | 'medium' | 'large';
  removable?: boolean;
  onRemove?: (tagId: string) => void;
  onClick?: (tagId: string) => void;
  className?: string;
}

export interface TagListProps {
  tags: Tag[];
  size?: 'small' | 'medium' | 'large';
  removable?: boolean;
  onRemove?: (tagId: string) => void;
  onClick?: (tagId: string) => void;
  maxVisible?: number;
  className?: string;
}

// ============================================================================
// Hook Return Types
// ============================================================================

export interface UseTasksReturn {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  createTask: (data: CreateTaskRequest) => Promise<Task>;
  updateTask: (taskId: string, data: UpdateTaskRequest) => Promise<Task>;
  deleteTask: (taskId: string) => Promise<void>;
  toggleComplete: (taskId: string) => Promise<Task>;
  setPriority: (taskId: string, priority: Priority) => Promise<Task>;
  addTag: (taskId: string, tagId: string) => Promise<Task>;
  removeTag: (taskId: string, tagId: string) => Promise<Task>;
  refresh: () => Promise<void>;
}

export interface UseTagsReturn {
  tags: Tag[];
  loading: boolean;
  error: string | null;
  createTag: (data: CreateTagRequest) => Promise<Tag>;
  updateTag: (tagId: string, data: UpdateTagRequest) => Promise<Tag>;
  deleteTag: (tagId: string) => Promise<void>;
  autocomplete: (query: string) => Promise<Tag[]>;
  refresh: () => Promise<void>;
}

export interface UseRealtimeSyncReturn {
  connected: boolean;
  mode: 'websocket' | 'polling' | 'disconnected';
  lastSync: string | null;
  error: string | null;
  start: () => Promise<void>;
  stop: () => void;
}

// ============================================================================
// Chat/MCP Types (for Phase 4)
// ============================================================================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  task_id?: string;
}

export interface MCPToolCall {
  tool: string;
  parameters: Record<string, any>;
  result?: any;
}

// ============================================================================
// Type Guards
// ============================================================================

export function isTask(obj: any): obj is Task {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.id === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.priority === 'string' &&
    typeof obj.completed === 'boolean'
  );
}

export function isTag(obj: any): obj is Tag {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.color === 'string'
  );
}

export function isTaskUpdateEvent(obj: any): obj is TaskUpdateEvent {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    obj.type === 'task_update' &&
    typeof obj.event === 'string' &&
    isTask(obj.task)
  );
}
