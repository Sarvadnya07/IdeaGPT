from typing import Optional, Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.ai_registry_service import AIRegistryService
from app.services.ai_task_service import AiTaskService
from app.ai.exceptions.ai_exceptions import AIException, AIUnavailableException

router = APIRouter(prefix="/ai", tags=["ai"])

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class TaskCreateRequest(BaseModel):
    task_type: str = Field(default="idea_evaluation", description="Type of task to perform")
    provider: str = Field(default="auto", description="Provider ID or 'auto'")
    model: str = Field(default="default", description="Model ID or 'default'")
    idea_id: Optional[str] = Field(default=None, description="Optional target idea ID")
    project_id: Optional[str] = Field(default=None, description="Optional target project ID")
    input_payload: Optional[Dict[str, Any]] = Field(default=None, description="Task inputs")
    idempotency_key: Optional[str] = Field(default=None, description="Optional idempotency key for deduplication")

class TaskResponse(BaseModel):
    id: str
    user_id: int
    task_type: str
    provider: str
    model: str
    status: str
    attempt: int
    idempotency_key: Optional[str]
    input_payload: Optional[Dict[str, Any]]
    result_payload: Optional[Dict[str, Any]]
    error_message: Optional[str]
    duration_ms: Optional[int]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/providers", summary="List available AI providers")
async def get_providers():
    """
    Returns list of registered AI providers and their configuration status.
    Uses cached health status to prevent external API spamming.
    """
    return AIRegistryService.get_providers()

@router.get("/models", summary="List available AI models")
async def get_models():
    """
    Returns list of supported AI models across configured providers.
    Uses dynamic model discovery and 60s TTL cache.
    """
    return await AIRegistryService.get_available_models_async()

@router.post("/registry/refresh", summary="Refresh AI provider and model registry cache")
async def refresh_registry():
    """
    Invalidates cached provider health and dynamic model metadata.
    """
    AIRegistryService.refresh_registry_cache()
    models = await AIRegistryService.get_available_models_async(force_refresh=True)
    return {
        "message": "Registry cache refreshed successfully.",
        "models_count": len(models)
    }

@router.post("/tasks", status_code=status.HTTP_202_ACCEPTED, summary="Create and enqueue an AI task")
async def create_ai_task(
    payload: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates an asynchronous AI task and enqueues execution.
    Enforces idempotency and returns 202 Accepted.
    """
    try:
        task = await AiTaskService.create_task(
            db=db,
            user=current_user,
            task_type=payload.task_type,
            provider=payload.provider,
            model=payload.model,
            input_payload=payload.input_payload,
            idea_id=payload.idea_id,
            project_id=payload.project_id,
            idempotency_key=payload.idempotency_key
        )
    except AIException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"{exc.code}: {exc.message}"
        )

    # Schedule background execution if newly queued
    if task.status == "QUEUED":
        background_tasks.add_task(AiTaskService.execute_task, db, task.id)

    return {
        "id": task.id,
        "status": task.status,
        "provider": task.provider,
        "model": task.model,
        "message": "Task accepted for processing."
    }

@router.get("/tasks/{task_id}", summary="Get AI task status and result")
async def get_ai_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Polls task status by ID.
    Enforces Safeguard #5: User Ownership Isolation.
    """
    try:
        task = await AiTaskService.get_task_by_id(db, current_user, task_id)
        return {
            "id": task.id,
            "user_id": task.user_id,
            "task_type": task.task_type,
            "provider": task.provider,
            "model": task.model,
            "status": task.status,
            "attempt": task.attempt,
            "result_payload": task.result_payload,
            "error_message": task.error_message,
            "duration_ms": task.duration_ms,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI task not found or access denied."
        )

# ---------------------------------------------------------------------------
# Architecture, Tech Stack, PRD & Pitch Deck Endpoints
# ---------------------------------------------------------------------------

class TechStackRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    focus: Optional[str] = Field(default="balanced", max_length=50)

class ArchitectureRequest(BaseModel):
    title: str = Field(default="Startup System", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    description: Optional[str] = Field(default="", max_length=1000)

class PRDRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    problem_statement: Optional[str] = Field(default="", max_length=2000)
    solution_description: Optional[str] = Field(default="", max_length=2000)
    target_users: Optional[str] = Field(default="", max_length=500)

class PitchDeckRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    problem: Optional[str] = Field(default="", max_length=2000)
    solution: Optional[str] = Field(default="", max_length=2000)

@router.post("/tech-stack", summary="Generate tailored technology stack recommendations")
async def generate_tech_stack(
    payload: TechStackRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates deterministic tech stack recommendations across Frontend, Backend, Database, AI, and DevOps layers.
    """
    from app.services.architecture_service import architecture_service
    return architecture_service.generate_tech_stack(
        category=payload.category,
        title=payload.title,
        requirements_focus=payload.focus or "balanced"
    )

@router.post("/architecture", summary="Generate system architecture blueprint and topology")
async def generate_architecture(
    payload: ArchitectureRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates system topology, database ER schema, API specs, and security blueprints.
    """
    from app.services.architecture_service import architecture_service
    return architecture_service.generate_architecture_blueprint(
        title=payload.title,
        category=payload.category,
        description=payload.description or ""
    )

@router.post("/prd", summary="Generate Product Requirements Document (PRD)")
async def generate_prd(
    payload: PRDRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates a structured Product Requirements Document (PRD) with user personas, functional requirements, and KPIs.
    """
    from app.services.architecture_service import architecture_service
    return architecture_service.generate_prd(
        title=payload.title,
        category=payload.category,
        problem_statement=payload.problem_statement or "Founders lack rapid technical feasibility validation.",
        solution_description=payload.solution_description or "Automated AI co-founder that scopes architectures and analyzes risk.",
        target_users=payload.target_users or "Startup Founders, Product Managers, Software Engineers"
    )

@router.post("/pitch-deck", summary="Generate 10-slide startup pitch deck outline")
async def generate_pitch_deck(
    payload: PitchDeckRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates a structured 10-slide venture pitch deck outline.
    """
    from app.services.architecture_service import architecture_service
    return {
        "title": payload.title,
        "category": payload.category,
        "slides": architecture_service.generate_pitch_deck_outline(
            title=payload.title,
            category=payload.category,
            problem=payload.problem or "",
            solution=payload.solution or ""
        )
    }
