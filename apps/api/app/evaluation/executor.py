import logging
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.models.evaluation import Evaluation
from app.models.evaluation_history import EvaluationHistory
from app.models.idea import Idea
from app.models.project import Project
from app.evaluation.state import (
    EvaluationStatus,
    EvaluationProgress,
    validate_transition,
    EvaluationConcurrencyConflictError,
)
from app.ai.orchestrator.generation_pipeline import (
    DeterministicFallback,
    is_deterministic_provider,
)

logger = logging.getLogger(__name__)


class EvaluationExecutor:
    """
    Handles atomic execution, transaction boundary separation, error capture,
    and history recording for evaluation jobs.
    """

    @classmethod
    async def record_history_event(
        cls,
        db: AsyncSession,
        evaluation_id: str,
        event_type: str,
        from_status: Optional[str] = None,
        to_status: Optional[str] = None,
        progress: Optional[str] = None,
        message: Optional[str] = None,
    ) -> EvaluationHistory:
        """Helper to create and persist a lifecycle history record."""
        event = EvaluationHistory(
            evaluation_id=evaluation_id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            progress=progress,
            message=message,
            created_at=datetime.now(timezone.utc),
        )
        db.add(event)
        return event

    @classmethod
    async def execute_evaluation(cls, evaluation_id: str) -> Evaluation:
        """
        Main execution flow with strict transaction separation:
        
        Tx 1: Mark RUNNING + Commit
        Comp: Run Deterministic Engine in-memory
        Tx 2: Persist Result + Mark COMPLETED + Commit
        On Error: Mark FAILED + Save Error + Commit
        """
        start_time = time.time()
        idea_id: Optional[str] = None

        # ---------------------------------------------------------------------
        # TRANSACTION 1: Transition to RUNNING
        # ---------------------------------------------------------------------
        async with AsyncSessionLocal() as db:
            async with db.begin():
                stmt = select(Evaluation).where(Evaluation.id == evaluation_id)
                if db.bind and db.bind.dialect.name != "sqlite":
                    stmt = stmt.with_for_update()

                result = await db.execute(stmt)
                evaluation = result.scalar_one_or_none()

                if not evaluation:
                    logger.error(f"Executor failed: Evaluation '{evaluation_id}' not found.")
                    raise ValueError(f"Evaluation '{evaluation_id}' not found.")

                curr_status = evaluation.status
                if curr_status not in [EvaluationStatus.PENDING.value, "QUEUED"]:
                    logger.warning(
                        f"Execution skipped for evaluation '{evaluation_id}': status is '{curr_status}'"
                    )
                    raise EvaluationConcurrencyConflictError(evaluation_id, curr_status)

                idea_id = evaluation.idea_id
                old_status = evaluation.status
                validate_transition(old_status, EvaluationStatus.RUNNING.value)

                evaluation.status = EvaluationStatus.RUNNING.value
                evaluation.progress = EvaluationProgress.VALIDATION.value
                evaluation.started_at = datetime.now(timezone.utc)
                evaluation.error_message = None

                await cls.record_history_event(
                    db=db,
                    evaluation_id=evaluation_id,
                    event_type="RUN_STARTED",
                    from_status=old_status,
                    to_status=EvaluationStatus.RUNNING.value,
                    progress=EvaluationProgress.VALIDATION.value,
                    message="Evaluation execution started by coordinator",
                )

        logger.info(f"Evaluation '{evaluation_id}' marked RUNNING. DB Tx 1 committed.")

        # ---------------------------------------------------------------------
        # COMPUTATION STAGE: Fetch Idea & Run AI Pipeline / Engine (Outside DB Tx)
        # ---------------------------------------------------------------------
        idea = None
        idea_snapshot: Optional[Dict[str, Any]] = None
        idea_context: Optional[Dict[str, Any]] = None
        try:
            # F-07 remediation: pre-fetch the Idea, its parent Project and the
            # evaluation metadata in a short session, then RELEASE the DB connection
            # before the external LLM call.
            #
            # PRODUCT-01 P-07: the session is closed, but the *prompt is built here*
            # via ContextBuilder.compile_context + prompt_registry so the orchestrator
            # renders byte-identical model input (same user/system prompt, same
            # prompt_version, temperature, max_tokens and cache key) as the legacy
            # db-backed path. Passing db=None alone would silently degrade the prompt
            # to a bare one-liner and bypass the evaluation cache.
            async with AsyncSessionLocal() as db:
                idea_result = await db.execute(select(Idea).where(Idea.id == idea_id))
                idea = idea_result.scalar_one_or_none()
                if not idea:
                    raise ValueError(f"Parent Idea '{idea_id}' not found.")

                eval_meta = await db.execute(select(Evaluation).where(Evaluation.id == evaluation_id))
                eval_obj = eval_meta.scalar_one_or_none()
                requested_provider = eval_obj.provider if eval_obj else "groq"
                requested_model = eval_obj.model if eval_obj else None

                # Detach the idea data we need so no lazy DB access happens after
                # the session is closed.
                idea_title = idea.title
                idea_problem = idea.problem_statement
                idea_solution = idea.solution_description
                idea_snapshot = {
                    "title": idea.title,
                    "problem_statement": idea.problem_statement,
                    "solution_description": idea.solution_description,
                    "target_users": idea.target_users,
                    "industry": idea.industry,
                    "business_model": idea.business_model,
                    "stage": idea.stage,
                    "tags": idea.tags,
                    "notes": idea.notes,
                }

                # Build the full prompt context while the session is still open.
                project_res = await db.execute(
                    select(Project).where(Project.id == idea.project_id)
                )
                project_obj = project_res.scalar_one_or_none()
                if project_obj is not None:
                    from app.ai.pipelines.context import ContextBuilder
                    idea_context = ContextBuilder.compile_context(idea, project_obj)

            # If user explicitly requested deterministic engine:
            if is_deterministic_provider(requested_provider):
                result_payload = DeterministicFallback.from_idea_snapshot(idea_snapshot)
            elif idea_context is not None:
                # Execute via AI Orchestrator with the detached context: no pooled
                # connection is held across the external call, and the prompt is
                # still the registry-rendered evaluation prompt.
                from app.ai.orchestrator.orchestrator import orchestrator
                result_payload = await orchestrator.analyze_startup_idea(
                    prompt=None,
                    db=None,
                    idea_id=None,
                    context=idea_context,
                    idea_snapshot=idea_snapshot,
                    preferred_provider=requested_provider,
                    requested_model=requested_model,
                )
            else:
                # Parent project could not be resolved (orphaned idea). Fall back to
                # the prompt-only path rather than failing the evaluation.
                from app.ai.orchestrator.orchestrator import orchestrator
                prompt_text = (
                    f"Analyze startup idea: {idea_title}. "
                    f"Problem: {idea_problem}. Solution: {idea_solution}"
                )
                result_payload = await orchestrator.analyze_startup_idea(
                    prompt=prompt_text,
                    db=None,
                    idea_id=None,
                    preferred_provider=requested_provider,
                    requested_model=requested_model,
                )

            duration_ms = int((time.time() - start_time) * 1000)
            if "metadata" not in result_payload:
                result_payload["metadata"] = {}
            result_payload["metadata"]["duration_ms"] = duration_ms

        except Exception as exc:
            logger.error(f"Execution failed for evaluation '{evaluation_id}': {str(exc)}", exc_info=True)
            # Resilient fallback to the deterministic engine via the shared policy.
            # Uses the detached idea_snapshot (no session held) so the fallback never
            # touches the database or a pooled connection.
            try:
                if idea_snapshot is not None:
                    result_payload = DeterministicFallback.from_idea_snapshot(idea_snapshot)
                elif idea is not None:
                    result_payload = DeterministicFallback.from_idea(idea)
                else:
                    raise exc
                duration_ms = int((time.time() - start_time) * 1000)
                if "metadata" not in result_payload:
                    result_payload["metadata"] = {}
                result_payload["metadata"]["duration_ms"] = duration_ms
                DeterministicFallback.with_reason(result_payload, str(exc))
            except Exception as fallback_exc:

                return await cls._handle_execution_failure(
                    evaluation_id=evaluation_id,
                    error_message=str(fallback_exc),
                    duration_ms=int((time.time() - start_time) * 1000),
                )

        # ---------------------------------------------------------------------
        # TRANSACTION 2: Persist Result & Mark COMPLETED
        # ---------------------------------------------------------------------
        async with AsyncSessionLocal() as db:
            async with db.begin():
                stmt = select(Evaluation).where(Evaluation.id == evaluation_id)
                if db.bind and db.bind.dialect.name != "sqlite":
                    stmt = stmt.with_for_update()

                res = await db.execute(stmt)
                evaluation = res.scalar_one_or_none()

                if not evaluation:
                    raise ValueError(f"Evaluation '{evaluation_id}' not found during completion transaction.")

                # Check if evaluation was cancelled concurrently while engine was computing
                if evaluation.status == EvaluationStatus.CANCELLED.value:
                    logger.warning(f"Evaluation '{evaluation_id}' was cancelled while executing. Skipping completion.")
                    return evaluation

                # If evaluation was already completed concurrently by another task, return safely
                if evaluation.status == EvaluationStatus.COMPLETED.value:
                    logger.info(f"Evaluation '{evaluation_id}' was already completed concurrently.")
                    return evaluation

                old_status = evaluation.status
                validate_transition(old_status, EvaluationStatus.COMPLETED.value)

                evaluation.result_payload = result_payload
                evaluation.provider = result_payload.get("metadata", {}).get("provider", "deterministic-engine-v2.6")
                evaluation.model = result_payload.get("metadata", {}).get("model", "rule-based-v2.6")
                evaluation.status = EvaluationStatus.COMPLETED.value
                evaluation.progress = EvaluationProgress.COMPLETED.value
                evaluation.completed_at = datetime.now(timezone.utc)
                evaluation.duration_ms = duration_ms
                evaluation.error_message = None

                # PRODUCT-01 P-13: persist measured usage and cost onto the typed
                # columns that already exist for them, instead of leaving them NULL
                # and forcing analytics to scrape result_payload. Values are only
                # written when the provider actually reported them — never invented.
                _meta = result_payload.get("metadata", {}) or {}
                _tokens = _meta.get("token_usage")
                if isinstance(_tokens, (int, float)) and not isinstance(_tokens, bool):
                    evaluation.token_usage = int(_tokens)
                _cost = _meta.get("estimated_cost")
                if isinstance(_cost, (int, float)) and not isinstance(_cost, bool):
                    evaluation.estimated_cost = float(_cost)

                await cls.record_history_event(
                    db=db,
                    evaluation_id=evaluation_id,
                    event_type="COMPLETED",
                    from_status=old_status,
                    to_status=EvaluationStatus.COMPLETED.value,
                    progress=EvaluationProgress.COMPLETED.value,
                    message=f"Evaluation completed successfully in {duration_ms}ms.",
                )

        logger.info(f"Evaluation '{evaluation_id}' marked COMPLETED. DB Tx 2 committed.")
        
        async with AsyncSessionLocal() as db:
            final_res = await db.execute(select(Evaluation).where(Evaluation.id == evaluation_id))
            return final_res.scalar_one()

    @classmethod
    async def _handle_execution_failure(
        cls, evaluation_id: str, error_message: str, duration_ms: int
    ) -> Evaluation:
        """Persists failure state safely in a dedicated database transaction."""
        safe_error = error_message.split("\n")[0][:500] if error_message else "Evaluation execution failed."

        async with AsyncSessionLocal() as db:
            async with db.begin():
                stmt = select(Evaluation).where(Evaluation.id == evaluation_id)
                if db.bind and db.bind.dialect.name != "sqlite":
                    stmt = stmt.with_for_update()

                res = await db.execute(stmt)
                evaluation = res.scalar_one_or_none()

                if evaluation:
                    old_status = evaluation.status
                    evaluation.status = EvaluationStatus.FAILED.value
                    evaluation.progress = EvaluationProgress.FAILED.value
                    evaluation.error_message = safe_error
                    evaluation.completed_at = datetime.now(timezone.utc)
                    evaluation.duration_ms = duration_ms

                    await cls.record_history_event(
                        db=db,
                        evaluation_id=evaluation_id,
                        event_type="FAILED",
                        from_status=old_status,
                        to_status=EvaluationStatus.FAILED.value,
                        progress=EvaluationProgress.FAILED.value,
                        message=f"Evaluation failed: {safe_error}",
                    )

        logger.info(f"Evaluation '{evaluation_id}' marked FAILED in DB transaction.")

        async with AsyncSessionLocal() as db:
            final_res = await db.execute(select(Evaluation).where(Evaluation.id == evaluation_id))
            return final_res.scalar_one()
