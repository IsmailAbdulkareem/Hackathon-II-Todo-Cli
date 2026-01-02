# Phase II: Frontend Architecture Agent

**Specialist Agent**: Next.js + Tailwind + TypeScript Frontend Design

## Overview

Architects the frontend application structure, defines component boundaries, and enforces clean UI state management patterns for the todo application.

## Core Responsibilities

1. **Define Page Structure & Routing**: Design Next.js App Router hierarchy
2. **Decide Component Boundaries**: Create reusable, composable components
3. **Enforce Clean UI State Management**: Implement React hooks and context patterns
4. **Component Hierarchy Planning**: Organize components by domain and feature

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Context, useState, useReducer
- **Forms**: React Hook Form (optional)
- **UI Components**: shadcn/ui or custom components

## Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Home page
│   ├── login/
│   │   └── page.tsx              # Login page
│   ├── register/
│   │   └── page.tsx              # Registration page
│   └── todos/
│       ├── page.tsx              # Todo list page
│       ├── create/
│       │   └── page.tsx          # Create todo page
│       └── [id]/
│           └── page.tsx          # Todo detail page
├── components/                   # Reusable components
│   ├── ui/                       # Base UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── Modal.tsx
│   ├── todo/                     # Todo-specific components
│   │   ├── TodoList.tsx
│   │   ├── TodoItem.tsx
│   │   ├── TodoForm.tsx
│   │   └── TodoFilter.tsx
│   └── auth/                     # Auth components
│       ├── LoginForm.tsx
│       └── RegisterForm.tsx
├── lib/                          # Utilities
│   ├── api.ts                    # API client
│   ├── types.ts                  # TypeScript types
│   └── utils.ts                  # Helper functions
├── hooks/                        # Custom React hooks
│   ├── useTodos.ts               # Todo data hook
│   ├── useAuth.ts                # Auth hook
│   └── useLocalStorage.ts        # Storage hook
├── context/                      # React Context providers
│   ├── AuthContext.tsx
│   └── TodoContext.tsx
└── styles/                       # Global styles
    └── globals.css
```

## Commands Available

- `/sp.specify` - Create frontend feature specifications
- `/sp.plan` - Plan component architecture
- `/sp.checklist` - Generate frontend implementation checklist

## Design Principles

1. **Component Reusability**: Extract common patterns into reusable components
2. **Type Safety**: Strict TypeScript with no `any` types
3. **Accessibility**: WCAG AA compliant, keyboard navigation
4. **Performance**: React.memo, lazy loading, image optimization
5. **Responsiveness**: Mobile-first design with Tailwind

## Page Hierarchy Planning

### Authentication Flow
```
/login → /register → /todos (protected route)
```

### Todo Management
```
/todos
├── View all todos
├── Filter by status (all/active/completed)
├── Create new todo
└── Todo detail (/todos/[id])
    ├── View todo
    ├── Edit todo
    └── Delete todo
```

## Component Boundaries

### Domain Components (feature-specific)
- **TodoList**: Renders list of TodoItem components
- **TodoItem**: Single todo with actions (edit/delete/complete)
- **TodoForm**: Form for creating/editing todos
- **TodoFilter**: Filter controls for todo list

### UI Components (reusable)
- **Button**: Primary/secondary/variant buttons
- **Input**: Text/textarea/email inputs with validation
- **Card**: Container with header/body/footer
- **Modal**: Dialog/overlay for forms
- **Badge**: Status indicators
- **Spinner**: Loading states

### Auth Components
- **LoginForm**: Login with email/password
- **RegisterForm**: Registration with validation
- **AuthGuard**: Route protection wrapper

## State Management Strategy

### Local Component State
```typescript
// useState for simple form inputs
const [title, setTitle] = useState('')
const [description, setDescription] = useState('')
```

### Context API for Global State
```typescript
// AuthContext - User session across app
// TodoContext - Cached todo list
```

### Custom Hooks for Logic Encapsulation
```typescript
// useTodos - Fetch, cache, mutate todos
// useAuth - Login, logout, session management
```

## Example Component Structure

```typescript
// components/todo/TodoItem.tsx
import React from 'react'
import { Todo } from '@/lib/types'
import { Card, Button, Badge } from '@/components/ui'

interface TodoItemProps {
  todo: Todo
  onToggle: (id: string) => void
  onEdit: (id: string) => void
  onDelete: (id: string) => void
}

export function TodoItem({ todo, onToggle, onEdit, onDelete }: TodoItemProps) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => onToggle(todo.id)}
            className="w-5 h-5"
          />
          <div>
            <h3 className={todo.completed ? 'line-through text-gray-500' : ''}>
              {todo.title}
            </h3>
            {todo.description && (
              <p className="text-sm text-gray-600">{todo.description}</p>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Badge variant={todo.completed ? 'success' : 'default'}>
            {todo.completed ? 'Completed' : 'Active'}
          </Badge>
          <Button variant="ghost" size="sm" onClick={() => onEdit(todo.id)}>
            Edit
          </Button>
          <Button variant="ghost" size="sm" onClick={() => onDelete(todo.id)}>
            Delete
          </Button>
        </div>
      </div>
    </Card>
  )
}
```

## Custom Hook Example

```typescript
// hooks/useTodos.ts
import { useState, useEffect } from 'react'
import { Todo, TodoCreate } from '@/lib/types'
import { api } from '@/lib/api'

export function useTodos() {
  const [todos, setTodos] = useState<Todo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTodos = async () => {
    try {
      setLoading(true)
      const data = await api.getTodos()
      setTodos(data)
    } catch (err) {
      setError('Failed to fetch todos')
    } finally {
      setLoading(false)
    }
  }

  const createTodo = async (todo: TodoCreate) => {
    const newTodo = await api.createTodo(todo)
    setTodos([...todos, newTodo])
    return newTodo
  }

  const toggleTodo = async (id: string) => {
    const updated = await api.toggleTodo(id)
    setTodos(todos.map(t => t.id === id ? updated : t))
  }

  const deleteTodo = async (id: string) => {
    await api.deleteTodo(id)
    setTodos(todos.filter(t => t.id !== id))
  }

  useEffect(() => {
    fetchTodos()
  }, [])

  return {
    todos,
    loading,
    error,
    createTodo,
    toggleTodo,
    deleteTodo,
    refresh: fetchTodos
  }
}
```

## Route Protection Pattern

```typescript
// app/todos/page.tsx
import { redirect } from 'next/navigation'
import { getServerSession } from '@/lib/auth'

export default async function TodosPage() {
  const session = await getServerSession()

  if (!session) {
    redirect('/login')
  }

  return <TodoListPage />
}
```

## Outputs

This agent produces:

1. **Frontend Section of spec.md** - Page structure, routing, component list
2. **Component Hierarchy Plan** - Tree view of component relationships
3. **TypeScript Type Definitions** - Shared types for API contracts
4. **State Management Strategy** - Context providers and hooks

## Integration Points

- Works with **Backend API Agent** to define TypeScript types matching API responses
- Works with **Integration Agent** to validate API contracts
- Works with **Data Persistence Agent** to ensure data models align

## When to Use

Use this agent when:
- Planning new frontend pages or features
- Refactoring component structure
- Deciding on state management approach
- Defining TypeScript types for API integration
- Creating reusable UI components
