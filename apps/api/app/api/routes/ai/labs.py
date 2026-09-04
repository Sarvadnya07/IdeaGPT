"""
AI Labs and Evidence Sub-Router: Secondary labs and grounded market/competitor/risk research.
"""

from typing import Optional, Any, Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.ai_artifact_service import AIArtifactService

router = APIRouter()


class GitHubLabRequest(BaseModel):
    project_id: Optional[str] = None
    idea_id: Optional[str] = None
    title: str = Field(default="Startup Project", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    tech_stack: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)

class InvestorLabRequest(BaseModel):
    project_id: Optional[str] = None
    idea_id: Optional[str] = None
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    market_size: Optional[str] = Field(default=None, max_length=200)
    target_raise: Optional[str] = Field(default=None, max_length=100)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)

class MentorLabRequest(BaseModel):
    project_id: Optional[str] = None
    idea_id: Optional[str] = None
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    stage: Optional[str] = Field(default=None, max_length=100)
    challenges: Optional[str] = Field(default=None, max_length=1000)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)

class RecruiterLabRequest(BaseModel):
    project_id: Optional[str] = None
    idea_id: Optional[str] = None
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    current_team_size: Optional[str] = Field(default=None, max_length=100)
    target_roles: Optional[str] = Field(default=None, max_length=500)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)

class StrategyLabRequest(BaseModel):
    project_id: Optional[str] = None
    idea_id: Optional[str] = None
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    competitors: Optional[str] = Field(default=None, max_length=500)
    value_proposition: Optional[str] = Field(default=None, max_length=500)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)

class ResearchPlanRequest(BaseModel):
    task_type: str = Field(default="market_analysis", max_length=50)
    title: str = Field(default="Startup Idea", max_length=100)
    industry: str = Field(default="Technology", max_length=50)
    target_audience: Optional[str] = Field(default=None, max_length=200)

class GroundedMarketRequest(BaseModel):
    title: str = Field(default="Startup Idea", max_length=100)
    industry: str = Field(default="Technology", max_length=50)
    problem_statement: str = Field(default="", max_length=2000)
    target_audience: Optional[str] = Field(default=None, max_length=200)
    provider: Optional[str] = Field(default="auto", max_length=50)
    model: Optional[str] = Field(default="auto", max_length=100)

class GroundedCompetitorRequest(BaseModel):
    title: str = Field(default="Startup Idea", max_length=100)
    industry: str = Field(default="Technology", max_length=50)
    solution_description: str = Field(default="", max_length=2000)
    provider: Optional[str] = Field(default="auto", max_length=50)
    model: Optional[str] = Field(default="auto", max_length=100)

class GroundedRiskRequest(BaseModel):
    title: str = Field(default="Startup Idea", max_length=100)
    industry: str = Field(default="Technology", max_length=50)
    tech_depth: Optional[str] = Field(default="High", max_length=50)
    provider: Optional[str] = Field(default="auto", max_length=50)
    model: Optional[str] = Field(default="auto", max_length=100)


@router.post("/labs/github", summary="Generate GitHub codebase scaffolding, directory tree, and CI/CD workflow")
async def generate_github_lab(
    payload: GitHubLabRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    res = await AIOrchestrator.generate_github_lab_ai(
        title=payload.title,
        category=payload.category,
        tech_stack=payload.tech_stack,
        description=payload.description,
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )
    exec_type = res.get("_execution_type", "REAL_PROVIDER") if isinstance(res, dict) else "REAL_PROVIDER"
    fb_used = res.get("_fallback_used", False) if isinstance(res, dict) else False

    artifact = await AIArtifactService.save_artifact(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        idea_id=payload.idea_id,
        artifact_type="github_lab",
        title=f"GitHub Blueprint: {payload.title}",
        content_payload=res,
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile",
        execution_type=exec_type,
        fallback_used=fb_used
    )
    if isinstance(res, dict):
        res["artifact_id"] = artifact.id
        res["execution_type"] = exec_type
        res["fallback_used"] = fb_used
    return res


@router.post("/labs/investor", summary="Generate institutional venture capital analysis, valuation, and cap table")
async def generate_investor_lab(
    payload: InvestorLabRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    return await AIOrchestrator.generate_investor_lab_ai(
        title=payload.title,
        category=payload.category,
        market_size=payload.market_size,
        target_raise=payload.target_raise,
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )


@router.post("/labs/mentor", summary="Generate founder advisory plan, blindspot diagnostics, and mental models")
async def generate_mentor_lab(
    payload: MentorLabRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    return await AIOrchestrator.generate_mentor_lab_ai(
        title=payload.title,
        category=payload.category,
        stage=payload.stage,
        challenges=payload.challenges,
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )


@router.post("/labs/recruiter", summary="Generate hiring roadmap, job descriptions, and compensation benchmarks")
async def generate_recruiter_lab(
    payload: RecruiterLabRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    return await AIOrchestrator.generate_recruiter_lab_ai(
        title=payload.title,
        category=payload.category,
        current_team_size=payload.current_team_size,
        target_roles=payload.target_roles,
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )


@router.post("/labs/strategy", summary="Generate Porter's Five Forces, Blue Ocean strategy, and defensibility moats")
async def generate_strategy_lab(
    payload: StrategyLabRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    return await AIOrchestrator.generate_strategy_lab_ai(
        title=payload.title,
        category=payload.category,
        competitors=payload.competitors,
        value_proposition=payload.value_proposition,
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )


@router.post("/research/plan", summary="Generate bounded research query plan")
async def plan_research(
    payload: ResearchPlanRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.evidence.planner import ResearchPlanner
    return ResearchPlanner.generate_plan(
        task_type=payload.task_type,
        idea_title=payload.title,
        industry=payload.industry,
        target_audience=payload.target_audience
    )


@router.post("/market-grounded", summary="Generate evidence-backed market analysis with citations")
async def generate_grounded_market(
    payload: GroundedMarketRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    return await AIOrchestrator.generate_grounded_market_ai(
        title=payload.title,
        industry=payload.industry,
        problem_statement=payload.problem_statement,
        target_audience=payload.target_audience,
        provider=payload.provider or "auto",
        model=payload.model or "auto"
    )


@router.post("/competitors-grounded", summary="Generate evidence-backed competitor analysis with citations")
async def generate_grounded_competitors(
    payload: GroundedCompetitorRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    return await AIOrchestrator.generate_grounded_competitors_ai(
        title=payload.title,
        industry=payload.industry,
        solution_description=payload.solution_description,
        provider=payload.provider or "auto",
        model=payload.model or "auto"
    )


@router.post("/risks-grounded", summary="Generate evidence-backed regulatory and technical risk analysis")
async def generate_grounded_risks(
    payload: GroundedRiskRequest,
    current_user: User = Depends(get_current_user)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    return await AIOrchestrator.generate_grounded_risks_ai(
        title=payload.title,
        industry=payload.industry,
        tech_depth=payload.tech_depth or "High",
        provider=payload.provider or "auto",
        model=payload.model or "auto"
    )
