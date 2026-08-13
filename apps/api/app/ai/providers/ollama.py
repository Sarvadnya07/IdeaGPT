import json
import time
import httpx
from typing import Any, Dict, List, Optional
from app.ai.providers.base import AIProvider
from app.core.config import settings

class OllamaProvider(AIProvider):
    def __init__(self):
        self.provider_id = "ollama"
        self.display_name = "Ollama (Local LLM)"

    def list_models(self) -> List[Dict[str, Any]]:
        is_configured = bool(settings.ENABLE_OLLAMA and settings.OLLAMA_URL)
        return [
            {
                "id": "llama3",
                "name": "Llama 3",
                "provider": self.provider_id,
                "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT"],
                "configured": is_configured,
                "available": is_configured,
            },
            {
                "id": "mistral",
                "name": "Mistral 7B",
                "provider": self.provider_id,
                "capabilities": ["TEXT_GENERATION", "STRUCTURED_OUTPUT"],
                "configured": is_configured,
                "available": is_configured,
            },
        ]

    async def health(self) -> Dict[str, Any]:
        if not settings.ENABLE_OLLAMA or not settings.OLLAMA_URL:
            return {"available": False, "latency_ms": 0, "error": "Ollama is disabled or URL unconfigured"}
        start = time.time()
        url = f"{settings.OLLAMA_URL.rstrip('/')}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return {"available": True, "latency_ms": int((time.time() - start) * 1000), "error": None}
                return {"available": False, "latency_ms": int((time.time() - start) * 1000), "error": f"Ollama HTTP {response.status_code}"}
        except Exception as e:
            return {"available": False, "latency_ms": int((time.time() - start) * 1000), "error": f"Connection failed: {str(e)}"}

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        response_format: str = "json",
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"{settings.OLLAMA_URL.rstrip('/')}/api/generate"
        target_model = model_override or "llama3"
        payload = {
            "model": target_model,
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
