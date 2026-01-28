"""Application configuration using Pydantic Settings."""

from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Database
    database_url: PostgresDsn
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: RedisDsn

    # Celery
    celery_broker_url: RedisDsn
    celery_result_backend: RedisDsn

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # AI Services (placeholders)
    claude_api_key: str | None = None
    originality_api_key: str | None = None

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
