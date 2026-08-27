"""
Provider Adapter Unit and Contract Tests for IdeaGPT AI Gateway v1.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.ai.gateway.models import (
    AIRequest,
    AIResult,
    ModelDescriptor,
    ResearchRequest,
)
from app.ai.gateway.contracts import AICapability, ModelCategory, ProviderState
from app.ai.gateway.providers.groq_adapter import GroqProviderAdapter, classify_groq_model_meta
from app.ai.gateway.providers.gemini_adapter import GeminiProviderAdapter
from app.ai.gateway.providers.ollama_adapter import OllamaProviderAdapter
from app.ai.gateway.providers.openai_adapter import OpenAIProviderAdapter
from app.ai.gateway.providers.tavily_adapter import TavilyResearchProviderAdapter
from app.ai.gateway.providers.mock_adapter import MockProviderAdapter


def test_groq_model_classification():
    """Verify conservative model classification for Groq models."""
    whisper_meta = classify_groq_model_meta("whisper-large-v3-turbo")
    assert whisper_meta["category"] == ModelCategory.SPEECH_TO_TEXT
    assert whisper_meta["structured_output"] is False

    guard_meta = classify_groq_model_meta("llama-guard-3-8b")
    assert guard_meta["category"] == ModelCategory.MODERATION
    assert AICapability.MODERATION in guard_meta["capabilities"]

    reasoning_meta = classify_groq_model_meta("deepseek-r1-distill-llama-70b")
    assert reasoning_meta["category"] == ModelCategory.REASONING
    assert AICapability.REASONING in reasoning_meta["capabilities"]

    chat_meta = classify_groq_model_meta("llama-3.3-70b-versatile")
    assert chat_meta["category"] == ModelCategory.CHAT
    assert AICapability.TEXT_GENERATION in chat_meta["capabilities"]


@pytest.mark.asyncio
async def test_groq_adapter_mocked_execution():
    """Verify Groq adapter execution and usage normalization."""
    adapter = GroqProviderAdapter()

    fake_choice = MagicMock()
    fake_choice.message.content = '{"score": 90, "strengths": ["Fast inference"]}'
    fake_choice.finish_reason = "stop"

    fake_response = MagicMock()
    fake_response.choices = [fake_choice]
    fake_response.usage.prompt_tokens = 42
    fake_response.usage.completion_tokens = 68

    with patch.object(adapter, "_get_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=fake_response)
        mock_client_factory.return_value = mock_client

        req = AIRequest(
            prompt="Analyze this idea",
            capability=AICapability.STRUCTURED_OUTPUT,
            byok_api_key="gsk_test_key"
        )
        result = await adapter.execute(req)

        assert isinstance(result, AIResult)
        assert result.provider == "groq"
        assert result.structured_data == {"score": 90, "strengths": ["Fast inference"]}
        assert result.usage.input_tokens == 42
        assert result.usage.output_tokens == 68
        assert result.usage.total_tokens == 110


@pytest.mark.asyncio
async def test_gemini_adapter_model_list_and_capabilities():
    """Verify Gemini adapter provides vision and document capabilities."""
    adapter = GeminiProviderAdapter()
    models = await adapter.list_models()

    assert len(models) >= 3
    flash = next(m for m in models if m.model_id == "gemini-2.0-flash")
    assert AICapability.VISION in flash.capabilities
    assert AICapability.DOCUMENT_UNDERSTANDING in flash.capabilities
    assert flash.supports_structured_output is True


@pytest.mark.asyncio
async def test_ollama_adapter_offline_graceful_handling():
    """Verify Ollama adapter does not crash when local daemon is unreachable."""
    adapter = OllamaProviderAdapter()
    health = await adapter.health()

    assert health.id == "ollama"
    # Even if offline, reports UNAVAILABLE instead of throwing an unhandled exception
    assert health.state in (ProviderState.UNAVAILABLE, ProviderState.AVAILABLE, ProviderState.DISABLED)


@pytest.mark.asyncio
async def test_tavily_adapter_research_normalization():
    """Verify Tavily web research adapter extracts citations and evidence items."""
    adapter = TavilyResearchProviderAdapter()

    fake_search_payload = {
        "results": [
            {
                "title": "Global AI Market Trends 2026",
                "url": "https://example.com/ai-trends",
                "content": "The global AI market is expanding at 38% CAGR.",
                "score": 0.95,
                "published_date": "2026-01-15",
            }
        ]
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = fake_search_payload
        mock_post.return_value = mock_resp

        req = ResearchRequest(query="AI market trends 2026")
        res = await adapter.search(req, byok_key="tvly-test-key")

        assert len(res.sources) == 1
        assert res.sources[0].title == "Global AI Market Trends 2026"
        assert res.sources[0].url == "https://example.com/ai-trends"
        assert len(res.evidence_items) == 1
        assert res.evidence_items[0].source_url == "https://example.com/ai-trends"


@pytest.mark.asyncio
async def test_mock_adapter_execution():
    """Verify MockProvider execution in test mode."""
    adapter = MockProviderAdapter()
    req = AIRequest(prompt="Evaluate idea", capability=AICapability.STRUCTURED_OUTPUT)
    res = await adapter.execute(req)

    assert res.provider == "mock"
    assert res.structured_data["score"] == 85
    assert "strengths" in res.structured_data
