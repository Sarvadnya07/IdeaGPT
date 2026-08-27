"""
Google Gemini AI Provider Adapter for IdeaGPT AI Gateway v1.
Implements Text Generation, Deep Reasoning, Structured Output,
Vision/Document Understanding, and BYOK credential support.
"""

import json
import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import httpx

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

GEMINI_STATIC_MODELS = [
    {
        "id": "gemini-2.0-flash",
        "name": "Gemini 2.0 Flash",
        "category": ModelCategory.CHAT,
        "capabilities": [
            AICapability.TEXT_GENERATION,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.VISION,
            AICapability.DOCUMENT_UNDERSTANDING,
        ],
        "context_window": 1048576,
        "vision": True,
        "docs": True,
    },
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro",
        "category": ModelCategory.REASONING,
        "capabilities": [
            AICapability.TEXT_GENERATION,
            AICapability.REASONING,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.VISION,
            AICapability.DOCUMENT_UNDERSTANDING,
        ],
        "context_window": 2097152,
        "vision": True,
        "docs": True,
    },
    {
        "id": "gemini-1.5-flash",
        "name": "Gemini 1.5 Flash",
        "category": ModelCategory.CHAT,
        "capabilities": [
            AICapability.TEXT_GENERATION,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.VISION,
            AICapability.DOCUMENT_UNDERSTANDING,
        ],
        "context_window": 1048576,
        "vision": True,
        "docs": True,
    },
]


class GeminiProviderAdapter(BaseProviderAdapter):
    def __init__(self):
        super().__init__(provider_id="gemini", display_name="Google Gemini")
        self.capabilities = [
            AICapability.TEXT_GENERATION,
            AICapability.REASONING,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.VISION,
            AICapability.DOCUMENT_UNDERSTANDING,
        ]

    @property
    def is_configured(self) -> bool:
        return bool(settings.GEMINI_API_KEY)

    @property
    def is_enabled(self) -> bool:
        if settings.ENABLE_GEMINI is False and not settings.GEMINI_API_KEY:
            return False
        return True

    def get_provider_state(self, user_byok: bool = False) -> ProviderState:
        if settings.ENABLE_GEMINI is False and not user_byok:
            return ProviderState.DISABLED
        if user_byok:
            return ProviderState.BYOK_CONNECTED
        if self.is_configured:
            return ProviderState.AVAILABLE
        return ProviderState.NOT_CONFIGURED

    async def health(self, byok_key: Optional[str] = None) -> ProviderDescriptor:
        key = byok_key or settings.GEMINI_API_KEY
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
            # Check models list with key
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url)
                latency = int((time.time() - start) * 1000)
                if res.status_code == 200:
                    models = res.json().get("models", [])
                    return ProviderDescriptor(
                        id=self.provider_id,
                        name=self.display_name,
                        capabilities=self.capabilities,
                        state=ProviderState.BYOK_CONNECTED if byok_key else ProviderState.AVAILABLE,
                        configured=True,
                        enabled=self.is_enabled,
                        latency_ms=latency,
                        models_count=len(models) or len(GEMINI_STATIC_MODELS),
                    )
                elif res.status_code == 400 or res.status_code == 401 or res.status_code == 403:
                    return ProviderDescriptor(
                        id=self.provider_id,
                        name=self.display_name,
                        capabilities=self.capabilities,
                        state=ProviderState.UNAVAILABLE,
                        configured=True,
                        enabled=self.is_enabled,
                        latency_ms=latency,
                        models_count=0,
                        error="Invalid Gemini API key or permission denied",
                    )
                else:
                    return ProviderDescriptor(
                        id=self.provider_id,
                        name=self.display_name,
                        capabilities=self.capabilities,
                        state=ProviderState.DEGRADED,
                        configured=True,
                        enabled=self.is_enabled,
                        latency_ms=latency,
                        models_count=len(GEMINI_STATIC_MODELS),
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
        key = byok_key or settings.GEMINI_API_KEY
        descriptors: List[ModelDescriptor] = []

        for m in GEMINI_STATIC_MODELS:
            descriptors.append(
                ModelDescriptor(
                    provider=self.provider_id,
                    model_id=m["id"],
                    display_name=m["name"],
                    category=m["category"],
                    capabilities=m["capabilities"],
                    capability_confidence=CapabilityConfidence.VERIFIED,
                    input_modalities=["text", "image", "document"] if m.get("vision") else ["text"],
                    output_modalities=["text"],
                    context_window=m["context_window"],
                    supports_structured_output=True,
                    supports_vision=m.get("vision", False),
                    supports_documents=m.get("docs", False),
                    status=ModelStatus.ACTIVE,
                    configured=bool(key),
                    available=bool(key),
                    last_seen=datetime.now(timezone.utc),
                )
            )

        return descriptors

    async def execute(self, request: AIRequest) -> AIResult:
        key = request.byok_api_key or settings.GEMINI_API_KEY
        if not key:
            raise AIAuthenticationException("Gemini API key is not configured.")

        target_model = request.model_override or "gemini-2.0-flash"
        if target_model in ("auto", "default", None):
            target_model = "gemini-2.0-flash"

        # Model name cleaning (remove prefix if present)
        clean_model = target_model.replace("models/", "")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={key}"

        # Construct Gemini payload
        contents = []
        if request.system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"SYSTEM INSTRUCTION:\n{request.system_prompt}"}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "Understood. I will strictly follow these instructions and return the requested format."}]
            })

        contents.append({
            "role": "user",
            "parts": [{"text": request.prompt}]
        })

        generation_config: Dict[str, Any] = {
            "temperature": request.temperature,
            "maxOutputTokens": request.max_output_tokens,
        }

        if request.capability == AICapability.STRUCTURED_OUTPUT or request.structured_schema:
            generation_config["responseMimeType"] = "application/json"

        body = {
            "contents": contents,
            "generationConfig": generation_config
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=body)
                duration_ms = int((time.time() - start_time) * 1000)

                if res.status_code == 400 or res.status_code == 401 or res.status_code == 403:
                    err_msg = res.json().get("error", {}).get("message", "Authentication failure with Gemini API.")
                    raise AIAuthenticationException(f"Gemini error ({res.status_code}): {err_msg}")
                elif res.status_code == 429:
                    raise AIRateLimitException("Gemini rate limit exceeded. Please retry shortly.")
                elif res.status_code >= 500:
                    raise AINetworkException(f"Gemini server error ({res.status_code})")
                elif res.status_code != 200:
                    raise AIException(f"Gemini unexpected status {res.status_code}: {res.text}")

                res_json = res.json()
                candidates = res_json.get("candidates", [])
                if not candidates:
                    raise AIException("Gemini returned empty candidate list.")

                content_parts = candidates[0].get("content", {}).get("parts", [])
                text_out = "".join(p.get("text", "") for p in content_parts)

                structured_data = None
                if request.capability == AICapability.STRUCTURED_OUTPUT or request.structured_schema:
                    try:
                        structured_data = json.loads(text_out)
                    except Exception:
                        if "```json" in text_out:
                            clean_json = text_out.split("```json")[1].split("```")[0].strip()
                            structured_data = json.loads(clean_json)

                usage_meta = res_json.get("usageMetadata", {})
                in_tok = usage_meta.get("promptTokenCount", 0)
                out_tok = usage_meta.get("candidatesTokenCount", 0)

                return AIResult(
                    text=text_out,
                    structured_data=structured_data,
                    provider=self.provider_id,
                    model=clean_model,
                    usage=AIUsage(
                        input_tokens=in_tok,
                        output_tokens=out_tok,
                        total_tokens=in_tok + out_tok,
                        duration_ms=duration_ms,
                    ),
                    duration_ms=duration_ms,
                    finish_reason=candidates[0].get("finishReason", "STOP"),
                )
        except httpx.TimeoutException:
            raise AITimeoutException("Gemini generation timed out after 30 seconds.")
        except (AIAuthenticationException, AIRateLimitException, AITimeoutException, AINetworkException):
            raise
        except Exception as exc:
            logger.error(f"Gemini execution error: {exc}", exc_info=True)
            raise AINetworkException(f"Failed to communicate with Google Gemini: {str(exc)}")
