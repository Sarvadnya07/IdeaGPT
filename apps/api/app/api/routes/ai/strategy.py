"""
AI Strategy Sub-Router: Strategic reasoning, decision modeling, what-if scenarios, unit economics, and red flags.
"""

from typing import Optional, Any, Dict, List
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


class StrategyAnalyzeRequest(BaseModel):
    title: str = Field(default="Startup Venture", max_length=100)
    industry: str = Field(default="Technology", max_length=50)
    problem_statement: str = Field(default="", max_length=2000)
    solution_description: str = Field(default="", max_length=2000)
    market_data: Optional[Dict[str, Any]] = None
    competitor_data: Optional[Dict[str, Any]] = None
    risk_data: Optional[Dict[str, Any]] = None
    evaluation_data: Optional[Dict[str, Any]] = None
    user_constraints: Optional[Dict[str, Any]] = None
    provider: Optional[str] = Field(default="auto", max_length=50)
    model: Optional[str] = Field(default="auto", max_length=100)


class StrategyScenarioRequest(BaseModel):
    budget_usd: float = Field(default=50000.0, ge=0.0)
    timeline_months: int = Field(default=12, ge=1, le=60)
    monthly_burn_rate_usd: float = Field(default=4000.0, ge=0.0)


class StrategySensitivityRequest(BaseModel):
    budget_usd: float = Field(default=50000.0, ge=0.0)
    timeline_months: int = Field(default=12, ge=1, le=60)
    target_pricing_usd: float = Field(default=49.0, ge=1.0)


class StrategyCompareRequest(BaseModel):
    ideas: List[Dict[str, Any]] = Field(..., min_length=2, max_length=5)


class StrategyLinkRoadmapRequest(BaseModel):
    project_id: str
    action_title: str
    rationale: str
    target_metric: str
    success_threshold: str
    milestone_title: Optional[str] = None


class RedFlagsRequest(BaseModel):
    title: str = Field(default="Startup Idea", max_length=100)
    industry: str = Field(default="Technology", max_length=50)
    problem: str = Field(default="", max_length=2000)
    solution: str = Field(default="", max_length=2000)
    score: float = Field(default=75.0, ge=0.0, le=100.0)


@router.post("/strategy/analyze", summary="Execute deep strategic reasoning with calibrated decision gates and trade-offs")
async def analyze_strategy(
    payload: StrategyAnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.pipeline import StrategicDecisionPipeline
    return await StrategicDecisionPipeline.analyze_strategy(
        idea_title=payload.title,
        industry=payload.industry,
        problem_statement=payload.problem_statement,
        solution_description=payload.solution_description,
        market_data=payload.market_data,
        competitor_data=payload.competitor_data,
        risk_data=payload.risk_data,
        evaluation_data=payload.evaluation_data,
        user_constraints=payload.user_constraints,
        provider=payload.provider or "auto",
        model=payload.model or "auto"
    )


@router.post("/strategy/assumptions", summary="Extract and prioritize underlying startup assumptions")
async def analyze_assumptions(
    payload: StrategyAnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.pipeline import StrategicDecisionPipeline
    res = await StrategicDecisionPipeline.analyze_strategy(
        idea_title=payload.title,
        industry=payload.industry,
        problem_statement=payload.problem_statement,
        solution_description=payload.solution_description,
        provider=payload.provider or "auto",
        model=payload.model or "auto"
    )
    return res.key_assumptions


@router.post("/strategy/scenario", summary="Generate controlled financial and operational what-if scenarios")
async def generate_scenarios(
    payload: StrategyScenarioRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.pipeline import StrategicDecisionPipeline
    return StrategicDecisionPipeline.generate_scenarios(
        budget_usd=payload.budget_usd,
        timeline_months=payload.timeline_months,
        monthly_burn_rate_usd=payload.monthly_burn_rate_usd
    )


@router.post("/strategy/sensitivity", summary="Perform single-variable sensitivity analysis")
async def analyze_sensitivity(
    payload: StrategySensitivityRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.pipeline import StrategicDecisionPipeline
    return StrategicDecisionPipeline.analyze_sensitivities(
        budget_usd=payload.budget_usd,
        timeline_months=payload.timeline_months,
        target_pricing_usd=payload.target_pricing_usd
    )


@router.post("/strategy/compare", summary="Perform multi-idea comparative decision modeling")
async def compare_strategy_ideas(
    payload: StrategyCompareRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.pipeline import StrategicDecisionPipeline
    return StrategicDecisionPipeline.compare_ideas(payload.ideas)


@router.post("/strategy/link-to-roadmap", summary="Convert strategic validation experiment to persisted roadmap task")
async def link_strategy_action_to_roadmap(
    payload: StrategyLinkRoadmapRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.ai.gateway.strategy.pipeline import StrategicDecisionPipeline
    return await StrategicDecisionPipeline.link_action_to_roadmap(
        db=db,
        project_id=payload.project_id,
        user_id=current_user.id,
        action_title=payload.action_title,
        rationale=payload.rationale,
        target_metric=payload.target_metric,
        success_threshold=payload.success_threshold,
        milestone_title=payload.milestone_title
    )


@router.post("/decision/red-flags", summary="Scan venture for investor red flags across regulatory, capital, and market")
async def scan_red_flags(
    payload: RedFlagsRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.decision_engines import RedFlagScannerEngine
    return RedFlagScannerEngine.scan(
        title=payload.title,
        industry=payload.industry,
        problem=payload.problem,
        solution=payload.solution,
        eval_score=payload.score
    )


@router.post("/decision/unit-economics", summary="Calculate deterministic SaaS unit economics, CAC payback, LTV, and runway")
async def calculate_unit_economics(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.unit_economics import UnitEconomicsEngine, UnitEconomicsInput
    inp = UnitEconomicsInput(**payload)
    return UnitEconomicsEngine.calculate(inp)


@router.post("/decision/regulatory-radar", summary="Classify statutory compliance and regulatory frameworks")
async def evaluate_regulatory_radar(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.decision_engines import RegulatoryRadarEngine
    return RegulatoryRadarEngine.evaluate(
        industry=payload.get("industry", "Technology"),
        solution_details=payload.get("solution", "")
    )


@router.post("/decision/moat-assessor", summary="Assess venture defensibility across 8 moat dimensions")
async def assess_moat(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.decision_engines import MoatAssessorEngine
    return MoatAssessorEngine.assess(
        idea_title=payload.get("title", "Startup Venture"),
        business_model=payload.get("business_model", "B2B SaaS")
    )


@router.post("/decision/resource-comparison", summary="Compare 2-5 ideas across engineering effort, team size, and capital")
async def compare_resources(
    payload: Dict[str, List[Dict[str, Any]]] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.decision_engines import ResourceComparisonEngine
    return ResourceComparisonEngine.compare_resources(payload.get("ideas", []))


@router.post("/decision/executive-summary", summary="Extract a concise 3-5 point evidence-grounded executive briefing")
async def generate_executive_summary(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.decision_engines import ExecutiveSummaryEngine
    return ExecutiveSummaryEngine.generate_summary(
        title=payload.get("title", "Startup Venture"),
        score=float(payload.get("score", 75.0)),
        strengths=payload.get("strengths", []),
        weaknesses=payload.get("weaknesses", []),
        gate=payload.get("decision_gate", "VALIDATE_FIRST")
    )


@router.post("/decision/tam-sam-som", summary="Retrieve structured TAM / SAM / SOM market sizing with citations")
async def get_tam_sam_som(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.decision_engines import TamSamSomEngine
    return TamSamSomEngine.get_market_sizing(
        title=payload.get("title", "Startup Venture"),
        industry=payload.get("industry", "Technology"),
        tam_estimate=payload.get("tam_estimate", "$4.2B"),
        growth_cagr=payload.get("growth_cagr", "14.5%")
    )


@router.post("/decision/pitch-variants", summary="Generate elevator pitch variants for founders, investors, and customers")
async def generate_pitch_variants(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.strategy.decision_engines import ElevatorPitchEngine
    return ElevatorPitchEngine.generate_pitches(
        title=payload.get("title", "Startup Venture"),
        problem=payload.get("problem", ""),
        solution=payload.get("solution", "")
    )
