"""
Capability Router & Scoring Engine Unit Tests for IdeaGPT AI Gateway v1.
"""

import pytest
from app.ai.gateway.router import CapabilityRouter, score_model_candidate
from app.ai.gateway.models import ModelDescriptor
from app.ai.gateway.contracts import AICapability, ModelCategory, ModelStatus
from app.ai.exceptions.ai_exceptions import AIUnavailableException, AIInvalidModelException


def test_score_model_candidate_deterministic():
    """Verify deterministic scoring ranking."""
    llama_70b = ModelDescriptor(
        provider="groq",
        model_id="llama-3.3-70b-versatile",
        display_name="Llama 3.3 70B",
        category=ModelCategory.CHAT,
        capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT, AICapability.REASONING],
        status=ModelStatus.ACTIVE,
        available=True,
    )
    score_70b = score_model_candidate(llama_70b, AICapability.STRUCTURED_OUTPUT)

    llama_8b = ModelDescriptor(
        provider="groq",
        model_id="llama-3.1-8b-instant",
        display_name="Llama 3.1 8B",
        category=ModelCategory.CHAT,
        capabilities=[AICapability.TEXT_GENERATION, AICapability.STRUCTURED_OUTPUT],
        status=ModelStatus.ACTIVE,
        available=True,
    )
    score_8b = score_model_candidate(llama_8b, AICapability.STRUCTURED_OUTPUT)

    # 70B versatile model should outrank 8B instant model for structured reasoning
    assert score_70b > score_8b


def test_route_request_auto_auto():
    """Verify AUTO/AUTO routing chooses a valid active provider and model."""
    decision = CapabilityRouter.route_request(
        task_type="idea_evaluation",
        requested_provider="auto",
        requested_model="auto"
    )

    assert "actual_provider" in decision
    assert "actual_model" in decision
    assert decision["capability"] == AICapability.STRUCTURED_OUTPUT
    assert decision["actual_provider"] in ("groq", "gemini", "openai", "mock", "ollama")


def test_route_request_explicit_provider_auto_model():
    """Verify routing to an explicit provider picks a model from that provider."""
    decision = CapabilityRouter.route_request(
        task_type="idea_evaluation",
        requested_provider="groq",
        requested_model="auto"
    )

    assert decision["actual_provider"] == "groq"
    assert "llama" in decision["actual_model"].lower() or "gpt-oss" in decision["actual_model"].lower()


def test_route_request_explicit_compatible_model():
    """Verify explicit compatible model is strictly honored."""
    decision = CapabilityRouter.route_request(
        task_type="idea_evaluation",
        requested_provider="groq",
        requested_model="llama-3.3-70b-versatile"
    )

    assert decision["actual_provider"] == "groq"
    assert decision["actual_model"] == "llama-3.3-70b-versatile"
    assert decision["fallback_used"] is False


def test_route_request_unknown_provider_raises_unavailable():
    """Verify non-existent provider raises AIUnavailableException."""
    with pytest.raises(AIUnavailableException):
        CapabilityRouter.route_request(
            task_type="idea_evaluation",
            requested_provider="non_existent_provider_xyz",
            requested_model="auto"
        )
