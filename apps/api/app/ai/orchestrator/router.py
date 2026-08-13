from app.core.config import settings
from app.ai.exceptions.ai_exceptions import AIUnavailableException

class AIRouter:
    @staticmethod
    def route(strategy: str = "auto", preferred: str = None) -> str:
        """
        Routes a request to a provider name based on strategy and availability.
        Enforces Safeguard #2: Raises AIUnavailableException if no real provider is available in production.
        """
        if preferred and preferred != "auto":
            return preferred

        # Auto Strategy: check keys & enabled flags
        if settings.ENABLE_OPENAI and settings.OPENAI_API_KEY:
            return "openai"
        if settings.ENABLE_GEMINI and settings.GEMINI_API_KEY:
            return "gemini"
        if settings.ENABLE_OLLAMA:
            return "ollama"
        if settings.CUSTOM_PROVIDER_URL:
            return "custom"

        # Allow mock ONLY in test mode or if explicitly set as DEFAULT_PROVIDER in dev
        if settings.APP_ENV == "test" or settings.DEFAULT_PROVIDER == "mock":
            return "mock"

        raise AIUnavailableException("No active AI provider is enabled on this system.")
