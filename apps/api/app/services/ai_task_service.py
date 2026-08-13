import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update

from app.models.ai_task import AiTask
from app.models.user import User
from app.ai.orchestrator.orchestrator import orchestrator
from app.ai.orchestrator.retry import AIRetryPolicy
from app.services.ai_quota_service import AIQuotaService
from app.ai.exceptions.ai_exceptions import AIException, AIUnavailableException, AIQuotaExceededException

logger = logging.getLogger(__name__)

VALID_STATUS_TRANSITIONS = {
    "QUEUED": {"RUNNING", "CANCELLED", "FAILED"},
    "RUNNING": {"COMPLETED", "FAILED", "CANCELLED"},
    "FAILED": {"QUEUED"},     # Retry allowed
    "CANCELLED": {"QUEUED"},  # Retry allowed
    "COMPLETED": set(),       # Terminal state
}

class AiTaskService:

    @classmethod
    async def create_task(
        cls,
        db: AsyncSession,
        user: User,
        task_type: str = "idea_evaluation",
        provider: str = "auto",
        model: str = "default",
        input_payload: Optional[Dict[str, Any]] = None,
        idea_id: Optional[str] = None,
        project_id: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> AiTask:
        """
        Creates a new AI task record with Quota enforcement and Idempotency Deduplication.
        """
        # Validate prompt input length
        prompt = (input_payload or {}).get("prompt", "Analyze startup idea.")
        AIQuotaService.validate_input_length(prompt)

        # Enforce per-user daily task quota
        await AIQuotaService.check_user_quota(db, user)

        # Safeguard #6: Check for existing in-flight task with matching idempotency key
        if idempotency_key:
            stmt = select(AiTask).where(
                and_(
                    AiTask.user_id == user.id,
                    AiTask.idempotency_key == idempotency_key,
                    AiTask.status.in_(["QUEUED", "RUNNING", "COMPLETED"])
                )
            )
            res = await db.execute(stmt)
            existing_task = res.scalars().first()
            if existing_task:
                logger.info(f"Idempotency hit: Returning existing AiTask {existing_task.id} for key {idempotency_key}")
                return existing_task

        new_task = AiTask(
            user_id=user.id,
            project_id=project_id,
            idea_id=idea_id,
            task_type=task_type,
            provider=provider,
            model=model,
            status="QUEUED",
            attempt=1,
            idempotency_key=idempotency_key,
            input_payload=input_payload,
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        return new_task

    @classmethod
    async def get_task_by_id(cls, db: AsyncSession, user: User, task_id: str) -> AiTask:
        """
        Retrieves task by ID enforcing Safeguard #5 (User Ownership Boundary).
        """
        stmt = select(AiTask).where(
            and_(
                AiTask.id == task_id,
                AiTask.user_id == user.id
            )
        )
        res = await db.execute(stmt)
        task = res.scalars().first()
        if not task:
            raise KeyError(f"Task with ID {task_id} not found or access denied.")
        return task

    @classmethod
    async def update_task_status(
        cls,
        db: AsyncSession,
        task: AiTask,
        new_status: str,
        result_payload: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> AiTask:
        """
        Enforces Safeguard #4: Explicit status transition state machine.
        """
        allowed_next = VALID_STATUS_TRANSITIONS.get(task.status, set())
        if new_status not in allowed_next:
            raise ValueError(f"Invalid status transition: {task.status} -> {new_status}")

        task.status = new_status
        now = datetime.now(timezone.utc)

        if new_status == "RUNNING":
            task.started_at = now
        elif new_status in ["COMPLETED", "FAILED", "CANCELLED"]:
            task.completed_at = now
            if result_payload:
                task.result_payload = result_payload
            if error_message:
                task.error_message = error_message
            if duration_ms is not None:
                task.duration_ms = duration_ms

        task.updated_at = now
        await db.commit()
        await db.refresh(task)
        return task

    @classmethod
    async def execute_task(cls, db: AsyncSession, task_id: str) -> AiTask:
        """
        Executes an AI task asynchronously with bounded retries and timeouts.
        """
        stmt = select(AiTask).where(AiTask.id == task_id)
        res = await db.execute(stmt)
        task = res.scalars().first()
        if not task:
            raise KeyError(f"Task {task_id} not found for execution.")

        # Transition QUEUED -> RUNNING
        await cls.update_task_status(db, task, "RUNNING")
        start_time = time.time()

        try:
            prompt = (task.input_payload or {}).get("prompt", "Analyze startup idea.")
            idea_id = task.idea_id
            preferred = task.provider if task.provider != "auto" else None

            # Execute via Orchestrator wrapped with AIRetryPolicy
            result = await AIRetryPolicy.execute_with_retry(
                orchestrator.analyze_startup_idea,
                prompt=prompt,
                db=db,
                idea_id=idea_id,
                preferred_provider=preferred,
                strategy="user_selected" if preferred else "auto"
            )

            duration_ms = int((time.time() - start_time) * 1000)
            return await cls.update_task_status(
                db=db,
                task=task,
                new_status="COMPLETED",
                result_payload=result,
                duration_ms=duration_ms
            )

        except AIUnavailableException as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            return await cls.update_task_status(
                db=db,
                task=task,
                new_status="FAILED",
                error_message=f"AI_UNAVAILABLE: {exc.message}",
                duration_ms=duration_ms
            )

        except Exception as exc:
            logger.error(f"Task execution failed for task {task_id}: {str(exc)}", exc_info=True)
            duration_ms = int((time.time() - start_time) * 1000)
            return await cls.update_task_status(
                db=db,
                task=task,
                new_status="FAILED",
                error_message=f"Execution error: {str(exc)}",
                duration_ms=duration_ms
            )

    @classmethod
    async def cleanup_stale_tasks(cls, db: AsyncSession, timeout_minutes: int = 5) -> int:
        """
        Sweeps tasks stuck in QUEUED or RUNNING for longer than timeout_minutes and transitions them to FAILED.
        """
        threshold = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
        stmt = select(AiTask).where(
            and_(
                AiTask.status.in_(["QUEUED", "RUNNING"]),
                AiTask.created_at < threshold
            )
        )
        res = await db.execute(stmt)
        stale_tasks = res.scalars().all()

        for t in stale_tasks:
            t.status = "FAILED"
            t.error_message = f"Task timed out after remaining in {t.status} state > {timeout_minutes}m."
            t.completed_at = datetime.now(timezone.utc)

        if stale_tasks:
            await db.commit()
            logger.info(f"Cleaned up {len(stale_tasks)} stale AI tasks.")
        return len(stale_tasks)
