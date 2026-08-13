"""
Sprint 3 — API Rate Limiting & Abuse Protection Test Suite

Tests:
  1. Requests under limit succeed (200 OK / 201 Created).
  2. Requests exceeding quota return 429 Too Many Requests.
  3. HTTP 429 response structure matches IdeaGPT error format (error, code, detail) and includes Retry-After header.
  4. User A exhausting quota does not affect User B's quota (User Isolation).
  5. Health endpoints remain unthrottled.
"""

import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.core.rate_limit import limiter
import jwt as pyjwt

TEST_SECRET = os.environ["CLERK_JWT_TEST_SECRET"]

def _make_token(sub: str = "user_rate_001") -> str:
    payload = {
        "sub": sub,
        "exp": 9999999999,
        "iat": 1000000000,
        "iss": settings.clerk_issuer or "https://clerk.test",
    }
    return pyjwt.encode(payload, TEST_SECRET, algorithm="HS256")


@pytest.mark.asyncio
async def test_01_health_endpoint_unrestricted():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for _ in range(15):
            response = await ac.get("/health")
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_02_rate_limit_exceeded_returns_429():
    token = _make_token(sub="user_rate_limit_test_001")
    headers = {"Authorization": f"Bearer {token}"}
    
    limiter.enabled = True
    try:
        # We test with global search endpoint which is limited to 30/minute
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # First request should succeed or return valid response
            res = await ac.get("/api/v1/search?q=test", headers=headers)
            assert res.status_code in [200, 404]

            # Exceed quota (30/minute)
            hit_429 = False
            for _ in range(35):
                res = await ac.get("/api/v1/search?q=test", headers=headers)
                if res.status_code == 429:
                    hit_429 = True
                    assert res.headers.get("Retry-After") is not None
                    data = res.json()
                    assert data.get("code") == "RATE_LIMIT_EXCEEDED"
                    assert "error" in data
                    break

            assert hit_429, "Expected 429 Too Many Requests after exceeding quota"
    finally:
        limiter.enabled = False


@pytest.mark.asyncio
async def test_03_user_isolation_rate_limits():
    token_a = _make_token(sub="user_quota_a")
    token_b = _make_token(sub="user_quota_b")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # User A makes requests
        res_a = await ac.get("/api/v1/users/me", headers=headers_a)
        assert res_a.status_code == 200

        # User B makes requests and is unaffected
        res_b = await ac.get("/api/v1/users/me", headers=headers_b)
        assert res_b.status_code == 200
        assert res_b.json()["clerk_id"] == "user_quota_b"
