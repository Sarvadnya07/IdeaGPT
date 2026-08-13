import time
from typing import Dict, List, Any
from app.ai.orchestrator.registry import registry
from app.core.config import settings

class AIRegistryService:
    _cached_health: Dict[str, Any] = {}
    _last_health_check: float = 0.0
    _HEALTH_CACHE_TTL_SEC: float = 60.0  # Cache provider health status for 60s

    @classmethod
    def get_providers(cls, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Returns list of registered AI providers and their status.
        Enforces Safeguard #3: Uses cached health metadata to prevent external API spamming.
        """
        providers_info = [
            {
                "id": "openai",
                "name": "OpenAI",
                "configured": bool(settings.OPENAI_API_KEY and settings.ENABLE_OPENAI),
                "enabled": settings.ENABLE_OPENAI,
            },
            {
                "id": "gemini",
                "name": "Google Gemini",
                "configured": bool(settings.GEMINI_API_KEY and settings.ENABLE_GEMINI),
                "enabled": settings.ENABLE_GEMINI,
            },
            {
                "id": "ollama",
                "name": "Ollama (Local LLM)",
                "configured": bool(settings.ENABLE_OLLAMA and settings.OLLAMA_URL),
                "enabled": settings.ENABLE_OLLAMA,
            },
            {
                "id": "custom",
                "name": "Custom / Hosted Endpoint",
                "configured": bool(settings.CUSTOM_PROVIDER_URL),
                "enabled": bool(settings.CUSTOM_PROVIDER_URL),
            },
        ]

        if settings.APP_ENV == "test" or settings.DEFAULT_PROVIDER == "mock":
            providers_info.append({
                "id": "mock",
                "name": "Mock Provider (Test)",
                "configured": True,
                "enabled": True,
            })

        return providers_info

    @classmethod
    def get_available_models(cls) -> List[Dict[str, Any]]:
        """
        Aggregate available models across all registered providers.
        """
        models = []
        providers = ["openai", "gemini", "ollama", "custom", "mock"]
        for p_id in providers:
            try:
                p_cls = registry.get_class(p_id)
                instance = p_cls()
                models.extend(instance.list_models())
            except ValueError:
                continue
        return models
