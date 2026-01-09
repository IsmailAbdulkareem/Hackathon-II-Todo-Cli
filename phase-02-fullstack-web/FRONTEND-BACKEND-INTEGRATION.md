# Frontend-Backend Integration Roadmap

## 🚀 Quick Start

Your Todo Backend API is now running at: **http://localhost:8001**

### API Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/` | Health check | `http://localhost:8001/` |
| GET | `/docs` | Interactive API documentation | `http://localhost:8001/docs` |
| GET | `/api/{user_id}/tasks` | Get all tasks for a user | `http://localhost:8001/api/user123/tasks` |
| POST | `/api/{user_id}/tasks` | Create a new task | `http://localhost:8001/api/user123/tasks` |
| GET | `/api/{user_id}/tasks/{id}` | Get a single task | `http://localhost:8001/api/user123/tasks/{task-id}` |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task | `http://localhost:8001/api/user123/tasks/{task-id}` |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task | `http://localhost:8001/api/user123/tasks/{task-id}` |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion | `http://localhost:8001/api/user123/tasks/{task-id}/complete` |

---

## 📋 Complete Integration Roadmap

### Phase 1: Test the API (5 minutes)

#### Step 1.1: Open API Documentation
Open your browser and go to: **http://localhost:8001/docs**

This is the interactive Swagger UI where you can test all endpoints.

#### Step 1.2: Test Creating a Task
1. In Swagger UI, click on `POST /api/{user_id}/tasks`
2. Click "Try it out"
3. Enter `user123` for `user_id`
4. Enter this JSON in the request body:
```json
{
  "title": "Test Task",
  "description": "This is a test task from Swagger UI"
}
```
5. Click "Execute"
6. You should see a 201 response with the created task (including auto-generated UUID and timestamps)

#### Step 1.3: Test Getting All Tasks
1. Click on `GET /api/{user_id}/tasks`
2. Click "Try it out"
3. Enter `user123` for `user_id`
4. Click "Execute"
5. You should see the task you just created

---

### Phase 2: Create API Service Layer (15 minutes)

#### Step 2.1: Create API Configuration File

Create `phase-02-fullstack-web/frontend/src/lib/api-config.ts`:

```typescript
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
```

#### Step 2.2: Create API Service

Create `phase-02-fullstack-web/frontend/src/lib/api-service.ts`:

```typescript
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
```

---

### Phase 3: Update Frontend Components (30 minutes)

#### Step 3.1: Update Environment Variables

Create/update `phase-02-fullstack-web/frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
```

#### Step 3.2: Update Your Main Todo Component

Example: `phase-02-fullstack-web/frontend/src/app/page.tsx` (or wherever your main component is):

```typescript
'use client';

import { useState, useEffect } from 'react';
import { apiService } from '@/lib/api-service';
import { Task } from '@/lib/api-config';

export default function TodoPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getTasks();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newTaskTitle.trim()) {
      setError('Title is required');
      return;
    }

    try {
      setError(null);
      const newTask = await apiService.createTask({
        title: newTaskTitle,
        description: newTaskDescription || null,
      });

      setTasks([...tasks, newTask]);
      setNewTaskTitle('');
      setNewTaskDescription('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    }
  };

  const handleToggleComplete = async (taskId: string) => {
    try {
      setError(null);
      const updatedTask = await apiService.toggleTaskCompletion(taskId);
      setTasks(tasks.map(task => task.id === taskId ? updatedTask : task));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle task');
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      setError(null);
      await apiService.deleteTask(taskId);
      setTasks(tasks.filter(task => task.id !== taskId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  const handleUpdateTask = async (taskId: string, title: string, description: string) => {
    try {
      setError(null);
      const updatedTask = await apiService.updateTask(taskId, { title, description });
      setTasks(tasks.map(task => task.id === taskId ? updatedTask : task));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    }
  };

  if (loading) {
    return <div className="p-8">Loading tasks...</div>;
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Todo App</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Create Task Form */}
      <form onSubmit={handleCreateTask} className="mb-8 space-y-4">
        <div>
          <input
            type="text"
            placeholder="Task title"
            value={newTaskTitle}
            onChange={(e) => setNewTaskTitle(e.target.value)}
            className="w-full px-4 py-2 border rounded"
            maxLength={500}
          />
        </div>
        <div>
          <textarea
            placeholder="Task description (optional)"
            value={newTaskDescription}
            onChange={(e) => setNewTaskDescription(e.target.value)}
            className="w-full px-4 py-2 border rounded"
            maxLength={2000}
            rows={3}
          />
        </div>
        <button
          type="submit"
          className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Add Task
        </button>
      </form>

      {/* Task List */}
      <div className="space-y-4">
        {tasks.length === 0 ? (
          <p className="text-gray-500">No tasks yet. Create one above!</p>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className="border rounded p-4 flex items-start justify-between"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => handleToggleComplete(task.id)}
                    className="w-5 h-5"
                  />
                  <h3
                    className={`text-lg font-semibold ${
                      task.completed ? 'line-through text-gray-500' : ''
                    }`}
                  >
                    {task.title}
                  </h3>
                </div>
                {task.description && (
                  <p className="text-gray-600 mt-2 ml-7">{task.description}</p>
                )}
                <p className="text-xs text-gray-400 mt-2 ml-7">
                  Created: {new Date(task.created_at).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => handleDeleteTask(task.id)}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
```

---

### Phase 4: Test the Integration (10 minutes)

#### Step 4.1: Start the Frontend

```bash
cd phase-02-fullstack-web/frontend
npm run dev
```

The frontend should start on `http://localhost:3000`

#### Step 4.2: Test All Features

1. **Create a task**: Fill in the form and click "Add Task"
2. **View tasks**: You should see the task appear immediately
3. **Toggle completion**: Click the checkbox to mark as complete/incomplete
4. **Delete task**: Click the "Delete" button to remove a task
5. **Check persistence**: Refresh the page - tasks should still be there (stored in SQLite database)

#### Step 4.3: Verify CORS is Working

If you see CORS errors in the browser console, the backend is already configured to allow `http://localhost:3000`. If you're using a different port, update the `.env` file in the backend:

```bash
# phase-02-fullstack-web/backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

### Phase 5: Advanced Features (Optional)

#### Step 5.1: Add React Query for Better State Management

```bash
cd phase-02-fullstack-web/frontend
npm install @tanstack/react-query
```

Create `phase-02-fullstack-web/frontend/src/hooks/useTasks.ts`:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@/lib/api-service';
import { CreateTaskRequest, UpdateTaskRequest } from '@/lib/api-config';

export function useTasks() {
  const queryClient = useQueryClient();

  const tasksQuery = useQuery({
    queryKey: ['tasks'],
    queryFn: () => apiService.getTasks(),
  });

  const createTaskMutation = useMutation({
    mutationFn: (data: CreateTaskRequest) => apiService.createTask(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const toggleCompleteMutation = useMutation({
    mutationFn: (taskId: string) => apiService.toggleTaskCompletion(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const deleteTaskMutation = useMutation({
    mutationFn: (taskId: string) => apiService.deleteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const updateTaskMutation = useMutation({
    mutationFn: ({ taskId, data }: { taskId: string; data: UpdateTaskRequest }) =>
      apiService.updateTask(taskId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  return {
    tasks: tasksQuery.data ?? [],
    isLoading: tasksQuery.isLoading,
    error: tasksQuery.error,
    createTask: createTaskMutation.mutate,
    toggleComplete: toggleCompleteMutation.mutate,
    deleteTask: deleteTaskMutation.mutate,
    updateTask: updateTaskMutation.mutate,
  };
}
```

#### Step 5.2: Add Loading States and Optimistic Updates

Update your component to use React Query for better UX with loading states and optimistic updates.

---

## 🔧 Troubleshooting

### Issue 1: CORS Errors

**Symptom**: Browser console shows "CORS policy" errors

**Solution**:
1. Check backend `.env` file has correct CORS_ORIGINS
2. Restart backend server after changing `.env`
3. Clear browser cache

### Issue 2: Connection Refused

**Symptom**: "Failed to fetch" or "Connection refused"

**Solution**:
1. Verify backend is running: `curl http://localhost:8001/`
2. Check if port 8001 is accessible
3. Verify API_URL in frontend `.env.local`

### Issue 3: 404 Not Found

**Symptom**: API returns 404 for valid endpoints

**Solution**:
1. Check the endpoint URL format matches the API specification
2. Verify user_id is being passed correctly
3. Check API documentation at `http://localhost:8001/docs`

### Issue 4: 422 Validation Error

**Symptom**: API returns 422 when creating/updating tasks

**Solution**:
1. Check title is not empty (required field)
2. Verify title is max 500 characters
3. Verify description is max 2000 characters
4. Check request body format matches API specification

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│                   http://localhost:3000                      │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   UI Layer   │───▶│ API Service  │───▶│  API Config  │ │
│  │ (Components) │    │   Layer      │    │   (Types)    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Requests
                              │ (JSON)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│                   http://localhost:8001                      │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Routes     │───▶│   Models     │───▶│   Database   │ │
│  │ (Endpoints)  │    │ (SQLModel)   │    │   (SQLite)   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Success Checklist

- [ ] Backend API running on http://localhost:8001
- [ ] Can access API documentation at http://localhost:8001/docs
- [ ] Created API service layer in frontend
- [ ] Updated frontend components to use API service
- [ ] Frontend running on http://localhost:3000
- [ ] Can create tasks from frontend
- [ ] Can view all tasks
- [ ] Can toggle task completion
- [ ] Can delete tasks
- [ ] Tasks persist after page refresh
- [ ] No CORS errors in browser console

---

## 🚀 Next Steps

1. **Phase III: Add Authentication** (JWT-based user authentication)
2. **Add Update Task Feature** (Edit task title/description)
3. **Add Filtering** (Show all/active/completed tasks)
4. **Add Sorting** (By date, title, completion status)
5. **Deploy to Production** (See backend README.md for deployment options)

---

## 📚 Additional Resources

- **Backend API Documentation**: http://localhost:8001/docs
- **Backend README**: `phase-02-fullstack-web/backend/README.md`
- **Testing Guide**: `phase-02-fullstack-web/backend/TESTING.md`
- **API Specification**: `specs/003-backend-api/spec.md`
- **Data Model**: `specs/003-backend-api/data-model.md`
