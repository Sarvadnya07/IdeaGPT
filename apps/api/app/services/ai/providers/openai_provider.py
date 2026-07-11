import json
from typing import Any, Dict
from app.services.ai.base import AIProvider
from app.core.config import settings

class OpenAIProvider(AIProvider):
    def __init__(self):
        self._client = None

    def _get_client(self):
        # Lazy load client only when actually needed
        if self._client is None:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is missing. Cannot initialize OpenAI provider.")
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
            kwargs["response_format"] = { "type": "json_object" }

        response = await client.chat.completions.create(**kwargs)
        result_text = response.choices[0].message.content
        
        if response_format == "json":
            return json.loads(result_text)
        return {"text": result_text}
