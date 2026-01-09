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
            settings.BETTER_AUTH_SECRET,
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
