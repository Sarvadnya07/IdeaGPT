import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models.evaluation import Evaluation
from app.models.evaluation_history import EvaluationHistory
from app.models.idea import Idea
from app.models.project import Project
from app.evaluation.state import (
    EvaluationStatus,
    EvaluationProgress,
    validate_transition,
    InvalidStateTransitionError,
    EvaluationConcurrencyConflictError,
)
from app.evaluation.executor import EvaluationExecutor

logger = logging.getLogger(__name__)


class EvaluationCoordinator:
    """
    Primary Orchestration Boundary for Evaluation Lifecycle Operations.
    Centralized validation, ownership isolation, idempotency, retries,
    cancellation, event auditing, and stale job recovery.
    """

    @classmethod
    async def verify_idea_ownership(cls, db: AsyncSession, idea_id: str, user_id: int) -> Idea:
        """Verifies user ownership of an idea via parent project."""
        res_idea = await db.execute(select(Idea).where(Idea.id == idea_id))
        idea = res_idea.scalar_one_or_none()
        if not idea:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")

        res_proj = await db.execute(
            select(Project).where(
                Project.id == idea.project_id,
                Project.user_id == user_id,
                Project.deleted_at.is_(None),
            )
        )
        project = res_proj.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project's ideas"
            )

        return idea

    @classmethod
    async def list_project_evaluations(cls, db: AsyncSession, project_id: str, user_id: int) -> List[Evaluation]:
        """Fetch all evaluations for a project across all statuses, enforcing user ownership isolation."""
        res_proj = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == user_id,
                Project.deleted_at.is_(None),
            )
        )
        project = res_proj.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied or project not found"
            )

        res_ideas = await db.execute(select(Idea.id).where(Idea.project_id == project_id))
        idea_ids = res_ideas.scalars().all()
        if not idea_ids:
            return []

        res_evals = await db.execute(
            select(Evaluation)
            .where(Evaluation.idea_id.in_(idea_ids))
            .order_by(Evaluation.created_at.desc())
        )
        # scalars().all() returns a Sequence; convert to list to satisfy return type List[Evaluation]
        return list(res_evals.scalars().all())

    @classmethod
    async def get_evaluation(cls, db: AsyncSession, evaluation_id: str, user_id: int) -> Evaluation:
        """Fetch evaluation and enforce strict user ownership isolation."""
        res = await db.execute(select(Evaluation).where(Evaluation.id == evaluation_id))
        evaluation = res.scalar_one_or_none()
        if not evaluation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")

        # Verify idea ownership
        await cls.verify_idea_ownership(db, evaluation.idea_id, user_id)
        return evaluation

    @classmethod
    async def create_evaluation(
        cls, db: AsyncSession, idea_id: str, evaluation_type: str, user_id: int
    ) -> Evaluation:
        """Creates a new evaluation record in PENDING state."""
        idea = await cls.verify_idea_ownership(db, idea_id, user_id)

        # Enforce single active evaluation per idea
        active_res = await db.execute(
            select(Evaluation).where(
                Evaluation.idea_id == idea_id,
                Evaluation.status.in_([EvaluationStatus.PENDING.value, EvaluationStatus.RUNNING.value, "QUEUED"]),
            )
        )
        existing_active = active_res.scalar_one_or_none()
        if existing_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active evaluation job '{existing_active.id}' is already in progress for this idea.",
            )

        evaluation = Evaluation(
            id=str(uuid.uuid4()),
            project_id=idea.project_id,
            idea_id=idea_id,
            evaluation_type=evaluation_type,
            status=EvaluationStatus.PENDING.value,
            progress=EvaluationProgress.PENDING.value,
            provider="deterministic-engine-v2.6",
            model="rule-based-v2.6",
            result_payload={},
        )
        db.add(evaluation)

        # Log CREATED history event
        await EvaluationExecutor.record_history_event(
            db=db,
            evaluation_id=evaluation.id,
            event_type="CREATED",
            from_status=None,
            to_status=EvaluationStatus.PENDING.value,
            progress=EvaluationProgress.PENDING.value,
            message="Evaluation job created in PENDING state",
        )

        await db.commit()
        await db.refresh(evaluation)
        return evaluation

    @classmethod
    async def run_evaluation(cls, db: AsyncSession, evaluation_id: str, user_id: int) -> Evaluation:
        """Runs the deterministic evaluation executor synchronously or task-based."""
        evaluation = await cls.get_evaluation(db, evaluation_id, user_id)

        if evaluation.status == EvaluationStatus.RUNNING.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Evaluation is currently running.",
            )

        if evaluation.status == EvaluationStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evaluation has already completed. Re-running a completed job is not permitted.",
            )

        if evaluation.status in [EvaluationStatus.FAILED.value, EvaluationStatus.CANCELLED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Evaluation is in '{evaluation.status}' state. Use the retry endpoint to run again.",
            )

        # Execute evaluation cleanly
        return await EvaluationExecutor.execute_evaluation(evaluation_id)

    @classmethod
    async def retry_evaluation(cls, db: AsyncSession, evaluation_id: str, user_id: int) -> Evaluation:
        """Retries a FAILED or CANCELLED evaluation job."""
        evaluation = await cls.get_evaluation(db, evaluation_id, user_id)

        if evaluation.status not in [EvaluationStatus.FAILED.value, EvaluationStatus.CANCELLED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only failed or cancelled jobs can be retried. Current status is '{evaluation.status}'.",
            )

        old_status = evaluation.status
        validate_transition(old_status, EvaluationStatus.PENDING.value)

        # Reset state to PENDING
        evaluation.status = EvaluationStatus.PENDING.value
        evaluation.progress = EvaluationProgress.PENDING.value
        evaluation.started_at = None
        evaluation.completed_at = None
        evaluation.error_message = None

        await EvaluationExecutor.record_history_event(
            db=db,
            evaluation_id=evaluation.id,
            event_type="RETRIED",
            from_status=old_status,
            to_status=EvaluationStatus.PENDING.value,
            progress=EvaluationProgress.PENDING.value,
            message=f"Evaluation retry initiated from '{old_status}' state",
        )

        await db.commit()
        await db.refresh(evaluation)

        # Re-execute evaluation
        return await EvaluationExecutor.execute_evaluation(evaluation.id)

    @classmethod
    async def cancel_evaluation(cls, db: AsyncSession, evaluation_id: str, user_id: int) -> Evaluation:
        """Cancels an active PENDING or RUNNING evaluation job."""
        evaluation = await cls.get_evaluation(db, evaluation_id, user_id)

        if evaluation.status not in [EvaluationStatus.PENDING.value, EvaluationStatus.RUNNING.value, "QUEUED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only active (PENDING or RUNNING) jobs can be cancelled. Current status is '{evaluation.status}'.",
            )

        old_status = evaluation.status
        validate_transition(old_status, EvaluationStatus.CANCELLED.value)

        evaluation.status = EvaluationStatus.CANCELLED.value
        evaluation.progress = EvaluationProgress.CANCELLED.value
        evaluation.completed_at = datetime.now(timezone.utc)

        await EvaluationExecutor.record_history_event(
            db=db,
            evaluation_id=evaluation.id,
            event_type="CANCELLED",
            from_status=old_status,
            to_status=EvaluationStatus.CANCELLED.value,
            progress=EvaluationProgress.CANCELLED.value,
            message="Evaluation job cancelled by user request",
        )

        await db.commit()
        await db.refresh(evaluation)
        return evaluation

    @classmethod
    async def delete_evaluation(cls, db: AsyncSession, evaluation_id: str, user_id: int) -> dict:
        """Deletes an evaluation record."""
        evaluation = await cls.get_evaluation(db, evaluation_id, user_id)
        await db.delete(evaluation)
        await db.commit()
        return {"status": "deleted", "id": evaluation_id}

    @classmethod
    async def get_evaluation_history(
        cls, db: AsyncSession, evaluation_id: str, user_id: int
    ) -> List[EvaluationHistory]:
        """Retrieves chronologically sorted lifecycle event history for an evaluation."""
        await cls.get_evaluation(db, evaluation_id, user_id)
        res = await db.execute(
            select(EvaluationHistory)
            .where(EvaluationHistory.evaluation_id == evaluation_id)
            .order_by(EvaluationHistory.created_at.asc())
        )
        # ensure a concrete list is returned to satisfy type List[EvaluationHistory]
        return list(res.scalars().all())

    @classmethod
    async def recover_stale_evaluations(
        cls, db: AsyncSession, threshold_seconds: int = 300
    ) -> int:
        """
        Stale Execution Recovery Strategy:
        Identifies RUNNING evaluations started before threshold_seconds ago,
        marking them FAILED due to process interruption or crash.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=threshold_seconds)
        stale_res = await db.execute(
            select(Evaluation).where(
                Evaluation.status == EvaluationStatus.RUNNING.value,
                Evaluation.started_at < cutoff,
            )
        )
        stale_evaluations = stale_res.scalars().all()

        recovered_count = 0
        for ev in stale_evaluations:
            old_status = ev.status
            ev.status = EvaluationStatus.FAILED.value
            ev.progress = EvaluationProgress.FAILED.value
            ev.error_message = (
                f"Execution timed out or system recovered from unexpected process restart (stale after {threshold_seconds}s)."
            )
            ev.completed_at = datetime.now(timezone.utc)

            await EvaluationExecutor.record_history_event(
                db=db,
                evaluation_id=ev.id,
                event_type="STALE_RECOVERY",
                from_status=old_status,
                to_status=EvaluationStatus.FAILED.value,
                progress=EvaluationProgress.FAILED.value,
                message=ev.error_message,
            )
            recovered_count += 1

        if recovered_count > 0:
            await db.commit()
            logger.info(f"Stale recovery strategy recovered {recovered_count} RUNNING evaluations.")

        return recovered_count
