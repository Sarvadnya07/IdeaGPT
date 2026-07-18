from app.ai.orchestrator.registry import registry
from app.ai.providers.base import AIProvider

class ProviderFactory:
    @staticmethod
    def create_provider(name: str) -> AIProvider:
        provider_cls = registry.get_class(name)
        return provider_cls()
