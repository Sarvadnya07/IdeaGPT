import json
import time
import logging
from typing import Any, Dict, List, Optional
from app.ai.providers.base import AIProvider
from app.core.config import settings
from app.ai.exceptions.ai_exceptions import (
    AIException,
    AIAuthenticationException,
    AIRateLimitException,
    AITimeoutException,
    AIInvalidModelException,
    AINetworkException,
)

logger = logging.getLogger(__name__)

def classify_groq_model(model_id: str) -> Dict[str, Any]:
    """
    Classifies model capabilities using a conservative hierarchy:
      1. Speech-to-Text / Audio (Whisper) -> SPEECH_TO_TEXT
      2. Moderation / Guard -> MODERATION
      3. Vision -> VISION
      4. Deep Reasoning -> REASONING
      5. Chat / Text Generation -> TEXT_GENERATION + STRUCTURED_OUTPUT
      6. Fallback -> UNKNOWN
    """
    mid = model_id.lower()

    if "whisper" in mid:
        return {
            "capabilities": ["SPEECH_TO_TEXT", "AUDIO_INPUT"],
            "capability_source": "model_metadata",
            "capability_confidence": "verified",
            "category": "SPEECH_TO_TEXT",
            "supports_structured_output": False,
        }

    if "guard" in mid or "moderation" in mid:
        return {
            "capabilities": ["MODERATION"],
            "capability_source": "model_metadata",
            "capability_confidence": "verified",
            "category": "MODERATION",
            "supports_structured_output": False,
        }

    if "vision" in mid or "llava" in mid:
        return {
            "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT", "VISION"],
            "capability_source": "model_metadata",
            "capability_confidence": "inferred",
            "category": "CHAT",
            "supports_structured_output": True,
        }

    if "deepseek-r1" in mid or "qwq" in mid or "reasoner" in mid:
        return {
            "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT", "REASONING"],
            "capability_source": "model_metadata",
            "capability_confidence": "verified",
            "category": "CHAT",
            "supports_structured_output": True,
        }

    if any(k in mid for k in ("llama-3.3", "llama-3.1", "mixtral", "gemma")):
        return {
            "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT"],
            "capability_source": "provider_metadata",
            "capability_confidence": "verified",
            "category": "CHAT",
            "supports_structured_output": True,
        }

    if any(k in mid for k in ("gpt-oss", "qwen")):
        return {
            "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT"],
            "capability_source": "provider_metadata",
            "capability_confidence": "inferred",
            "category": "CHAT",
            "supports_structured_output": True,
        }

    return {
        "capabilities": ["TEXT_GENERATION"],
        "capability_source": "fallback",
        "capability_confidence": "unknown",
        "category": "TEXT",
        "supports_structured_output": False,
    }

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

    def get_provider_state(self) -> str:
        if settings.ENABLE_GROQ is False:
            return "DISABLED"
        if not settings.GROQ_API_KEY:
            return "NOT_CONFIGURED"
        return "AVAILABLE"

    def _get_client(self):
        if self._client is None:
            if not settings.GROQ_API_KEY:
                raise AIAuthenticationException("GROQ_API_KEY is not configured.")
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
        Uses model capability classification hierarchy.
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

                meta = classify_groq_model(model_id)

                descriptors.append({
                    "id": model_id,
                    "name": model_id.split("/")[-1].replace("-", " ").title(),
                    "provider": self.provider_id,
                    "capabilities": meta["capabilities"],
                    "capability_source": meta["capability_source"],
                    "capability_confidence": meta["capability_confidence"],
                    "category": meta["category"],
                    "supports_structured_output": meta["supports_structured_output"],
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
                "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT"],
                "capability_source": "provider_metadata",
                "capability_confidence": "verified",
                "category": "CHAT",
                "supports_structured_output": True,
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

        # Build prioritized list of model candidates
        candidate_models: List[str] = []
        if model_override and model_override != "auto":
            candidate_models.append(model_override)

        models = await self.list_models_async()
        active_chat_models = [m["id"] for m in models if m.get("available") and m.get("category") == "CHAT"]

        # Standard unblocked production models
        for fallback in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]:
            if fallback in active_chat_models and fallback not in candidate_models:
                candidate_models.append(fallback)
        for m in active_chat_models:
            if m not in candidate_models:
                candidate_models.append(m)

        if not candidate_models:
            candidate_models = ["llama-3.3-70b-versatile"]

        kwargs: Dict[str, Any] = {
            "messages": messages,
        }
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        last_exc = None
        for target_model in candidate_models:
            kwargs["model"] = target_model
            start_time = time.time()
            try:
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

            except Exception as e:
                err_str = str(e)
                if "model_permission_blocked_project" in err_str or "blocked at the project level" in err_str:
                    logger.warning(f"Groq model {target_model} blocked at project level, trying next candidate...")
                    last_exc = e
                    continue
                else:
                    if "401" in err_str or "auth" in err_str.lower() or "api key" in err_str.lower():
                        raise AIAuthenticationException(f"Groq API authentication failed: {err_str}")
                    elif "429" in err_str or "rate limit" in err_str.lower():
                        raise AIRateLimitException(f"Groq rate limit exceeded: {err_str}")
                    elif "timeout" in err_str.lower():
                        raise AITimeoutException(f"Groq request timed out: {err_str}")
                    elif "400" in err_str or "model" in err_str.lower():
                        raise AIInvalidModelException(f"Groq model or request invalid: {err_str}")
                    else:
                        raise AINetworkException(f"Groq provider error: {err_str}")

        if last_exc:
            raise AIInvalidModelException(f"Groq model or request invalid: {last_exc}")
