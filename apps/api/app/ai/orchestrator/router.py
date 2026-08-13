from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.ai.exceptions.ai_exceptions import AIUnavailableException
from app.services.ai_registry_service import AIRegistryService

class AIRouter:
    @staticmethod
    def route_task(
        task_type: str = "idea_evaluation",
        requested_provider: str = "auto",
        requested_model: str = "auto"
    ) -> Dict[str, Any]:
        """
        Routes an AI request to a specific provider and model based on task requirements,
        available providers, model capabilities, and user preference.

        Supports 3 Routing Modes:
          1. Provider = AUTO, Model = AUTO -> Auto-select best provider & model.
          2. Provider = GROQ, Model = AUTO -> Use Groq, auto-select active model.
          3. Provider = GROQ, Model = <specific_model> -> Use Groq & specific model.
        """
        req_prov = (requested_provider or "auto").lower()
        req_mod = (requested_model or "auto").lower()

        # Step 1: Explicit Provider & Explicit Model
        if req_prov != "auto" and req_mod != "auto":
            return {
                "requested_provider": requested_provider,
                "requested_model": requested_model,
                "actual_provider": req_prov,
                "actual_model": requested_model,
                "fallback_reason": None
            }

        # Step 2: Determine Available Providers
        providers = AIRegistryService.get_providers()
        available_prov_ids = [p["id"] for p in providers if p.get("configured") and p.get("state") == "AVAILABLE"]

        # If test mode or mock default
        if settings.APP_ENV == "test" or settings.DEFAULT_PROVIDER == "mock":
            if "mock" not in available_prov_ids:
                available_prov_ids.append("mock")

        if not available_prov_ids:
            raise AIUnavailableException("No active AI provider is enabled on this system.")

        # Step 3: Handle Explicit Provider + AUTO Model
        if req_prov != "auto":
            if req_prov not in available_prov_ids and req_prov != "mock":
                raise AIUnavailableException(f"Requested AI provider '{requested_provider}' is not available or configured.")

            target_model = req_mod
            if req_mod == "auto":
                # Find models for requested provider
                all_models = AIRegistryService.get_available_models()
                p_models = [m for m in all_models if m.get("provider") == req_prov and m.get("available")]

                # Filter by task capability requirements
                if task_type in ("idea_evaluation", "structured_report"):
                    p_models = [m for m in p_models if "STRUCTURED_OUTPUT" in m.get("capabilities", [])]

                if p_models:
                    target_model = p_models[0]["id"]
                else:
                    target_model = "auto"

            return {
                "requested_provider": requested_provider,
                "requested_model": requested_model,
                "actual_provider": req_prov,
                "actual_model": target_model,
                "fallback_reason": None
            }

        # Step 4: AUTO Provider + AUTO Model Selection Policy
        # Priority order: Groq -> OpenAI -> Gemini -> Ollama -> Custom -> Mock
        priority = ["groq", "openai", "gemini", "ollama", "custom", "mock"]
        chosen_prov = None
        fallback_reason = None

        for p_id in priority:
            if p_id in available_prov_ids:
                chosen_prov = p_id
                break

        if not chosen_prov:
            raise AIUnavailableException("No available AI provider matched routing policy.")

        # Discover active model for chosen provider
        all_models = AIRegistryService.get_available_models()
        p_models = [m for m in all_models if m.get("provider") == chosen_prov and m.get("available")]

        if task_type in ("idea_evaluation", "structured_report"):
            p_models = [m for m in p_models if "STRUCTURED_OUTPUT" in m.get("capabilities", [])]

        chosen_mod = p_models[0]["id"] if p_models else "auto"

        return {
            "requested_provider": requested_provider,
            "requested_model": requested_model,
            "actual_provider": chosen_prov,
            "actual_model": chosen_mod,
            "fallback_reason": fallback_reason
        }

    @staticmethod
    def route(strategy: str = "auto", preferred: str = None) -> str:
        """Legacy helper string router for backward compatibility."""
        decision = AIRouter.route_task(task_type="idea_evaluation", requested_provider=preferred or strategy)
        return decision["actual_provider"]
