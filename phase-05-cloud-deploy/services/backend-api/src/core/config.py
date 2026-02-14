"""
Application configuration settings.

All settings are loaded from environment variables with sensible defaults
for local development. Production deployments should override via .env file
or Kubernetes secrets.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # Application configuration
    APP_NAME: str = "TaskAI Backend API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production

    # Database configuration
    DATABASE_URL: str

    # CORS configuration
    CORS_ORIGINS: str = "http://localhost:3000"

    # JWT Authentication configuration
    BETTER_AUTH_SECRET: str

    # OpenAI configuration (Phase 3: AI Chatbot)
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    MCP_SERVER_PORT: int = 8001

    # Dapr configuration (Phase 5: Microservices)
    DAPR_HTTP_PORT: int = 3500
    DAPR_GRPC_PORT: int = 50001
    DAPR_APP_ID: str = "backend-api"
    DAPR_PUBSUB_NAME: str = "kafka-pubsub"
    DAPR_STATE_STORE_NAME: str = "statestore"
    DAPR_SECRETS_STORE_NAME: str = "kubernetes"

    # Kafka configuration (Phase 5: Event-Driven Architecture)
    KAFKA_BROKER_URL: str = "localhost:9092"
    KAFKA_TOPIC_TASK_EVENTS: str = "task-events"
    KAFKA_TOPIC_REMINDERS: str = "reminders"
    KAFKA_TOPIC_TASK_UPDATES: str = "task-updates"
    KAFKA_CONSUMER_GROUP: str = "taskai-backend-api"

    # Resend configuration (Phase 5: Email Notifications)
    RESEND_API_KEY: str = ""  # Optional for local dev
    RESEND_FROM_EMAIL: str = "noreply@taskai.app"
    RESEND_FROM_NAME: str = "TaskAI"

    # Service URLs (Phase 5: Microservices Communication)
    RECURRING_SERVICE_URL: str = "http://localhost:8002"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8003"
    FRONTEND_URL: str = "http://localhost:3000"

    # Feature flags (Phase 5: Advanced Features)
    ENABLE_REAL_TIME_SYNC: bool = True
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_RECURRING_TASKS: bool = True
    ENABLE_AI_CHAT: bool = True

    # Performance configuration
    MAX_TASKS_PER_USER: int = 10000
    MAX_TAGS_PER_USER: int = 100
    MAX_REMINDERS_PER_TASK: int = 5
    SEARCH_RESULTS_LIMIT: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into a list of origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    @property
    def dapr_base_url(self) -> str:
        """Get Dapr HTTP base URL."""
        return f"http://localhost:{self.DAPR_HTTP_PORT}"

    @property
    def kafka_brokers_list(self) -> list[str]:
        """Parse KAFKA_BROKER_URL string into a list of brokers."""
        return [broker.strip() for broker in self.KAFKA_BROKER_URL.split(",")]


# Global settings instance
settings = Settings()
