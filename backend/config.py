"""
Backend Configuration

Loads configuration from environment variables with sensible defaults.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""

    # Application
    APP_NAME: str = "Bizy AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # API
    API_PREFIX: str = "/api"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # CORS
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    )

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///~/.business-agent/tasks.db"  # Default to existing CLI database
    )

    # PostgreSQL (for Phase 3 migration)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "bizy")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "bizy_password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "bizy_dev")

    @property
    def postgres_url(self) -> str:
        """Construct PostgreSQL connection URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Password Hashing
    BCRYPT_ROUNDS: int = 12

    # AI (Anthropic Claude)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@bizy.ai")

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    # Rate Limiting
    RATE_LIMIT_AUTHENTICATED: int = 100  # requests per minute
    RATE_LIMIT_UNAUTHENTICATED: int = 10  # requests per minute

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded once.
    """
    return Settings()


# Convenience export
settings = get_settings()
