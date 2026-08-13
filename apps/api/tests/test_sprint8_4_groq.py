import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.ai.providers.groq import GroqProvider
from app.services.ai_registry_service import AIRegistryService
from app.ai.orchestrator.router import AIRouter

client = TestClient(app)

@pytest.mark.asyncio
async def test_groq_not_configured():
    """Verifies that unconfigured Groq returns NOT_CONFIGURED state without application crashes."""
    with patch.object(settings, "GROQ_API_KEY", None), patch.object(settings, "ENABLE_GROQ", None):
        AIRegistryService.refresh_registry_cache()
        providers = AIRegistryService.get_providers()
        groq_info = next((p for p in providers if p["id"] == "groq"), None)

        assert groq_info is not None
        assert groq_info["configured"] is False
        assert groq_info["state"] == "NOT_CONFIGURED"

@pytest.mark.asyncio
async def test_groq_configuration_auto_detected():
    """Verifies that setting GROQ_API_KEY auto-detects Groq as AVAILABLE without needing ENABLE_GROQ=True."""
    with patch.object(settings, "GROQ_API_KEY", "gsk_test_mock_key_12345"), patch.object(settings, "ENABLE_GROQ", None):
        AIRegistryService.refresh_registry_cache()
        providers = AIRegistryService.get_providers()
        groq_info = next((p for p in providers if p["id"] == "groq"), None)

        assert groq_info is not None
        assert groq_info["configured"] is True
        assert groq_info["state"] == "AVAILABLE"

@pytest.mark.asyncio
async def test_groq_model_discovery_mocked():
    """Mocks Groq models API payload and verifies normalized descriptor metadata."""
    mock_model_1 = MagicMock()
    mock_model_1.id = "llama-3.3-70b-versatile"
    mock_model_1.active = True
    mock_model_1.context_window = 131072

    mock_models_response = MagicMock()
    mock_models_response.data = [mock_model_1]

    mock_client = AsyncMock()
    mock_client.models.list.return_value = mock_models_response

    provider = GroqProvider()
    with patch.object(settings, "GROQ_API_KEY", "gsk_mock_123"), patch.object(provider, "_get_client", return_value=mock_client):
        descriptors = await provider.list_models_async()

        assert len(descriptors) == 1
        d = descriptors[0]
        assert d["id"] == "llama-3.3-70b-versatile"
        assert d["provider"] == "groq"
        assert "STRUCTURED_OUTPUT" in d["capabilities"]
        assert d["capability_source"] == "provider_metadata"
        assert d["capability_confidence"] == "verified"
        assert d["context_window"] == 131072
        assert d["state"] == "ACTIVE"

@pytest.mark.asyncio
async def test_three_routing_semantics():
    """Verifies the 3 required routing semantics (AUTO/AUTO, GROQ/AUTO, GROQ/SPECIFIC)."""
    # 1. Provider = AUTO, Model = AUTO
    decision_1 = AIRouter.route_task(task_type="idea_evaluation", requested_provider="auto", requested_model="auto")
    assert decision_1["requested_provider"] == "auto"
    assert decision_1["actual_provider"] in ("groq", "openai", "gemini", "ollama", "custom", "mock")

    # 2. Provider = GROQ, Model = AUTO
    with patch.object(settings, "GROQ_API_KEY", "gsk_mock_123"), patch.object(settings, "ENABLE_GROQ", True):
        AIRegistryService.refresh_registry_cache()
        decision_2 = AIRouter.route_task(task_type="idea_evaluation", requested_provider="groq", requested_model="auto")
        assert decision_2["requested_provider"] == "groq"
        assert decision_2["actual_provider"] == "groq"

    # 3. Provider = GROQ, Model = specific
    decision_3 = AIRouter.route_task(task_type="idea_evaluation", requested_provider="groq", requested_model="llama-3.3-70b-versatile")
    assert decision_3["actual_provider"] == "groq"
    assert decision_3["actual_model"] == "llama-3.3-70b-versatile"

@pytest.mark.asyncio
async def test_groq_generation_usage_tracking_mocked():
    """Mocks Groq chat completions and verifies token usage metadata extraction."""
    mock_choice = MagicMock()
    mock_choice.message.content = '{"summary": "Test evaluation", "score": 85}'

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 120
    mock_usage.completion_tokens = 45
    mock_usage.total_tokens = 165

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = mock_usage

    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = mock_response

    provider = GroqProvider()
    with patch.object(settings, "GROQ_API_KEY", "gsk_mock_123"), patch.object(provider, "_get_client", return_value=mock_client):
        result = await provider.generate(
            prompt="Analyze test startup",
            system_prompt="Return JSON",
            response_format="json",
            model_override="llama-3.3-70b-versatile"
        )

        assert result["summary"] == "Test evaluation"
        assert result["score"] == 85
        assert "_usage" in result
        assert result["_usage"]["input_tokens"] == 120
        assert result["_usage"]["output_tokens"] == 45
        assert result["_usage"]["total_tokens"] == 165

@pytest.mark.skipif(os.getenv("GROQ_E2E") != "true", reason="Opt-in real Groq E2E test requires GROQ_E2E=true and GROQ_API_KEY")
@pytest.mark.asyncio
async def test_optin_real_groq_e2e():
    """Opt-in real Groq E2E test. Only executes when GROQ_E2E=true environment variable is set."""
    provider = GroqProvider()
    assert provider.is_configured is True

    models = await provider.list_models_async()
    assert len(models) > 0

    res = await provider.generate(
        prompt="Analyze a dev tool idea.",
        system_prompt="Return JSON with summary and score.",
        response_format="json"
    )
    assert "summary" in res or "raw_response" in res
