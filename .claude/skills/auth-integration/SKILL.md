# Authentication Integration Generator

**Critical for Phases:** II, III, IV, V

Generates authentication middleware, JWT validation, and user extraction for FastAPI.

## Usage

```
/gen.auth-integration <provider> <backend-framework>

# Examples:
/gen.auth-integration "better-auth" "fastapi"
/gen.auth-integration "jwt" "fastapi"
```

## What It Generates

- Authentication middleware for FastAPI
- JWT token validation logic
- User extraction dependency
- Password hashing utilities
- Token generation and refresh
- Protected route decorators
- Session management
- OAuth integration (if applicable)

## Output Structure

```
phase-XX/src/auth/
  ├── middleware.py        # Auth middleware
  ├── jwt_handler.py      # JWT token logic
  ├── password.py          # Password hashing
  ├── dependencies.py      # FastAPI deps
  └── models.py          # Auth models (Token, User)
```

## Features

- JWT token generation and validation
- Password hashing with bcrypt
- Token refresh mechanism
- CORS configuration
- Protected route decorators
- User session management
- OAuth 2.0 support (optional)
- Rate limiting per user
- Token expiration handling

## Phase Usage

- **Phase II:** JWT auth for API
- **Phase II:** User registration/login endpoints
- **Phase III:** Auth for chat endpoints
- **Phase III:** Session management for AI conversations
- **Phase IV-V:** Auth in K8s secrets

## Example Output

```python
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# FastAPI dependency for protected routes
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    """Extract and validate user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = session.get(User, user_id)
    if user is None:
        raise credentials_exception

    return user

# Usage in endpoints
@router.post("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    """Endpoint protected by JWT authentication."""
    return {"user_id": current_user.id, "email": current_user.email}
```

## Auth Endpoints Generated

```
POST   /api/v1/auth/register    - Register new user
POST   /api/v1/auth/login       - Login and get token
POST   /api/v1/auth/refresh     - Refresh access token
POST   /api/v1/auth/logout      - Logout (invalidate token)
GET     /api/v1/auth/me          - Get current user profile
PUT     /api/v1/auth/me          - Update profile
```

## Security Features

- **Password Security:** bcrypt hashing with salt
- **JWT Security:** Short-lived tokens, secret rotation
- **Token Storage:** HttpOnly cookies (optional)
- **Rate Limiting:** Prevent brute force
- **Session Management:** Invalidate tokens on logout
- **HTTPS Enforcement:** Production only
- **CORS:** Configured for frontend domain

## Configuration (environment variables)

```bash
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
```

## Best Practices

- Never log passwords or tokens
- Use environment variables for secrets
- Implement rate limiting on auth endpoints
- Validate email format
- Strong password requirements (min 8 chars, mixed case, numbers)
- Token expiration (15-30 minutes for access tokens)
- Refresh token rotation
- Secure HttpOnly cookies for tokens
