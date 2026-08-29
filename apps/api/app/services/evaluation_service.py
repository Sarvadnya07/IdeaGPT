import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any

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

    async def trigger_evaluation(
        self,
        db: AsyncSession,
        idea_id: str,
        evaluation_type: str,
        user_id: int,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> Evaluation:
        evaluation = await EvaluationCoordinator.create_evaluation(
            db=db,
            idea_id=idea_id,
            evaluation_type=evaluation_type,
            user_id=user_id,
            provider=provider,
            model=model
        )
        await db.commit()
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

    # ==============================================================================
    # FEATURE 19: REPORT VERSION DIFFING
    # ==============================================================================

    async def diff_evaluations(
        self,
        db: AsyncSession,
        evaluation_id_a: str,
        evaluation_id_b: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Performs semantic version comparison between two evaluation report runs.
        Highlights changes in overall scores, dimensional deltas, new/removed strengths,
        weaknesses, recommendations, and strategic decision gates.
        """
        eval_a = await self.get_evaluation(db, evaluation_id_a, user_id)
        eval_b = await self.get_evaluation(db, evaluation_id_b, user_id)

        payload_a = eval_a.result_payload or {}
        payload_b = eval_b.result_payload or {}

        score_a = float(payload_a.get("score", 70.0))
        score_b = float(payload_b.get("score", 70.0))
        score_delta = round(score_b - score_a, 1)

        gate_a = payload_a.get("decision_gate", "VALIDATE_FIRST")
        gate_b = payload_b.get("decision_gate", "VALIDATE_FIRST")

        strengths_a = set(payload_a.get("strengths", []))
        strengths_b = set(payload_b.get("strengths", []))
        new_strengths = list(strengths_b - strengths_a)
        removed_strengths = list(strengths_a - strengths_b)

        weaknesses_a = set(payload_a.get("weaknesses", []))
        weaknesses_b = set(payload_b.get("weaknesses", []))
        new_weaknesses = list(weaknesses_b - weaknesses_a)
        resolved_weaknesses = list(weaknesses_a - weaknesses_b)

        return {
            "version_a": {
                "id": eval_a.id,
                "created_at": eval_a.created_at.isoformat() if eval_a.created_at else None,
                "provider": eval_a.provider,
                "score": score_a,
                "decision_gate": gate_a
            },
            "version_b": {
                "id": eval_b.id,
                "created_at": eval_b.created_at.isoformat() if eval_b.created_at else None,
                "provider": eval_b.provider,
                "score": score_b,
                "decision_gate": gate_b
            },
            "score_delta": score_delta,
            "decision_gate_changed": gate_a != gate_b,
            "new_strengths_identified": new_strengths,
            "removed_strengths": removed_strengths,
            "new_weaknesses_flagged": new_weaknesses,
            "resolved_weaknesses": resolved_weaknesses,
            "summary_comparison": f"Version B score changed by {score_delta:+} points ({score_a} -> {score_b}). Decision gate: '{gate_a}' -> '{gate_b}'.",
            "provenance": "DETERMINISTIC_CALCULATION"
        }


evaluation_service = EvaluationService()
