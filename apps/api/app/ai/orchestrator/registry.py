from typing import Dict, Type
from app.ai.providers.base import AIProvider

class ProviderRegistry:
    def __init__(self):
        self._registry: Dict[str, Type[AIProvider]] = {}

    def register(self, name: str, provider_cls: Type[AIProvider]):
        self._registry[name] = provider_cls

    def get_class(self, name: str) -> Type[AIProvider]:
        provider_cls = self._registry.get(name)
        if not provider_cls:
            raise ValueError(f"AI Provider '{name}' is not registered.")
        return provider_cls

registry = ProviderRegistry()

# Register all providers
from app.ai.providers.openai import OpenAIProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.ollama import OllamaProvider
from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.ai.providers.mock import MockProvider

registry.register("openai", OpenAIProvider)
registry.register("gemini", GeminiProvider)
registry.register("ollama", OllamaProvider)
registry.register("custom", OpenAICompatibleProvider)
registry.register("mock", MockProvider)
