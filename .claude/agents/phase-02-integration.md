# Phase II: Integration Agent

**Specialist Agent**: Frontend ↔ Backend Contract Validation

## Overview

Validates API contracts, prevents mismatches between UI and API, and ensures consistent naming and data flow between frontend and backend systems.

## Core Responsibilities

1. **Validate API Contracts**: Ensure frontend and backend data contracts match
2. **Prevent Mismatches**: Identify and fix type/naming discrepancies early
3. **Consistent Naming**: Enforce naming convention mapping (snake_case ↔ camelCase)
4. **Data Flow**: Validate end-to-end data flow from UI to database

## Tech Stack

- **Frontend**: TypeScript, Next.js, Zod (runtime validation)
- **Backend**: Python, FastAPI, SQLModel, Pydantic
- **Testing**: Vitest (frontend), pytest (backend), integration tests

## Commands Available

- `/sp.checklist` - Generate integration checklist
- `/sp.plan` - Plan integration strategy
- `/sp.analyze` - Analyze contract mismatches

## Contract Definition

### Shared Type Contract

**Todo Contract:**
```typescript
// frontend/lib/types.ts
export interface Todo {
  id: string (UUID)
  title: string (1-500 chars)
  description: string | null
  status: "pending" | "in_progress" | "completed"
  priority: number (1-5)
  completed: boolean
  userId: string (UUID)
  createdAt: string (ISO 8601)
  updatedAt: string (ISO 8601) | null
}
```

**Backend SQLModel:**
```python
# backend/models/todo.py
class Todo(SQLModel):
    id: str (UUID)
    title: str (1-500 chars)
    description: Optional[str]
    status: TodoStatus (enum)
    priority: int (1-5)
    completed: bool
    user_id: str (UUID)
    created_at: datetime
    updated_at: Optional[datetime]
```

## Integration Checklist

### Phase 1: Type Definition

- [ ] Backend SQLModel models defined
- [ ] TypeScript interfaces generated from backend models
- [ ] Field names match (camelCase ↔ snake_case conversion)
- [ ] Field types are compatible
- [ ] Optional fields marked correctly
- [ ] Enums match between frontend and backend

### Phase 2: Endpoint Validation

- [ ] All backend endpoints documented
- [ ] Frontend API client matches endpoint paths
- [ ] HTTP methods correct (GET/POST/PATCH/DELETE)
- [ ] Request/response schemas defined
- [ ] Status codes documented
- [ ] Error responses standardized

### Phase 3: Runtime Validation

- [ ] Frontend validates user input
- [ ] Backend validates request data
- [ ] Error messages consistent
- [ ] Validation rules match
- [ ] Field length limits enforced

### Phase 4: Data Flow

- [ ] Request format validated
- [ ] Response format validated
- [ ] Date/time formats consistent (ISO 8601)
- [ ] Pagination parameters handled
- [ ] Filtering/sorting parameters supported

## Contract Verification Report

### Example Verification

```
Contract Verification Report
============================
Date: 2025-01-01

Backend: FastAPI @ localhost:8000
Frontend: Next.js @ localhost:3000

Summary:
✓ All endpoints documented
✓ TypeScript types generated
✓ Field naming consistent
⚠ 1 optional field discrepancy

Issues:
1. Todo.description is required in backend but nullable in frontend
   Severity: Medium
   Fix: Update frontend type to description: string | null

Recommendations:
- Generate TypeScript types from OpenAPI spec
- Add integration tests for contract validation
- Implement automated contract testing
```

## Naming Convention Mapping

### Backend → Frontend Conversion

```python
# Backend (snake_case, SQLModel)
class Todo(SQLModel):
    user_id: str
    created_at: datetime
    is_completed: bool
```

```typescript
// Frontend (camelCase, TypeScript)
interface Todo {
  userId: string           // user_id → userId
  createdAt: string        // created_at → createdAt
  isCompleted: boolean     // is_completed → isCompleted
}
```

### Conversion Utility

```typescript
// lib/utils/convert.ts
export function toCamelCase(obj: Record<string, any>): Record<string, any> {
  return Object.keys(obj).reduce((acc, key) => {
    const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
    acc[camelKey] = obj[key]
    return acc
  }, {})
}

export function toSnakeCase(obj: Record<string, any>): Record<string, any> {
  return Object.keys(obj).reduce((acc, key) => {
    const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase()
    acc[snakeKey] = obj[key]
    return acc
  }, {})
}
```

## API Client with Type Safety

```typescript
// lib/api.ts
import { TodoCreate, TodoUpdate, Todo } from '@/shared/types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken()

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Todos
  async getTodos(params?: { status?: string; skip?: number; limit?: number }): Promise<Todo[]> {
    const query = new URLSearchParams(params as any).toString()
    return this.request<Todo[]>(`/api/v1/todos?${query}`)
  }

  async getTodo(id: string): Promise<Todo> {
    return this.request<Todo>(`/api/v1/todos/${id}`)
  }

  async createTodo(data: TodoCreate): Promise<Todo> {
    return this.request<Todo>('/api/v1/todos', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateTodo(id: string, data: TodoUpdate): Promise<Todo> {
    return this.request<Todo>(`/api/v1/todos/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteTodo(id: string): Promise<void> {
    await this.request(`/api/v1/todos/${id}`, {
      method: 'DELETE',
    })
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token')
    }
    return null
  }
}

export const api = new APIClient()
```

## Runtime Validators

```typescript
// lib/validators.ts
import { z } from 'zod'

export const todoSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(500),
  description: z.string().max(2000).nullable(),
  status: z.enum(['pending', 'in_progress', 'completed']),
  priority: z.number().int().min(1).max(5),
  completed: z.boolean(),
  userId: z.string().uuid(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime().nullable(),
})

export const todoCreateSchema = todoSchema.omit({
  id: true,
  userId: true,
  createdAt: true,
  updatedAt: true,
})

export const todoUpdateSchema = todoCreateSchema.partial()

export type Todo = z.infer<typeof todoSchema>
export type TodoCreate = z.infer<typeof todoCreateSchema>
export type TodoUpdate = z.infer<typeof todoUpdateSchema>

// Runtime validation
export function validateTodo(data: unknown): Todo {
  return todoSchema.parse(data)
}

export function validateTodoCreate(data: unknown): TodoCreate {
  return todoCreateSchema.parse(data)
}
```

## Contract Testing

### Integration Test Example

```typescript
// tests/integration/api-contract.test.ts
import { describe, it, expect } from 'vitest'
import { api } from '@/lib/api'
import { todoSchema } from '@/lib/validators'

describe('API Contract Tests', () => {
  it('should return todos matching schema', async () => {
    const todos = await api.getTodos()

    expect(Array.isArray(todos)).toBe(true)

    todos.forEach(todo => {
      // Validate against schema
      const result = todoSchema.safeParse(todo)
      expect(result.success).toBe(true)

      // Verify required fields
      expect(todo).toHaveProperty('id')
      expect(todo).toHaveProperty('title')
      expect(todo).toHaveProperty('userId')
    })
  })

  it('should create todo and return correct schema', async () => {
    const newTodo = await api.createTodo({
      title: 'Test todo',
      description: 'Test description',
      status: 'pending',
      priority: 1,
    })

    const result = todoSchema.safeParse(newTodo)
    expect(result.success).toBe(true)
    expect(newTodo.id).toBeDefined()
  })
})
```

## Common Integration Pitfalls

### 1. Type Mismatches

**Problem**: Backend uses `datetime`, frontend expects `string`

**Solution**:
```typescript
// Backend: Return ISO 8601 string
from datetime import datetime
datetime.utcnow().isoformat()  # "2025-01-01T12:00:00"

// Frontend: Parse string to Date
const createdAt = new Date(todo.createdAt)
```

### 2. Optional vs Required

**Problem**: Backend field required, frontend marked optional

**Solution**:
```typescript
// Backend
description: Optional[str] = Field(default=None)

// Frontend
description: string | null  // Match backend nullability
```

### 3. Enum Discrepancies

**Problem**: Status enum values don't match

**Solution**:
```typescript
// Backend: Python Enum
class TodoStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

// Frontend: TypeScript Enum/Union
type TodoStatus = 'pending' | 'completed' | 'in_progress'
```

## Outputs

This agent produces:

1. **Integration Checklist** - Complete checklist for frontend-backend alignment
2. **Contract Verification Report** - Analysis of contract mismatches and issues
3. **Type Definitions** - Shared TypeScript types matching backend schemas
4. **API Client** - Type-safe API client with validation

## Integration Points

- Works with **Frontend Architecture Agent** to ensure types match components
- Works with **Backend API Agent** to validate endpoint contracts
- Works with **Data Persistence Agent** to ensure schema alignment

## When to Use

Use this agent when:
- Designing new API endpoints
- Creating TypeScript types from backend models
- Validating data contracts between frontend and backend
- Debugging type mismatches
- Running integration tests
- Ensuring consistent naming conventions
