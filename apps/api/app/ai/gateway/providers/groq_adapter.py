"""
Groq AI Provider Adapter for IdeaGPT AI Gateway v1.
Implements dynamic model discovery, conservative model capability classification,
BYOK support, and schema-structured output.
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


def classify_groq_model_meta(model_id: str) -> Dict[str, Any]:
    mid = model_id.lower()

    if "whisper" in mid or "audio" in mid:
        return {
            "category": ModelCategory.SPEECH_TO_TEXT,
            "capabilities": [],
            "confidence": CapabilityConfidence.VERIFIED,
            "structured_output": False,
        }

    if "guard" in mid or "moderation" in mid or "safeguard" in mid:
        return {
            "category": ModelCategory.MODERATION,
            "capabilities": [AICapability.MODERATION],
            "confidence": CapabilityConfidence.VERIFIED,
            "structured_output": False,
        }

    if "deepseek-r1" in mid or "qwq" in mid or "reasoner" in mid or "120b" in mid:
        return {
            "category": ModelCategory.REASONING,
            "capabilities": [
                AICapability.TEXT_GENERATION,
                AICapability.REASONING,
                AICapability.STRUCTURED_OUTPUT,
            ],
            "confidence": CapabilityConfidence.VERIFIED,
            "structured_output": True,
        }

    return {
        "category": ModelCategory.CHAT,
        "capabilities": [
            AICapability.TEXT_GENERATION,
            AICapability.STRUCTURED_OUTPUT,
        ],
        "confidence": CapabilityConfidence.VERIFIED,
        "structured_output": True,
    }


class GroqProviderAdapter(BaseProviderAdapter):
    def __init__(self):
        super().__init__(provider_id="groq", display_name="Groq AI")
        self.capabilities = [
            AICapability.TEXT_GENERATION,
            AICapability.REASONING,
            AICapability.STRUCTURED_OUTPUT,
        ]

    @property
    def is_configured(self) -> bool:
        return bool(settings.GROQ_API_KEY)

    @property
    def is_enabled(self) -> bool:
        if settings.ENABLE_GROQ is False:
            return False
        return True

    def get_provider_state(self, user_byok: bool = False) -> ProviderState:
        if settings.ENABLE_GROQ is False:
            return ProviderState.DISABLED
        if user_byok:
            return ProviderState.BYOK_CONNECTED
        if self.is_configured:
            return ProviderState.AVAILABLE
        return ProviderState.NOT_CONFIGURED

    def _get_client(self, api_key: Optional[str] = None):
        key = api_key or settings.GROQ_API_KEY
        if not key:
            raise AIAuthenticationException("Groq API key is not configured.")
        from openai import AsyncOpenAI
        return AsyncOpenAI(
            base_url=settings.GROQ_BASE_URL or "https://api.groq.com/openai/v1",
            api_key=key,
            timeout=30.0,
        )

    async def health(self, byok_key: Optional[str] = None) -> ProviderDescriptor:
        key = byok_key or settings.GROQ_API_KEY
        state = self.get_provider_state(user_byok=bool(byok_key))
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
            models = await self.list_models(byok_key=key)
            latency = int((time.time() - start) * 1000)
            return ProviderDescriptor(
                id=self.provider_id,
                name=self.display_name,
                capabilities=self.capabilities,
                state=ProviderState.BYOK_CONNECTED if byok_key else ProviderState.AVAILABLE,
                configured=True,
                enabled=self.is_enabled,
                latency_ms=latency,
                models_count=len(models),
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
        key = byok_key or settings.GROQ_API_KEY
        if not key:
            return []

        try:
            client = self._get_client(api_key=key)
            response = await client.models.list()
            raw_models = getattr(response, "data", []) or []

            descriptors: List[ModelDescriptor] = []
            for m in raw_models:
                m_id = getattr(m, "id", None) or str(m)
                is_active = getattr(m, "active", True)
                ctx = getattr(m, "context_window", 131072) or 131072
                meta = classify_groq_model_meta(m_id)

                descriptors.append(
                    ModelDescriptor(
                        provider=self.provider_id,
                        model_id=m_id,
                        display_name=m_id.split("/")[-1].replace("-", " ").title(),
                        category=meta["category"],
                        capabilities=meta["capabilities"],
                        capability_confidence=meta["confidence"],
                        context_window=ctx,
                        supports_structured_output=meta["structured_output"],
                        status=ModelStatus.ACTIVE if is_active else ModelStatus.INACTIVE,
                        configured=True,
                        available=is_active,
                        last_seen=datetime.now(timezone.utc),
                    )
                )
            return descriptors
        except Exception as e:
            logger.warning(f"Groq dynamic model discovery failed: {e}")
            return []

    async def execute(self, request: AIRequest) -> AIResult:
        client = self._get_client(api_key=request.byok_api_key)

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        if request.messages:
            messages.extend(request.messages)
        else:
            messages.append({"role": "user", "content": request.prompt})

        from app.ai.gateway.registry import gateway_registry

        target_model = request.model_override or "openai/gpt-oss-120b"
        if target_model in ("auto", "default", None):
            target_model = "openai/gpt-oss-120b"

        kwargs: Dict[str, Any] = {
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
        }

        if request.capability == AICapability.STRUCTURED_OUTPUT or request.structured_schema:
            kwargs["response_format"] = {"type": "json_object"}

        candidate_models = [
            target_model,
            "openai/gpt-oss-120b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "openai/gpt-oss-20b",
        ]
        # Filter out quarantined models and deduplicate
        unique_candidates = []
        for c in candidate_models:
            if c not in unique_candidates and not gateway_registry.is_quarantined(c):
                unique_candidates.append(c)

        if not unique_candidates:
            unique_candidates = ["openai/gpt-oss-120b", "llama-3.1-8b-instant"]

        last_exc = None
        start_time = time.time()

        for model_name in unique_candidates:
            try:
                kwargs["model"] = model_name
                resp = await client.chat.completions.create(**kwargs)
                duration_ms = int((time.time() - start_time) * 1000)

                content = resp.choices[0].message.content or ""
                structured_data = None
                if request.capability == AICapability.STRUCTURED_OUTPUT or request.structured_schema:
                    try:
                        structured_data = json.loads(content)
                    except Exception:
                        # Attempt markdown json block extraction
                        if "```json" in content:
                            json_str = content.split("```json")[1].split("```")[0].strip()
                            structured_data = json.loads(json_str)

                in_tokens = getattr(getattr(resp, "usage", None), "prompt_tokens", 0) or 0
                out_tokens = getattr(getattr(resp, "usage", None), "completion_tokens", 0) or 0

                return AIResult(
                    text=content,
                    structured_data=structured_data,
                    provider=self.provider_id,
                    model=model_name,
                    usage=AIUsage(
                        input_tokens=in_tokens,
                        output_tokens=out_tokens,
                        total_tokens=in_tokens + out_tokens,
                        duration_ms=duration_ms,
                    ),
                    duration_ms=duration_ms,
                    finish_reason=resp.choices[0].finish_reason or "stop",
                    fallback_used=(model_name != target_model),
                    fallback_reason=f"Primary model '{target_model}' unavailable, failed over to '{model_name}'" if model_name != target_model else None,
                )
            except Exception as exc:
                last_exc = exc
                err_str = str(exc).lower()
                if "invalid_api_key" in err_str or "unauthorized" in err_str or "401" in err_str:
                    raise AIAuthenticationException("Invalid Groq API key.")
                if "rate_limit" in err_str or "429" in err_str:
                    raise AIRateLimitException("Groq rate limit exceeded.")

                # Quarantine models that return 404 (not found) or 403 (blocked at project level)
                if "model_not_found" in err_str or "404" in err_str or "model_permission_blocked_project" in err_str or "403" in err_str:
                    gateway_registry.quarantine_model(model_name, duration_sec=300.0, reason=str(exc))

                logger.warning(f"Groq candidate '{model_name}' failed: {exc}. Trying next candidate...")

        duration_ms = int((time.time() - start_time) * 1000)
        raise AINetworkException(f"All Groq model candidates failed: {last_exc}")
