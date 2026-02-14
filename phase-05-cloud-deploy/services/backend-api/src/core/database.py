"""
Database connection and session management with multi-schema support.

Supports PostgreSQL schemas for microservices architecture:
- public: Shared tables (users)
- tasks: Backend API tables (tasks, tags, reminders, recurrence_rules)
- notifications: Notification Service tables
- audit: Recurring Service tables

Each model specifies its schema via __table_args__ = {"schema": "schema_name"}
"""

import logging
from typing import Generator

from sqlalchemy import text
from sqlmodel import Session, create_engine

from .config import settings

logger = logging.getLogger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Maximum number of connections to create beyond pool_size
    connect_args={
        "options": "-c search_path=public,tasks,notifications,audit"
    }
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session.

    Yields:
        Session: SQLModel database session with multi-schema support

    Usage:
        @app.get("/endpoint")
        def endpoint(session: Session = Depends(get_session)):
            # Use session here
            pass
    """
    with Session(engine) as session:
        yield session


def verify_schemas() -> bool:
    """
    Verify that required database schemas exist.

    Returns:
        bool: True if all schemas exist, False otherwise

    Raises:
        Exception: If database connection fails
    """
    required_schemas = ["public", "tasks", "notifications", "audit"]

    try:
        with Session(engine) as session:
            result = session.exec(
                text(
                    "SELECT schema_name FROM information_schema.schemata "
                    "WHERE schema_name IN :schemas"
                ),
                {"schemas": tuple(required_schemas)}
            )
            existing_schemas = {row[0] for row in result}

            missing_schemas = set(required_schemas) - existing_schemas

            if missing_schemas:
                logger.warning(
                    f"Missing database schemas: {', '.join(missing_schemas)}. "
                    "Run migrations to create them."
                )
                return False

            logger.info("All required database schemas exist")
            return True

    except Exception as e:
        logger.error(f"Failed to verify database schemas: {e}")
        raise


def init_db() -> None:
    """
    Initialize database connection and verify schemas.

    Should be called during application startup.

    Raises:
        Exception: If database initialization fails
    """
    try:
        # Test database connection
        with Session(engine) as session:
            session.exec(text("SELECT 1"))

        logger.info("Database connection established")

        # Verify schemas exist
        verify_schemas()

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
