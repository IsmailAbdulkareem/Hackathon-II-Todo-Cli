"""
Notification service configuration.

Loads settings from environment variables for:
- Dapr integration
- Resend API (email notifications)
- Kafka topics
- Retry policies
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Notification service configuration settings."""

    # Application configuration
    APP_NAME: str = "TaskAI Notification Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Dapr configuration
    DAPR_HTTP_PORT: int = 3500
    DAPR_GRPC_PORT: int = 50001
    DAPR_APP_ID: str = "notification-service"
    DAPR_APP_PORT: int = 8001
    DAPR_PUBSUB_NAME: str = "kafka-pubsub"

    # Kafka configuration
    KAFKA_TOPIC_REMINDERS: str = "reminders"
    KAFKA_CONSUMER_GROUP: str = "taskai-notification-service"

    # Resend API configuration
    RESEND_API_KEY: str
    RESEND_FROM_EMAIL: str = "noreply@taskai.app"
    RESEND_FROM_NAME: str = "TaskAI"

    # Retry configuration
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAYS: list[int] = [0, 300, 900]  # 0s, 5min, 15min in seconds

    # Email templates
    REMINDER_EMAIL_SUBJECT: str = "⏰ Reminder: {task_title}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def dapr_base_url(self) -> str:
        """Get Dapr HTTP base URL."""
        return f"http://localhost:{self.DAPR_HTTP_PORT}"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"


# Global settings instance
settings = Settings()
