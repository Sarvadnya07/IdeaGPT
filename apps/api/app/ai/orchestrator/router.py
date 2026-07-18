from app.core.config import settings

class AIRouter:
    @staticmethod
    def route(strategy: str = "auto", preferred: str = None) -> str:
        """
        Routes a request to a provider name based on strategy and availability.
        """
        if strategy == "user_selected" and preferred:
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

        # Fallback to DEFAULT_PROVIDER
        return settings.DEFAULT_PROVIDER
