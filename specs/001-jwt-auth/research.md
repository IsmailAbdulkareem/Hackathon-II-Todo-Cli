# Research: JWT-Based Authentication Implementation

**Feature**: 001-jwt-auth
**Date**: 2026-01-09
**Phase**: 0 (Research)

## Purpose

This document resolves technical unknowns and clarifies implementation approaches for JWT-based authentication using Better Auth (frontend) and python-jose (backend).

## Research Questions

### Q1: How does Better Auth integrate with Next.js 16+ App Router?

**Answer**: Better Auth provides a Next.js adapter that works with the App Router through:
- API route handlers in `app/api/auth/[...all]/route.ts`
- Server-side session management with JWT token issuance
- Built-in credential provider for email/password authentication
- Automatic JWT signing with configurable secret (BETTER_AUTH_SECRET)

**Implementation Approach**:
```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth"
export const { GET, POST } = auth.handler()
```

**Key Configuration**:
- `BETTER_AUTH_SECRET`: Shared secret for JWT signing (must match backend)
- `BETTER_AUTH_URL`: Base URL for authentication endpoints
- Database adapter: Better Auth can store user credentials in its own database

**Decision**: Use Better Auth's built-in credential provider with separate user database (not the task database). Frontend handles all authentication logic.

---

### Q2: How does python-jose verify JWT tokens in FastAPI?

**Answer**: python-jose provides JWT verification through the `jose.jwt.decode()` function:

```python
from jose import jwt, JWTError

def verify_jwt_token(token: str, secret: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"]  # Better Auth default algorithm
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Implementation Approach**:
- Create FastAPI dependency `get_current_user()` that extracts and verifies JWT
- Extract `Authorization: Bearer <token>` header
- Decode JWT using shared BETTER_AUTH_SECRET
- Extract `user_id` from JWT claims
- Return authenticated user_id for route handlers

**Decision**: Implement JWT verification as a FastAPI dependency that can be injected into all protected routes.

---

### Q3: What JWT claims does Better Auth include by default?

**Answer**: Better Auth JWT tokens typically include:
- `sub` (subject): User ID
- `iat` (issued at): Token creation timestamp
- `exp` (expiration): Token expiration timestamp
- `email`: User email address (optional)

**Mapping to Backend**:
- Backend will extract `sub` claim as `user_id`
- Backend will validate `exp` claim for token expiration
- Backend will ignore other claims (email, etc.)

**Decision**: Backend extracts `user_id` from JWT `sub` claim and uses it for all authorization checks.

---

### Q4: How should the shared secret (BETTER_AUTH_SECRET) be managed?

**Answer**: The secret must be:
1. **Generated**: Use cryptographically secure random string (minimum 32 characters)
2. **Stored**: Environment variables in both frontend and backend
3. **Shared**: Same value in both `.env` files

**Frontend (.env.local)**:
```bash
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

**Backend (.env)**:
```bash
BETTER_AUTH_SECRET=your-secret-key-here
DATABASE_URL=postgresql://...
```

**Security Considerations**:
- Never commit secrets to version control
- Use different secrets for development/production
- Rotate secrets periodically in production

**Decision**: Document secret generation in quickstart guide. Require manual secret setup in both environments.

---

### Q5: How should HTTP 401 vs 403 status codes be used?

**Answer**: Based on RFC 7235 and REST best practices:

**401 Unauthorized** (Authentication Failure):
- Missing `Authorization` header
- Invalid JWT signature
- Malformed JWT token
- Expired JWT token
- JWT verification fails for any reason

**403 Forbidden** (Authorization Failure):
- Valid JWT token (authentication succeeded)
- User authenticated but lacks permission
- JWT `user_id` does not match URL `user_id`
- Attempting to access another user's resources

**Implementation**:
```python
# 401: Authentication failure
if not token:
    raise HTTPException(status_code=401, detail="Missing authentication token")

# 401: Invalid token
try:
    payload = jwt.decode(token, secret, algorithms=["HS256"])
except JWTError:
    raise HTTPException(status_code=401, detail="Invalid or expired token")

# 403: Authorization failure
jwt_user_id = payload.get("sub")
if jwt_user_id != url_user_id:
    raise HTTPException(status_code=403, detail="Access denied")
```

**Decision**: Implement two-stage validation: authentication (401) then authorization (403).

---

### Q6: Should the backend validate that the user exists in a user table?

**Answer**: **No** - Backend does not need a user table because:
- Better Auth manages user credentials and user database (frontend responsibility)
- JWT token signature verification proves the token was issued by Better Auth
- If JWT signature is valid, the user exists in Better Auth's system
- Backend only needs to verify JWT signature and extract `user_id`

**Rationale**:
- Stateless architecture: Backend trusts JWT signature
- No user synchronization needed between frontend and backend
- Simpler backend implementation (no user table, no user CRUD)

**Edge Case**: If a user is deleted from Better Auth but has a valid JWT:
- Token remains valid until expiration (stateless architecture)
- This is acceptable because token expiration is short (e.g., 24 hours)
- No server-side token invalidation (per specification constraints)

**Decision**: Backend does NOT maintain a user table. JWT signature verification is sufficient proof of user existence.

---

### Q7: How should the frontend attach JWT tokens to API requests?

**Answer**: Better Auth provides client-side utilities to access the current session:

```typescript
import { useSession } from "@/lib/auth-client"

const { data: session } = useSession()
const token = session?.token

// Attach to API requests
fetch('/api/user123/tasks', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

**Implementation Approach**:
- Update `src/lib/api-service.ts` to include Authorization header
- Extract token from Better Auth session
- Attach to all API requests

**Decision**: Modify existing `ApiService` class to automatically include JWT token from Better Auth session.

---

### Q8: What happens when a JWT token expires while the user is active?

**Answer**:
- Backend returns HTTP 401 Unauthorized
- Frontend detects 401 response
- Frontend redirects user to login page
- User must re-authenticate to get new JWT token

**Implementation**:
```typescript
// In api-service.ts
if (response.status === 401) {
  // Token expired or invalid
  window.location.href = '/login'
  throw new Error('Session expired. Please log in again.')
}
```

**No Automatic Refresh**: Per specification, no refresh token mechanism is implemented. Users must manually re-authenticate.

**Decision**: Frontend handles 401 responses by redirecting to login page. No automatic token refresh.

---

## Technical Decisions Summary

| Decision | Rationale |
|----------|-----------|
| Better Auth handles all user registration and login | Separates authentication concerns from task management |
| python-jose verifies JWT tokens in backend | Lightweight, standard JWT library for Python |
| Backend does NOT maintain user table | Stateless architecture, JWT signature is proof of user existence |
| Shared secret (BETTER_AUTH_SECRET) in both environments | Required for JWT signing (frontend) and verification (backend) |
| JWT `sub` claim maps to `user_id` | Standard JWT claim for user identity |
| Two-stage validation: 401 for auth, 403 for authz | Clear separation of authentication vs authorization failures |
| No automatic token refresh | Simplifies implementation, users re-authenticate on expiration |
| Frontend redirects to login on 401 | Standard UX pattern for expired sessions |

## Dependencies Confirmed

**Frontend**:
- `better-auth` - Authentication library for Next.js
- `@better-auth/react` - React hooks for Better Auth

**Backend**:
- `python-jose[cryptography]` - JWT verification library
- `passlib[bcrypt]` - Password hashing (used by Better Auth, not backend)

## Open Questions

None - all technical unknowns have been resolved.

## Next Steps

Proceed to Phase 1 (Design):
1. Generate `data-model.md` with User and JWT token structure
2. Generate API contracts for JWT middleware
3. Generate `quickstart.md` with step-by-step implementation guide
