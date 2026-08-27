"""
Base Provider Adapter Interface for IdeaGPT AI Gateway v1.
"""

import abc
import time
from typing import Any, Dict, List, Optional
from app.ai.gateway.models import AIRequest, AIResult, ModelDescriptor, ProviderDescriptor
from app.ai.gateway.contracts import AICapability, ProviderState


class BaseProviderAdapter(abc.ABC):
    def __init__(self, provider_id: str, display_name: str):
        self.provider_id = provider_id
        self.display_name = display_name
        self.capabilities: List[AICapability] = []

    @property
    @abc.abstractmethod
    def is_configured(self) -> bool:
        """Returns True if default provider API key / endpoint is configured."""
        ...

    @property
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        """Returns True if provider is not administratively disabled."""
        ...

    @abc.abstractmethod
    def get_provider_state(self, user_byok: bool = False) -> ProviderState:
        """Calculates current runtime state for the provider."""
        ...

    @abc.abstractmethod
    async def health(self, byok_key: Optional[str] = None) -> ProviderDescriptor:
        """Checks connectivity and returns sanitized health descriptor."""
        ...

    @abc.abstractmethod
    async def list_models(self, byok_key: Optional[str] = None) -> List[ModelDescriptor]:
        """Discovers or enumerates supported active models."""
        ...

    @abc.abstractmethod
    async def execute(self, request: AIRequest) -> AIResult:
        """Executes a normalized AI request and returns a normalized AIResult."""
        ...
