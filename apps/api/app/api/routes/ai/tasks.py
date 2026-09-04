"""
AI Tasks Sub-Router: Task creation, retrieval, and SSE streaming lifecycle.
"""

from typing import Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.ai_task_service import AiTaskService
from app.ai.exceptions.ai_exceptions import AIException

router = APIRouter()


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

    async def event_generator():
        # First verify ownership
        from app.db.session import AsyncSessionLocal
        terminal_states = {"COMPLETED", "FAILED", "CANCELLED"}
        max_duration_seconds = 120  # Maximum stream lifetime to prevent runaway connections
        poll_interval_seconds = 1.0
        elapsed = 0.0

        try:
            async with AsyncSessionLocal() as session:
                task = await AiTaskService.get_task_by_id(session, current_user, task_id)
        except KeyError:
            yield f"event: error\ndata: {json.dumps({'error': 'AI task not found or access denied.'})}\n\n"
            return

        last_status = None
        while elapsed < max_duration_seconds:
            try:
                async with AsyncSessionLocal() as session:
                    task = await AiTaskService.get_task_by_id(session, current_user, task_id)

                current_status = task.status
                payload = {
                    "task_id": task.id,
                    "status": current_status,
                    "attempt": task.attempt,
                    "provider": task.provider,
                    "model": task.model,
                    "duration_ms": task.duration_ms,
                    "error_message": task.error_message,
                    "has_result": task.result_payload is not None,
                }

                if current_status in terminal_states:
                    if current_status == "COMPLETED":
                        payload["result"] = task.result_payload
                    yield f"event: done\ndata: {json.dumps(payload)}\n\n"
                    break
                else:
                    yield f"event: progress\ndata: {json.dumps(payload)}\n\n"

                last_status = current_status
                await asyncio.sleep(poll_interval_seconds)
                elapsed += poll_interval_seconds

            except asyncio.CancelledError:
                break
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
