import time
import asyncio
import logging
from typing import Dict, List, Any
from app.ai.orchestrator.registry import registry
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIRegistryService:
    _cached_models: List[Dict[str, Any]] = []
    _last_models_fetch: float = 0.0
    _CACHE_TTL_SEC: float = 60.0

    @classmethod
    def get_providers(cls) -> List[Dict[str, Any]]:
        """
        Returns list of registered AI providers and their status.
        Supports automatic detection without requiring explicit ENABLE_GROQ flag.
        """
        groq_configured = bool(settings.GROQ_API_KEY and settings.ENABLE_GROQ is not False)
        groq_state = (
            "DISABLED" if settings.ENABLE_GROQ is False
            else ("AVAILABLE" if groq_configured else "NOT_CONFIGURED")
        )

        providers_info = [
            {
                "id": "groq",
                "name": "Groq AI",
                "configured": groq_configured,
                "enabled": settings.ENABLE_GROQ is not False,
                "state": groq_state,
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "configured": bool(settings.OPENAI_API_KEY and settings.ENABLE_OPENAI),
                "enabled": settings.ENABLE_OPENAI,
                "state": "AVAILABLE" if (settings.OPENAI_API_KEY and settings.ENABLE_OPENAI) else "NOT_CONFIGURED",
            },
            {
                "id": "gemini",
                "name": "Google Gemini",
                "configured": bool(settings.GEMINI_API_KEY and settings.ENABLE_GEMINI),
                "enabled": settings.ENABLE_GEMINI,
                "state": "AVAILABLE" if (settings.GEMINI_API_KEY and settings.ENABLE_GEMINI) else "NOT_CONFIGURED",
            },
            {
                "id": "ollama",
                "name": "Ollama (Local LLM)",
                "configured": bool(settings.ENABLE_OLLAMA and settings.OLLAMA_URL),
                "enabled": settings.ENABLE_OLLAMA,
                "state": "AVAILABLE" if settings.ENABLE_OLLAMA else "NOT_CONFIGURED",
            },
            {
                "id": "custom",
                "name": "Custom / Hosted Endpoint",
                "configured": bool(settings.CUSTOM_PROVIDER_URL),
                "enabled": bool(settings.CUSTOM_PROVIDER_URL),
                "state": "AVAILABLE" if settings.CUSTOM_PROVIDER_URL else "NOT_CONFIGURED",
            },
        ]

        if settings.APP_ENV == "test" or (settings.APP_ENV == "development" and settings.DEFAULT_PROVIDER == "mock"):
            providers_info.append({
                "id": "mock",
                "name": "Mock Provider (Test)",
                "configured": True,
                "enabled": True,
                "state": "AVAILABLE",
            })

        return providers_info

    @classmethod
    async def get_available_models_async(cls, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Aggregate available models across all registered providers with 60s TTL caching.
        Performs dynamic model discovery for providers like Groq.
        """
        now = time.time()
        if not force_refresh and cls._cached_models and (now - cls._last_models_fetch < cls._CACHE_TTL_SEC):
            return cls._cached_models

        models: List[Dict[str, Any]] = []
        providers = ["groq", "openai", "gemini", "ollama", "custom", "mock"]

        for p_id in providers:
            try:
                p_cls = registry.get_class(p_id)
                instance = p_cls()

                if hasattr(instance, "list_models_async"):
                    p_models = await instance.list_models_async()
                else:
                    p_models = instance.list_models()

                models.extend(p_models)
            except Exception as e:
                logger.warning(f"Error fetching models for provider '{p_id}': {e}")
                continue

        cls._cached_models = models
        cls._last_models_fetch = now
        return models

    @classmethod
    def get_available_models(cls) -> List[Dict[str, Any]]:
        """Synchronous wrapper for models list."""
        if cls._cached_models:
            return cls._cached_models

        # Sync fallback
        models: List[Dict[str, Any]] = []
        providers = ["groq", "openai", "gemini", "ollama", "custom", "mock"]
        for p_id in providers:
            try:
                p_cls = registry.get_class(p_id)
                instance = p_cls()
                models.extend(instance.list_models())
            except Exception:
                continue
        return models

    @classmethod
    def refresh_registry_cache(cls):
        """Invalidate models and health cache."""
        cls._cached_models = []
        cls._last_models_fetch = 0.0
