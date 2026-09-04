from typing import Optional
from app.ai.orchestrator.registry import registry
from app.ai.providers.base import AIProvider
from app.ai.gateway.registry import gateway_registry
from app.ai.gateway.providers.base_adapter import BaseProviderAdapter
from app.ai.orchestrator.gateway_adapter import GatewayAIProviderAdapter

class ProviderFactory:
    @staticmethod
    def create_provider(name: str) -> AIProvider:
        """
        Creates an AIProvider. Priority:
        1. Gateway canonical BaseProviderAdapter (wrapped in GatewayAIProviderAdapter)
        2. Legacy registered AIProvider class
        """
        # Check legacy registry first if registered
        try:
            provider_cls = registry.get_class(name)
            return provider_cls()
        except ValueError:
            pass

        # Fallback to Gateway canonical BaseProviderAdapter
        lookup_name = name.lower()
        adapter = gateway_registry.get_adapter(lookup_name)
        if adapter:
            return GatewayAIProviderAdapter(adapter)

        raise ValueError(f"AI Provider '{name}' is not registered.")

    @staticmethod
    def get_gateway_adapter(name: str) -> Optional[BaseProviderAdapter]:
        """Direct access to canonical Gateway BaseProviderAdapter."""
        return gateway_registry.get_adapter(name.lower())
