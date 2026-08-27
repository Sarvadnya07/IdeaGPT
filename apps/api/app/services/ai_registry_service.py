"""
AI Registry Service for IdeaGPT.
Proxies to the unified GatewayProviderRegistry with 60s TTL caching.
"""

import time
import logging
from typing import Dict, List, Any
from app.ai.gateway.registry import gateway_registry
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIRegistryService:
    @classmethod
    def get_providers(cls) -> List[Dict[str, Any]]:
        """
        Returns list of registered AI providers and their configuration status.
        """
        adapters = gateway_registry.list_adapters()
        results = []
        for a in adapters:
            if a.provider_id == "mock" and settings.APP_ENV not in ("test", "development"):
                continue
            results.append({
                "id": a.provider_id,
                "name": a.display_name,
                "configured": a.is_configured,
                "enabled": a.is_enabled,
                "state": a.get_provider_state().value,
                "capabilities": [c.value for c in a.capabilities],
                "byok_supported": True if a.provider_id != "mock" else False,
            })
        return results

    @classmethod
    async def get_available_models_async(cls, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Aggregate available models across all registered gateway providers.
        """
        models = await gateway_registry.get_available_models_async(force_refresh=force_refresh)
        out = []
        for m in models:
            d = m.model_dump()
            d["id"] = m.model_id
            d["name"] = m.display_name
            out.append(d)
        return out

    @classmethod
    def get_available_models(cls) -> List[Dict[str, Any]]:
        """Synchronous wrapper for models list."""
        if gateway_registry._cached_models:
            return [m.model_dump() for m in gateway_registry._cached_models]

        # Fast fallback descriptors
        results = []
        for a in gateway_registry.list_adapters():
            if a.is_enabled and a.provider_id == "groq" and a.is_configured:
                results.append({
                    "id": "llama-3.3-70b-versatile",
                    "name": "Llama 3.3 70B Versatile",
                    "provider": "groq",
                    "category": "CHAT",
                    "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT", "REASONING"],
                    "supports_structured_output": True,
                    "available": True,
                })
        return results

    @classmethod
    def refresh_registry_cache(cls):
        """Invalidate models and health cache."""
        gateway_registry.invalidate_cache()
