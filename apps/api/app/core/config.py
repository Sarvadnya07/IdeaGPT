from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    PROJECT_NAME: str = "IdeaGPT API"
    VERSION: str = "1.0.0"

    DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///./ideagpt.db" # Default fallback
    REDIS_URL: Optional[str] = None

    # AI Providers (Loaded lazily, no placeholder text)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

settings = Settings()
