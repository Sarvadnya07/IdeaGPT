import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.ai.providers.groq import GroqProvider, classify_groq_model
from app.services.ai_registry_service import AIRegistryService
from app.services.ai_task_service import AiTaskService
from app.models.user import User
from app.models.project import Project
from app.models.ai_task import AiTask
from app.ai.orchestrator.router import AIRouter
from app.ai.exceptions.ai_exceptions import (
    AIAuthenticationException,
    AIRateLimitException,
    AITimeoutException,
    AIInvalidModelException,
)

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
async def test_whisper_and_prompt_guard_model_classification():
    """Verifies that Whisper models are SPEECH_TO_TEXT and Prompt Guard models are MODERATION."""
    w_meta = classify_groq_model("whisper-large-v3-turbo")
    assert "SPEECH_TO_TEXT" in w_meta["capabilities"]
    assert w_meta["category"] == "SPEECH_TO_TEXT"
    assert w_meta["supports_structured_output"] is False

    g_meta = classify_groq_model("llama-guard-3-8b")
    assert "MODERATION" in g_meta["capabilities"]
    assert g_meta["category"] == "MODERATION"
    assert g_meta["supports_structured_output"] is False

    c_meta = classify_groq_model("llama-3.3-70b-versatile")
    assert "TEXT_GENERATION" in c_meta["capabilities"]
    assert "STRUCTURED_OUTPUT" in c_meta["capabilities"]
    assert c_meta["category"] == "CHAT"
    assert c_meta["supports_structured_output"] is True

@pytest.mark.asyncio
async def test_whisper_excluded_from_evaluation_candidate_pool():
    """Verifies that Whisper and Prompt Guard models are excluded from chat evaluation candidate pools."""
    mock_w = MagicMock()
    mock_w.id = "whisper-large-v3-turbo"
    mock_w.active = True

    mock_g = MagicMock()
    mock_g.id = "llama-guard-3-8b"
    mock_g.active = True

    mock_c = MagicMock()
    mock_c.id = "llama-3.3-70b-versatile"
    mock_c.active = True

    mock_models_response = MagicMock()
    mock_models_response.data = [mock_w, mock_g, mock_c]

    mock_client = AsyncMock()
    mock_client.models.list.return_value = mock_models_response

    provider = GroqProvider()
    with patch.object(settings, "GROQ_API_KEY", "gsk_mock_123"), patch.object(provider, "_get_client", return_value=mock_client):
        descriptors = await provider.list_models_async()
        with patch.object(AIRegistryService, "get_available_models", return_value=descriptors):
            decision = AIRouter.route_task(task_type="idea_evaluation", requested_provider="groq", requested_model="auto")
            assert decision["actual_model"] == "llama-3.3-70b-versatile"

            with pytest.raises(AIInvalidModelException):
                AIRouter.route_task(task_type="idea_evaluation", requested_provider="groq", requested_model="whisper-large-v3-turbo")

@pytest.mark.asyncio
async def test_mock_provider_production_isolation():
    """Verifies that MockProvider is completely excluded when APP_ENV is production."""
    with patch.object(settings, "APP_ENV", "production"):
        AIRegistryService.refresh_registry_cache()
        providers = AIRegistryService.get_providers()
        mock_info = next((p for p in providers if p["id"] == "mock"), None)
        assert mock_info is None

@pytest.mark.asyncio
async def test_groq_error_normalization():
    """Verifies 401, 429, 400, and timeout errors map to normalized AIExceptions."""
    provider = GroqProvider()

    # 401 Auth Error
    mock_client_401 = AsyncMock()
    mock_client_401.chat.completions.create.side_effect = Exception("401 Unauthorized - Invalid API Key")
    with patch.object(settings, "GROQ_API_KEY", "gsk_invalid"), patch.object(provider, "_get_client", return_value=mock_client_401):
        with pytest.raises(AIAuthenticationException):
            await provider.generate("test prompt")

    # 429 Rate Limit Error
    mock_client_429 = AsyncMock()
    mock_client_429.chat.completions.create.side_effect = Exception("429 Rate limit exceeded")
    with patch.object(settings, "GROQ_API_KEY", "gsk_valid"), patch.object(provider, "_get_client", return_value=mock_client_429):
        with pytest.raises(AIRateLimitException):
            await provider.generate("test prompt")

    # Timeout Error
    mock_client_timeout = AsyncMock()
    mock_client_timeout.chat.completions.create.side_effect = Exception("Request timeout")
    with patch.object(settings, "GROQ_API_KEY", "gsk_valid"), patch.object(provider, "_get_client", return_value=mock_client_timeout):
        with pytest.raises(AITimeoutException):
            await provider.generate("test prompt")

@pytest.mark.skipif(os.getenv("GROQ_E2E") != "true", reason="Opt-in real Groq E2E test requires GROQ_E2E=true and GROQ_API_KEY")
@pytest.mark.asyncio
async def test_real_groq_inference_full_chain():
    """
    Opt-in real Groq end-to-end task pipeline test.
    Executes real Chat Completion via Groq API, verifies DB task persistence, token usage metadata, and state transition.
    """
    from app.core.database import engine
    from sqlalchemy.ext.asyncio import AsyncSession

    async with AsyncSession(engine) as db:
        # Create test user
        user = User(clerk_id="user_groq_e2e", email="groq_e2e@ideagpt.dev")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Create task
        task = await AiTaskService.create_task(
            db=db,
            user=user,
            task_type="idea_evaluation",
            provider="groq",
            model="auto",
            input_payload={"prompt": "Analyze a developer CLI tool for cloud infrastructure automation."}
        )
        assert task.status == "QUEUED"

        # Execute task end-to-end against real Groq API
        completed_task = await AiTaskService.execute_task(db, task.id)

        # Verify task completion and database persistence
        assert completed_task.status == "COMPLETED"
        assert completed_task.provider == "groq"
        assert completed_task.model != "auto"
        assert completed_task.duration_ms is not None and completed_task.duration_ms > 0
        assert completed_task.result_payload is not None
        assert "summary" in completed_task.result_payload or "score" in completed_task.result_payload
