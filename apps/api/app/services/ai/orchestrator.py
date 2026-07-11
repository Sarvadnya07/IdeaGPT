from app.services.ai.registry import registry
from app.services.ai.providers.openai_provider import OpenAIProvider

# Register default providers
registry.register("openai", OpenAIProvider())
# We can register "gemini", "ollama", etc. later

class AIOrchestrator:
    @staticmethod
    async def analyze_startup_idea(prompt: str, provider_name: str = "openai") -> dict:
        """
        Orchestrates an AI analysis for a startup idea using the specified provider.
        Business logic remains unaware of the underlying HTTP client.
        """
        provider = registry.get(provider_name)
        system_prompt = "You are a world-class AI Startup Analyst. You must return your analysis strictly as JSON matching the requested structure."
        
        return await provider.generate(prompt=prompt, system_prompt=system_prompt, response_format="json")

orchestrator = AIOrchestrator()
