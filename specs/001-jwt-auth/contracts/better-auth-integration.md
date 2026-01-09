# API Contract: Better Auth Integration

**Feature**: 001-jwt-auth
**Component**: Frontend Authentication
**Date**: 2026-01-09

## Overview

This contract defines the Better Auth integration for user registration, login, and JWT token management in the Next.js frontend.

## Better Auth Configuration

### Installation

```bash
npm install better-auth @better-auth/react
```

### Configuration File

**Location**: `src/lib/auth.ts`

```typescript
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  // Database configuration for user credentials
  database: {
    provider: "postgresql",
    url: process.env.BETTER_AUTH_DATABASE_URL!
  },

  // JWT configuration
  secret: process.env.BETTER_AUTH_SECRET!,

  // Base URL for authentication endpoints
  baseURL: process.env.BETTER_AUTH_URL!,

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60 * 24,  // 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24    // 24 hours
    }
  },

  // Email/password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false // Optional: enable for production
  }
})
```

---

## API Route Handler

### Authentication Endpoints

**Location**: `app/api/auth/[...all]/route.ts`

```typescript
import { auth } from "@/lib/auth"

export const { GET, POST } = auth.handler()
```

**Generated Endpoints**:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/sign-up` | User registration |
| POST | `/api/auth/sign-in` | User login |
| POST | `/api/auth/sign-out` | User logout |
| GET | `/api/auth/session` | Get current session |

---

## Client-Side Integration

### Auth Client Configuration

**Location**: `src/lib/auth-client.ts`

```typescript
import { createAuthClient } from "@better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000"
})

export const { useSession, signIn, signUp, signOut } = authClient
```

---

## Registration Flow

### Sign Up Function

**Usage**:
```typescript
import { signUp } from "@/lib/auth-client"

const handleSignUp = async (email: string, password: string) => {
  try {
    const result = await signUp.email({
      email,
      password,
      name: email.split('@')[0] // Optional: extract name from email
    })

    if (result.error) {
      console.error("Registration failed:", result.error)
      return { success: false, error: result.error.message }
    }

    return { success: true, user: result.data }
  } catch (error) {
    console.error("Registration error:", error)
    return { success: false, error: "Registration failed" }
  }
}
```

**Request Format**:
```json
POST /api/auth/sign-up
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "User Name"
}
```

**Success Response (200)**:
```json
{
  "user": {
    "id": "user-uuid-here",
    "email": "user@example.com",
    "name": "User Name",
    "emailVerified": false
  },
  "session": {
    "token": "jwt-token-here",
    "expiresAt": 1704153600
  }
}
```

**Error Response (400)**:
```json
{
  "error": {
    "message": "Email already exists",
    "code": "EMAIL_ALREADY_EXISTS"
  }
}
```

---

## Login Flow

### Sign In Function

**Usage**:
```typescript
import { signIn } from "@/lib/auth-client"

const handleSignIn = async (email: string, password: string) => {
  try {
    const result = await signIn.email({
      email,
      password
    })

    if (result.error) {
      console.error("Login failed:", result.error)
      return { success: false, error: result.error.message }
    }

    return { success: true, session: result.data }
  } catch (error) {
    console.error("Login error:", error)
    return { success: false, error: "Login failed" }
  }
}
```

**Request Format**:
```json
POST /api/auth/sign-in
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Success Response (200)**:
```json
{
  "user": {
    "id": "user-uuid-here",
    "email": "user@example.com",
    "name": "User Name"
  },
  "session": {
    "token": "jwt-token-here",
    "expiresAt": 1704153600
  }
}
```

**Error Response (401)**:
```json
{
  "error": {
    "message": "Invalid email or password",
    "code": "INVALID_CREDENTIALS"
  }
}
```

---

## Session Management

### Get Current Session

**Usage**:
```typescript
import { useSession } from "@/lib/auth-client"

function ProtectedComponent() {
  const { data: session, isPending } = useSession()

  if (isPending) {
    return <div>Loading...</div>
  }

  if (!session) {
    return <div>Not authenticated</div>
  }

  return (
    <div>
      <p>Logged in as: {session.user.email}</p>
      <p>User ID: {session.user.id}</p>
    </div>
  )
}
```

**Session Object Structure**:
```typescript
interface Session {
  user: {
    id: string
    email: string
    name: string
    emailVerified: boolean
  }
  session: {
    token: string      // JWT token
    expiresAt: number  // Unix timestamp
  }
}
```

---

## Logout Flow

### Sign Out Function

**Usage**:
```typescript
import { signOut } from "@/lib/auth-client"

const handleSignOut = async () => {
  try {
    await signOut()
    // Redirect to login page
    window.location.href = "/login"
  } catch (error) {
    console.error("Logout error:", error)
  }
}
```

**Request Format**:
```json
POST /api/auth/sign-out
```

**Success Response (200)**:
```json
{
  "success": true
}
```

---

## API Service Integration

### Updated API Service with JWT

**Location**: `src/lib/api-service.ts`

```typescript
import { authClient } from "./auth-client"

class ApiService {
  private baseURL: string

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    const session = await authClient.getSession()

    if (!session?.session?.token) {
      throw new Error("Not authenticated")
    }

    return {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${session.session.token}`
    }
  }

  async getTasks(userId: string): Promise<Task[]> {
    const headers = await this.getAuthHeaders()

    const response = await fetch(`${this.baseURL}/api/${userId}/tasks`, {
      headers
    })

    if (response.status === 401) {
      // Token expired or invalid
      window.location.href = "/login"
      throw new Error("Session expired. Please log in again.")
    }

    if (response.status === 403) {
      throw new Error("Access denied")
    }

    if (!response.ok) {
      throw new Error("Failed to fetch tasks")
    }

    return response.json()
  }

  // Similar updates for createTask, updateTask, deleteTask, etc.
}

export const apiService = new ApiService()
```

---

## Route Protection

### Protected Page Example

**Location**: `app/dashboard/page.tsx`

```typescript
"use client"

import { useSession } from "@/lib/auth-client"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function DashboardPage() {
  const { data: session, isPending } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (!isPending && !session) {
      router.push("/login")
    }
  }, [session, isPending, router])

  if (isPending) {
    return <div>Loading...</div>
  }

  if (!session) {
    return null
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, {session.user.email}</p>
    </div>
  )
}
```

---

## Environment Variables

**Frontend (.env.local)**:
```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-here-minimum-32-chars
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_DATABASE_URL=postgresql://user:pass@host:5432/auth_db

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Error Handling

### Common Error Codes

| Code | Message | Action |
|------|---------|--------|
| EMAIL_ALREADY_EXISTS | Email already registered | Show error, suggest login |
| INVALID_CREDENTIALS | Invalid email or password | Show error, allow retry |
| WEAK_PASSWORD | Password too weak | Show requirements |
| SESSION_EXPIRED | Session has expired | Redirect to login |
| NETWORK_ERROR | Network request failed | Show retry button |

---

## Testing Contract

### Unit Tests

**Test: Successful Registration**:
```typescript
test("signUp creates new user", async () => {
  const result = await signUp.email({
    email: "test@example.com",
    password: "securePassword123"
  })

  expect(result.error).toBeNull()
  expect(result.data.user.email).toBe("test@example.com")
  expect(result.data.session.token).toBeDefined()
})
```

**Test: Duplicate Email Registration**:
```typescript
test("signUp rejects duplicate email", async () => {
  await signUp.email({
    email: "test@example.com",
    password: "password123"
  })

  const result = await signUp.email({
    email: "test@example.com",
    password: "password456"
  })

  expect(result.error).toBeDefined()
  expect(result.error.code).toBe("EMAIL_ALREADY_EXISTS")
})
```

**Test: Successful Login**:
```typescript
test("signIn authenticates user", async () => {
  const result = await signIn.email({
    email: "test@example.com",
    password: "securePassword123"
  })

  expect(result.error).toBeNull()
  expect(result.data.session.token).toBeDefined()
})
```

---

## Compliance with Specification

This contract satisfies:

- **FR-F001**: Frontend integrates Better Auth for registration
- **FR-F002**: Frontend uses Better Auth for credential validation
- **FR-F003**: Frontend uses Better Auth for JWT issuance
- **FR-F004**: Frontend stores JWT in httpOnly cookies
- **FR-F005**: Frontend attaches JWT to API requests
- **FR-F006**: Frontend implements logout (token deletion)
- **FR-F007**: Frontend protects routes with session checks
- **FR-F008**: Frontend handles 401 responses
- **FR-F009**: Frontend handles 403 responses
