import json
import time
from typing import Any, Dict, List, Optional
from app.ai.providers.base import AIProvider
from app.core.config import settings

class OpenAICompatibleProvider(AIProvider):
    def __init__(self):
        self._client = None
        self.provider_id = "custom"
        self.display_name = "Custom / Hosted Model"

    def _get_client(self):
        if self._client is None:
            if not settings.CUSTOM_PROVIDER_URL:
                raise ValueError("CUSTOM_PROVIDER_URL is not configured.")
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                base_url=settings.CUSTOM_PROVIDER_URL,
                api_key=settings.CUSTOM_PROVIDER_KEY or "dummy_key",
                timeout=30.0
            )
        return self._client

    def list_models(self) -> List[Dict[str, Any]]:
        is_configured = bool(settings.CUSTOM_PROVIDER_URL)
        return [
            {
                "id": "custom-model",
                "name": "User Hosted Model",
                "provider": self.provider_id,
                "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT"],
                "configured": is_configured,
                "available": is_configured,
            }
        ]

    async def health(self) -> Dict[str, Any]:
        if not settings.CUSTOM_PROVIDER_URL:
            return {"available": False, "latency_ms": 0, "error": "CUSTOM_PROVIDER_URL unconfigured"}
        start = time.time()
        try:
            _ = self._get_client()
            return {"available": True, "latency_ms": int((time.time() - start) * 1000), "error": None}
        except Exception as e:
            return {"available": False, "latency_ms": int((time.time() - start) * 1000), "error": str(e)}

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

        target_model = model_override or "custom-model"
        kwargs = {
            "model": target_model,
            "messages": messages,
        }
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = await client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content

        if response_format == "json":
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_response": content, "error": "Failed to parse JSON response"}
        return {"text": content}
