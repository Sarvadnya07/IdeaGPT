import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import Settings

@pytest.mark.asyncio
async def test_health_liveness_and_readiness():
    """Verify separate liveness and readiness endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Liveness check (process alive)
        res_live = await client.get("/health/live")
        assert res_live.status_code == 200
        assert res_live.json()["status"] == "live"

        # Readiness check (DB connected)
        res_ready = await client.get("/health/ready")
        assert res_ready.status_code == 200
        assert res_ready.json()["status"] == "ready"

@pytest.mark.asyncio
async def test_request_correlation_id_propagation():
    """Verify x-request-id header correlation ID is attached to HTTP responses."""
    custom_req_id = "test-correlation-id-999"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health/live", headers={"x-request-id": custom_req_id})
        assert res.status_code == 200
        assert res.headers.get("x-request-id") == custom_req_id

@pytest.mark.asyncio
async def test_operational_metrics_endpoint():
    """Verify /metrics operational endpoint returns system metrics."""
    from tests.test_auth import _make_token
    auth_header = {"Authorization": f"Bearer {_make_token(sub='test_ops_metrics_user')}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/metrics", headers=auth_header)
        assert res.status_code == 200
        data = res.json()
        assert "service" in data
        assert "ai_task_metrics" in data
        assert "total_tasks" in data["ai_task_metrics"]

def test_production_config_validation_rules():
    """Verify production configuration validation raises RuntimeError for insecure settings."""
    # Test missing clerk issuer in production
    s1 = Settings(_env_file=None, APP_ENV="production", CLERK_PUBLISHABLE_KEY="", CLERK_JWT_ISSUER="")
    with pytest.raises(RuntimeError, match="CLERK_PUBLISHABLE_KEY"):
        s1.validate_production_config()

    # Test test secret set in production
    s2 = Settings(
        _env_file=None,
        APP_ENV="production",
        CLERK_JWT_ISSUER="https://healthy-sunbeam-68.clerk.accounts.dev",
        CLERK_JWT_TEST_SECRET="should-not-exist"
    )
    with pytest.raises(RuntimeError, match="CLERK_JWT_TEST_SECRET"):
        s2.validate_production_config()

    # Test wildcard CORS in production
    s3 = Settings(
        _env_file=None,
        APP_ENV="production",
        CLERK_JWT_ISSUER="https://healthy-sunbeam-68.clerk.accounts.dev",
        CLERK_JWT_TEST_SECRET="",
        CORS_ORIGINS="*"
    )
    with pytest.raises(RuntimeError, match="wildcard"):
        s3.validate_production_config()
