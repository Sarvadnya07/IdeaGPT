import logging
from typing import Optional
from app.ai.orchestrator.registry import registry
from app.ai.providers.base import AIProvider
from app.ai.gateway.registry import gateway_registry
from app.ai.gateway.providers.base_adapter import BaseProviderAdapter
from app.ai.orchestrator.gateway_adapter import GatewayAIProviderAdapter

logger = logging.getLogger(__name__)

class ProviderFactory:
    """
    Single entry point for resolving a provider implementation.

    CANONICAL PATH: ``gateway_registry`` -> ``BaseProviderAdapter``, wrapped in
    ``GatewayAIProviderAdapter``. Every registered first-party provider (groq,
    gemini, openai, ollama, mock, tavily) resolves here.

    LEGACY PATH: the deprecated ``app.ai.providers`` registry. It remains
    reachable only for providers that have no gateway adapter (currently
    ``custom``) and emits a deprecation warning. It is scheduled for removal;
    see ``app/ai/providers/__init__.py``.
    """

    @staticmethod
    def create_provider(name: str) -> AIProvider:
        """
        Creates an AIProvider. Priority:
        1. Gateway canonical BaseProviderAdapter (wrapped in GatewayAIProviderAdapter)
        2. Legacy registered AIProvider class (deprecated fallback)
        """
        # Canonical Gateway BaseProviderAdapter path
        lookup_name = name.lower()
        adapter = gateway_registry.get_adapter(lookup_name)
        if adapter:
            return GatewayAIProviderAdapter(adapter)

        # Deprecated fallback to legacy registry
        try:
            provider_cls = registry.get_class(name)
            logger.warning(
                f"[DEPRECATION] Provider '{name}' resolved via legacy AIProvider "
                f"registry because no gateway adapter is registered. Add a "
                f"BaseProviderAdapter for '{name}' in gateway_registry to remove "
                f"this path."
            )
            return provider_cls()
        except ValueError:
            pass

        raise ValueError(f"AI Provider '{name}' is not registered.")

    @staticmethod
    def get_gateway_adapter(name: str) -> Optional[BaseProviderAdapter]:
        """Direct access to canonical Gateway BaseProviderAdapter."""
        return gateway_registry.get_adapter(name.lower())
