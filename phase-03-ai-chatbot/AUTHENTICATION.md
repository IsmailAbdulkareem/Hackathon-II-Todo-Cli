# JWT Authentication Guide

## Overview

This application implements stateless JWT authentication with a clear separation between frontend and backend responsibilities:

- **Frontend**: Better Auth handles user registration, login, and JWT issuance
- **Backend**: python-jose verifies JWT tokens and enforces authorization

## Architecture

### Stateless JWT Design

- **No server-side sessions**: Backend does not maintain session state
- **No token blacklists**: Tokens are valid until expiration
- **No invalidation mechanism**: Logout is client-side only (cookie deletion)

### Two-Stage Security Model

1. **Authentication (401)**: Verify JWT signature and expiration
2. **Authorization (403)**: Validate user owns the requested resource

### Component Responsibilities

#### Frontend (Better Auth)
- User registration and login
- JWT token issuance (HS256 algorithm)
- Token storage in httpOnly cookies
- Session management
- Logout (cookie deletion)

#### Backend (python-jose)
- JWT signature verification
- JWT expiration validation
- User ID extraction from 'sub' claim
- Resource ownership validation
- **IMPORTANT**: Backend is completely isolated from Better Auth's database

## Setup Instructions

### 1. Generate JWT Secret (ONE-TIME ONLY)

**CRITICAL**: Generate the JWT secret ONCE using a cryptographically secure method and store it securely. Never regenerate it casually per environment.

```bash
# Generate a secure 256-bit secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output**: `Ch-Y7I7DtTJFP7ZxEahV3J_0R9IWaOhavIfOg2HawdA`

### 2. Configure Backend Environment

Create `backend/.env`:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/tasks_db

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app

# JWT Authentication Secret (shared with frontend)
# IMPORTANT: This must match the frontend's BETTER_AUTH_SECRET
BETTER_AUTH_SECRET=Ch-Y7I7DtTJFP7ZxEahV3J_0R9IWaOhavIfOg2HawdA
```

### 3. Configure Frontend Environment

Create `frontend/.env.local`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=Ch-Y7I7DtTJFP7ZxEahV3J_0R9IWaOhavIfOg2HawdA
BETTER_AUTH_URL=http://localhost:3000

# Better Auth Database Configuration
# IMPORTANT: Better Auth can use:
# 1. The same database as your application (shared)
# 2. A separate database (dedicated)
# 3. An external identity provider
# It does NOT require a separate PostgreSQL database.
BETTER_AUTH_DATABASE_URL=postgresql://user:pass@host:5432/auth_db
```

### 4. Install Dependencies

**Backend**:
```bash
cd backend
pip install python-jose[cryptography]>=3.3.0
```

**Frontend**:
```bash
cd frontend
npm install better-auth @better-auth/react
```

## Security Features

### JWT Token Storage

**Production-grade**: httpOnly cookies ONLY

- ✅ **httpOnly cookies**: Secure, not accessible to JavaScript
- ❌ **Session storage**: Vulnerable to XSS attacks
- ❌ **Local storage**: Vulnerable to XSS attacks

Better Auth automatically uses httpOnly cookies for JWT storage.

### JWT Validation

The backend validates:

1. **Token presence**: Returns 401 if Authorization header is missing
2. **Token format**: Returns 401 if not "Bearer <token>"
3. **Signature**: Returns 401 if signature is invalid
4. **Expiration**: Returns 401 if token is expired
5. **Claims**: Returns 401 if 'sub' claim is missing
6. **Ownership**: Returns 403 if JWT user_id ≠ URL user_id

### Error Responses

**401 Unauthorized** (Authentication failure):
```json
{
  "detail": "Missing authentication token"
}
```

**403 Forbidden** (Authorization failure):
```json
{
  "detail": "Access denied: You can only access your own resources"
}
```

All 401 responses include `WWW-Authenticate: Bearer` header.

## API Usage

### Authentication Flow

1. **Register**: POST to `/api/auth/sign-up`
2. **Login**: POST to `/api/auth/sign-in`
3. **Access Protected Routes**: Include JWT in Authorization header
4. **Logout**: Client-side cookie deletion

### Making Authenticated Requests

```bash
# Get JWT token from Better Auth session
TOKEN="your-jwt-token"

# Include in Authorization header
curl -H "Authorization: Bearer $TOKEN" \
  https://api.example.com/api/user123/tasks
```

### Frontend API Service

The frontend API service automatically includes JWT tokens:

```typescript
// src/lib/api-service.ts
private async getAuthHeaders(): Promise<HeadersInit> {
  const session = await authClient.getSession();

  if (!session?.session?.token) {
    throw new Error("Not authenticated");
  }

  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${session.session.token}`
  };
}
```

## Backend Implementation

### JWT Verification Middleware

Located in `backend/src/core/auth.py`:

```python
async def get_current_user_id(
    authorization: str = Header(None)
) -> str:
    """
    Verify JWT token and extract authenticated user ID.

    Returns:
        Authenticated user ID from JWT 'sub' claim

    Raises:
        HTTPException: 401 if authentication fails
    """
    # Validates: presence, format, signature, expiration, claims
```

### User Ownership Validation

```python
def validate_user_ownership(jwt_user_id: str, url_user_id: str) -> None:
    """
    Validate that JWT user_id matches URL user_id.

    Raises:
        HTTPException: 403 if user IDs don't match
    """
```

### Protected Route Pattern

All task routes follow this pattern:

```python
@router.get("/{user_id}/tasks")
async def get_all_tasks(
    user_id: str = Depends(validate_user_id),
    jwt_user_id: str = Depends(get_current_user_id),  # JWT verification
    session: Session = Depends(get_session)
) -> list[Task]:
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    # Use jwt_user_id for database query (not url user_id)
    statement = select(Task).where(Task.user_id == jwt_user_id)
    tasks = session.exec(statement).all()
    return tasks
```

## Testing

### Security Tests

Run comprehensive security tests:

```bash
cd backend
pytest tests/test_auth_security.py -v
```

**Test coverage**:
- Missing Authorization header (401)
- Malformed Authorization header (401)
- Invalid JWT signature (401)
- Expired JWT token (401)
- Missing 'sub' claim (401)
- Cross-user access attempts (403)
- All routes require authentication (401)
- Valid token allows access

### Manual Testing

**Test authentication failure**:
```bash
curl http://localhost:8000/api/test-user/tasks
# Expected: 401 Unauthorized
```

**Test cross-user access**:
```bash
# Login as user-a, try to access user-b's tasks
curl -H "Authorization: Bearer <user-a-token>" \
  http://localhost:8000/api/user-b/tasks
# Expected: 403 Forbidden
```

## Troubleshooting

### "Missing authentication token"

**Cause**: No Authorization header in request

**Solution**: Ensure frontend includes JWT token in all API requests

### "Invalid or expired token"

**Cause**: JWT signature invalid or token expired

**Solution**:
- Verify BETTER_AUTH_SECRET matches between frontend and backend
- Check token expiration (default: 24 hours)
- Re-login to get fresh token

### "Access denied: You can only access your own resources"

**Cause**: JWT user_id doesn't match URL user_id

**Solution**: Ensure frontend uses authenticated user's ID in API URLs

### CORS Errors

**Cause**: Backend CORS_ORIGINS doesn't include frontend URL

**Solution**: Update backend/.env:
```bash
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

## Performance

### JWT Verification Latency

- **Target**: <50ms per request
- **Actual**: ~5-10ms (python-jose HS256 verification)

### Optimization Tips

1. **Use HS256 algorithm**: Faster than RS256 for symmetric keys
2. **Cache JWT secret**: Loaded once at startup
3. **Minimize token size**: Only include essential claims

## Security Best Practices

1. **Secret Management**:
   - Generate JWT secret once using cryptographically secure method
   - Store in environment variables, never in code
   - Use different secrets for development and production
   - Rotate secrets periodically (requires re-authentication)

2. **Token Expiration**:
   - Default: 24 hours
   - Adjust based on security requirements
   - Shorter expiration = more secure, more frequent logins

3. **HTTPS Only**:
   - Always use HTTPS in production
   - httpOnly cookies require secure transport

4. **CORS Configuration**:
   - Whitelist specific origins, never use "*"
   - Include credentials: true for cookie-based auth

## Architecture Decision Records

For detailed architectural decisions, see:
- ADR-001: Stateless JWT Authentication
- ADR-002: Better Auth Integration
- ADR-003: Two-Stage Security Model

## References

- [Better Auth Documentation](https://better-auth.com)
- [python-jose Documentation](https://python-jose.readthedocs.io)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
