"""
IdeaGPT AI Gateway v1 — Central Provider and Model Registry.
Manages adapter lifecycle, 60s TTL model and health caching, and capability resolution.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from app.ai.gateway.providers.base_adapter import BaseProviderAdapter
from app.ai.gateway.providers.groq_adapter import GroqProviderAdapter
from app.ai.gateway.providers.gemini_adapter import GeminiProviderAdapter
from app.ai.gateway.providers.ollama_adapter import OllamaProviderAdapter
from app.ai.gateway.providers.openai_adapter import OpenAIProviderAdapter
from app.ai.gateway.providers.tavily_adapter import TavilyResearchProviderAdapter
from app.ai.gateway.providers.mock_adapter import MockProviderAdapter
from app.ai.gateway.models import ModelDescriptor, ProviderDescriptor
from app.ai.gateway.contracts import AICapability, ProviderState

logger = logging.getLogger(__name__)


class GatewayProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseProviderAdapter] = {}
        self._cached_models: List[ModelDescriptor] = []
        self._last_models_fetch: float = 0.0
        self._cached_health: Dict[str, ProviderDescriptor] = {}
        self._last_health_fetch: float = 0.0
        self._CACHE_TTL_SEC: float = 60.0

        # Register standard adapters
        self.register(GroqProviderAdapter())
        self.register(GeminiProviderAdapter())
        self.register(OllamaProviderAdapter())
        self.register(OpenAIProviderAdapter())
        self.register(TavilyResearchProviderAdapter())
        self.register(MockProviderAdapter())

    def register(self, adapter: BaseProviderAdapter) -> None:
        self._providers[adapter.provider_id.lower()] = adapter

    def get_adapter(self, provider_id: str) -> Optional[BaseProviderAdapter]:
        return self._providers.get(provider_id.lower())

    def list_adapters(self) -> List[BaseProviderAdapter]:
        return list(self._providers.values())

    async def get_providers_status(self, force_refresh: bool = False) -> List[ProviderDescriptor]:
        """
        Aggregate provider health and status with 60s TTL caching.
        """
        now = time.time()
        if not force_refresh and self._cached_health and (now - self._last_health_fetch < self._CACHE_TTL_SEC):
            return list(self._cached_health.values())

        health_map: Dict[str, ProviderDescriptor] = {}
        for p_id, adapter in self._providers.items():
            try:
                desc = await adapter.health()
                health_map[p_id] = desc
            except Exception as exc:
                health_map[p_id] = ProviderDescriptor(
                    id=adapter.provider_id,
                    name=adapter.display_name,
                    capabilities=adapter.capabilities,
                    state=ProviderState.UNAVAILABLE,
                    configured=adapter.is_configured,
                    enabled=adapter.is_enabled,
                    error=str(exc),
                )

        self._cached_health = health_map
        self._last_health_fetch = now
        return list(health_map.values())

    async def get_available_models_async(self, force_refresh: bool = False) -> List[ModelDescriptor]:
        """
        Aggregate available models across all registered providers with 60s TTL caching.
        """
        now = time.time()
        if not force_refresh and self._cached_models and (now - self._last_models_fetch < self._CACHE_TTL_SEC):
            return self._cached_models

        all_models: List[ModelDescriptor] = []
        for p_id, adapter in self._providers.items():
            if not adapter.is_enabled:
                continue
            try:
                p_models = await adapter.list_models()
                all_models.extend(p_models)
            except Exception as exc:
                logger.warning(f"Failed to fetch models for provider '{p_id}': {exc}")
                continue

        self._cached_models = all_models
        self._last_models_fetch = now
        return all_models

    def invalidate_cache(self) -> None:
        self._cached_models = []
        self._last_models_fetch = 0.0
        self._cached_health = {}
        self._last_health_fetch = 0.0


# Module-level singleton
gateway_registry = GatewayProviderRegistry()
