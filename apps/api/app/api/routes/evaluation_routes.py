from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from app.db.session import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.schemas.evaluation_schema import EvaluationResponse, EvaluationCreate
from app.services.evaluation_service import evaluation_service

router = APIRouter()

@router.post("/ideas/{idea_id}/evaluations", response_model=EvaluationResponse)
async def trigger_evaluation(
    idea_id: str,
    payload: EvaluationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
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
