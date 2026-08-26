from fastapi import APIRouter, Depends, HTTPException, Body, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from typing import List, Annotated, Dict, Any, Optional

from app.db.session import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.schemas.evaluation_schema import (
    EvaluationResponse,
    EvaluationCreate,
    EvaluationHistoryResponse,
    IdeaCompareRequest,
    IdeaComparisonResponse
)
from app.services.evaluation_service import evaluation_service
from app.services.project_service import project_service
from app.services.insight_service import insight_service, scoring_service
from app.services.comparison_service import comparison_service
from app.services.export_service import export_service
from app.services.visualization_service import visualization_service
from app.evaluation.coordinator import EvaluationCoordinator
from app.core.rate_limit import limiter
from app.core.config import settings

router = APIRouter()


@router.post("/ideas/{idea_id}/evaluations", response_model=EvaluationResponse)
@limiter.limit(settings.AI_EVALUATION_RATE_LIMIT)
async def trigger_evaluation(
    request: Request,
    idea_id: str,
    payload: EvaluationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Creates and executes an AI or deterministic evaluation job for an idea.
    """
    return await evaluation_service.trigger_evaluation(
        db=db,
        idea_id=idea_id,
        evaluation_type=payload.evaluation_type or "startup_evaluation",
        user_id=current_user.id,
        provider=payload.provider,
        model=payload.model
    )

@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves evaluation status and report payload.
    """
    return await evaluation_service.get_evaluation(db, evaluation_id, current_user.id)

@router.get("/ideas/{idea_id}/evaluations", response_model=List[EvaluationResponse])
async def get_idea_evaluations(
    idea_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all evaluation jobs for a specific idea.
    """
    return await evaluation_service.list_idea_evaluations(db, idea_id, current_user.id)

@router.get("/projects/{project_id}/evaluations", response_model=List[EvaluationResponse])
async def get_project_evaluations(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all evaluation jobs for all ideas in a specific project.
    """
    return await evaluation_service.list_project_evaluations(db, project_id, current_user.id)

@router.post("/evaluations/{evaluation_id}/retry", response_model=EvaluationResponse)
@limiter.limit(settings.AI_EVALUATION_RATE_LIMIT)
async def retry_evaluation(
    request: Request,
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Retries a FAILED or CANCELLED evaluation job.
    """
    return await evaluation_service.retry_evaluation(db, evaluation_id, current_user.id)

@router.post("/evaluations/{evaluation_id}/cancel", response_model=EvaluationResponse)
async def cancel_evaluation(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Cancels an active (PENDING or RUNNING) evaluation job.
    """
    return await evaluation_service.cancel_evaluation(db, evaluation_id, current_user.id)

@router.delete("/evaluations/{evaluation_id}")
async def delete_evaluation(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes an evaluation record.
    """
    return await evaluation_service.delete_evaluation(db, evaluation_id, current_user.id)

@router.post("/evaluations/{evaluation_id}/run", response_model=EvaluationResponse)
@limiter.limit(settings.AI_EVALUATION_RATE_LIMIT)
async def run_evaluation_pipeline(
    request: Request,
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers/runs the evaluation pipeline via EvaluationCoordinator.
    """
    return await evaluation_service.run_evaluation(db, evaluation_id, current_user.id)

@router.get("/evaluations/{evaluation_id}/insights")
async def get_evaluation_insights(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves granular structured insights (SWOT, Feasibility, etc.)
    """
    await evaluation_service.get_evaluation(db, evaluation_id, current_user.id)
    return await insight_service.get_insights(db, evaluation_id)

@router.get("/evaluations/{evaluation_id}/scores")
async def get_evaluation_scores(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves multi-dimensional analysis scores.
    """
    await evaluation_service.get_evaluation(db, evaluation_id, current_user.id)
    return await scoring_service.get_scores(db, evaluation_id)

@router.get("/evaluations/{evaluation_id}/history", response_model=List[EvaluationHistoryResponse])
async def get_evaluation_history(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves historical lifecycle audit events for an evaluation.
    """
    return await evaluation_service.get_history(db, evaluation_id, current_user.id)

@router.post("/evaluations/compare", response_model=IdeaComparisonResponse)
async def compare_ideas(
    payload: IdeaCompareRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Compares 2-5 user-owned ideas using real persisted data and evaluation metrics.
    Enforces user ownership isolation across all selected ideas.
    """
    return await comparison_service.compare_ideas(db, current_user.id, payload.idea_ids)

@router.get("/projects/{project_id}/comparisons")
async def get_project_comparisons(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    evaluation_ids: Optional[List[str]] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves comparison matrix for multiple ideas/evaluations.
    """
    await project_service.get_project(db, project_id, current_user.id)
    return await comparison_service.compare_evaluations(db, evaluation_ids)

@router.get("/evaluations/{evaluation_id}/export")
@limiter.limit("20/minute")
async def get_evaluation_export(
    request: Request,
    evaluation_id: str,
    format: str = Query("json", pattern="^(json|markdown|md)$", description="Export format: json or markdown"),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    RESTful GET export for evaluation payload as JSON or Markdown.
    """
    evaluation = await evaluation_service.get_evaluation(db, evaluation_id, current_user.id)
    payload = evaluation.result_payload or {}

    if format in ("markdown", "md"):
        return {
            "filename": f"evaluation_{evaluation_id}.md",
            "format": "markdown",
            "content": export_service.to_markdown(payload),
        }
    return {
        "filename": f"evaluation_{evaluation_id}.json",
        "format": "json",
        "content": export_service.to_json(payload),
    }

@router.post("/exports/json")
@limiter.limit("20/minute")
async def export_evaluation_json(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    evaluation_id: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """
    Exports evaluation payload as raw JSON.
    """
    evaluation = await evaluation_service.get_evaluation(db, evaluation_id, current_user.id)
    return {
        "filename": f"evaluation_{evaluation_id}.json",
        "content": export_service.to_json(evaluation.result_payload or {}),
    }

@router.post("/exports/markdown")
@limiter.limit("20/minute")
async def export_evaluation_markdown(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    evaluation_id: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """
    Exports evaluation payload as Markdown.
    """
    evaluation = await evaluation_service.get_evaluation(db, evaluation_id, current_user.id)
    return {
        "filename": f"evaluation_{evaluation_id}.md",
        "content": export_service.to_markdown(evaluation.result_payload or {}),
    }

@router.get("/evaluations/{evaluation_id}/charts")
async def get_evaluation_charts(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Returns chart-ready visualization data for radar, bar, and risk heatmap.
    """
    await evaluation_service.get_evaluation(db, evaluation_id, current_user.id)
    return await visualization_service.get_chart_data(db, evaluation_id)

@router.get("/search")
@limiter.limit("30/minute")
async def global_search(
    request: Request,
    q: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Global search across ideas and evaluations scoped to current_user.
    """
    from app.models.idea import Idea
    from app.models.project import Project

    if not q or len(q) < 2:
        return {"results": []}

    query = q.lower()

    ideas_result = await db.execute(
        select(Idea, Project.title.label("project_title"))
        .join(Project, Idea.project_id == Project.id)
        .where(Project.user_id == current_user.id, Project.deleted_at.is_(None))
        .where(
            or_(
                func.lower(Idea.title).contains(query),
                func.lower(Idea.problem_statement).contains(query),
                func.lower(Idea.solution_description).contains(query),
                func.lower(Idea.tags).contains(query),
            )
        )
        .limit(10)
    )
    idea_rows = ideas_result.all()

    results = []
    for idea, project_title in idea_rows:
        results.append({
            "type": "idea",
            "id": str(idea.id),
            "title": idea.title or "Untitled Idea",
            "description": (idea.problem_statement or "")[:120],
            "project_title": project_title,
            "url": f"/projects/{idea.project_id}/idea",
        })

    return {"results": results, "count": len(results), "query": q}
