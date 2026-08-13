from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.models.idea import Idea
from app.models.project import Project
from app.models.evaluation import Evaluation
from app.schemas.evaluation_schema import IdeaComparisonResponse, IdeaComparisonItem

class ComparisonService:
    @staticmethod
    def _calculate_completeness(idea: Idea) -> int:
        """
        Calculates deterministic completeness score (0-100%) based on filled idea fields.
        """
        weights = [
            (bool(idea.title and len(idea.title.strip()) > 0), 15),
            (bool(idea.problem_statement and len(idea.problem_statement.strip()) > 10), 20),
            (bool(idea.solution_description and len(idea.solution_description.strip()) > 10), 20),
            (bool(idea.target_users and len(idea.target_users.strip()) > 0), 10),
            (bool(idea.industry and len(idea.industry.strip()) > 0), 10),
            (bool(idea.business_model and len(idea.business_model.strip()) > 0), 10),
            (bool(idea.stage and len(idea.stage.strip()) > 0), 10),
            (bool(idea.tags and len(idea.tags.strip()) > 0), 5),
        ]
        return sum(w for condition, w in weights if condition)

    async def compare_ideas(
        self,
        db: AsyncSession,
        user_id: int,
        idea_ids: List[str]
    ) -> IdeaComparisonResponse:
        """
        Compares 2-5 user-owned ideas using persisted evaluation scores and deterministic metadata.
        Enforces Safeguard Phase 8.1.3 (Ownership Boundary).
        """
        if not idea_ids or len(idea_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 ideas must be selected for comparison."
            )

        if len(idea_ids) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A maximum of 5 ideas can be compared at once."
            )

        if len(set(idea_ids)) != len(idea_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate idea IDs in selection."
            )

        # Enforce Ownership Security Matrix
        stmt = (
            select(Idea, Project)
            .join(Project, Idea.project_id == Project.id)
            .where(
                and_(
                    Idea.id.in_(idea_ids),
                    Project.user_id == user_id,
                    Project.deleted_at.is_(None)
                )
            )
        )
        res = await db.execute(stmt)
        rows = res.all()

        if len(rows) != len(idea_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="One or more selected ideas do not exist or access is denied."
            )

        # Maintain original request order
        idea_map = {str(idea.id): idea for idea, _ in rows}
        ordered_ideas = [idea_map[i_id] for i_id in idea_ids if i_id in idea_map]

        # Fetch latest completed evaluation for each idea
        eval_stmt = (
            select(Evaluation)
            .where(
                and_(
                    Evaluation.idea_id.in_(idea_ids),
                    Evaluation.status == "COMPLETED"
                )
            )
            .order_by(Evaluation.created_at.desc())
        )
        eval_res = await db.execute(eval_stmt)
        all_evals = eval_res.scalars().all()

        # Group latest evaluation by idea_id
        latest_eval_map: Dict[str, Evaluation] = {}
        for ev in all_evals:
            if ev.idea_id not in latest_eval_map:
                latest_eval_map[ev.idea_id] = ev

        # Extract scores and rank evaluated ideas
        evaluated_scores = []
        for i_id, ev in latest_eval_map.items():
            payload = ev.result_payload or {}
            score = payload.get("score")
            if score is not None:
                evaluated_scores.append((i_id, score))

        top_score = None
        top_idea_id = None
        score_rankings = {}

        if evaluated_scores:
            # Sort by score descending
            evaluated_scores.sort(key=lambda x: x[1], reverse=True)
            top_idea_id = evaluated_scores[0][0]
            top_score = evaluated_scores[0][1]

            for rank, (i_id, score) in enumerate(evaluated_scores, start=1):
                score_rankings[i_id] = {
                    "rank": rank,
                    "delta": score - top_score
                }

        # Build comparison items
        comparison_items = []
        for idea in ordered_ideas:
            i_id = str(idea.id)
            ev = latest_eval_map.get(i_id)
            completeness = self._calculate_completeness(idea)

            if ev and ev.result_payload:
                payload = ev.result_payload
                dims = payload.get("dimensions", {})
                score = payload.get("score")
                ranking_info = score_rankings.get(i_id, {})

                comparison_items.append(
                    IdeaComparisonItem(
                        idea_id=i_id,
                        project_id=str(idea.project_id),
                        title=idea.title,
                        problem_statement=idea.problem_statement,
                        solution_description=idea.solution_description,
                        target_users=idea.target_users,
                        industry=idea.industry,
                        business_model=idea.business_model,
                        stage=idea.stage,
                        tags=idea.tags,
                        completeness_score=completeness,
                        evaluation_status="evaluated",
                        evaluation_id=str(ev.id),
                        overall_score=score,
                        score_delta=ranking_info.get("delta"),
                        rank=ranking_info.get("rank"),
                        dimensions={
                            "innovation": dims.get("innovation", 0),
                            "market_potential": dims.get("market_potential", 0),
                            "execution_complexity": dims.get("execution_complexity", 0),
                            "technical_feasibility": dims.get("technical_feasibility", 0),
                            "business_viability": dims.get("business_viability", 0),
                            "scalability": dims.get("scalability", 0),
                            "competitive_differentiation": dims.get("competitive_differentiation", 0)
                        },
                        evaluated_at=ev.completed_at.isoformat() if ev.completed_at else (ev.created_at.isoformat() if ev.created_at else None)
                    )
                )
            else:
                # Unevaluated Truthful Response
                comparison_items.append(
                    IdeaComparisonItem(
                        idea_id=i_id,
                        project_id=str(idea.project_id),
                        title=idea.title,
                        problem_statement=idea.problem_statement,
                        solution_description=idea.solution_description,
                        target_users=idea.target_users,
                        industry=idea.industry,
                        business_model=idea.business_model,
                        stage=idea.stage,
                        tags=idea.tags,
                        completeness_score=completeness,
                        evaluation_status="unevaluated",
                        evaluation_id=None,
                        overall_score=None,
                        score_delta=None,
                        rank=None,
                        dimensions={},
                        evaluated_at=None
                    )
                )

        return IdeaComparisonResponse(
            compared_count=len(comparison_items),
            highest_score_idea_id=top_idea_id,
            ideas=comparison_items
        )

comparison_service = ComparisonService()
