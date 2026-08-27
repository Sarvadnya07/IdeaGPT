"""
Tavily Web Research Provider Adapter for IdeaGPT AI Gateway v1.
Implements web search, source extraction, and normalized evidence collection.
Treated strictly as a ResearchProvider (not text generation).
"""

import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import httpx

from app.core.config import settings
from app.ai.gateway.providers.base_adapter import BaseProviderAdapter
from app.ai.gateway.models import (
    AIRequest,
    AIResult,
    Citation,
    EvidenceItem,
    ResearchRequest,
    ResearchResult,
    ModelDescriptor,
    ProviderDescriptor,
)
from app.ai.gateway.contracts import (
    AICapability,
    CapabilityConfidence,
    ModelCategory,
    ModelStatus,
    ProviderState,
    EvidenceType,
)
from app.ai.exceptions.ai_exceptions import (
    AIException,
    AIAuthenticationException,
    AIRateLimitException,
    AITimeoutException,
    AINetworkException,
)

logger = logging.getLogger(__name__)


class TavilyResearchProviderAdapter(BaseProviderAdapter):
    def __init__(self):
        super().__init__(provider_id="tavily", display_name="Tavily Research AI")
        self.capabilities = [AICapability.WEB_RESEARCH]

    @property
    def is_configured(self) -> bool:
        return bool(getattr(settings, "TAVILY_API_KEY", None))

    @property
    def is_enabled(self) -> bool:
        return bool(getattr(settings, "ENABLE_TAVILY", True))

    def get_provider_state(self, user_byok: bool = False) -> ProviderState:
        if user_byok:
            return ProviderState.BYOK_CONNECTED
        if self.is_configured:
            return ProviderState.AVAILABLE
        return ProviderState.NOT_CONFIGURED

    async def health(self, byok_key: Optional[str] = None) -> ProviderDescriptor:
        key = byok_key or getattr(settings, "TAVILY_API_KEY", None)
        if not key:
            return ProviderDescriptor(
                id=self.provider_id,
                name=self.display_name,
                capabilities=self.capabilities,
                state=ProviderState.NOT_CONFIGURED,
                configured=False,
                enabled=self.is_enabled,
                latency_ms=0,
                models_count=0,
            )

        start = time.time()
        try:
            # Test simple ping/search
            url = "https://api.tavily.com/search"
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(
                    url,
                    json={"api_key": key, "query": "startup market trends", "max_results": 1}
                )
                latency = int((time.time() - start) * 1000)
                if res.status_code == 200:
                    return ProviderDescriptor(
                        id=self.provider_id,
                        name=self.display_name,
                        capabilities=self.capabilities,
                        state=ProviderState.BYOK_CONNECTED if byok_key else ProviderState.AVAILABLE,
                        configured=True,
                        enabled=self.is_enabled,
                        latency_ms=latency,
                        models_count=1,
                    )
                return ProviderDescriptor(
                    id=self.provider_id,
                    name=self.display_name,
                    capabilities=self.capabilities,
                    state=ProviderState.UNAVAILABLE,
                    configured=True,
                    enabled=self.is_enabled,
                    latency_ms=latency,
                    models_count=0,
                    error=f"Tavily returned status {res.status_code}",
                )
        except Exception as exc:
            latency = int((time.time() - start) * 1000)
            return ProviderDescriptor(
                id=self.provider_id,
                name=self.display_name,
                capabilities=self.capabilities,
                state=ProviderState.UNAVAILABLE,
                configured=True,
                enabled=self.is_enabled,
                latency_ms=latency,
                models_count=0,
                error=str(exc),
            )

    async def list_models(self, byok_key: Optional[str] = None) -> List[ModelDescriptor]:
        key = byok_key or getattr(settings, "TAVILY_API_KEY", None)
        return [
            ModelDescriptor(
                provider=self.provider_id,
                model_id="tavily-search-v1",
                display_name="Tavily Deep Web Search",
                category=ModelCategory.RESEARCH,
                capabilities=[AICapability.WEB_RESEARCH],
                capability_confidence=CapabilityConfidence.VERIFIED,
                input_modalities=["text"],
                output_modalities=["text"],
                context_window=16384,
                supports_structured_output=True,
                status=ModelStatus.ACTIVE,
                configured=bool(key),
                available=bool(key),
                last_seen=datetime.now(timezone.utc),
            )
        ]

    async def search(self, request: ResearchRequest, byok_key: Optional[str] = None) -> ResearchResult:
        key = byok_key or getattr(settings, "TAVILY_API_KEY", None)
        if not key:
            raise AIAuthenticationException("Tavily API key is not configured.")

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": key,
            "query": request.query,
            "search_depth": request.search_depth,
            "max_results": request.max_results,
            "include_answer": True,
        }
        if request.include_domains:
            payload["include_domains"] = request.include_domains
        if request.exclude_domains:
            payload["exclude_domains"] = request.exclude_domains

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                duration_ms = int((time.time() - start_time) * 1000)

                if res.status_code == 401 or res.status_code == 403:
                    raise AIAuthenticationException("Invalid Tavily API key.")
                elif res.status_code == 429:
                    raise AIRateLimitException("Tavily search rate limit exceeded.")
                elif res.status_code != 200:
                    raise AINetworkException(f"Tavily search error ({res.status_code}): {res.text}")

                data = res.json()
                raw_results = data.get("results", [])

                citations: List[Citation] = []
                evidence_items: List[EvidenceItem] = []

                for r in raw_results:
                    title = r.get("title", "Web Source")
                    url_str = r.get("url", "")
                    content = r.get("content", "")
                    pub_date = r.get("published_date")

                    citations.append(
                        Citation(
                            title=title,
                            url=url_str,
                            snippet=content[:300] if content else "",
                            source="Tavily Web Search",
                            published_date=pub_date,
                        )
                    )

                    evidence_items.append(
                        EvidenceItem(
                            evidence_type=EvidenceType.FACT,
                            claim=content[:200] if content else title,
                            source_title=title,
                            source_url=url_str,
                            confidence=float(r.get("score", 0.9)),
                            retrieved_at=datetime.now(timezone.utc),
                        )
                    )

                return ResearchResult(
                    query=request.query,
                    sources=citations,
                    evidence_items=evidence_items,
                    duration_ms=duration_ms,
                    provider=self.provider_id,
                )
        except httpx.TimeoutException:
            raise AITimeoutException("Tavily web search timed out.")
        except (AIAuthenticationException, AIRateLimitException, AITimeoutException, AINetworkException):
            raise
        except Exception as exc:
            logger.error(f"Tavily research error: {exc}", exc_info=True)
            raise AINetworkException(f"Failed to execute web research: {str(exc)}")

    async def execute(self, request: AIRequest) -> AIResult:
        # If routed as an execute call, run search on prompt query
        res = await self.search(
            ResearchRequest(query=request.prompt, user_id=request.user_id),
            byok_key=request.byok_api_key
        )
        return AIResult(
            text=f"Retrieved {len(res.sources)} research sources for '{request.prompt}'",
            structured_data={"sources": [s.model_dump() for s in res.sources]},
            evidence_items=res.evidence_items,
            citations=res.sources,
            provider=self.provider_id,
            model="tavily-search-v1",
            duration_ms=res.duration_ms,
        )
