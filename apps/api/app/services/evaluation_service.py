import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import traceback
import uuid
from datetime import datetime

from app.models.evaluation import Evaluation
from app.models.idea import Idea
from app.models.project import Project
from app.db.session import AsyncSessionLocal
from app.ai import orchestrator

logger = logging.getLogger(__name__)

class EvaluationService:
    async def _verify_idea_ownership(self, db: AsyncSession, idea_id: str, user_id: int) -> Idea:
        # Fetch idea
        result = await db.execute(select(Idea).where(Idea.id == idea_id))
        idea = result.scalar_one_or_none()
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")

        # Fetch parent project to verify ownership
        proj_result = await db.execute(
            select(Project).where(Project.id == idea.project_id, Project.user_id == user_id, Project.deleted_at.is_(None))
        )
        project = proj_result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=403, detail="Access denied to this project's ideas")
        
        return idea

    async def get_evaluation(self, db: AsyncSession, evaluation_id: str, user_id: int) -> Evaluation:
        result = await db.execute(select(Evaluation).where(Evaluation.id == evaluation_id))
        evaluation = result.scalar_one_or_none()
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        await self._verify_idea_ownership(db, evaluation.idea_id, user_id)
        return evaluation

    async def list_idea_evaluations(self, db: AsyncSession, idea_id: str, user_id: int):
        await self._verify_idea_ownership(db, idea_id, user_id)
        result = await db.execute(
            select(Evaluation).where(Evaluation.idea_id == idea_id).order_by(Evaluation.created_at.desc())
        )
        return result.scalars().all()

    async def trigger_evaluation(self, db: AsyncSession, idea_id: str, evaluation_type: str, user_id: int):
        idea = await self._verify_idea_ownership(db, idea_id, user_id)

        # Check if an evaluation is already running
        existing_res = await db.execute(
            select(Evaluation).where(
                Evaluation.idea_id == idea_id,
                Evaluation.status.in_(["PENDING", "QUEUED", "RUNNING"])
            )
        )
        if existing_res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Evaluation job already in progress")

        # Create evaluation record
        evaluation = Evaluation(
            id=str(uuid.uuid4()),
            project_id=idea.project_id,
            idea_id=idea_id,
            evaluation_type=evaluation_type,
            status="QUEUED",
            progress="QUEUED"
        )
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)

        # Dispatch Celery Task
        from app.workers.evaluation_worker import run_evaluation_task
        run_evaluation_task.delay(evaluation.id)

        return evaluation

    async def retry_evaluation(self, db: AsyncSession, evaluation_id: str, user_id: int):
        evaluation = await self.get_evaluation(db, evaluation_id, user_id)

        if evaluation.status not in ["FAILED", "CANCELLED", "EXPIRED"]:
            raise HTTPException(status_code=400, detail="Only failed, cancelled, or expired jobs can be retried")

        evaluation.status = "QUEUED"
        evaluation.progress = "QUEUED"
        evaluation.started_at = None
        evaluation.completed_at = None
        evaluation.error_message = None
        
        db.add(evaluation)
        await db.commit()

        # Re-dispatch Celery Task
        from app.workers.evaluation_worker import run_evaluation_task
        run_evaluation_task.delay(evaluation.id)

        return evaluation

    async def cancel_evaluation(self, db: AsyncSession, evaluation_id: str, user_id: int):
        evaluation = await self.get_evaluation(db, evaluation_id, user_id)

        if evaluation.status not in ["PENDING", "QUEUED", "RUNNING"]:
            raise HTTPException(status_code=400, detail="Only active jobs can be cancelled")

        evaluation.status = "CANCELLED"
        evaluation.progress = "CANCELLED"
        evaluation.completed_at = func.now() if hasattr(func, "now") else datetime.utcnow()
        
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation

    async def delete_evaluation(self, db: AsyncSession, evaluation_id: str, user_id: int):
        evaluation = await self.get_evaluation(db, evaluation_id, user_id)
        await db.delete(evaluation)
        await db.commit()
        return {"status": "deleted"}

    def _build_prompt(self, idea: Idea) -> str:
        return f"""
        Analyze the following startup idea submission.
        
        Title: {idea.title}
        Problem: {idea.problem_statement}
        Solution: {idea.solution_description}
        Target Users: {idea.target_users}
        Industry: {idea.industry}
        Business Model: {idea.business_model}
        Stage: {idea.stage}
        Tags: {idea.tags}
        Notes: {idea.notes}
        
        Provide a structured JSON output with the following keys:
        - "score": A number out of 100 representing overall potential.
        - "strengths": Array of strings.
        - "weaknesses": Array of strings.
        - "market_analysis": A short paragraph.
        - "recommendations": Array of strings.
        - "architecture_breakdown": Markdown string detailing technical feasibility and system architecture recommendations.
        """

evaluation_service = EvaluationService()
