"""
Configuration settings for recurring service.

Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Recurring service configuration."""

    # Service settings
    SERVICE_NAME: str = "recurring-service"
    SERVICE_PORT: int = 8002
    LOG_LEVEL: str = "INFO"

    # Dapr settings
    DAPR_HTTP_PORT: int = 3500
    DAPR_GRPC_PORT: int = 50001

    # Kafka/Pub-Sub settings
    PUBSUB_NAME: str = "kafka-pubsub"
    TASK_EVENTS_TOPIC: str = "task-events"

    # Backend API settings
    BACKEND_API_URL: str = "http://localhost:8000"
    BACKEND_API_APP_ID: str = "backend-api"

    # Database settings (for audit logging)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/taskai"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
