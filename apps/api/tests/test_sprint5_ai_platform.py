import pytest
import jwt
import time
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

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
async def test_ai_providers_endpoint():
    """GET /api/v1/ai/providers returns registered providers and configuration state."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/ai/providers")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        provider_ids = [p["id"] for p in data]
        assert "openai" in provider_ids
        assert "gemini" in provider_ids
        assert "ollama" in provider_ids

@pytest.mark.asyncio
async def test_ai_models_endpoint():
    """GET /api/v1/ai/models returns available model metadata."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/ai/models")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "provider" in data[0]

@pytest.mark.asyncio
async def test_ai_task_lifecycle_and_ownership():
    """Verify AI task creation, status polling, and cross-user ownership isolation."""
    user_a_headers = _make_auth_header("user_ai_test_a")
    user_b_headers = _make_auth_header("user_ai_test_b")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Task for User A
        create_res = await client.post(
            "/api/v1/ai/tasks",
            json={
                "task_type": "idea_evaluation",
                "provider": "mock",
                "model": "mock-deterministic-v1",
                "input_payload": {"prompt": "Test AI Idea"},
                "idempotency_key": "task-test-key-001"
            },
            headers=user_a_headers
        )
        assert create_res.status_code == 202
        task_data = create_res.json()
        task_id = task_data["id"]
        assert task_data["status"] in ["QUEUED", "RUNNING", "COMPLETED"]

        # Poll Task as User A -> 200 OK
        poll_a = await client.get(f"/api/v1/ai/tasks/{task_id}", headers=user_a_headers)
        assert poll_a.status_code == 200
        assert poll_a.json()["id"] == task_id

        # Poll Task as User B -> 404 Not Found (Safeguard #5 User Ownership Isolation)
        poll_b = await client.get(f"/api/v1/ai/tasks/{task_id}", headers=user_b_headers)
        assert poll_b.status_code == 404

@pytest.mark.asyncio
async def test_ai_task_idempotency_deduplication():
    """Verify duplicate submission with same idempotency key returns same task record."""
    user_headers = _make_auth_header("user_idempotency_test")
    idempotency_key = "uniq-key-999"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res1 = await client.post(
            "/api/v1/ai/tasks",
            json={
                "provider": "mock",
                "idempotency_key": idempotency_key
            },
            headers=user_headers
        )
        assert res1.status_code == 202
        task_id_1 = res1.json()["id"]

        res2 = await client.post(
            "/api/v1/ai/tasks",
            json={
                "provider": "mock",
                "idempotency_key": idempotency_key
            },
            headers=user_headers
        )
        assert res2.status_code == 202
        task_id_2 = res2.json()["id"]

        assert task_id_1 == task_id_2
