import json
import time
from typing import Any, Dict, List, Optional
from app.ai.providers.base import AIProvider
from app.core.config import settings

class GeminiProvider(AIProvider):
    def __init__(self):
        self._client = None
        self.provider_id = "gemini"
        self.display_name = "Google Gemini"

    def _get_client(self, model_name: str = "gemini-1.5-flash"):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel(model_name)

    def list_models(self) -> List[Dict[str, Any]]:
        is_configured = bool(settings.GEMINI_API_KEY and settings.ENABLE_GEMINI)
        return [
            {
                "id": "gemini-1.5-flash",
                "name": "Gemini 1.5 Flash",
                "provider": self.provider_id,
                "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT"],
                "configured": is_configured,
                "available": is_configured,
            },
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "provider": self.provider_id,
                "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT"],
                "configured": is_configured,
                "available": is_configured,
            },
        ]

    async def health(self) -> Dict[str, Any]:
        if not settings.GEMINI_API_KEY or not settings.ENABLE_GEMINI:
            return {"available": False, "latency_ms": 0, "error": "Gemini provider disabled or missing API key"}
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
        target_model = model_override or "gemini-1.5-flash"
        model = self._get_client(target_model)
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        generation_config = {}
        if response_format == "json":
            generation_config["response_mime_type"] = "application/json"

        response = await model.generate_content_async(
            full_prompt,
            generation_config=generation_config
        )
        content = response.text

        if response_format == "json":
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_response": content, "error": "Failed to parse JSON response"}
        return {"text": content}
