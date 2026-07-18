import json
from typing import Any, Dict
from app.ai.providers.base import AIProvider
from app.core.config import settings

class GeminiProvider(AIProvider):
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not configured.")
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._client = genai.GenerativeModel("gemini-1.5-flash")
        return self._client

    async def generate(self, prompt: str, system_prompt: str = "", response_format: str = "json") -> Dict[str, Any]:
        model = self._get_client()
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
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
