"""
Unified AI Router for IdeaGPT.
Routes task requests through the capability scoring engine in app.ai.gateway.router.
"""

from typing import Optional, Dict, Any, List
from app.ai.gateway.router import CapabilityRouter
from app.ai.exceptions.ai_exceptions import AIUnavailableException, AIInvalidModelException
from app.core.config import settings


class AIRouter:
    @staticmethod
    def route(task_type: str = "idea_evaluation") -> str:
        """Legacy helper returning provider name string."""
        if settings.GROQ_API_KEY and settings.ENABLE_GROQ is not False:
            return "groq"
        if settings.OPENAI_API_KEY and settings.ENABLE_OPENAI:
            return "openai"
        if settings.GEMINI_API_KEY and settings.ENABLE_GEMINI:
            return "gemini"
        if settings.ENABLE_OLLAMA:
            return "ollama"
        return "mock"

    @staticmethod
    def route_task(
        task_type: str = "idea_evaluation",
        requested_provider: str = "auto",
        requested_model: str = "auto",
        has_byok: bool = False
    ) -> Dict[str, Any]:
        """
        Routes an AI request to a specific provider and model based on task requirements,
        available providers, model capabilities, and user preference.
        """
        return CapabilityRouter.route_request(
            task_type=task_type,
            requested_provider=requested_provider,
            requested_model=requested_model,
            has_byok=has_byok
        )
