from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # Database configuration
    DATABASE_URL: str

    # CORS configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # JWT Authentication configuration
    BETTER_AUTH_SECRET: str

    # OpenAI configuration (Phase 3: AI Chatbot)
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    MCP_SERVER_PORT: int = 8001

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into a list of origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
