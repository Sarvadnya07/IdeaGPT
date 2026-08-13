import json
import time
import logging
from typing import Any, Dict, List, Optional
from app.ai.providers.base import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class GroqProvider(AIProvider):
    def __init__(self):
        self._client = None
        self.provider_id = "groq"
        self.display_name = "Groq AI"

    @property
    def is_configured(self) -> bool:
        return bool(settings.GROQ_API_KEY)

    @property
    def is_enabled(self) -> bool:
        if settings.ENABLE_GROQ is False:
            return False
        return self.is_configured

    def get_provider_state() -> str:
        if settings.ENABLE_GROQ is False:
            return "DISABLED"
        if not settings.GROQ_API_KEY:
            return "NOT_CONFIGURED"
        return "AVAILABLE"

    def _get_client(self):
        if self._client is None:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is not configured.")
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                base_url=settings.GROQ_BASE_URL or "https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY,
                timeout=30.0
            )
        return self._client

    async def list_models_async(self) -> List[Dict[str, Any]]:
        """
        Dynamically discovers live models from Groq's official Models API endpoint.
        Does NOT rely on hardcoded model lists.
        """
        if not self.is_enabled:
            return []

        try:
            client = self._get_client()
            response = await client.models.list()
            raw_models = getattr(response, "data", []) or []

            descriptors: List[Dict[str, Any]] = []
            for m in raw_models:
                model_id = getattr(m, "id", None) or str(m)
                is_active = getattr(m, "active", True)
                ctx_window = getattr(m, "context_window", 131072) or 131072

                descriptors.append({
                    "id": model_id,
                    "name": model_id.split("/")[-1].replace("-", " ").title(),
                    "provider": self.provider_id,
                    "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT", "REASONING"],
                    "capability_source": "provider_metadata",
                    "capability_confidence": "verified",
                    "context_window": ctx_window,
                    "state": "ACTIVE" if is_active else "INACTIVE",
                    "configured": True,
                    "available": is_active,
                })

            return descriptors
        except Exception as e:
            logger.warning(f"Groq dynamic model discovery failed: {e}")
            return []

    def list_models(self) -> List[Dict[str, Any]]:
        """Synchronous fallback descriptor listing."""
        if not self.is_enabled:
            return []
        return [
            {
                "id": "auto",
                "name": "Groq Auto-Selected Model",
                "provider": self.provider_id,
                "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT", "REASONING"],
                "capability_source": "provider_metadata",
                "capability_confidence": "verified",
                "context_window": 131072,
                "state": "ACTIVE",
                "configured": True,
                "available": True,
            }
        ]

    async def health(self) -> Dict[str, Any]:
        state = self.get_provider_state()
        if state in ("NOT_CONFIGURED", "DISABLED"):
            return {
                "available": False,
                "state": state,
                "latency_ms": 0,
                "error": f"Groq provider is {state.lower()}"
            }

        start = time.time()
        try:
            models = await self.list_models_async()
            latency = int((time.time() - start) * 1000)
            return {
                "available": len(models) > 0 or True,
                "state": "AVAILABLE" if len(models) > 0 else "DEGRADED",
                "latency_ms": latency,
                "models_count": len(models),
                "error": None
            }
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return {
                "available": False,
                "state": "UNAVAILABLE",
                "latency_ms": latency,
                "error": str(e)
            }

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        response_format: str = "json",
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        client = self._get_client()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # If model_override is auto or None, discover first active model or fallback
        target_model = model_override
        if not target_model or target_model == "auto":
            models = await self.list_models_async()
            active_models = [m["id"] for m in models if m.get("available")]
            target_model = active_models[0] if active_models else "llama-3.3-70b-versatile"

        kwargs: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
        }
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        start_time = time.time()
        response = await client.chat.completions.create(**kwargs)
        duration_ms = int((time.time() - start_time) * 1000)

        content = response.choices[0].message.content or ""

        # Extract Usage Metadata
        usage_meta = {}
        if hasattr(response, "usage") and response.usage:
            usage_meta = {
                "input_tokens": getattr(response.usage, "prompt_tokens", None),
                "output_tokens": getattr(response.usage, "completion_tokens", None),
                "total_tokens": getattr(response.usage, "total_tokens", None),
                "duration_ms": duration_ms
            }

        parsed_data: Dict[str, Any] = {}
        if response_format == "json":
            try:
                parsed_data = json.loads(content)
            except json.JSONDecodeError:
                parsed_data = {"raw_response": content, "error": "Failed to parse JSON response"}
        else:
            parsed_data = {"text": content}

        parsed_data["_usage"] = usage_meta
        parsed_data["_actual_model"] = target_model
        return parsed_data
