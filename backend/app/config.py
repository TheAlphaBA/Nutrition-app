"""
Application configuration using Pydantic Settings.
Loads values from environment variables or .env file.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Settings
    llm_provider: str = "gemini"  # "gemini" or "openai"
    gemini_api_key: str = ""
    openai_api_key: str = ""

    # Database
    database_url: str = "sqlite:///./nutrition.db"

    # Environment
    environment: str = "development"

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Logging
    log_level: str = "info"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        import os
        from pathlib import Path

        env_file = Path(__file__).resolve().parent.parent / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
