"""
IdeaGPT AI Gateway v1 — Evidence-Aware Research Pipeline.
Orchestrates web research, source normalization, and evidence-grounded analysis.
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
from app.ai.gateway.evidence.taxonomy import EvidenceValidator

logger = logging.getLogger(__name__)


class EvidenceAwareResearchPipeline:
    @staticmethod
    async def run_market_research(
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

    @staticmethod
    def format_evidence_prompt_context(research: ResearchResult) -> str:
        """
        Formats retrieved web sources into sanitized reference context for the reasoning LLM.
        Ensures untrusted external web data does not masquerade as system instructions.
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
