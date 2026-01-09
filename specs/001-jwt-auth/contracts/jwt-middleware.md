# API Contract: JWT Verification Middleware

**Feature**: 001-jwt-auth
**Component**: Backend JWT Verification
**Date**: 2026-01-09

## Overview

This contract defines the JWT verification middleware that protects all task API endpoints. The middleware extracts, verifies, and validates JWT tokens before allowing access to protected resources.

## Middleware Function

### `get_current_user_id()`

**Purpose**: FastAPI dependency that verifies JWT tokens and extracts authenticated user ID.

**Signature**:
```python
async def get_current_user_id(
    authorization: str = Header(None)
) -> str
```

**Input**:
- `authorization`: HTTP Authorization header (format: `Bearer <token>`)

**Output**:
- `str`: Authenticated user ID extracted from JWT `sub` claim

**Exceptions**:

| Status Code | Condition | Detail Message |
|-------------|-----------|----------------|
| 401 | Missing Authorization header | "Missing authentication token" |
| 401 | Invalid header format (not "Bearer <token>") | "Invalid authorization header format" |
| 401 | Invalid JWT signature | "Invalid or expired token" |
| 401 | Expired JWT token | "Invalid or expired token" |
| 401 | Malformed JWT token | "Invalid or expired token" |
| 401 | Missing `sub` claim in JWT | "Invalid token claims" |

**Implementation**:
```python
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
    # Check if Authorization header is present
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Validate header format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = parts[1]

    # Verify JWT token
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

    # Extract user_id from sub claim
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user_id
```

---

## Authorization Validation

### `validate_user_ownership()`

**Purpose**: Validates that the authenticated user (from JWT) matches the user in the URL path.

**Signature**:
```python
def validate_user_ownership(
    jwt_user_id: str,
    url_user_id: str
) -> None
```

**Input**:
- `jwt_user_id`: User ID extracted from JWT token
- `url_user_id`: User ID from URL path parameter

**Output**:
- `None` (raises exception if validation fails)

**Exceptions**:

| Status Code | Condition | Detail Message |
|-------------|-----------|----------------|
| 403 | JWT user_id != URL user_id | "Access denied: You can only access your own resources" |

**Implementation**:
```python
def validate_user_ownership(
    jwt_user_id: str,
    url_user_id: str
) -> None:
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

## Protected Route Pattern

### Example: Get All Tasks

**Before (No Authentication)**:
```python
@router.get("/{user_id}/tasks", response_model=list[TaskRead])
async def get_all_tasks(
    user_id: str = Path(...),
    session: Session = Depends(get_session)
) -> list[Task]:
    # Query tasks by user_id from URL (INSECURE)
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks
```

**After (With JWT Authentication)**:
```python
@router.get("/{user_id}/tasks", response_model=list[TaskRead])
async def get_all_tasks(
    user_id: str = Path(...),
    jwt_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> list[Task]:
    # Validate user ownership
    validate_user_ownership(jwt_user_id, user_id)

    # Query tasks by JWT user_id (SECURE)
    statement = select(Task).where(Task.user_id == jwt_user_id)
    tasks = session.exec(statement).all()
    return tasks
```

**Key Changes**:
1. Add `jwt_user_id: str = Depends(get_current_user_id)` to extract authenticated user
2. Call `validate_user_ownership(jwt_user_id, user_id)` to check authorization
3. Use `jwt_user_id` (not `user_id`) in database queries

---

## Configuration

### Environment Variables

**Backend (.env)**:
```bash
BETTER_AUTH_SECRET=<shared-secret-32-chars-minimum>
```

**Settings Class**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    better_auth_secret: str
    database_url: str
    cors_origins: str

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Error Response Format

All authentication/authorization errors follow this format:

```json
{
  "detail": "Error message here"
}
```

**Examples**:

**401 Unauthorized (Missing Token)**:
```json
{
  "detail": "Missing authentication token"
}
```

**401 Unauthorized (Invalid Token)**:
```json
{
  "detail": "Invalid or expired token"
}
```

**403 Forbidden (Wrong User)**:
```json
{
  "detail": "Access denied: You can only access your own resources"
}
```

---

## Testing Contract

### Unit Tests

**Test: Valid JWT Token**:
```python
def test_get_current_user_id_valid_token():
    token = create_test_jwt(user_id="user123")
    user_id = await get_current_user_id(f"Bearer {token}")
    assert user_id == "user123"
```

**Test: Missing Authorization Header**:
```python
def test_get_current_user_id_missing_header():
    with pytest.raises(HTTPException) as exc:
        await get_current_user_id(None)
    assert exc.value.status_code == 401
    assert "Missing authentication token" in exc.value.detail
```

**Test: Invalid Token Format**:
```python
def test_get_current_user_id_invalid_format():
    with pytest.raises(HTTPException) as exc:
        await get_current_user_id("InvalidFormat")
    assert exc.value.status_code == 401
```

**Test: Expired Token**:
```python
def test_get_current_user_id_expired_token():
    token = create_expired_jwt(user_id="user123")
    with pytest.raises(HTTPException) as exc:
        await get_current_user_id(f"Bearer {token}")
    assert exc.value.status_code == 401
    assert "Invalid or expired token" in exc.value.detail
```

**Test: User Ownership Validation**:
```python
def test_validate_user_ownership_mismatch():
    with pytest.raises(HTTPException) as exc:
        validate_user_ownership("user123", "user456")
    assert exc.value.status_code == 403
    assert "Access denied" in exc.value.detail
```

---

## Integration with Existing Routes

### Routes to Protect

All task routes must be updated:

1. `GET /{user_id}/tasks` - Get all tasks
2. `POST /{user_id}/tasks` - Create task
3. `GET /{user_id}/tasks/{id}` - Get single task
4. `PUT /{user_id}/tasks/{id}` - Update task
5. `DELETE /{user_id}/tasks/{id}` - Delete task
6. `PATCH /{user_id}/tasks/{id}/complete` - Toggle completion

### Routes to Keep Public

These routes remain public (no JWT required):

1. `GET /` - Health check
2. `GET /docs` - API documentation
3. `GET /redoc` - ReDoc documentation

---

## Security Guarantees

This middleware provides:

✅ **Authentication**: Only requests with valid JWT tokens are allowed
✅ **Authorization**: Users can only access their own resources
✅ **Stateless**: No server-side session storage
✅ **Tamper-Proof**: Invalid signatures are rejected
✅ **Expiration**: Expired tokens are rejected
✅ **User Isolation**: JWT user_id vs URL user_id comparison prevents cross-user access

---

## Performance Considerations

- JWT verification adds ~10-50ms latency per request
- No database queries for authentication (stateless)
- Signature verification is CPU-bound (HS256 algorithm)
- Consider caching decoded tokens for repeated requests (optional optimization)

---

## Compliance with Specification

This contract satisfies:

- **FR-B001**: Backend uses python-jose for JWT verification
- **FR-B002**: Backend loads BETTER_AUTH_SECRET from environment
- **FR-B003**: Backend extracts user_id from JWT claims
- **FR-B004**: Backend compares JWT user_id with URL user_id
- **FR-B005**: Backend returns 403 when user_id mismatch
- **FR-B006**: Backend returns 401 for missing tokens
- **FR-B007**: Backend returns 401 for invalid tokens
- **FR-B008**: Backend returns 401 for expired tokens
- **FR-B009**: Backend filters queries by JWT user_id
