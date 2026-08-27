"""
IdeaGPT AI Gateway — Research Query Planner.
Generates focused, deterministic, bounded web search queries for startup validation tasks.
"""

from typing import List, Dict, Any, Optional
from app.ai.gateway.evidence.models import ResearchQueryPlan


class ResearchPlanner:
    """
    Generates bounded, highly relevant search queries tailored for specific startup research tasks.
    Enforces a strict upper bound of 4 queries to prevent search bloat and rate-limit exhaustion.
    """

    MAX_QUERIES = 4

    @classmethod
    def generate_plan(
        cls,
        task_type: str,
        idea_title: str,
        industry: str = "Technology",
        target_audience: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> ResearchQueryPlan:
        clean_title = (idea_title or "Startup Idea").strip()
        clean_industry = (industry or "Tech").strip()
        audience = (target_audience or "").strip()
        kw_str = " ".join(keywords[:3]) if keywords else ""

        queries: List[str] = []
        focus_areas: List[str] = []

        if task_type == "market_analysis":
            focus_areas = ["market size & growth", "target segment adoption", "industry trends"]
            queries.append(f"{clean_industry} market size TAM growth CAGR 2024 2025 2026")
            if audience:
                queries.append(f"{clean_industry} {audience} market demand and spending")
            else:
                queries.append(f"{clean_title} {clean_industry} market opportunity drivers")
            queries.append(f"{clean_industry} market trends challenges and forecasts")

        elif task_type == "competitor_analysis":
            focus_areas = ["direct competitors", "substitute platforms", "pricing & moats"]
            queries.append(f"{clean_title} top competitors alternatives market landscape")
            queries.append(f"{clean_industry} leading startups companies platforms")
            queries.append(f"{clean_industry} competitor pricing monetization business models")

        elif task_type == "risk_analysis":
            focus_areas = ["regulatory compliance", "technical vulnerabilities", "market adoption barriers"]
            queries.append(f"{clean_industry} regulatory requirements compliance liabilities")
            queries.append(f"{clean_title} {clean_industry} startup risks and technical challenges")
            queries.append(f"{clean_industry} security data privacy regulations")

        else:
            # General / Idea evaluation research plan
            focus_areas = ["market validation", "competitive landscape", "industry risks"]
            queries.append(f"{clean_title} {clean_industry} market size overview")
            queries.append(f"{clean_industry} competitors and market leaders")
            queries.append(f"{clean_industry} industry growth and technology risks")

        # Bounded query truncation
        bounded_queries = queries[:cls.MAX_QUERIES]

        return ResearchQueryPlan(
            task_type=task_type,
            idea_title=clean_title,
            industry=clean_industry,
            queries=bounded_queries,
            focus_areas=focus_areas,
        )
