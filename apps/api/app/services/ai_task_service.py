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

        # F-02 remediation: reject cross-tenant linkage before persisting
        from app.services.ai_artifact_service import assert_tenant_links
        await assert_tenant_links(db, user.id, project_id, idea_id)

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
                # API-03 Idempotency Validation: Same Idempotency-Key + Different Payload -> Reject (409 Conflict)
                if existing_task.task_type != task_type or (existing_task.input_payload or {}) != (input_payload or {}):
                    raise AIException(
                        code="IDEMPOTENCY_CONFLICT",
                        message=f"Idempotency key '{idempotency_key}' was previously used with a different payload.",
                        status_code=409
                    )
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
        try:
            await db.commit()
        except Exception as exc:
            # F-06: if uq_ai_tasks_user_idempotency fired (concurrent insert with the
            # same key), fetch and return the existing task instead of erroring.
            await db.rollback()
            from sqlalchemy.exc import IntegrityError
            if isinstance(exc, IntegrityError) and idempotency_key:
                existing = await db.execute(
                    select(AiTask).where(
                        and_(
                            AiTask.user_id == user.id,
                            AiTask.idempotency_key == idempotency_key,
                        )
                    )
                )
                existing_task = existing.scalars().first()
                if existing_task:
                    logger.info(
                        "Idempotency race resolved: returning existing AiTask %s for key %s",
                        existing_task.id,
                        idempotency_key,
                    )
                    return existing_task
            raise
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
    async def execute_task(cls, first_arg: Any, second_arg: Optional[str] = None) -> AiTask:
        """
        Executes an AI task asynchronously with bounded retries and timeouts.
        Supports both execute_task(task_id) for background tasks with isolated session,
        and legacy execute_task(db, task_id) for synchronous test suites.
        """
        if isinstance(first_arg, AsyncSession) and second_arg is not None:
            db = first_arg
            task_id = second_arg
            return await cls._execute_task_internal(db, task_id)
        
        task_id = str(first_arg)
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            return await cls._execute_task_internal(session, task_id)

    @classmethod
    async def _execute_task_internal(cls, db: AsyncSession, task_id: str) -> AiTask:
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
            req_model = task.model if task.model not in ("auto", "default", None) else None

            # F-07 remediation: hold a DB session ONLY for state transitions.
            # The orchestrator call must not hold a pooled DB connection across the
            # external provider round-trip. In BackgroundTasks execution the session
            # commits before dispatch, so we pass db=None.
            #
            # PRODUCT-01 P-07: build the full prompt context here (while the session
            # is available) and pass it down, so the orchestrator renders the same
            # registry prompt it would have rendered with db + idea_id — instead of
            # silently degrading to a bare one-liner and bypassing the prompt version
            # and evaluation cache.
            prompt_text = prompt
            idea_context: Optional[Dict[str, Any]] = None
            idea_snapshot: Optional[Dict[str, Any]] = None
            if idea_id and db is not None:
                try:
                    from app.models.idea import Idea
                    from app.models.project import Project
                    from app.ai.pipelines.context import ContextBuilder

                    idea_res = await db.execute(select(Idea).where(Idea.id == idea_id))
                    idea_row = idea_res.scalar_one_or_none()
                    if idea_row:
                        project_res = await db.execute(
                            select(Project).where(Project.id == idea_row.project_id)
                        )
                        project_row = project_res.scalar_one_or_none()
                        if project_row is not None:
                            idea_context = ContextBuilder.compile_context(idea_row, project_row)
                        idea_snapshot = {
                            "title": idea_row.title,
                            "problem_statement": idea_row.problem_statement,
                            "solution_description": idea_row.solution_description,
                            "target_users": idea_row.target_users,
                            "industry": idea_row.industry,
                            "business_model": idea_row.business_model,
                            "stage": idea_row.stage,
                            "tags": idea_row.tags,
                            "notes": idea_row.notes,
                        }
                except Exception:
                    idea_context = None
                    idea_snapshot = None

            # When no idea context could be assembled, keep the historical
            # prompt-only behaviour rather than failing the task.
            if idea_context is None:
                idea_snapshot = None
                if idea_id:
                    prompt_text = prompt

            # Execute via Orchestrator wrapped with AIRetryPolicy
            result = await AIRetryPolicy.execute_with_retry(
                orchestrator.analyze_startup_idea,
                prompt=None if idea_context is not None else prompt_text,
                db=None,
                idea_id=None,
                context=idea_context,
                idea_snapshot=idea_snapshot,
                preferred_provider=preferred,
                requested_model=req_model,
                strategy=task.provider
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Record actual provider/model used in execution
            meta = result.get("metadata", {})
            if meta.get("provider"):
                task.provider = meta["provider"]
            if meta.get("model"):
                task.model = meta["model"]

            await cls.update_task_status(
                db,
                task,
                "COMPLETED",
                result_payload=result,
                duration_ms=duration_ms
            )
            return task

        except AIUnavailableException as exc:
            logger.warning(f"Task {task_id} AI unavailable: {exc}")
            duration_ms = int((time.time() - start_time) * 1000)
            return await cls.update_task_status(
                db=db,
                task=task,
                new_status="FAILED",
                error_message="AI service is currently unavailable. Please check provider configuration or retry later.",
                duration_ms=duration_ms
            )

        except AIQuotaExceededException as exc:
            logger.warning(f"Task {task_id} quota exceeded: {exc}")
            duration_ms = int((time.time() - start_time) * 1000)
            return await cls.update_task_status(
                db=db,
                task=task,
                new_status="FAILED",
                error_message="Daily AI task quota reached for your account.",
                duration_ms=duration_ms
            )

        except AIException as exc:
            logger.warning(f"Task {task_id} AI exception: {exc}")
            duration_ms = int((time.time() - start_time) * 1000)
            return await cls.update_task_status(
                db=db,
                task=task,
                new_status="FAILED",
                error_message="An error occurred during AI model processing. Please try again.",
                duration_ms=duration_ms
            )

        except Exception as exc:
            logger.error(f"Task execution failed for task {task_id}: {str(exc)}", exc_info=True)
            duration_ms = int((time.time() - start_time) * 1000)
            return await cls.update_task_status(
                db=db,
                task=task,
                new_status="FAILED",
                error_message="An unexpected error occurred during task execution. Please try again later.",
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
