"""
IdeaGPT AI Gateway v1 — Central Provider and Model Registry.
Manages adapter lifecycle, fast TTL model/health caching, dynamic model quarantine,
and sub-second SWR discovery.
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone

from app.core.config import settings
from app.ai.gateway.providers.base_adapter import BaseProviderAdapter
from app.ai.gateway.providers.groq_adapter import GroqProviderAdapter
from app.ai.gateway.providers.gemini_adapter import GeminiProviderAdapter
from app.ai.gateway.providers.ollama_adapter import OllamaProviderAdapter
from app.ai.gateway.providers.openai_adapter import OpenAIProviderAdapter
from app.ai.gateway.providers.tavily_adapter import TavilyResearchProviderAdapter
from app.ai.gateway.providers.mock_adapter import MockProviderAdapter
from app.ai.gateway.models import ModelDescriptor, ProviderDescriptor
from app.ai.gateway.contracts import (
    AICapability,
    CapabilityConfidence,
    ModelCategory,
    ModelStatus,
    ProviderState,
)

logger = logging.getLogger(__name__)

# Baseline fast static models for instant cold-start response (<10ms)
STATIC_BASELINE_MODELS: List[ModelDescriptor] = [
    ModelDescriptor(
        provider="groq",
        model_id="openai/gpt-oss-120b",
        display_name="GPT-OSS 120B (Groq LPU)",
        category=ModelCategory.REASONING,
        capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.REASONING],
        capability_confidence=CapabilityConfidence.VERIFIED,
        context_window=131072,
        supports_structured_output=True,
        status=ModelStatus.ACTIVE,
        configured=True,
        available=True,
    ),
    ModelDescriptor(
        provider="groq",
        model_id="llama-3.3-70b-versatile",
        display_name="Llama 3.3 70B Versatile",
        category=ModelCategory.CHAT,
        capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.REASONING],
        capability_confidence=CapabilityConfidence.VERIFIED,
        context_window=131072,
        supports_structured_output=True,
        status=ModelStatus.ACTIVE,
        configured=True,
        available=True,
    ),
    ModelDescriptor(
        provider="groq",
        model_id="llama-3.1-8b-instant",
        display_name="Llama 3.1 8B Instant",
        category=ModelCategory.CHAT,
        capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT],
        capability_confidence=CapabilityConfidence.VERIFIED,
        context_window=131072,
        supports_structured_output=True,
        status=ModelStatus.ACTIVE,
        configured=True,
        available=True,
    ),
    ModelDescriptor(
        provider="gemini",
        model_id="gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        category=ModelCategory.VISION,
        capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.VISION, AICapability.DOCUMENT_UNDERSTANDING],
        capability_confidence=CapabilityConfidence.VERIFIED,
        context_window=1048576,
        supports_structured_output=True,
        status=ModelStatus.ACTIVE,
        configured=False,
        available=False,
    ),
    ModelDescriptor(
        provider="tavily",
        model_id="tavily-search-v1",
        display_name="Tavily Deep Web Search",
        category=ModelCategory.RESEARCH,
        capabilities=[AICapability.WEB_RESEARCH],
        capability_confidence=CapabilityConfidence.VERIFIED,
        context_window=16384,
        supports_structured_output=True,
        status=ModelStatus.ACTIVE,
        configured=True,
        available=True,
    ),
]


class GatewayProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseProviderAdapter] = {}
        self._cached_models: List[ModelDescriptor] = list(STATIC_BASELINE_MODELS)
        self._last_models_fetch: float = 0.0
        self._cached_health: Dict[str, ProviderDescriptor] = {}
        self._last_health_fetch: float = 0.0
        self._CACHE_TTL_SEC: float = 60.0
        # Dynamic Model Quarantine (model_id -> (expiry_ts, reason))
        self._quarantined_models: Dict[str, tuple[float, str]] = {}

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

    def quarantine_model(self, model_id: str, duration_sec: float = 300.0, reason: str = "") -> None:
        """Quarantines a model that produced 404/403 or fatal errors, preventing repeat failures."""
        expiry = time.time() + duration_sec
        mid = model_id.lower().strip()
        self._quarantined_models[mid] = (expiry, reason)
        logger.warning(f"Quarantined model '{model_id}' for {duration_sec}s. Reason: {reason}")
        # Evict from cached models immediately
        self._cached_models = [m for m in self._cached_models if m.model_id.lower() != mid]

    def is_quarantined(self, model_id: str) -> bool:
        """Checks if a model is currently in quarantine."""
        mid = model_id.lower().strip()
        if mid not in self._quarantined_models:
            return False
        expiry, _ = self._quarantined_models[mid]
        if time.time() > expiry:
            del self._quarantined_models[mid]
            return False
        return True

    async def _fetch_adapter_health_safe(self, adapter: BaseProviderAdapter) -> ProviderDescriptor:
        try:
            if not adapter.is_configured and adapter.provider_id != "mock":
                return ProviderDescriptor(
                    id=adapter.provider_id,
                    name=adapter.display_name,
                    capabilities=adapter.capabilities,
                    state=ProviderState.NOT_CONFIGURED,
                    configured=False,
                    enabled=adapter.is_enabled,
                    latency_ms=0,
                    models_count=0,
                )
            return await asyncio.wait_for(adapter.health(), timeout=2.5)
        except Exception as exc:
            return ProviderDescriptor(
                id=adapter.provider_id,
                name=adapter.display_name,
                capabilities=adapter.capabilities,
                state=ProviderState.UNAVAILABLE,
                configured=adapter.is_configured,
                enabled=adapter.is_enabled,
                latency_ms=0,
                models_count=0,
                error=str(exc),
            )

    async def _fetch_adapter_models_safe(self, adapter: BaseProviderAdapter) -> List[ModelDescriptor]:
        try:
            if not adapter.is_enabled or (not adapter.is_configured and adapter.provider_id != "mock"):
                return []
            models = await asyncio.wait_for(adapter.list_models(), timeout=2.5)
            # Filter out quarantined models
            return [m for m in models if not self.is_quarantined(m.model_id)]
        except Exception as exc:
            logger.warning(f"Fast discovery skipped for '{adapter.provider_id}': {exc}")
            return []

    async def get_providers_status(self, force_refresh: bool = False) -> List[ProviderDescriptor]:
        """
        Aggregate provider health concurrently with 60s TTL caching.
        """
        now = time.time()
        if not force_refresh and self._cached_health and (now - self._last_health_fetch < self._CACHE_TTL_SEC):
            return list(self._cached_health.values())

        adapters = list(self._providers.values())
        results = await asyncio.gather(*[self._fetch_adapter_health_safe(a) for a in adapters], return_exceptions=True)

        health_map: Dict[str, ProviderDescriptor] = {}
        for idx, res in enumerate(results):
            a = adapters[idx]
            if isinstance(res, ProviderDescriptor):
                health_map[a.provider_id] = res
            else:
                health_map[a.provider_id] = ProviderDescriptor(
                    id=a.provider_id,
                    name=a.display_name,
                    capabilities=a.capabilities,
                    state=ProviderState.UNAVAILABLE,
                    configured=a.is_configured,
                    enabled=a.is_enabled,
                    error=str(res),
                )

        self._cached_health = health_map
        self._last_health_fetch = now
        return list(health_map.values())

    async def get_available_models_async(self, force_refresh: bool = False) -> List[ModelDescriptor]:
        """
        Aggregate available models across all registered providers concurrently with 60s TTL caching.
        Returns instantly (<10ms) from cache/baseline if available.
        """
        now = time.time()
        if not force_refresh and self._cached_models and (now - self._last_models_fetch < self._CACHE_TTL_SEC):
            return [m for m in self._cached_models if not self.is_quarantined(m.model_id)]

        adapters = list(self._providers.values())
        results = await asyncio.gather(*[self._fetch_adapter_models_safe(a) for a in adapters], return_exceptions=True)

        all_models: List[ModelDescriptor] = []
        for res in results:
            if isinstance(res, list):
                all_models.extend(res)

        if all_models:
            self._cached_models = all_models
            self._last_models_fetch = now
        elif not self._cached_models:
            self._cached_models = [m for m in STATIC_BASELINE_MODELS if not self.is_quarantined(m.model_id)]

        return [m for m in self._cached_models if not self.is_quarantined(m.model_id)]

    def invalidate_cache(self) -> None:
        self._cached_models = []
        self._last_models_fetch = 0.0
        self._cached_health = {}
        self._last_health_fetch = 0.0


# Module-level singleton
gateway_registry = GatewayProviderRegistry()
