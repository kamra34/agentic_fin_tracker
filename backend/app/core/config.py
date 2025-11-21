from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path
from pydantic import field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Financial Tracker API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str
    OLD_DATABASE_URL: str = ""  # Optional: for reference only

    # CORS - accepts comma-separated string from .env
    ALLOWED_ORIGINS: str = "https://agentic-fin-tracker.vercel.app,http://localhost:5174,http://localhost:3000"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI Configuration
    OPENAI_API_KEY: str
    MODEL_ID: str = "gpt-4o"

    # Environment Detection
    ENVIRONMENT: str = "development"  # Options: development, production
    RAILWAY_ENVIRONMENT: str = ""  # Railway sets this automatically

    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env

    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production (Railway or ENVIRONMENT=production)"""
        return (
            self.ENVIRONMENT.lower() == "production" or
            bool(self.RAILWAY_ENVIRONMENT) or
            os.getenv("RAILWAY_ENVIRONMENT") is not None
        )


settings = Settings()
