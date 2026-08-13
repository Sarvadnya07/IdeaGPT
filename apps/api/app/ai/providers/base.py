from typing import Any, Dict, List, Optional

class AIProvider:
    """Base interface for all AI Providers."""

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
