"""
Security & Tenant Isolation Regression Tests for IdeaGPT AI Gateway v1.
"""

import pytest
import time
import jwt
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.ai.gateway.providers.mock_adapter import MockProviderAdapter
from app.ai.gateway.contracts import AICapability, ProviderState
from app.ai.gateway.router import CapabilityRouter
from app.ai.exceptions.ai_exceptions import AIInvalidModelException, AIUnavailableException
from app.services.credential_vault_service import mask_api_key, CredentialVaultService

TEST_SECRET = "test-secret-for-unit-tests-only-never-production"


def _make_token(sub: str = "test_sec_user_1", role: str = "user") -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": f"{sub}@example.com",
        "role": role,
        "iat": now,
        "exp": now + 3600,
        "iss": "https://healthy-sunbeam-68.clerk.accounts.dev"
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")


@pytest.mark.asyncio
async def test_byok_secret_never_returned_in_api():
    """Verify that stored BYOK API keys are encrypted and raw secrets are never returned."""
    token = _make_token(sub="test_byok_never_leak_user")
    headers = {"Authorization": f"Bearer {token}"}

    raw_secret_key = "gsk_super_secret_groq_api_key_123456789"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Save key
        save_res = await client.post(
            "/api/v1/ai/credentials",
            headers=headers,
            json={"provider": "groq", "api_key": raw_secret_key}
        )
        assert save_res.status_code == 200
        data = save_res.json()
        assert raw_secret_key not in str(data)
        assert data["key_hint"] == "gsk_...6789"
        assert "encrypted_secret" not in data

        # List keys
        list_res = await client.get("/api/v1/ai/credentials", headers=headers)
        assert list_res.status_code == 200
        list_data = list_res.json()
        assert raw_secret_key not in str(list_data)
        assert any(c["key_hint"] == "gsk_...6789" for c in list_data)


@pytest.mark.asyncio
async def test_byok_cross_tenant_isolation():
    """User B must not be able to list, verify, or delete User A's credentials."""
    token_a = _make_token(sub="user_a_creds")
    token_b = _make_token(sub="user_b_creds")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # User A saves key
        await client.post(
            "/api/v1/ai/credentials",
            headers=headers_a,
            json={"provider": "openai", "api_key": "sk-proj-user-a-secret-key-9999"}
        )

        # User B lists credentials -> User A's key must not appear
        res_b = await client.get("/api/v1/ai/credentials", headers=headers_b)
        assert res_b.status_code == 200
        b_creds = res_b.json()
        assert len(b_creds) == 0

        # User B attempts to delete User A's openai credential -> returns 404
        del_b = await client.delete("/api/v1/ai/credentials/openai", headers=headers_b)
        assert del_b.status_code == 404


@pytest.mark.asyncio
async def test_mock_provider_blocked_in_production():
    """Verify MockProvider is strictly disabled when APP_ENV is production."""
    mock = MockProviderAdapter()
    original_env = settings.APP_ENV

    try:
        settings.APP_ENV = "production"
        assert mock.is_enabled is False
        assert mock.get_provider_state() == ProviderState.DISABLED

        health = await mock.health()
        assert health.state == ProviderState.DISABLED
    finally:
        settings.APP_ENV = original_env


def test_speech_to_text_and_guard_models_rejected_from_text_tasks():
    """Verify Whisper or Guard models are rejected when routed for structured idea evaluation."""
    with pytest.raises(AIInvalidModelException) as exc1:
        CapabilityRouter.route_request(
            task_type="idea_evaluation",
            requested_provider="groq",
            requested_model="whisper-large-v3-turbo"
        )
    assert "structured text generation" in str(exc1.value)

    with pytest.raises(AIInvalidModelException) as exc2:
        CapabilityRouter.route_request(
            task_type="idea_evaluation",
            requested_provider="groq",
            requested_model="llama-guard-3-8b"
        )
    assert "moderation guard" in str(exc2.value)
