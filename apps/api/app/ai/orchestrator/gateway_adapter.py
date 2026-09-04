"""
IdeaGPT AI Gateway — Legacy AIProvider Compatibility Adapter.
Wraps any canonical BaseProviderAdapter to satisfy the legacy AIProvider interface
(generate, health, list_models). Ensures 100% single canonical provider execution path.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from app.ai.providers.base import AIProvider
from app.ai.gateway.providers.base_adapter import BaseProviderAdapter
from app.ai.gateway.models import AIRequest
from app.ai.gateway.contracts import AICapability

logger = logging.getLogger(__name__)


class GatewayAIProviderAdapter(AIProvider):
    """
    Adapter that wraps a canonical BaseProviderAdapter and presents
    the legacy AIProvider interface.
    """

    def __init__(self, adapter: BaseProviderAdapter):
        self.adapter = adapter
        self.provider_id = adapter.provider_id
        self.display_name = adapter.display_name

    def list_models(self) -> List[Dict[str, Any]]:
        """Synchronously exposes active model descriptors for legacy callers."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                models = [
                    {
                        "id": f"{self.provider_id}-default",
                        "name": f"{self.display_name} Model",
                        "provider": self.provider_id,
                        "capabilities": [c.value for c in self.adapter.capabilities],
                        "configured": self.adapter.is_configured,
                        "available": self.adapter.is_enabled,
                    }
                ]
                return models
            else:
                models_desc = loop.run_until_complete(self.adapter.list_models())
                return [m.model_dump() for m in models_desc]
        except Exception:
            return [
                {
                    "id": f"{self.provider_id}-default",
                    "name": f"{self.display_name} Model",
                    "provider": self.provider_id,
                    "capabilities": [c.value for c in self.adapter.capabilities],
                    "configured": self.adapter.is_configured,
                    "available": self.adapter.is_enabled,
                }
            ]

    async def health(self) -> Dict[str, Any]:
        """Delegates health check to gateway adapter."""
        try:
            desc = await self.adapter.health()
            return {
                "available": desc.configured and desc.enabled,
                "latency_ms": desc.latency_ms,
                "error": desc.error,
            }
        except Exception as e:
            return {"available": False, "latency_ms": 0, "error": str(e)}

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        response_format: str = "json",
        model_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes generation via the canonical BaseProviderAdapter.
        Returns parsed JSON dict if response_format == 'json'.
        """
        req = AIRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            capability=AICapability.STRUCTURED_OUTPUT if response_format == "json" else AICapability.TEXT_GENERATION,
            model_override=model_override,
        )

        res = await self.adapter.execute(req)

        if res.structured_data:
            out = dict(res.structured_data)
            out["_actual_model"] = res.model
            out["_provider"] = res.provider
            out["_usage"] = res.usage.model_dump() if res.usage else {}
            return out

        if res.text:
            cleaned = res.text.strip()
            if response_format == "json":
                from app.ai.validators.output_validator import OutputValidator
                try:
                    cleaned_json = OutputValidator.clean_json_string(cleaned)
                    out = json.loads(cleaned_json)
                    if isinstance(out, dict):
                        out["_actual_model"] = res.model
                        out["_provider"] = res.provider
                        out["_usage"] = res.usage.model_dump() if res.usage else {}
                        return out
                except Exception as e:
                    logger.warning(f"Failed to parse JSON text from gateway adapter: {e}")
            return {
                "text": cleaned,
                "_actual_model": res.model,
                "_provider": res.provider,
                "_usage": res.usage.model_dump() if res.usage else {},
            }

        return {
            "_actual_model": res.model,
            "_provider": res.provider,
            "_usage": res.usage.model_dump() if res.usage else {},
        }
