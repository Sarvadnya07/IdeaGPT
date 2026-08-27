from typing import Optional, Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Header, Request
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

from typing import Annotated

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

@router.post("/tasks", status_code=status.HTTP_202_ACCEPTED, summary="Create and enqueue an AI task")
async def create_ai_task(
    payload: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
):
    """
    Creates an asynchronous AI task and enqueues execution.
    Enforces idempotency (via Idempotency-Key header or request body) and returns 202 Accepted.
    """
    effective_idempotency_key = idempotency_key or x_idempotency_key or payload.idempotency_key

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
            idempotency_key=effective_idempotency_key
        )
    except AIException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=f"{exc.code}: {exc.message}"
        )

    # Schedule background execution if newly queued
    if task.status == "QUEUED":
        background_tasks.add_task(AiTaskService.execute_task, task.id)

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

@router.get("/tasks/{task_id}/stream", summary="Stream AI task lifecycle events via Server-Sent Events (SSE)")
async def stream_ai_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Streams task status and incremental progress updates in real-time via Server-Sent Events (SSE).
    Terminates when the task reaches COMPLETED, FAILED, or CANCELLED, or on client disconnect / timeout.
    """
    import asyncio
    import json
    from fastapi.responses import StreamingResponse
    from app.db.session import AsyncSessionLocal

    async def event_generator():
        # First verify user ownership
        try:
            task = await AiTaskService.get_task_by_id(db, current_user, task_id)
        except KeyError:
            yield f"event: error\ndata: {json.dumps({'error': 'AI task not found or access denied.'})}\n\n"
            return

        max_polls = 60  # 60 * 0.5s = 30s timeout
        for _ in range(max_polls):
            try:
                async with AsyncSessionLocal() as session:
                    task = await AiTaskService.get_task_by_id(session, current_user, task_id)

                payload = {
                    "id": task.id,
                    "task_type": task.task_type,
                    "status": task.status,
                    "provider": task.provider,
                    "model": task.model,
                    "duration_ms": task.duration_ms,
                    "error_message": task.error_message,
                    "result_payload": task.result_payload if task.status == "COMPLETED" else None,
                }

                yield f"event: task_update\ndata: {json.dumps(payload)}\n\n"

                if task.status in ("COMPLETED", "FAILED", "CANCELLED"):
                    yield f"event: done\ndata: {json.dumps({'status': task.status})}\n\n"
                    break

                await asyncio.sleep(0.5)
            except Exception as e:
                import logging
                logging.getLogger("ideagpt.sse").error(f"SSE stream error for task {task_id}: {e}", exc_info=True)
                yield f"event: error\ndata: {json.dumps({'error': 'An internal error occurred while streaming task updates.'})}\n\n"
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ---------------------------------------------------------------------------
# Architecture, Tech Stack, PRD & Pitch Deck Endpoints
# ---------------------------------------------------------------------------

class TechStackRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    focus: Optional[str] = Field(default="balanced", max_length=50)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)

class ArchitectureRequest(BaseModel):
    title: str = Field(default="Startup System", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    description: Optional[str] = Field(default="", max_length=1000)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)

class PRDRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    problem_statement: Optional[str] = Field(default="", max_length=2000)
    solution_description: Optional[str] = Field(default="", max_length=2000)
    target_users: Optional[str] = Field(default="", max_length=500)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)

class RoadmapRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    problem_statement: Optional[str] = Field(default="", max_length=2000)
    solution_description: Optional[str] = Field(default="", max_length=2000)
    target_users: Optional[str] = Field(default="", max_length=500)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)

class PitchDeckRequest(BaseModel):
    title: str = Field(default="Startup Concept", max_length=100)
    category: str = Field(default="B2B SaaS", max_length=50)
    problem: Optional[str] = Field(default="", max_length=2000)
    solution: Optional[str] = Field(default="", max_length=2000)
    provider: Optional[str] = Field(default="groq", max_length=50)
    model: Optional[str] = Field(default="llama-3.3-70b-versatile", max_length=100)

@router.post("/roadmap", summary="Generate AI-powered startup roadmap milestones and tasks")
async def generate_roadmap(
    payload: RoadmapRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates tailored milestone phases and engineering tasks synthesized directly from startup idea metadata via Groq LLM.
    """
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
    return {
        "title": payload.title,
        "category": payload.category,
        "milestones": milestones,
        "provider": payload.provider or "groq",
        "model": payload.model or "llama-3.3-70b-versatile",
    }

@router.post("/tech-stack", summary="Generate tailored technology stack recommendations")
async def generate_tech_stack(
    payload: TechStackRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates dynamic technology stack recommendations synthesized directly via Groq LLM.
    """
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    return await AIOrchestrator.generate_tech_stack_ai(
        title=payload.title,
        category=payload.category,
        focus=payload.focus or "balanced",
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )

@router.post("/architecture", summary="Generate system architecture blueprint and topology")
async def generate_architecture(
    payload: ArchitectureRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates dynamic system topology, database ER schema, API specs, and security blueprints via Groq LLM.
    """
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    return await AIOrchestrator.generate_architecture_ai(
        title=payload.title,
        category=payload.category,
        description=payload.description or "",
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )

@router.post("/prd", summary="Generate Product Requirements Document (PRD)")
async def generate_prd(
    payload: PRDRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates a structured Product Requirements Document (PRD) with user personas, functional requirements, and KPIs via Groq LLM.
    """
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    return await AIOrchestrator.generate_prd_ai(
        title=payload.title,
        category=payload.category,
        problem_statement=payload.problem_statement or "",
        solution_description=payload.solution_description or "",
        target_users=payload.target_users or "",
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )

@router.post("/pitch-deck", summary="Generate 10-slide startup pitch deck outline")
async def generate_pitch_deck(
    payload: PitchDeckRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates a structured 10-slide venture pitch deck outline via Groq LLM.
    """
    from app.ai.orchestrator.orchestrator import AIOrchestrator
    slides = await AIOrchestrator.generate_pitch_deck_ai(
        title=payload.title,
        category=payload.category,
        problem=payload.problem or "",
        solution=payload.solution or "",
        provider=payload.provider or "groq",
        model=payload.model or "llama-3.3-70b-versatile"
    )
    return {
        "title": payload.title,
        "category": payload.category,
        "slides": slides,
        "provider": payload.provider or "groq",
        "model": payload.model or "llama-3.3-70b-versatile",
    }
