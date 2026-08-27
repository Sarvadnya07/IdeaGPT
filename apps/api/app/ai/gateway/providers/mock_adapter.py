"""
Mock AI Provider Adapter for IdeaGPT AI Gateway v1.
Strictly isolated for unit tests and local mock development.
PROHIBITED in production environments.
"""

import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.ai.gateway.providers.base_adapter import BaseProviderAdapter
from app.ai.gateway.models import (
    AIRequest,
    AIResult,
    AIUsage,
    ModelDescriptor,
    ProviderDescriptor,
)
from app.ai.gateway.contracts import (
    AICapability,
    CapabilityConfidence,
    ModelCategory,
    ModelStatus,
    ProviderState,
)
from app.ai.exceptions.ai_exceptions import AIUnavailableException

logger = logging.getLogger(__name__)


class MockProviderAdapter(BaseProviderAdapter):
    def __init__(self):
        super().__init__(provider_id="mock", display_name="Mock Provider (Test Only)")
        self.capabilities = [
            AICapability.TEXT_GENERATION,
            AICapability.REASONING,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.EMBEDDING,
            AICapability.MODERATION,
        ]

    @property
    def is_configured(self) -> bool:
        return True

    @property
    def is_enabled(self) -> bool:
        # Strictly forbidden in production
        if settings.APP_ENV == "production":
            return False
        return settings.APP_ENV == "test" or (settings.APP_ENV == "development" and settings.DEFAULT_PROVIDER == "mock")

    def get_provider_state(self, user_byok: bool = False) -> ProviderState:
        if not self.is_enabled:
            return ProviderState.DISABLED
        return ProviderState.AVAILABLE

    async def health(self, byok_key: Optional[str] = None) -> ProviderDescriptor:
        if not self.is_enabled:
            return ProviderDescriptor(
                id=self.provider_id,
                name=self.display_name,
                capabilities=self.capabilities,
                state=ProviderState.DISABLED,
                configured=False,
                enabled=False,
                latency_ms=0,
                models_count=0,
                error="Mock provider is prohibited in production.",
            )

        return ProviderDescriptor(
            id=self.provider_id,
            name=self.display_name,
            capabilities=self.capabilities,
            state=ProviderState.AVAILABLE,
            configured=True,
            enabled=True,
            latency_ms=1,
            models_count=1,
        )

    async def list_models(self, byok_key: Optional[str] = None) -> List[ModelDescriptor]:
        if not self.is_enabled:
            return []
        return [
            ModelDescriptor(
                provider=self.provider_id,
                model_id="mock-model",
                display_name="Deterministic Mock Model",
                category=ModelCategory.CHAT,
                capabilities=self.capabilities,
                capability_confidence=CapabilityConfidence.VERIFIED,
                context_window=32768,
                supports_structured_output=True,
                status=ModelStatus.ACTIVE,
                configured=True,
                available=True,
                last_seen=datetime.now(timezone.utc),
            )
        ]

    async def execute(self, request: AIRequest) -> AIResult:
        if not self.is_enabled:
            raise AIUnavailableException("Mock provider is disabled in production.")

        start_time = time.time()
        mock_output = {
            "score": 85,
            "strengths": [
                "Strong product-market alignment",
                "High leverage AI augmentation",
                "Clear unit economics"
            ],
            "weaknesses": [
                "Initial distribution cold-start",
                "Competitive pressure"
            ],
            "architecture_breakdown": "Scalable Next.js and FastAPI architecture with PostgreSQL and Redis caching.",
            "dimensions": {
                "innovation": 85,
                "market_potential": 88,
                "technical_feasibility": 82,
                "business_viability": 80,
                "scalability": 90,
                "execution_complexity": 75,
                "competitive_differentiation": 84
            }
        }
        duration_ms = int((time.time() - start_time) * 1000) or 5

        return AIResult(
            text=str(mock_output),
            structured_data=mock_output,
            provider=self.provider_id,
            model="mock-model",
            usage=AIUsage(
                input_tokens=50,
                output_tokens=150,
                total_tokens=200,
                duration_ms=duration_ms,
            ),
            duration_ms=duration_ms,
            finish_reason="stop",
        )
