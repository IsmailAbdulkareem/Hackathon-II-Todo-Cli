# Quickstart Guide: JWT Authentication Implementation

**Feature**: 001-jwt-auth
**Date**: 2026-01-09
**Estimated Implementation Time**: 4-6 hours

## Overview

This guide provides step-by-step instructions for implementing JWT-based authentication using Better Auth (frontend) and python-jose (backend).

## Prerequisites

- Node.js 20+ installed
- Python 3.13+ installed
- PostgreSQL database for Better Auth user storage
- Existing task management application running

## Phase 1: Backend JWT Verification (2-3 hours)

### Step 1.1: Install Dependencies

```bash
cd phase-02-fullstack-web/backend
pip install python-jose[cryptography]
```

**Verify Installation**:
```bash
python -c "from jose import jwt; print('python-jose installed successfully')"
```

---

### Step 1.2: Generate Shared Secret

Generate a cryptographically secure secret (minimum 32 characters):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example Output**:
```
xK9mP2vL8nQ4rT6wY1zA3bC5dE7fG9hJ0kM
```

**Save this secret** - you'll need it for both frontend and backend.

---

### Step 1.3: Update Backend Environment Variables

Edit `phase-02-fullstack-web/backend/.env`:

```bash
# Add this line (use the secret you generated)
BETTER_AUTH_SECRET=xK9mP2vL8nQ4rT6wY1zA3bC5dE7fG9hJ0kM

# Existing variables
DATABASE_URL=postgresql://...
CORS_ORIGINS=http://localhost:3000
```

---

### Step 1.4: Update Settings Configuration

Edit `phase-02-fullstack-web/backend/src/core/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    cors_origins: str
    better_auth_secret: str  # Add this line

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"

settings = Settings()
```

---

### Step 1.5: Create JWT Middleware

Create `phase-02-fullstack-web/backend/src/core/auth.py`:

```python
"""JWT authentication middleware for FastAPI."""

from fastapi import Header, HTTPException, status
from jose import jwt, JWTError
from src.core.config import settings


async def get_current_user_id(
    authorization: str = Header(None)
) -> str:
    """
    Verify JWT token and extract authenticated user ID.

    Args:
        authorization: Authorization header (Bearer <token>)

    Returns:
        Authenticated user ID from JWT sub claim

    Raises:
        HTTPException: 401 if authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = parts[1]

    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user_id


def validate_user_ownership(jwt_user_id: str, url_user_id: str) -> None:
    """
    Validate that JWT user_id matches URL user_id.

    Args:
        jwt_user_id: User ID from JWT token
        url_user_id: User ID from URL path

    Raises:
        HTTPException: 403 if user IDs don't match
    """
    if jwt_user_id != url_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources"
        )
```

---

### Step 1.6: Update Task Routes

Edit `phase-02-fullstack-web/backend/src/api/tasks.py`:

**Add imports**:
```python
from src.core.auth import get_current_user_id, validate_user_ownership
```

**Update each route** (example for GET all tasks):

```python
@router.get("/{user_id}/tasks", response_model=list[TaskRead])
async def get_all_tasks(
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),  # Add this
    session: Session = Depends(get_session)
) -> list[Task]:
    # Add this validation
    validate_user_ownership(jwt_user_id, user_id)

    # Use jwt_user_id instead of user_id for queries
    statement = select(Task).where(Task.user_id == jwt_user_id)
    tasks = session.exec(statement).all()
    return tasks
```

**Repeat for all routes**:
- `POST /{user_id}/tasks` (create_task)
- `GET /{user_id}/tasks/{id}` (get_task_by_id)
- `PUT /{user_id}/tasks/{id}` (update_task)
- `DELETE /{user_id}/tasks/{id}` (delete_task)
- `PATCH /{user_id}/tasks/{id}/complete` (toggle_task_completion)

---

### Step 1.7: Test Backend JWT Verification

**Start backend**:
```bash
cd phase-02-fullstack-web/backend
uvicorn main:app --reload
```

**Test without token (should return 401)**:
```bash
curl http://localhost:8000/api/user123/tasks
```

**Expected Response**:
```json
{"detail": "Missing authentication token"}
```

**Test with invalid token (should return 401)**:
```bash
curl -H "Authorization: Bearer invalid-token" http://localhost:8000/api/user123/tasks
```

**Expected Response**:
```json
{"detail": "Invalid or expired token"}
```

---

## Phase 2: Frontend Better Auth Integration (2-3 hours)

### Step 2.1: Install Dependencies

```bash
cd phase-02-fullstack-web/frontend
npm install better-auth @better-auth/react
```

---

### Step 2.2: Set Up Better Auth Database

Create a separate PostgreSQL database for user credentials:

```sql
CREATE DATABASE todo_auth;
```

**Get connection string**:
```
postgresql://user:password@host:5432/todo_auth?sslmode=require
```

---

### Step 2.3: Update Frontend Environment Variables

Edit `phase-02-fullstack-web/frontend/.env.local`:

```bash
# Better Auth Configuration (use the SAME secret from backend)
BETTER_AUTH_SECRET=xK9mP2vL8nQ4rT6wY1zA3bC5dE7fG9hJ0kM
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_DATABASE_URL=postgresql://user:password@host:5432/todo_auth?sslmode=require

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### Step 2.4: Create Better Auth Configuration

Create `phase-02-fullstack-web/frontend/src/lib/auth.ts`:

```typescript
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    url: process.env.BETTER_AUTH_DATABASE_URL!
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL!,
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60 * 24,
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24
    }
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false
  }
})
```

---

### Step 2.5: Create Auth API Route

Create `phase-02-fullstack-web/frontend/src/app/api/auth/[...all]/route.ts`:

```typescript
import { auth } from "@/lib/auth"

export const { GET, POST } = auth.handler()
```

---

### Step 2.6: Create Auth Client

Create `phase-02-fullstack-web/frontend/src/lib/auth-client.ts`:

```typescript
import { createAuthClient } from "@better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000"
})

export const { useSession, signIn, signUp, signOut } = authClient
```

---

### Step 2.7: Create Login Page

Create `phase-02-fullstack-web/frontend/src/app/login/page.tsx`:

```typescript
"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { signIn } from "@/lib/auth-client"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    const result = await signIn.email({ email, password })

    if (result.error) {
      setError(result.error.message)
      return
    }

    router.push("/")
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-4">
        <h1 className="text-2xl font-bold">Login</h1>

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded">
            {error}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />

        <button
          type="submit"
          className="w-full bg-blue-500 text-white p-2 rounded"
        >
          Login
        </button>

        <p className="text-center">
          Don't have an account?{" "}
          <a href="/register" className="text-blue-500">
            Register
          </a>
        </p>
      </form>
    </div>
  )
}
```

---

### Step 2.8: Create Registration Page

Create `phase-02-fullstack-web/frontend/src/app/register/page.tsx`:

```typescript
"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { signUp } from "@/lib/auth-client"

export default function RegisterPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    const result = await signUp.email({
      email,
      password,
      name: email.split("@")[0]
    })

    if (result.error) {
      setError(result.error.message)
      return
    }

    router.push("/")
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-4">
        <h1 className="text-2xl font-bold">Register</h1>

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded">
            {error}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 border rounded"
          minLength={8}
          required
        />

        <button
          type="submit"
          className="w-full bg-blue-500 text-white p-2 rounded"
        >
          Register
        </button>

        <p className="text-center">
          Already have an account?{" "}
          <a href="/login" className="text-blue-500">
            Login
          </a>
        </p>
      </form>
    </div>
  )
}
```

---

### Step 2.9: Update API Service

Edit `phase-02-fullstack-web/frontend/src/lib/api-service.ts`:

**Add auth import**:
```typescript
import { authClient } from "./auth-client"
```

**Update request method**:
```typescript
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
```

**Update all other methods** (createTask, updateTask, deleteTask, toggleComplete) to use `getAuthHeaders()`.

---

### Step 2.10: Protect Main Page

Edit `phase-02-fullstack-web/frontend/src/app/page.tsx`:

```typescript
"use client"

import { useSession } from "@/lib/auth-client"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function HomePage() {
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
      <h1>Welcome, {session.user.email}</h1>
      {/* Existing todo list component */}
    </div>
  )
}
```

---

## Phase 3: Testing (1 hour)

### Test 1: User Registration

1. Start frontend: `npm run dev`
2. Navigate to http://localhost:3000/register
3. Register with email: `test@example.com`, password: `password123`
4. Verify redirect to home page

### Test 2: User Login

1. Navigate to http://localhost:3000/login
2. Login with registered credentials
3. Verify redirect to home page

### Test 3: Authenticated API Requests

1. Open browser DevTools → Network tab
2. Create a new task
3. Verify request includes `Authorization: Bearer <token>` header
4. Verify task is created successfully

### Test 4: Token Expiration

1. Login and get JWT token
2. Wait 24 hours (or manually expire token)
3. Try to create a task
4. Verify redirect to login page with "Session expired" message

### Test 5: Unauthorized Access

1. Login as User A
2. Try to access User B's tasks via URL manipulation
3. Verify 403 Forbidden response

---

## Troubleshooting

### Issue: "Missing authentication token"

**Cause**: Frontend not sending Authorization header

**Solution**: Verify `getAuthHeaders()` is called in all API methods

---

### Issue: "Invalid or expired token"

**Cause**: BETTER_AUTH_SECRET mismatch between frontend and backend

**Solution**: Ensure both `.env` files have the SAME secret

---

### Issue: "Access denied"

**Cause**: JWT user_id doesn't match URL user_id

**Solution**: Ensure frontend uses authenticated user's ID in API URLs

---

### Issue: Better Auth database connection error

**Cause**: Invalid BETTER_AUTH_DATABASE_URL

**Solution**: Verify PostgreSQL connection string format and database exists

---

## Success Checklist

- [ ] Backend JWT verification middleware created
- [ ] All task routes protected with JWT dependency
- [ ] Better Auth installed and configured
- [ ] Login and registration pages created
- [ ] API service updated to include JWT tokens
- [ ] Main page protected with session check
- [ ] User can register successfully
- [ ] User can login successfully
- [ ] Authenticated API requests work
- [ ] Unauthorized access returns 401/403
- [ ] Token expiration redirects to login

---

## Next Steps

After completing this quickstart:

1. Run `/sp.tasks` to generate implementation tasks
2. Implement tasks in order (Red-Green-Refactor)
3. Test each task thoroughly
4. Deploy to production with proper secrets management
