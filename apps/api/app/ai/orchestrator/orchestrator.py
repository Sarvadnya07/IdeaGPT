from app.ai.orchestrator.factory import ProviderFactory
from app.ai.orchestrator.router import AIRouter

class AIOrchestrator:
    @staticmethod
    async def analyze_startup_idea(prompt: str, strategy: str = "auto", preferred_provider: str = None) -> dict:
        """
        Main entry point for startup idea AI evaluation.
        Decoupled from direct vendor imports.
        """
        provider_name = AIRouter.route(strategy=strategy, preferred=preferred_provider)
        provider = ProviderFactory.create_provider(provider_name)
        
        system_prompt = "You are a world-class AI Startup Analyst. You must return your analysis strictly as JSON matching the requested structure."
        return await provider.generate(prompt=prompt, system_prompt=system_prompt, response_format="json")

orchestrator = AIOrchestrator()
