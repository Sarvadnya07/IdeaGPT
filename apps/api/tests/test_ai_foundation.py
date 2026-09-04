import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.ai.orchestrator.registry import registry
from app.ai.orchestrator.factory import ProviderFactory
from app.ai.providers.base import AIProvider
from app.ai.orchestrator.router import AIRouter
from app.ai.orchestrator.orchestrator import orchestrator
from app.core.config import settings

@pytest.mark.anyio
async def test_registry_has_providers():
    # Assert all providers are registered successfully
    openai_cls = registry.get_class("openai")
    gemini_cls = registry.get_class("gemini")
    ollama_cls = registry.get_class("ollama")
    custom_cls = registry.get_class("custom")
    mock_cls = registry.get_class("mock")
    
    assert openai_cls is not None
    assert gemini_cls is not None
    assert ollama_cls is not None
    assert custom_cls is not None
    assert mock_cls is not None

@pytest.mark.anyio
async def test_factory_creates_instances():
    mock_prov = ProviderFactory.create_provider("mock")
    assert isinstance(mock_prov, AIProvider)
    assert mock_prov.provider_id == "mock"
    assert mock_prov.__class__.__name__ in ("GatewayAIProviderAdapter", "MockProvider")

@pytest.mark.anyio
async def test_router_fallbacks_to_mock_by_default():
    # Store settings to restore later
    old_openai = settings.ENABLE_OPENAI
    old_gemini = settings.ENABLE_GEMINI
    old_ollama = settings.ENABLE_OLLAMA
    old_groq = settings.GROQ_API_KEY

    settings.ENABLE_OPENAI = False
    settings.ENABLE_GEMINI = False
    settings.ENABLE_OLLAMA = False
    settings.GROQ_API_KEY = None
    settings.ENABLE_GROQ = False

    routed = AIRouter.route()
    assert routed == "mock"

    settings.ENABLE_OPENAI = old_openai
    settings.ENABLE_GEMINI = old_gemini
    settings.ENABLE_OLLAMA = old_ollama
    settings.GROQ_API_KEY = old_groq
    settings.ENABLE_GROQ = None
    settings.ENABLE_OLLAMA = old_ollama

@pytest.mark.anyio
async def test_mock_provider_output():
    mock_prov = ProviderFactory.create_provider("mock")
    res = await mock_prov.generate("test prompt")
    assert "score" in res
    assert "strengths" in res
    assert "weaknesses" in res
    assert "architecture_breakdown" in res

@pytest.mark.anyio
async def test_orchestrator_integration():
    res = await orchestrator.analyze_startup_idea("test pitch", strategy="user_selected", preferred_provider="mock")
    assert res["score"] == 85

from tests.test_auth import _make_token

def _make_auth_header(sub: str = "test_user_ai") -> dict:
    return {"Authorization": f"Bearer {_make_token(sub=sub)}"}

@pytest.mark.anyio
async def test_health_endpoints():
    auth_header = _make_auth_header()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        res_ai = await ac.get("/health/ai", headers=auth_header)
        assert res_ai.status_code == 200
        assert "default_provider" in res_ai.json()
        assert "enabled_providers" in res_ai.json()

        res_prov = await ac.get("/health/providers", headers=auth_header)
        assert res_prov.status_code == 200
        assert "mock" in res_prov.json()
        assert res_prov.json()["mock"] == "healthy"
