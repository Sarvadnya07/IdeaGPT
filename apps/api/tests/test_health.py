import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"service": "IdeaGPT API", "status": "healthy"}

@pytest.mark.asyncio
async def test_health_config():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health/config")
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
