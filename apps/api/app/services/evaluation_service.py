import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.models.evaluation import Evaluation
from app.models.idea import Idea
from app.evaluation.coordinator import EvaluationCoordinator

logger = logging.getLogger(__name__)

class EvaluationService:
    async def _verify_idea_ownership(self, db: AsyncSession, idea_id: str, user_id: int) -> Idea:
        return await EvaluationCoordinator.verify_idea_ownership(db, idea_id, user_id)

    async def get_evaluation(self, db: AsyncSession, evaluation_id: str, user_id: int) -> Evaluation:
        return await EvaluationCoordinator.get_evaluation(db, evaluation_id, user_id)

    async def list_idea_evaluations(self, db: AsyncSession, idea_id: str, user_id: int) -> List[Evaluation]:
        await EvaluationCoordinator.verify_idea_ownership(db, idea_id, user_id)
        result = await db.execute(
            select(Evaluation).where(Evaluation.idea_id == idea_id).order_by(Evaluation.created_at.desc())
        )
        return result.scalars().all()

    async def list_project_evaluations(self, db: AsyncSession, project_id: str, user_id: int) -> List[Evaluation]:
        return await EvaluationCoordinator.list_project_evaluations(db, project_id, user_id)

    async def trigger_evaluation(self, db: AsyncSession, idea_id: str, evaluation_type: str, user_id: int) -> Evaluation:
        evaluation = await EvaluationCoordinator.create_evaluation(db, idea_id, evaluation_type, user_id)
        # Execute deterministic pipeline
        return await EvaluationCoordinator.run_evaluation(db, evaluation.id, user_id)

    async def run_evaluation(self, db: AsyncSession, evaluation_id: str, user_id: int) -> Evaluation:
        return await EvaluationCoordinator.run_evaluation(db, evaluation_id, user_id)

    async def retry_evaluation(self, db: AsyncSession, evaluation_id: str, user_id: int) -> Evaluation:
        return await EvaluationCoordinator.retry_evaluation(db, evaluation_id, user_id)

    async def cancel_evaluation(self, db: AsyncSession, evaluation_id: str, user_id: int) -> Evaluation:
        return await EvaluationCoordinator.cancel_evaluation(db, evaluation_id, user_id)

    async def delete_evaluation(self, db: AsyncSession, evaluation_id: str, user_id: int) -> dict:
        return await EvaluationCoordinator.delete_evaluation(db, evaluation_id, user_id)

    async def get_history(self, db: AsyncSession, evaluation_id: str, user_id: int):
        return await EvaluationCoordinator.get_evaluation_history(db, evaluation_id, user_id)

evaluation_service = EvaluationService()
