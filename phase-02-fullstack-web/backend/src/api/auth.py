"""Authentication API routes."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from src.core.config import settings
from src.core.database import get_session
from src.models.user import User, UserCreate, UserLogin, Token, UserRead

# Create router for auth endpoints
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, expires_delta: timedelta = timedelta(hours=24)) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": user_id,
        "exp": expire
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")


@router.post("/sign-up", response_model=Token, status_code=status.HTTP_201_CREATED)
async def sign_up(
    user_data: UserCreate,
    session: Session = Depends(get_session)
) -> Token:
    """
    Register a new user.

    Args:
        user_data: User registration data (email, password)
        session: Database session (injected)

    Returns:
        JWT token for the new user

    Raises:
        HTTPException: 400 if email already exists
        HTTPException: 500 if database error
    """
    try:
        # Check if user already exists
        statement = select(User).where(User.email == user_data.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user with hashed password
        hashed_password = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        # Generate JWT token
        access_token = create_access_token(str(user.id))

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=str(user.id)
        )

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/sign-in", response_model=Token, status_code=status.HTTP_200_OK)
async def sign_in(
    credentials: UserLogin,
    session: Session = Depends(get_session)
) -> Token:
    """
    Authenticate a user and return JWT token.

    Args:
        credentials: User login credentials (email, password)
        session: Database session (injected)

    Returns:
        JWT token for authenticated user

    Raises:
        HTTPException: 401 if credentials are invalid
        HTTPException: 500 if database error
    """
    try:
        # Find user by email
        statement = select(User).where(User.email == credentials.email)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Generate JWT token
        access_token = create_access_token(str(user.id))

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=str(user.id)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_current_user(
    user_id: str = Depends(lambda: None),  # Will be replaced with JWT dependency
    session: Session = Depends(get_session)
) -> User:
    """
    Get current authenticated user.

    Args:
        user_id: User ID from JWT token
        session: Database session (injected)

    Returns:
        Current user information

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 404 if user not found
    """
    # TODO: Implement JWT verification dependency
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented yet"
    )
