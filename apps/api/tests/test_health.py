import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.test_auth import _make_token

def _make_auth_header(sub: str = "test_user_health") -> dict:
    return {"Authorization": f"Bearer {_make_token(sub=sub)}"}

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"service": "IdeaGPT API", "status": "healthy"}

@pytest.mark.asyncio
async def test_health_config():
    auth_header = _make_auth_header()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health/config", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "APP_ENV" in data
    assert "CLERK_PUBLISHABLE_KEY" in data
    assert "CLERK_JWT_ISSUER" in data
    assert "CORS_ORIGINS" in data
    # Ensure no secret values are returned
    for v in data.values():
        assert "sk_test" not in str(v)
        assert "pk_test" not in str(v)


@pytest.mark.asyncio
async def test_health_db_diagnostics():
    auth_header = _make_auth_header()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health/db-diagnostics", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "env" in data
    assert "connection_target" in data
    assert "dns" in data
    assert "tcp" in data
    assert "select_1" in data
    # Ensure no passwords or secrets are leaked
    data_str = str(data)
    assert "sk_test" not in data_str
    assert "password" not in data_str.lower() or "***" in data_str

