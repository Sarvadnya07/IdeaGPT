import json
from typing import Any, Dict
from app.ai.providers.base import AIProvider
from app.core.config import settings

class OpenAIProvider(AIProvider):
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not configured.")
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    async def generate(self, prompt: str, system_prompt: str = "", response_format: str = "json") -> Dict[str, Any]:
        client = self._get_client()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": "gpt-4o-mini",
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
