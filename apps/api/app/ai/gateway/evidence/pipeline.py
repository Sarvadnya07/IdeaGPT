"""
IdeaGPT AI Gateway — Evidence-Aware Research Pipeline.
Orchestrates web research, source normalization, evidence classification, and grounded domain analysis.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.ai.gateway.models import (
    AIRequest,
    AIResult,
    Citation,
    EvidenceItem,
    ResearchRequest,
    ResearchResult,
)
from app.ai.gateway.contracts import AICapability, EvidenceType
from app.ai.gateway.registry import gateway_registry
from app.ai.gateway.evidence.models import (
    NormalizedSource,
    NormalizedEvidence,
    ResearchQueryPlan,
    GroundedMarketAnalysis,
    GroundedCompetitorAnalysis,
    GroundedRiskAnalysis,
)
from app.ai.gateway.evidence.planner import ResearchPlanner
from app.ai.gateway.evidence.normalizer import SourceNormalizer
from app.ai.gateway.evidence.taxonomy import EvidenceValidator
from app.ai.gateway.evidence.cache import ResearchCacheService
from app.ai.gateway.evidence.grounded_analyzers import (
    GroundedResearchService,
    GroundedMarketAnalyzer,
    GroundedCompetitorAnalyzer,
    GroundedRiskAnalyzer,
)

logger = logging.getLogger(__name__)


class EvidenceAwareResearchPipeline:
    @classmethod
    async def run_market_research(
        cls,
        query: str,
        user_id: Optional[int] = None,
        byok_tavily_key: Optional[str] = None
    ) -> ResearchResult:
        """
        Executes web search via Tavily and normalizes results into verified evidence sources.
        """
        tavily_adapter = gateway_registry.get_adapter("tavily")
        if not tavily_adapter:
            return ResearchResult(query=query, sources=[], evidence_items=[])

        req = ResearchRequest(query=query, max_results=5, user_id=user_id)
        try:
            return await tavily_adapter.search(req, byok_key=byok_tavily_key)
        except Exception as exc:
            logger.warning(f"Web research execution skipped or failed: {exc}")
            return ResearchResult(query=query, sources=[], evidence_items=[])

    @classmethod
    async def generate_grounded_market_analysis(
        cls,
        idea_title: str,
        industry: str,
        problem_statement: str,
        target_audience: Optional[str] = None,
        provider: str = "auto",
        model: str = "auto",
        byok_key: Optional[str] = None,
        byok_tavily_key: Optional[str] = None,
    ) -> GroundedMarketAnalysis:
        return await GroundedMarketAnalyzer.analyze(
            idea_title=idea_title,
            industry=industry,
            problem_statement=problem_statement,
            target_audience=target_audience,
            provider=provider,
            model=model,
            byok_key=byok_key,
            byok_tavily_key=byok_tavily_key
        )

    @classmethod
    async def generate_grounded_competitor_analysis(
        cls,
        idea_title: str,
        industry: str,
        solution_description: str,
        provider: str = "auto",
        model: str = "auto",
        byok_key: Optional[str] = None,
        byok_tavily_key: Optional[str] = None,
    ) -> GroundedCompetitorAnalysis:
        return await GroundedCompetitorAnalyzer.analyze(
            idea_title=idea_title,
            industry=industry,
            solution_description=solution_description,
            provider=provider,
            model=model,
            byok_key=byok_key,
            byok_tavily_key=byok_tavily_key
        )

    @classmethod
    async def generate_grounded_risk_analysis(
        cls,
        idea_title: str,
        industry: str,
        tech_depth: Optional[str] = "High",
        provider: str = "auto",
        model: str = "auto",
        byok_key: Optional[str] = None,
        byok_tavily_key: Optional[str] = None,
    ) -> GroundedRiskAnalysis:
        return await GroundedRiskAnalyzer.analyze(
            idea_title=idea_title,
            industry=industry,
            tech_depth=tech_depth,
            provider=provider,
            model=model,
            byok_key=byok_key,
            byok_tavily_key=byok_tavily_key
        )

    @staticmethod
    def format_evidence_prompt_context(research: ResearchResult) -> str:
        """
        Formats retrieved web sources into sanitized reference context for the reasoning LLM.
        """
        if not research.sources:
            return "No external web sources retrieved. Use internal domain knowledge and mark unverifiable claims as ESTIMATE or UNKNOWN."

        lines = ["EXTERNAL VERIFIED SOURCES (Use for factual grounding only):"]
        for idx, src in enumerate(research.sources, 1):
            lines.append(f"[{idx}] Title: {src.title}")
            lines.append(f"    URL: {src.url}")
            lines.append(f"    Content Summary: {src.snippet}")

        lines.append("\nINSTRUCTION: Ground market sizes, competitor names, and trends in these sources.")
        lines.append("Return each external claim with evidence_type: 'FACT' and the corresponding source_url.")
        lines.append("If a claim is an assumption or model calculation, mark it as 'ESTIMATE' or 'INFERENCE'.")
        return "\n".join(lines)

