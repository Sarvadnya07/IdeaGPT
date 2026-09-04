import os
import time
import pytest
import jwt
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.ai.exceptions.ai_exceptions import AIQuotaExceededException, AIInvalidInputException
from app.services.ai_quota_service import AIQuotaService
from app.services.ai_task_service import AiTaskService
from app.ai.orchestrator.retry import AIRetryPolicy

TEST_SECRET = "test-secret-for-unit-tests-only-never-production"

def _make_auth_header(sub: str, email: str = None) -> dict:
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": email or f"{sub}@example.com",
        "iat": now,
        "exp": now + 3600,
        "iss": "https://healthy-sunbeam-68.clerk.accounts.dev"
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_oversized_prompt_rejection():
    """Server-side input validation rejects prompts exceeding 8,000 characters."""
    headers = _make_auth_header("user_prompt_overflow")
    huge_prompt = "A" * 8501

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/ai/tasks",
            json={
                "provider": "mock",
                "input_payload": {"prompt": huge_prompt}
            },
            headers=headers
        )
        assert res.status_code == 400
        assert "INVALID_REQUEST" in res.text or "exceeds" in res.text

@pytest.mark.asyncio
async def test_quota_exceeded_rejection():
    """Per-user daily quota limits prevent runaway AI submissions."""
    headers = _make_auth_header("user_quota_heavy")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Submit tasks up to daily quota limit
        for i in range(AIQuotaService.DAILY_TASK_QUOTA_PER_USER):
            res = await client.post(
                "/api/v1/ai/tasks",
                json={
                    "provider": "mock",
                    "idempotency_key": f"quota-key-{i}"
                },
                headers=headers
            )
            assert res.status_code == 202

        # 21st task should be rejected with HTTP 429 Quota Exceeded
        res_over = await client.post(
            "/api/v1/ai/tasks",
            json={
                "provider": "mock",
                "idempotency_key": "quota-key-overflow"
            },
            headers=headers
        )
        assert res_over.status_code == 429
        assert "QUOTA_EXCEEDED" in res_over.text or "quota" in res_over.text.lower()

@pytest.mark.asyncio
async def test_zero_ai_core_independence():
    """Deterministic evaluation works 100% independently when no AI providers are configured."""
    headers = _make_auth_header("user_zero_ai")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Project
        p_res = await client.post(
            "/api/v1/projects/",
            json={"title": "Zero AI Project", "slug": "zero-ai-proj"},
            headers=headers
        )
        assert p_res.status_code == 201
        p_id = p_res.json()["id"]

        # Create Idea
        i_res = await client.post(
            f"/api/v1/projects/{p_id}/ideas",
            json={
                "title": "Standalone Idea",
                "problem_statement": "Need math scoring without AI keys",
                "solution_description": "Use deterministic engine",
                "is_draft": False
            },
            headers=headers
        )
        assert i_res.status_code == 201
        i_id = i_res.json()["id"]

        # Trigger Deterministic Evaluation
        e_res = await client.post(
            f"/api/v1/ideas/{i_id}/evaluations",
            json={"evaluation_type": "full"},
            headers=headers
        )
        assert e_res.status_code == 201
        eval_data = e_res.json()
        assert eval_data["status"] == "COMPLETED"
        assert "score" in eval_data["result_payload"]

# Opt-in Real Provider Integration Tests
@pytest.mark.skipif(not os.getenv("OPENAI_E2E"), reason="Opt-in OpenAI E2E test disabled unless OPENAI_E2E=true")
@pytest.mark.asyncio
async def test_optin_real_openai_e2e():
    """Real OpenAI provider invocation test."""
    from app.ai.providers.openai import OpenAIProvider
    provider = OpenAIProvider()
    res = await provider.generate("Return valid json: {\"status\": \"ok\"}", response_format="json")
    assert isinstance(res, dict)

@pytest.mark.skipif(not os.getenv("GEMINI_E2E"), reason="Opt-in Gemini E2E test disabled unless GEMINI_E2E=true")
@pytest.mark.asyncio
async def test_optin_real_gemini_e2e():
    """Real Gemini provider invocation test."""
    from app.ai.providers.gemini import GeminiProvider
    provider = GeminiProvider()
    res = await provider.generate("Return valid json: {\"status\": \"ok\"}", response_format="json")
    assert isinstance(res, dict)

@pytest.mark.skipif(not os.getenv("OLLAMA_E2E"), reason="Opt-in Ollama E2E test disabled unless OLLAMA_E2E=true")
@pytest.mark.asyncio
async def test_optin_real_ollama_e2e():
    """Real Ollama local provider invocation test."""
    from app.ai.providers.ollama import OllamaProvider
    provider = OllamaProvider()
    res = await provider.generate("Return valid json: {\"status\": \"ok\"}", response_format="json")
    assert isinstance(res, dict)
