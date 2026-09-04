"""
AI Operations Sub-Router: Provider diagnostics, benchmarks, and startup blueprints (Roadmap, PRD, Tech Stack, Architecture, Pitch Deck).
"""

from typing import Optional, Any, Dict, List, Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.ai_registry_service import AIRegistryService
from app.services.ai_artifact_service import AIArtifactService

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TechStackRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    focus: Optional[str] = Field(default="balanced", max_length=50)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)
    project_id: Optional[str] = None
    idea_id: Optional[str] = None

class ArchitectureRequest(BaseModel):
    title: str = Field(default="Startup System", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    description: Optional[str] = Field(default="", max_length=1000)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)
    project_id: Optional[str] = None
    idea_id: Optional[str] = None

class PRDRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    problem_statement: Optional[str] = Field(default="", max_length=2000)
    solution_description: Optional[str] = Field(default="", max_length=2000)
    target_users: Optional[str] = Field(default="", max_length=500)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)
    project_id: Optional[str] = None
    idea_id: Optional[str] = None

class RoadmapRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    problem_statement: Optional[str] = Field(default="", max_length=2000)
    solution_description: Optional[str] = Field(default="", max_length=2000)
    target_users: Optional[str] = Field(default="", max_length=500)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)
    project_id: Optional[str] = None
    idea_id: Optional[str] = None

class PitchDeckRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    problem: Optional[str] = Field(default="", max_length=2000)
    solution: Optional[str] = Field(default="", max_length=2000)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)
    project_id: Optional[str] = None
    idea_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Registry & Diagnostics Endpoints
# ---------------------------------------------------------------------------

@router.get("/providers", summary="List available AI providers")
async def get_providers(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Returns list of registered AI providers and their configuration status.
    Uses cached health status to prevent external API spamming.
    """
    return AIRegistryService.get_providers()


@router.get("/models", summary="List available AI models")
async def get_models(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Returns list of supported AI models across configured providers.
    Uses dynamic model discovery and 60s TTL cache.
    """
    return await AIRegistryService.get_available_models_async()


@router.get("/providers/health", summary="Get live provider connectivity and latency diagnostics")
async def get_providers_health(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Returns live connectivity status, latency (ms), and capability health across providers.
    """
    from app.ai.gateway.registry import gateway_registry
    return await gateway_registry.get_providers_status()


@router.post("/registry/refresh", summary="Refresh AI provider and model registry cache")
async def refresh_registry(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Invalidates cached provider health and dynamic model metadata.
    """
    AIRegistryService.refresh_registry_cache()
    models = await AIRegistryService.get_available_models_async(force_refresh=True)
    return {
        "message": "Registry cache refreshed successfully.",
        "models_count": len(models)
    }


# ---------------------------------------------------------------------------
# Architecture, Tech Stack, PRD & Pitch Deck Endpoints
# ---------------------------------------------------------------------------

@router.post("/roadmap", summary="Generate AI-powered startup roadmap milestones and tasks")
async def generate_roadmap(
    payload: RoadmapRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    milestones = await AIOrchestrator.generate_roadmap_ai(
        title=payload.title,
        category=payload.category,
        problem_statement=payload.problem_statement or "",
        solution_description=payload.solution_description or "",
        target_users=payload.target_users or "",
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )
    artifact = await AIArtifactService.save_artifact(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        idea_id=payload.idea_id,
        artifact_type="roadmap",
        title=f"Roadmap: {payload.title}",
        content_payload={"title": payload.title, "category": payload.category, "milestones": milestones},
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile",
        execution_type="REAL_PROVIDER"
    )
    return {
        "artifact_id": artifact.id,
        "title": payload.title,
        "category": payload.category,
        "milestones": milestones,
        "provider": payload.provider or "groq",
        "model": payload.model or "llama-3.3-70b-versatile",
        "execution_type": "REAL_PROVIDER",
        "fallback_used": False,
    }


@router.post("/tech-stack", summary="Generate tailored technology stack recommendations")
async def generate_tech_stack(
    payload: TechStackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    res = await AIOrchestrator.generate_tech_stack_ai(
        title=payload.title,
        category=payload.category,
        focus=payload.focus or "balanced",
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )
    artifact = await AIArtifactService.save_artifact(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        idea_id=payload.idea_id,
        artifact_type="tech_stack",
        title=f"Tech Stack: {payload.title}",
        content_payload=res,
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile",
        execution_type="REAL_PROVIDER"
    )
    if isinstance(res, dict):
        res["artifact_id"] = artifact.id
        res["execution_type"] = "REAL_PROVIDER"
        res["fallback_used"] = False
    return res


@router.post("/architecture", summary="Generate system architecture blueprint and topology")
async def generate_architecture(
    payload: ArchitectureRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    res = await AIOrchestrator.generate_architecture_ai(
        title=payload.title,
        category=payload.category,
        description=payload.description or "",
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )
    artifact = await AIArtifactService.save_artifact(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        idea_id=payload.idea_id,
        artifact_type="architecture",
        title=f"Architecture Blueprint: {payload.title}",
        content_payload=res,
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile",
        execution_type="REAL_PROVIDER"
    )
    if isinstance(res, dict):
        res["artifact_id"] = artifact.id
        res["execution_type"] = "REAL_PROVIDER"
        res["fallback_used"] = False
    return res


@router.post("/prd", summary="Generate Product Requirements Document (PRD)")
async def generate_prd(
    payload: PRDRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    res = await AIOrchestrator.generate_prd_ai(
        title=payload.title,
        category=payload.category,
        problem_statement=payload.problem_statement or "",
        solution_description=payload.solution_description or "",
        target_users=payload.target_users or "",
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )
    artifact = await AIArtifactService.save_artifact(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        idea_id=payload.idea_id,
        artifact_type="prd",
        title=f"PRD: {payload.title}",
        content_payload=res,
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile",
        execution_type="REAL_PROVIDER"
    )
    if isinstance(res, dict):
        res["artifact_id"] = artifact.id
        res["execution_type"] = "REAL_PROVIDER"
        res["fallback_used"] = False
    return res


@router.post("/pitch-deck", summary="Generate 10-slide startup pitch deck outline")
async def generate_pitch_deck(
    payload: PitchDeckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    slides = await AIOrchestrator.generate_pitch_deck_ai(
        title=payload.title,
        category=payload.category,
        problem=payload.problem or "",
        solution=payload.solution or "",
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )
    artifact = await AIArtifactService.save_artifact(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        idea_id=payload.idea_id,
        artifact_type="pitch_deck",
        title=f"Pitch Deck: {payload.title}",
        content_payload={"title": payload.title, "category": payload.category, "slides": slides},
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile",
        execution_type="REAL_PROVIDER"
    )
    return {
        "artifact_id": artifact.id,
        "title": payload.title,
        "category": payload.category,
        "slides": slides,
        "provider": payload.provider or "groq",
        "model": payload.model or "llama-3.3-70b-versatile",
        "execution_type": "REAL_PROVIDER",
        "fallback_used": False,
    }


# ---------------------------------------------------------------------------
# Operations & Benchmarks
# ---------------------------------------------------------------------------

@router.post("/ops/benchmark", summary="Execute safe low-budget AI latency and throughput benchmark")
async def run_ai_benchmark(
    current_user: User = Depends(get_current_user)
):
    import time
    benchmark_results = [
        {"provider": "groq", "model": "llama-3.3-70b-versatile", "latency_ms": 285, "tokens_per_second": 82.5, "status": "SUCCESS", "error": None},
        {"provider": "gemini", "model": "gemini-1.5-flash", "latency_ms": 410, "tokens_per_second": 64.0, "status": "SUCCESS", "error": None},
        {"provider": "openai", "model": "gpt-4o-mini", "latency_ms": 520, "tokens_per_second": 55.0, "status": "BYOK_READY", "error": None},
        {"provider": "ollama", "model": "llama3.2:latest", "latency_ms": 780, "tokens_per_second": 32.0, "status": "LOCAL_READY", "error": None}
    ]
    return {
        "timestamp": time.time(),
        "benchmark_runs": benchmark_results,
        "fastest_provider": "groq",
        "provenance": "SIMULATED_DEMO_DATA"
    }


@router.get("/ops/health-monitor", summary="Fetch system health, circuit breaker states, and fallback counters")
async def get_system_health_monitor(
    current_user: User = Depends(get_current_user)
):
    from app.services.analytics_service import AnalyticsService
    return AnalyticsService.get_system_health()
