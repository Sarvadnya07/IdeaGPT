"""
IdeaGPT AI Gateway v1 — Capability Router & Scoring Engine.
Implements multi-factor deterministic candidate ranking, explicit model validation,
and observable fallback policies.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.ai.gateway.models import AIRequest, ModelDescriptor
from app.ai.gateway.contracts import AICapability, ModelCategory, ModelStatus, ProviderState
from app.ai.gateway.registry import gateway_registry
from app.ai.exceptions.ai_exceptions import (
    AIUnavailableException,
    AIInvalidModelException,
)

logger = logging.getLogger(__name__)


def score_model_candidate(
    model: ModelDescriptor,
    required_capability: AICapability,
    preferred_provider: Optional[str] = None,
    has_byok: bool = False
) -> float:
    """
    Deterministic scoring:
      Capability match (30%)
      Quality (20%)
      Availability & Health (15%)
      Cost (10%)
      Latency (10%)
      Free quota (5%)
      User/BYOK preference (5%)
      Privacy (5%)
    """
    score = 0.0

    # 1. Capability Match (30 pts)
    if required_capability in model.capabilities:
        score += 30.0
    elif required_capability == AICapability.STRUCTURED_OUTPUT and model.supports_structured_output:
        score += 25.0
    else:
        return 0.0  # Incompatible

    # 2. Quality & Model Family (20 pts)
    m_id = model.model_id.lower()
    if any(k in m_id for k in ("llama-3.3-70b", "gpt-4o", "gemini-2.0-flash", "o3-mini", "120b")):
        score += 20.0
    elif any(k in m_id for k in ("gemini-1.5-pro", "llama-3.1-8b", "gpt-4o-mini", "qwen3.8")):
        score += 16.0
    elif any(k in m_id for k in ("mistral", "gemma", "phi3")):
        score += 12.0
    else:
        score += 8.0

    # 3. Availability & Status (15 pts)
    if model.status == ModelStatus.ACTIVE and model.available:
        score += 15.0
    elif model.status == ModelStatus.PREVIEW:
        score += 10.0

    # 4. Latency / Fast Provider (10 pts)
    if model.provider == "groq":
        score += 10.0
    elif model.provider in ("gemini", "openai"):
        score += 8.0
    elif model.provider == "ollama":
        score += 6.0

    # 5. Cost / Free Tier Preference (10 pts)
    if model.provider in ("groq", "ollama", "gemini"):
        score += 10.0
    else:
        score += 6.0

    # 6. Free Quota & Default (5 pts)
    if model.provider == "groq":
        score += 5.0

    # 7. User / BYOK Preference (5 pts)
    if preferred_provider and model.provider.lower() == preferred_provider.lower():
        score += 5.0
    elif has_byok:
        score += 3.0

    # 8. Privacy (5 pts)
    if model.provider == "ollama":
        score += 5.0
    else:
        score += 3.0

    return score


PROVIDER_MODEL_ALLOWLIST: Dict[str, Dict[str, Dict[str, Any]]] = {
    "groq": {
        "llama-3.3-70b-versatile": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.REASONING], "status": ModelStatus.ACTIVE},
        "llama-3.1-8b-instant": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT], "status": ModelStatus.ACTIVE},
        "openai/gpt-oss-120b": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.REASONING], "status": ModelStatus.ACTIVE},
        "llama-3.3-70b-specdec": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT], "status": ModelStatus.ACTIVE},
        "qwen/qwen3.8-27b": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT], "status": ModelStatus.ACTIVE},
        "mixtral-8x7b-32768": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT], "status": ModelStatus.ACTIVE},
        "whisper-large-v3": {"capabilities": [], "status": ModelStatus.ACTIVE},
        "llama-guard-3-8b": {"capabilities": [AICapability.MODERATION], "status": ModelStatus.ACTIVE},
    },
    "gemini": {
        "gemini-2.0-flash": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.VISION, AICapability.DOCUMENT_UNDERSTANDING], "status": ModelStatus.ACTIVE},
        "gemini-1.5-pro": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.REASONING, AICapability.STRUCTURED_OUTPUT, AICapability.VISION, AICapability.DOCUMENT_UNDERSTANDING], "status": ModelStatus.ACTIVE},
        "gemini-1.5-flash": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.VISION], "status": ModelStatus.ACTIVE},
    },
    "openai": {
        "gpt-4o": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.VISION], "status": ModelStatus.ACTIVE},
        "gpt-4o-mini": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.VISION], "status": ModelStatus.ACTIVE},
        "o3-mini": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.REASONING, AICapability.STRUCTURED_OUTPUT], "status": ModelStatus.ACTIVE},
        "text-embedding-3-small": {"capabilities": [AICapability.EMBEDDING], "status": ModelStatus.ACTIVE},
    },
    "ollama": {
        "llama3.2": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT], "status": ModelStatus.ACTIVE},
        "deepseek-r1": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.REASONING, AICapability.STRUCTURED_OUTPUT], "status": ModelStatus.ACTIVE},
        "mistral": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT], "status": ModelStatus.ACTIVE},
    },
    "tavily": {
        "tavily-search-v1": {"capabilities": [AICapability.WEB_RESEARCH], "status": ModelStatus.ACTIVE},
    },
    "mock": {
        "mock-model": {"capabilities": [AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.REASONING, AICapability.VISION, AICapability.DOCUMENT_UNDERSTANDING, AICapability.EMBEDDING, AICapability.MODERATION, AICapability.WEB_RESEARCH], "status": ModelStatus.ACTIVE}
    }
}


class CapabilityRouter:
    @staticmethod
    def map_task_to_capability(task_type: str) -> AICapability:
        mapping = {
            "idea_evaluation": AICapability.STRUCTURED_OUTPUT,
            "startup_evaluation": AICapability.STRUCTURED_OUTPUT,
            "structured_report": AICapability.STRUCTURED_OUTPUT,
            "market_analysis": AICapability.STRUCTURED_OUTPUT,
            "competitor_analysis": AICapability.STRUCTURED_OUTPUT,
            "roadmap_generation": AICapability.STRUCTURED_OUTPUT,
            "tech_stack": AICapability.STRUCTURED_OUTPUT,
            "architecture": AICapability.STRUCTURED_OUTPUT,
            "prd": AICapability.STRUCTURED_OUTPUT,
            "pitch_deck": AICapability.STRUCTURED_OUTPUT,
            "fast_summary": AICapability.TEXT_GENERATION,
            "deep_reasoning": AICapability.REASONING,
            "web_research": AICapability.WEB_RESEARCH,
            "vision_analysis": AICapability.VISION,
            "document_analysis": AICapability.DOCUMENT_UNDERSTANDING,
            "similarity": AICapability.EMBEDDING,
            "moderation": AICapability.MODERATION,
        }
        return mapping.get(task_type, AICapability.STRUCTURED_OUTPUT)

    @classmethod
    def route_request(
        cls,
        task_type: str = "idea_evaluation",
        requested_provider: Optional[str] = "auto",
        requested_model: Optional[str] = "auto",
        has_byok: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates optimal routing decision based on task capability requirements,
        available configured providers, and explicit user selection.
        """
        req_prov = (requested_provider or "auto").lower()
        req_mod = (requested_model or "auto").lower()
        if req_mod in ("default", "none", ""):
            req_mod = "auto"

        required_cap = cls.map_task_to_capability(task_type)

        # ------------------------------------------------------------------
        # Step 0: Validate model compatibility first
        # ------------------------------------------------------------------
        if req_mod != "auto":
            if "whisper" in req_mod and required_cap != AICapability.TEXT_GENERATION:
                raise AIInvalidModelException(f"Model '{requested_model}' does not support structured text generation.")
            if ("guard" in req_mod or "moderation" in req_mod) and required_cap not in (AICapability.MODERATION,):
                raise AIInvalidModelException(f"Model '{requested_model}' is a moderation guard and cannot generate text.")

        # ------------------------------------------------------------------
        # Step 1: Explicit Provider & Explicit Model Validation (Allowlist & Capabilities)
        # ------------------------------------------------------------------
        if req_prov != "auto" and req_mod != "auto":
            if req_prov not in PROVIDER_MODEL_ALLOWLIST and req_prov != "mock":
                raise AIUnavailableException(f"Requested provider '{requested_provider}' is not supported.")

            adapter = gateway_registry.get_adapter(req_prov)
            if not adapter or (not adapter.is_enabled and settings.APP_ENV != "test"):
                if req_prov == "mock" and settings.APP_ENV == "test":
                    pass
                else:
                    raise AIUnavailableException(f"Requested provider '{requested_provider}' is not available or configured.")

            allowed_models = PROVIDER_MODEL_ALLOWLIST.get(req_prov, {})
            # Find matched model (case-insensitive)
            matched_key = next((k for k in allowed_models.keys() if k.lower() == req_mod), None)
            if not matched_key and req_prov != "mock":
                raise AIInvalidModelException(f"Model '{requested_model}' is not in the allowlist for provider '{requested_provider}'.")

            model_meta = allowed_models.get(matched_key, {})
            if model_meta.get("status") == ModelStatus.UNAVAILABLE:
                raise AIInvalidModelException(f"Model '{requested_model}' is currently retired or unavailable.")

            caps = model_meta.get("capabilities", [])
            if required_cap not in caps and required_cap != AICapability.TEXT_GENERATION and req_prov != "mock":
                raise AIInvalidModelException(f"Model '{requested_model}' does not support required capability '{required_cap.value}' for task '{task_type}'.")

            return {
                "requested_provider": requested_provider,
                "requested_model": requested_model,
                "actual_provider": req_prov,
                "actual_model": matched_key or requested_model,
                "fallback_used": False,
                "fallback_reason": None,
                "capability": required_cap,
            }

        # ------------------------------------------------------------------
        # Step 2: Determine Available Models Pool
        # ------------------------------------------------------------------
        adapters = gateway_registry.list_adapters()
        candidate_models: List[Tuple[ModelDescriptor, float]] = []

        for adapter in adapters:
            if not adapter.is_enabled and settings.APP_ENV != "test":
                continue

            # In test environment, allow mock
            if adapter.provider_id == "mock":
                if settings.APP_ENV != "test" and not (settings.APP_ENV == "development" and settings.DEFAULT_PROVIDER == "mock"):
                    continue

            # If user requested explicit provider, restrict to that provider
            if req_prov != "auto" and adapter.provider_id != req_prov:
                continue

            # List models sync/cached
            try:
                # Fast sync listing for routing
                if adapter.provider_id == "groq":
                    m_list = [
                        ModelDescriptor(
                            provider="groq",
                            model_id="llama-3.3-70b-versatile",
                            display_name="Llama 3.3 70B Versatile",
                            capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.REASONING],
                            supports_structured_output=True,
                            available=True,
                        ),
                        ModelDescriptor(
                            provider="groq",
                            model_id="openai/gpt-oss-120b",
                            display_name="GPT-OSS 120B",
                            capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.REASONING],
                            supports_structured_output=True,
                            available=True,
                        ),
                        ModelDescriptor(
                            provider="groq",
                            model_id="llama-3.1-8b-instant",
                            display_name="Llama 3.1 8B Instant",
                            capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT],
                            supports_structured_output=True,
                            available=True,
                        ),
                    ]
                elif adapter.provider_id == "gemini":
                    m_list = [
                        ModelDescriptor(
                            provider="gemini",
                            model_id="gemini-2.0-flash",
                            display_name="Gemini 2.0 Flash",
                            capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.VISION, AICapability.DOCUMENT_UNDERSTANDING],
                            supports_structured_output=True,
                            available=True,
                        ),
                        ModelDescriptor(
                            provider="gemini",
                            model_id="gemini-1.5-pro",
                            display_name="Gemini 1.5 Pro",
                            capabilities=[AICapability.TEXT_GENERATION, AICapability.REASONING, AICapability.STRUCTURED_OUTPUT, AICapability.VISION, AICapability.DOCUMENT_UNDERSTANDING],
                            supports_structured_output=True,
                            available=True,
                        ),
                    ]
                elif adapter.provider_id == "openai":
                    m_list = [
                        ModelDescriptor(
                            provider="openai",
                            model_id="gpt-4o",
                            display_name="GPT-4o",
                            capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.VISION],
                            supports_structured_output=True,
                            available=True,
                        ),
                        ModelDescriptor(
                            provider="openai",
                            model_id="gpt-4o-mini",
                            display_name="GPT-4o Mini",
                            capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.VISION],
                            supports_structured_output=True,
                            available=True,
                        ),
                    ]
                elif adapter.provider_id == "mock":
                    m_list = [
                        ModelDescriptor(
                            provider="mock",
                            model_id="mock-model",
                            display_name="Mock Model",
                            capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.REASONING],
                            supports_structured_output=True,
                            available=True,
                        )
                    ]
                else:
                    m_list = []

                for m in m_list:
                    score = score_model_candidate(m, required_cap, preferred_provider=req_prov if req_prov != "auto" else None, has_byok=has_byok)
                    if score > 0:
                        candidate_models.append((m, score))
            except Exception:
                continue

        if not candidate_models:
            # Check if explicit provider was requested and failed
            if req_prov != "auto":
                raise AIUnavailableException(f"Requested AI provider '{requested_provider}' is not available or configured.")
            raise AIUnavailableException("No active AI provider is enabled on this system.")

        # Sort candidate models by score descending
        candidate_models.sort(key=lambda x: x[1], reverse=True)
        best_model, best_score = candidate_models[0]

        return {
            "requested_provider": requested_provider,
            "requested_model": requested_model,
            "actual_provider": best_model.provider,
            "actual_model": best_model.model_id,
            "fallback_used": (req_prov != "auto" and req_prov != best_model.provider),
            "fallback_reason": f"Routed via capability scoring (score: {best_score:.1f})",
            "capability": required_cap,
        }
