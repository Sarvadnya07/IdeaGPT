from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.session import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.schemas.evaluation_schema import EvaluationJobResponse
from app.services.evaluation_service import evaluation_service

router = APIRouter()

@router.post("/projects/{project_id}/evaluate", response_model=EvaluationJobResponse)
async def trigger_evaluation(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await evaluation_service.trigger_evaluation(db, project_id, current_user.id)

@router.get("/evaluations/{job_id}/status", response_model=EvaluationJobResponse)
async def get_evaluation_status(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await evaluation_service.get_job_status(db, job_id, current_user.id)

@router.post("/evaluations/{job_id}/retry", response_model=EvaluationJobResponse)
async def retry_evaluation(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    job = await evaluation_service.get_job_status(db, job_id, current_user.id)
    # Relaunch pipeline
    return await evaluation_service.trigger_evaluation(db, job.idea.project_id, current_user.id)
