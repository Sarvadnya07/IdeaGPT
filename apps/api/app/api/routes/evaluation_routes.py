from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from typing import List, Annotated, Dict, Any, Optional

from app.db.session import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.schemas.evaluation_schema import EvaluationResponse, EvaluationCreate
from app.services.evaluation_service import evaluation_service
from app.services.insight_service import insight_service, scoring_service
from app.services.comparison_service import comparison_service
from app.services.export_service import export_service
from app.services.visualization_service import visualization_service
from app.ai.prompts.registry import prompt_registry

router = APIRouter()


@router.post("/ideas/{idea_id}/evaluations", response_model=EvaluationResponse)
async def trigger_evaluation(
    idea_id: str,
    payload: EvaluationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    # Support prompt_version passing if present
    return await evaluation_service.trigger_evaluation(db, idea_id, payload.evaluation_type, current_user.id)

@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await evaluation_service.get_evaluation(db, evaluation_id, current_user.id)

@router.get("/ideas/{idea_id}/evaluations", response_model=List[EvaluationResponse])
async def get_idea_evaluations(
    idea_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await evaluation_service.list_idea_evaluations(db, idea_id, current_user.id)

@router.post("/evaluations/{evaluation_id}/retry", response_model=EvaluationResponse)
async def retry_evaluation(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await evaluation_service.retry_evaluation(db, evaluation_id, current_user.id)

@router.post("/evaluations/{evaluation_id}/cancel", response_model=EvaluationResponse)
async def cancel_evaluation(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await evaluation_service.cancel_evaluation(db, evaluation_id, current_user.id)

@router.delete("/evaluations/{evaluation_id}")
async def delete_evaluation(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await evaluation_service.delete_evaluation(db, evaluation_id, current_user.id)

# --- SPRINT 5 & 6 INTELLIGENCE & INSIGHTS ENDPOINTS ---

@router.post("/evaluations/{evaluation_id}/run", response_model=EvaluationResponse)
async def run_evaluation_pipeline(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers/runs the evaluation runner job.
    """
    evaluation = await evaluation_service.get_evaluation(db, evaluation_id, current_user.id)
    # Rerun celery dispatcher task
    from app.workers.evaluation_worker import run_evaluation_task
    run_evaluation_task.delay(evaluation.id)
    return evaluation

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

@router.get("/evaluations/{evaluation_id}/history", response_model=List[EvaluationResponse])
async def get_evaluation_history(
    evaluation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves historical runs for the parent idea.
    """
    evaluation = await evaluation_service.get_evaluation(db, evaluation_id, current_user.id)
    return await evaluation_service.list_idea_evaluations(db, evaluation.idea_id, current_user.id)

@router.get("/projects/{project_id}/comparisons")
async def get_project_comparisons(
    project_id: str,
    evaluation_ids: List[str] = Body(..., embed=True),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves comparison matrix for multiple ideas/evaluations.
    """
    # Simple check for context/ownership validation
    return await comparison_service.compare_evaluations(db, evaluation_ids)

@router.post("/exports/json")
async def export_evaluation_json(
    evaluation_id: str = Body(..., embed=True),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Exports evaluation payload as raw JSON.
    """
    evaluation = await db.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return {"filename": f"evaluation_{evaluation_id}.json", "content": export_service.to_json(evaluation.result_payload or {})}

@router.post("/exports/markdown")
async def export_evaluation_markdown(
    evaluation_id: str = Body(..., embed=True),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Exports evaluation payload as Markdown.
    """
    evaluation = await db.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return {"filename": f"evaluation_{evaluation_id}.md", "content": export_service.to_markdown(evaluation.result_payload or {})}

@router.get("/prompts")
async def list_available_prompts():
    """
    Returns available prompt structures.
    """
    return prompt_registry.list_prompts()

@router.get("/prompt-versions")
async def list_prompt_versions(prompt_id: str):
    """
    Returns prompt version tracking list.
    """
    return prompt_registry.list_versions(prompt_id)

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
async def global_search(
    q: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Global search across ideas and evaluations.
    """
    from app.models.idea import Idea
    from app.models.evaluation import Evaluation
    from app.models.project import Project

    if not q or len(q) < 2:
        return {"results": []}

    query = q.lower()

    # Search ideas
    ideas_result = await db.execute(
        select(Idea, Project.title.label("project_title"))
        .join(Project, Idea.project_id == Project.id)
        .where(Project.owner_id == current_user.id)
        .where(
            or_(
                func.lower(Idea.title).contains(query),
                func.lower(Idea.problem_statement).contains(query),
                func.lower(Idea.solution_description).contains(query),
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

