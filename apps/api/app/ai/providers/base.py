from typing import Any, Dict

class AIProvider:
    """Base interface for all AI Providers."""
    async def generate(self, prompt: str, system_prompt: str = "", response_format: str = "json") -> Dict[str, Any]:
        """
        Generate a response given a prompt.
        Must return a parsed JSON dictionary if response_format == 'json'.
        """
        raise NotImplementedError("AI Providers must implement generate()")
