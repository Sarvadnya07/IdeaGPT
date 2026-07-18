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

    DEFAULT_PROVIDER: str = "mock"
    ENABLE_OPENAI: bool = False
    ENABLE_GEMINI: bool = False
    ENABLE_OLLAMA: bool = False
    OLLAMA_URL: str = "http://localhost:11434"
    CUSTOM_PROVIDER_URL: Optional[str] = None
    CUSTOM_PROVIDER_KEY: Optional[str] = None

settings = Settings()
