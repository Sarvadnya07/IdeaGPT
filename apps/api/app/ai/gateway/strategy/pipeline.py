"""
IdeaGPT Phase C — Strategy & Decision Pipeline.
Unified entry point orchestrating deep strategic reasoning, assumption extraction,
scenario variations, sensitivity curves, and multi-idea comparative decisions.
"""

import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gateway.strategy.models import (
    DeepStrategyAnalysis,
    ScenarioResult,
    SensitivityMetric,
    MultiIdeaComparisonResult,
    AssumptionItem,
)
from app.ai.gateway.strategy.reasoning import StrategyReasoningEngine
from app.ai.gateway.strategy.scenario import ScenarioEngine, SensitivityEngine
from app.ai.gateway.strategy.comparative import ComparativeStrategyEngine
from app.ai.gateway.strategy.linkage import StrategyLinkageService

logger = logging.getLogger(__name__)


class StrategicDecisionPipeline:
    @classmethod
    async def analyze_strategy(
        cls,
        idea_title: str,
        industry: str,
        problem_statement: str,
        solution_description: str,
        market_data: Optional[Dict[str, Any]] = None,
        competitor_data: Optional[Dict[str, Any]] = None,
        risk_data: Optional[Dict[str, Any]] = None,
        evaluation_data: Optional[Dict[str, Any]] = None,
        user_constraints: Optional[Dict[str, Any]] = None,
        provider: str = "auto",
        model: str = "auto",
        byok_key: Optional[str] = None,
    ) -> DeepStrategyAnalysis:
        return await StrategyReasoningEngine.analyze_idea_strategy(
            idea_title=idea_title,
            industry=industry,
            problem_statement=problem_statement,
            solution_description=solution_description,
            market_data=market_data,
            competitor_data=competitor_data,
            risk_data=risk_data,
            evaluation_data=evaluation_data,
            user_constraints=user_constraints,
            provider=provider,
            model=model,
            byok_key=byok_key,
        )

    @classmethod
    def generate_scenarios(
        cls,
        budget_usd: float = 50000.0,
        timeline_months: float = 3.0,
        monthly_burn_rate_usd: float = 6000.0,
    ) -> List[ScenarioResult]:
        return ScenarioEngine.generate_scenarios(
            base_budget=budget_usd,
            base_timeline_months=timeline_months,
            monthly_burn=monthly_burn_rate_usd,
        )

    @classmethod
    def analyze_sensitivities(
        cls,
        budget_usd: float = 50000.0,
        timeline_months: float = 3.0,
        target_pricing_usd: float = 29.0,
    ) -> List[SensitivityMetric]:
        return SensitivityEngine.analyze_sensitivities(
            base_budget=budget_usd,
            base_timeline=timeline_months,
            base_pricing=target_pricing_usd,
        )

    @classmethod
    def compare_ideas(
        cls,
        ideas_data: List[Dict[str, Any]]
    ) -> MultiIdeaComparisonResult:
        return ComparativeStrategyEngine.compare_multiple_ideas(ideas_data)

    @classmethod
    async def link_action_to_roadmap(
        cls,
        db: AsyncSession,
        project_id: str,
        user_id: int,
        action_title: str,
        rationale: str,
        target_metric: str,
        success_threshold: str,
        milestone_title: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await StrategyLinkageService.add_strategy_experiment_to_roadmap(
            db=db,
            project_id=project_id,
            user_id=user_id,
            action_title=action_title,
            rationale=rationale,
            target_metric=target_metric,
            success_threshold=success_threshold,
            milestone_title=milestone_title,
        )
