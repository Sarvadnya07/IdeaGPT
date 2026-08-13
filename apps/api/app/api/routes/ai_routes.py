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
    """
    return AIRegistryService.get_available_models()

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
