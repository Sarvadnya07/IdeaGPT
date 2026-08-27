"""
OpenAI Premium Provider Adapter for IdeaGPT AI Gateway v1.
Implements Text Generation, Deep Reasoning, Structured Output,
Embeddings, and BYOK credential support.
"""

import json
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
from app.ai.exceptions.ai_exceptions import (
    AIException,
    AIAuthenticationException,
    AIRateLimitException,
    AITimeoutException,
    AIInvalidModelException,
    AINetworkException,
)

logger = logging.getLogger(__name__)

OPENAI_STATIC_MODELS = [
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "category": ModelCategory.CHAT,
        "capabilities": [
            AICapability.TEXT_GENERATION,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.VISION,
        ],
        "context_window": 128000,
    },
    {
        "id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "category": ModelCategory.CHAT,
        "capabilities": [
            AICapability.TEXT_GENERATION,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.VISION,
        ],
        "context_window": 128000,
    },
    {
        "id": "o3-mini",
        "name": "o3-mini (Reasoning)",
        "category": ModelCategory.REASONING,
        "capabilities": [
            AICapability.TEXT_GENERATION,
            AICapability.REASONING,
            AICapability.STRUCTURED_OUTPUT,
        ],
        "context_window": 200000,
    },
    {
        "id": "text-embedding-3-small",
        "name": "Text Embedding 3 Small",
        "category": ModelCategory.EMBEDDING,
        "capabilities": [AICapability.EMBEDDING],
        "context_window": 8191,
    },
]


class OpenAIProviderAdapter(BaseProviderAdapter):
    def __init__(self):
        super().__init__(provider_id="openai", display_name="OpenAI (Premium)")
        self.capabilities = [
            AICapability.TEXT_GENERATION,
            AICapability.REASONING,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.VISION,
            AICapability.EMBEDDING,
            AICapability.MODERATION,
        ]

    @property
    def is_configured(self) -> bool:
        return bool(settings.OPENAI_API_KEY)

    @property
    def is_enabled(self) -> bool:
        if settings.ENABLE_OPENAI is False and not settings.OPENAI_API_KEY:
            return False
        return True

    def get_provider_state(self, user_byok: bool = False) -> ProviderState:
        if settings.ENABLE_OPENAI is False and not user_byok:
            return ProviderState.DISABLED
        if user_byok:
            return ProviderState.BYOK_CONNECTED
        if self.is_configured:
            return ProviderState.AVAILABLE
        return ProviderState.NOT_CONFIGURED

    def _get_client(self, api_key: Optional[str] = None):
        key = api_key or settings.OPENAI_API_KEY
        if not key:
            raise AIAuthenticationException("OpenAI API key is not configured.")
        from openai import AsyncOpenAI
        return AsyncOpenAI(api_key=key, timeout=30.0)

    async def health(self, byok_key: Optional[str] = None) -> ProviderDescriptor:
        key = byok_key or settings.OPENAI_API_KEY
        if not key:
            return ProviderDescriptor(
                id=self.provider_id,
                name=self.display_name,
                capabilities=self.capabilities,
                state=ProviderState.NOT_CONFIGURED,
                configured=False,
                enabled=self.is_enabled,
                latency_ms=0,
                models_count=0,
            )

        start = time.time()
        try:
            client = self._get_client(api_key=key)
            resp = await client.models.list()
            latency = int((time.time() - start) * 1000)
            models = getattr(resp, "data", [])
            return ProviderDescriptor(
                id=self.provider_id,
                name=self.display_name,
                capabilities=self.capabilities,
                state=ProviderState.BYOK_CONNECTED if byok_key else ProviderState.AVAILABLE,
                configured=True,
                enabled=self.is_enabled,
                latency_ms=latency,
                models_count=len(models) or len(OPENAI_STATIC_MODELS),
            )
        except Exception as exc:
            latency = int((time.time() - start) * 1000)
            return ProviderDescriptor(
                id=self.provider_id,
                name=self.display_name,
                capabilities=self.capabilities,
                state=ProviderState.UNAVAILABLE,
                configured=True,
                enabled=self.is_enabled,
                latency_ms=latency,
                models_count=0,
                error=str(exc),
            )

    async def list_models(self, byok_key: Optional[str] = None) -> List[ModelDescriptor]:
        key = byok_key or settings.OPENAI_API_KEY
        descriptors: List[ModelDescriptor] = []

        for m in OPENAI_STATIC_MODELS:
            descriptors.append(
                ModelDescriptor(
                    provider=self.provider_id,
                    model_id=m["id"],
                    display_name=m["name"],
                    category=m["category"],
                    capabilities=m["capabilities"],
                    capability_confidence=CapabilityConfidence.VERIFIED,
                    input_modalities=["text", "image"] if AICapability.VISION in m["capabilities"] else ["text"],
                    output_modalities=["text"],
                    context_window=m["context_window"],
                    supports_structured_output=True,
                    status=ModelStatus.ACTIVE,
                    configured=bool(key),
                    available=bool(key),
                    last_seen=datetime.now(timezone.utc),
                )
            )

        return descriptors

    async def execute(self, request: AIRequest) -> AIResult:
        client = self._get_client(api_key=request.byok_api_key)

        target_model = request.model_override or "gpt-4o-mini"
        if target_model in ("auto", "default", None):
            target_model = "gpt-4o-mini"

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        if request.messages:
            messages.extend(request.messages)
        else:
            messages.append({"role": "user", "content": request.prompt})

        kwargs: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
        }

        if request.capability == AICapability.STRUCTURED_OUTPUT or request.structured_schema:
            kwargs["response_format"] = {"type": "json_object"}

        start_time = time.time()
        try:
            resp = await client.chat.completions.create(**kwargs)
            duration_ms = int((time.time() - start_time) * 1000)

            content = resp.choices[0].message.content or ""
            structured_data = None
            if request.capability == AICapability.STRUCTURED_OUTPUT or request.structured_schema:
                try:
                    structured_data = json.loads(content)
                except Exception:
                    if "```json" in content:
                        clean_json = content.split("```json")[1].split("```")[0].strip()
                        structured_data = json.loads(clean_json)

            in_tokens = getattr(getattr(resp, "usage", None), "prompt_tokens", 0) or 0
            out_tokens = getattr(getattr(resp, "usage", None), "completion_tokens", 0) or 0

            return AIResult(
                text=content,
                structured_data=structured_data,
                provider=self.provider_id,
                model=target_model,
                usage=AIUsage(
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    total_tokens=in_tokens + out_tokens,
                    duration_ms=duration_ms,
                ),
                duration_ms=duration_ms,
                finish_reason=resp.choices[0].finish_reason or "stop",
            )
        except Exception as exc:
            err_str = str(exc).lower()
            if "invalid_api_key" in err_str or "unauthorized" in err_str or "401" in err_str:
                raise AIAuthenticationException("Invalid OpenAI API key.")
            if "rate_limit" in err_str or "429" in err_str:
                raise AIRateLimitException("OpenAI rate limit exceeded.")
            raise AINetworkException(f"OpenAI error: {str(exc)}")
