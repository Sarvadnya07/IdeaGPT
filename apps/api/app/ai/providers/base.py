"""
DEPRECATED LEGACY PROVIDER INTERFACE.

This module is retained only as a compatibility shim for the AI Gateway
transition. The canonical provider contract is
``app.ai.gateway.providers.base_adapter.BaseProviderAdapter``.

Do NOT add new providers here, and do NOT import this module from services,
routes, or workers. ``ProviderFactory.create_provider()`` wraps every
canonical adapter in ``GatewayAIProviderAdapter``, so all production execution
already flows through the gateway. This rule is enforced by
``tests/test_architecture_fitness.py``.
"""

from typing import Any, Dict, List, Optional


class AIProvider:
    """
    Deprecated base interface for AI Providers.

    Superseded by ``BaseProviderAdapter``; see the module docstring.
    """

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        response_format: str = "json",
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response given a prompt.
        Must return a parsed JSON dictionary if response_format == 'json'.
        """
        raise NotImplementedError("AI Providers must implement generate()")

    async def health(self) -> Dict[str, Any]:
        """
        Check provider health and connectivity.
        Returns dictionary with keys: available (bool), latency_ms (int), error (str|None).
        """
        return {"available": False, "latency_ms": 0, "error": "Health check not implemented"}

    def list_models(self) -> List[Dict[str, Any]]:
        """
        Returns list of model metadata dictionaries:
        [{ "id": str, "name": str, "capabilities": List[str], "configured": bool, "available": bool }]
        """
        return []
