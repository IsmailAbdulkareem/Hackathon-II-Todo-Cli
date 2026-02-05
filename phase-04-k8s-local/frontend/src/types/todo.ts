export type TodoStatus = 'pending' | 'completed';

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TodoStatus;
  priority: number;
  completed: boolean;
  createdAt: string;
  updatedAt: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TodoStatus;
  priority?: number;
  completed?: boolean;
}
