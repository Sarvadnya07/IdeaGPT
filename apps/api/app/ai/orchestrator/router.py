from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.ai.exceptions.ai_exceptions import AIUnavailableException, AIInvalidModelException
from app.services.ai_registry_service import AIRegistryService

def filter_and_rank_models(models: List[Dict[str, Any]], task_type: str) -> List[Dict[str, Any]]:
    """
    Semantic capability filtering and deterministic ranking.
    Excludes incompatible models (e.g., Whisper, Prompt Guard) from chat/evaluation task candidate pools.
    """
    active = [m for m in models if m.get("available") and m.get("state") == "ACTIVE"]
    candidates = []

    for m in active:
        caps = m.get("capabilities", [])
        cat = m.get("category", "CHAT")

        if task_type in ("idea_evaluation", "structured_report"):
            # Requires TEXT_GENERATION + STRUCTURED_OUTPUT; exclude SPEECH_TO_TEXT and MODERATION
            if "TEXT_GENERATION" in caps and "STRUCTURED_OUTPUT" in caps and cat not in ("SPEECH_TO_TEXT", "MODERATION"):
                candidates.append(m)
        elif task_type == "fast_summary":
            if "TEXT_GENERATION" in caps and cat not in ("SPEECH_TO_TEXT", "MODERATION"):
                candidates.append(m)
        elif task_type == "speech_to_text":
            if "SPEECH_TO_TEXT" in caps or cat == "SPEECH_TO_TEXT":
                candidates.append(m)
        else:
            if "TEXT_GENERATION" in caps and cat not in ("SPEECH_TO_TEXT", "MODERATION"):
                candidates.append(m)

    # Deterministic ranking: verified confidence > model family preference > context window
    def sort_key(m):
        conf_score = 2 if m.get("capability_confidence") == "verified" else 1
        mid = m.get("id", "").lower()
        # Prioritize production-ready versatile models (Llama 3.3 70b / Llama 3.1 8b / Mixtral) over preview models
        fam_score = (
            10 if "llama-3.3-70b-versatile" in mid
            else (9 if "llama-3.1-8b-instant" in mid
            else (8 if "mixtral" in mid
            else (7 if "gemma" in mid
            else (5 if "llama" in mid or "qwen" in mid
            else 0))))
        )
        ctx_score = m.get("context_window", 0)
        return (conf_score, fam_score, ctx_score)

    candidates.sort(key=sort_key, reverse=True)
    return candidates

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
          2. Provider = GROQ, Model = AUTO -> Use Groq, auto-select active chat model.
          3. Provider = GROQ, Model = <specific_model> -> Use Groq & specific model.
        """
        req_prov = (requested_provider or "auto").lower()
        req_mod = (requested_model or "auto").lower()
        if req_mod in ("default", "none", ""):
            req_mod = "auto"

        # Step 1: Explicit Provider & Explicit Model Validation
        if req_prov != "auto" and req_mod != "auto":
            # Verify explicit model is not incompatible with task
            all_models = AIRegistryService.get_available_models()
            matched = next((m for m in all_models if m["id"].lower() == req_mod and m["provider"].lower() == req_prov), None)
            if not matched and req_prov == "groq":
                from app.ai.providers.groq import classify_groq_model
                meta = classify_groq_model(req_mod)
                matched = {"id": req_mod, "provider": "groq", "category": meta.get("category", "CHAT")}

            if matched:
                cat = matched.get("category", "CHAT")
                if task_type in ("idea_evaluation", "structured_report") and cat in ("SPEECH_TO_TEXT", "MODERATION"):
                    raise AIInvalidModelException(f"Model '{requested_model}' ({cat}) does not support text generation/structured evaluation.")

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

        # Restrict mock provider to test environment or explicit dev mock mode
        if settings.APP_ENV == "test" or (settings.APP_ENV == "development" and settings.DEFAULT_PROVIDER == "mock"):
            if "mock" not in available_prov_ids:
                available_prov_ids.append("mock")

        if not available_prov_ids:
            raise AIUnavailableException("No active AI provider is enabled on this system.")

        # Step 3: Handle Explicit Provider + AUTO Model
        if req_prov != "auto":
            if req_prov not in available_prov_ids and req_prov != "mock":
                raise AIUnavailableException(f"Requested AI provider '{requested_provider}' is not available or configured.")

            all_models = AIRegistryService.get_available_models()
            p_models = [m for m in all_models if m.get("provider") == req_prov]
            ranked = filter_and_rank_models(p_models, task_type)

            target_model = ranked[0]["id"] if ranked else "auto"

            return {
                "requested_provider": requested_provider,
                "requested_model": requested_model,
                "actual_provider": req_prov,
                "actual_model": target_model,
                "fallback_reason": None
            }

        # Step 4: AUTO Provider + AUTO Model Selection Policy
        import os
        if settings.APP_ENV == "test" and os.getenv("GROQ_E2E") != "true":
            priority = ["mock", "groq", "openai", "gemini", "ollama", "custom"]
        else:
            priority = ["groq", "openai", "gemini", "ollama", "custom", "mock"]
        chosen_prov = None
        chosen_mod = "auto"
        fallback_reason = None

        all_models = AIRegistryService.get_available_models()

        for p_id in priority:
            if p_id in available_prov_ids:
                p_models = [m for m in all_models if m.get("provider") == p_id]
                ranked = filter_and_rank_models(p_models, task_type)
                if ranked or p_id == "mock":
                    chosen_prov = p_id
                    chosen_mod = ranked[0]["id"] if ranked else "auto"
                    break

        if not chosen_prov:
            raise AIUnavailableException("No available AI provider matched task routing policy.")

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
