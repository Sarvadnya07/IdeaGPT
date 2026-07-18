import json
import httpx
from typing import Any, Dict
from app.ai.providers.base import AIProvider
from app.core.config import settings

class OllamaProvider(AIProvider):
    def __init__(self):
        pass

    async def generate(self, prompt: str, system_prompt: str = "", response_format: str = "json") -> Dict[str, Any]:
        url = f"{settings.OLLAMA_URL.rstrip('/')}/api/generate"
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
        }
        if response_format == "json":
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            res_data = response.json()
            content = res_data.get("response", "")

            if response_format == "json":
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"raw_response": content, "error": "Failed to parse JSON response"}
            return {"text": content}
