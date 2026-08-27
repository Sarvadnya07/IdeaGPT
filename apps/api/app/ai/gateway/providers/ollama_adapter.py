"""
Ollama Local AI Provider Adapter for IdeaGPT AI Gateway v1.
Implements local model discovery, graceful unavailable state, and local execution.
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
    AIUnavailableException,
    AITimeoutException,
    AINetworkException,
)

logger = logging.getLogger(__name__)


class OllamaProviderAdapter(BaseProviderAdapter):
    def __init__(self):
        super().__init__(provider_id="ollama", display_name="Ollama (Local LLM)")
        self.capabilities = [
            AICapability.TEXT_GENERATION,
            AICapability.REASONING,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.EMBEDDING,
        ]

    @property
    def is_configured(self) -> bool:
        return bool(settings.ENABLE_OLLAMA and settings.OLLAMA_URL)

    @property
    def is_enabled(self) -> bool:
        return bool(settings.ENABLE_OLLAMA)

    def get_provider_state(self, user_byok: bool = False) -> ProviderState:
        if not settings.ENABLE_OLLAMA:
            return ProviderState.DISABLED
        return ProviderState.AVAILABLE

    async def health(self, byok_key: Optional[str] = None) -> ProviderDescriptor:
        if not settings.ENABLE_OLLAMA:
            return ProviderDescriptor(
                id=self.provider_id,
                name=self.display_name,
                capabilities=self.capabilities,
                state=ProviderState.DISABLED,
                configured=False,
                enabled=False,
                latency_ms=0,
                models_count=0,
            )

        start = time.time()
        url = f"{settings.OLLAMA_URL.rstrip('/')}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(url)
                latency = int((time.time() - start) * 1000)
                if res.status_code == 200:
                    models = res.json().get("models", [])
                    return ProviderDescriptor(
                        id=self.provider_id,
                        name=self.display_name,
                        capabilities=self.capabilities,
                        state=ProviderState.AVAILABLE,
                        configured=True,
                        enabled=True,
                        latency_ms=latency,
                        models_count=len(models),
                    )
                return ProviderDescriptor(
                    id=self.provider_id,
                    name=self.display_name,
                    capabilities=self.capabilities,
                    state=ProviderState.UNAVAILABLE,
                    configured=True,
                    enabled=True,
                    latency_ms=latency,
                    models_count=0,
                    error=f"Ollama returned status {res.status_code}",
                )
        except Exception as exc:
            latency = int((time.time() - start) * 1000)
            return ProviderDescriptor(
                id=self.provider_id,
                name=self.display_name,
                capabilities=self.capabilities,
                state=ProviderState.UNAVAILABLE,
                configured=True,
                enabled=True,
                latency_ms=latency,
                models_count=0,
                error="Local Ollama daemon is offline or unreachable",
            )

    async def list_models(self, byok_key: Optional[str] = None) -> List[ModelDescriptor]:
        if not settings.ENABLE_OLLAMA:
            return []

        url = f"{settings.OLLAMA_URL.rstrip('/')}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(url)
                if res.status_code != 200:
                    return []
                raw_models = res.json().get("models", [])
                descriptors: List[ModelDescriptor] = []
                for m in raw_models:
                    m_name = m.get("name", "llama3")
                    descriptors.append(
                        ModelDescriptor(
                            provider=self.provider_id,
                            model_id=m_name,
                            display_name=f"Ollama: {m_name.capitalize()}",
                            category=ModelCategory.CHAT,
                            capabilities=[
                                AICapability.TEXT_GENERATION,
                                AICapability.STRUCTURED_OUTPUT,
                            ],
                            capability_confidence=CapabilityConfidence.INFERRED,
                            input_modalities=["text"],
                            output_modalities=["text"],
                            context_window=32768,
                            supports_structured_output=True,
                            status=ModelStatus.ACTIVE,
                            configured=True,
                            available=True,
                            last_seen=datetime.now(timezone.utc),
                        )
                    )
                return descriptors
        except Exception:
            return []

    async def execute(self, request: AIRequest) -> AIResult:
        if not settings.ENABLE_OLLAMA:
            raise AIUnavailableException("Ollama provider is disabled in configuration.")

        target_model = request.model_override or "llama3"
        if target_model in ("auto", "default", None):
            target_model = "llama3"

        url = f"{settings.OLLAMA_URL.rstrip('/')}/api/generate"
        payload = {
            "model": target_model,
            "prompt": f"{request.system_prompt}\n\n{request.prompt}" if request.system_prompt else request.prompt,
            "stream": False,
            "format": "json" if (request.capability == AICapability.STRUCTURED_OUTPUT or request.structured_schema) else None,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_output_tokens,
            },
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload)
                duration_ms = int((time.time() - start_time) * 1000)

                if res.status_code != 200:
                    raise AINetworkException(f"Ollama error {res.status_code}: {res.text}")

                res_data = res.json()
                raw_text = res_data.get("response", "")

                structured_data = None
                if request.capability == AICapability.STRUCTURED_OUTPUT or request.structured_schema:
                    try:
                        structured_data = json.loads(raw_text)
                    except Exception:
                        if "```json" in raw_text:
                            clean_json = raw_text.split("```json")[1].split("```")[0].strip()
                            structured_data = json.loads(clean_json)

                eval_count = res_data.get("eval_count", 0)
                prompt_eval_count = res_data.get("prompt_eval_count", 0)

                return AIResult(
                    text=raw_text,
                    structured_data=structured_data,
                    provider=self.provider_id,
                    model=target_model,
                    usage=AIUsage(
                        input_tokens=prompt_eval_count,
                        output_tokens=eval_count,
                        total_tokens=prompt_eval_count + eval_count,
                        duration_ms=duration_ms,
                    ),
                    duration_ms=duration_ms,
                    finish_reason="stop",
                )
        except httpx.TimeoutException:
            raise AITimeoutException("Local Ollama execution timed out.")
        except Exception as exc:
            logger.error(f"Ollama execution error: {exc}", exc_info=True)
            raise AINetworkException(f"Failed to communicate with local Ollama daemon: {str(exc)}")
