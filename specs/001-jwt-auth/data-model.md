# Data Model: JWT-Based Authentication

**Feature**: 001-jwt-auth
**Date**: 2026-01-09
**Phase**: 1 (Design)

## Overview

This document defines the data structures for JWT-based authentication. The system uses a **stateless architecture** where user credentials are managed by Better Auth (frontend) and the backend only verifies JWT tokens.

## Key Entities

### 1. User (Frontend Only - Better Auth)

**Location**: Better Auth database (managed by Better Auth library)

**Purpose**: Stores user credentials and authentication information. Backend does NOT have access to this table.

```typescript
interface User {
  id: string              // UUID - Primary key
  email: string           // Unique email address
  password: string        // Hashed password (bcrypt)
  emailVerified: boolean  // Email verification status
  createdAt: Date         // Account creation timestamp
  updatedAt: Date         // Last update timestamp
}
```

**Constraints**:
- `email` must be unique
- `password` is hashed using bcrypt (never stored in plaintext)
- Managed entirely by Better Auth library
- Backend never queries or modifies this table

**Relationships**:
- One User can have many Tasks (via `user_id` foreign key in Task table)
- Relationship is logical only (no database foreign key constraint)

---

### 2. JWT Token (Stateless - Not Stored)

**Location**: Client-side storage (httpOnly cookie or memory) and transmitted in HTTP headers

**Purpose**: Cryptographically signed token proving user identity. Not stored in any database (stateless architecture).

```typescript
interface JWTPayload {
  sub: string       // Subject - User ID (UUID)
  email: string     // User email address
  iat: number       // Issued at timestamp (Unix epoch)
  exp: number       // Expiration timestamp (Unix epoch)
}
```

**Token Format**:
```
Authorization: Bearer <JWT_TOKEN>

Example JWT structure:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzA0MDY3MjAwLCJleHAiOjE3MDQxNTM2MDB9.signature
```

**Constraints**:
- Signed with BETTER_AUTH_SECRET using HS256 algorithm
- Expiration time: 24 hours (configurable in Better Auth)
- Cannot be revoked (stateless architecture)
- Must be verified on every backend request

**Lifecycle**:
1. **Issuance**: Better Auth issues JWT after successful login
2. **Storage**: Frontend stores in httpOnly cookie or secure memory
3. **Transmission**: Attached to every API request in Authorization header
4. **Verification**: Backend verifies signature and expiration
5. **Expiration**: Token becomes invalid after `exp` timestamp
6. **Renewal**: User must re-authenticate to get new token

---

### 3. Task (Backend Database)

**Location**: PostgreSQL database (Neon) - `tasks` table

**Purpose**: Stores user tasks with ownership tracking via `user_id`.

```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str                 # UUID - Primary key
    user_id: str            # User identifier from JWT (indexed)
    title: str              # Task title (max 500 chars)
    description: str | None # Task description (max 2000 chars, optional)
    completed: bool         # Completion status (default: False)
    created_at: datetime    # Creation timestamp (UTC)
    updated_at: datetime    # Last update timestamp (UTC)
```

**Constraints**:
- `user_id` is indexed for fast filtering
- `user_id` comes from JWT `sub` claim (not from request body/URL)
- All queries MUST filter by authenticated `user_id`
- No foreign key to User table (stateless architecture)

**Relationships**:
- Many Tasks belong to one User (logical relationship via `user_id`)
- No database-level foreign key constraint
- User existence is proven by valid JWT signature

---

## Data Flow

### Authentication Flow

```
1. User Registration (Frontend Only)
   ┌─────────┐
   │ Browser │ ──register──> Better Auth ──store──> User DB
   └─────────┘                                       (Frontend)

2. User Login (Frontend Only)
   ┌─────────┐
   │ Browser │ ──login──> Better Auth ──verify──> User DB
   └─────────┘                 │                   (Frontend)
                               │
                               ├──issue JWT──> Browser
                               │               (httpOnly cookie)
                               └──sign with──> BETTER_AUTH_SECRET

3. API Request (Frontend → Backend)
   ┌─────────┐
   │ Browser │ ──GET /api/user123/tasks──> Backend
   └─────────┘    Authorization: Bearer <JWT>
                               │
                               ├──verify JWT──> python-jose
                               │                (BETTER_AUTH_SECRET)
                               │
                               ├──extract user_id──> JWT.sub
                               │
                               ├──compare user_id──> URL user_id
                               │  (user123 == JWT.sub?)
                               │
                               └──query tasks──> PostgreSQL
                                  WHERE user_id = JWT.sub
```

### Authorization Flow

```
Request: GET /api/user123/tasks
Authorization: Bearer <JWT>

Step 1: Extract JWT from Authorization header
  ├─ Missing header? → 401 Unauthorized
  └─ Header present → Continue

Step 2: Verify JWT signature
  ├─ Invalid signature? → 401 Unauthorized
  ├─ Expired token? → 401 Unauthorized
  ├─ Malformed token? → 401 Unauthorized
  └─ Valid signature → Continue

Step 3: Extract user_id from JWT.sub
  └─ user_id = JWT.sub (e.g., "user123")

Step 4: Compare JWT user_id with URL user_id
  ├─ JWT.sub != URL.user_id? → 403 Forbidden
  └─ JWT.sub == URL.user_id → Continue

Step 5: Query database
  └─ SELECT * FROM tasks WHERE user_id = JWT.sub
```

---

## Database Schema Changes

### No Changes to Existing Task Table

The existing `tasks` table already has the required structure:
- `user_id` field exists and is indexed
- No schema migration needed

### No New Tables Required

**Backend does NOT create**:
- ❌ User table (managed by Better Auth in frontend)
- ❌ Token blacklist table (stateless architecture)
- ❌ Session table (stateless architecture)

---

## Environment Variables

### Frontend (.env.local)

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=<shared-secret-32-chars-minimum>
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_DATABASE_URL=<separate-database-for-users>

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)

```bash
# JWT Verification
BETTER_AUTH_SECRET=<same-shared-secret-as-frontend>

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/tasks_db

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

---

## Security Considerations

### JWT Token Security

1. **Secret Management**:
   - BETTER_AUTH_SECRET must be cryptographically random (minimum 32 characters)
   - Never commit secrets to version control
   - Use different secrets for development/production

2. **Token Transmission**:
   - Always use HTTPS in production
   - httpOnly cookies prevent XSS attacks
   - Authorization header for API requests

3. **Token Expiration**:
   - Short expiration time (24 hours recommended)
   - No automatic refresh (users must re-authenticate)
   - Expired tokens are rejected with 401

### User Isolation

1. **Backend Enforcement**:
   - All queries filter by JWT `user_id` (never URL `user_id`)
   - JWT `user_id` vs URL `user_id` comparison prevents unauthorized access
   - 403 Forbidden for valid tokens attempting to access other users' data

2. **No Trust in Client Input**:
   - Backend ignores `user_id` from request body
   - Backend ignores `user_id` from URL for authorization
   - Only JWT `sub` claim is trusted (after signature verification)

---

## Testing Considerations

### Unit Tests

- JWT verification logic (valid/invalid/expired tokens)
- User ID extraction from JWT claims
- Authorization comparison (JWT user_id vs URL user_id)

### Integration Tests

- End-to-end authentication flow (register → login → API request)
- Token expiration handling
- Unauthorized access attempts (401 and 403 scenarios)

### Security Tests

- Tampered JWT tokens (invalid signature)
- Expired JWT tokens
- Missing Authorization header
- Cross-user access attempts (User A accessing User B's tasks)

---

## Migration Path

### Phase 1: Add JWT Verification (Backend)

1. Install `python-jose[cryptography]`
2. Create JWT verification dependency
3. Add dependency to existing task routes
4. No database changes needed

### Phase 2: Integrate Better Auth (Frontend)

1. Install `better-auth` and `@better-auth/react`
2. Configure Better Auth with separate user database
3. Create login/register pages
4. Update API service to include JWT token

### Phase 3: Testing and Validation

1. Test authentication flow
2. Test authorization enforcement
3. Test token expiration handling
4. Security testing (unauthorized access attempts)

---

## Summary

This data model implements **stateless JWT authentication** with:
- ✅ User credentials managed by Better Auth (frontend)
- ✅ JWT tokens for stateless authentication
- ✅ Backend verification using python-jose
- ✅ User isolation enforced by JWT claims
- ✅ No server-side sessions or token storage
- ✅ Clear separation of frontend (auth) and backend (verification) responsibilities
