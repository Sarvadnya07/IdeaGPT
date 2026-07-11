from typing import Dict, Type
from app.services.ai.base import AIProvider

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, AIProvider] = {}

    def register(self, name: str, provider: AIProvider):
        self._providers[name] = provider

    def get(self, name: str) -> AIProvider:
        provider = self._providers.get(name)
        if not provider:
            raise ValueError(f"Provider '{name}' not registered.")
        return provider

registry = ProviderRegistry()
