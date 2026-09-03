from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from app.db.session import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.schemas.idea_schema import IdeaCreate, IdeaUpdate, IdeaResponse
from app.services.idea_service import idea_service

router = APIRouter()

@router.post("/projects/{project_id}/ideas", response_model=IdeaResponse, status_code=201)
async def create_idea(
    project_id: str,
    payload: IdeaCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await idea_service.create_idea(db, project_id, payload, current_user.id)

@router.get("/projects/{project_id}/ideas", response_model=List[IdeaResponse])
async def get_project_ideas(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await idea_service.get_project_ideas(db, project_id, current_user.id)

@router.get("/ideas/{idea_id}", response_model=IdeaResponse)
async def get_idea(
    idea_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await idea_service.get_idea(db, idea_id, current_user.id)

@router.patch("/ideas/{idea_id}", response_model=IdeaResponse)
async def update_idea(
    idea_id: str,
    payload: IdeaUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await idea_service.update_idea(db, idea_id, payload, current_user.id)

@router.delete("/ideas/{idea_id}")
async def delete_idea(
    idea_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await idea_service.delete_idea(db, idea_id, current_user.id)

@router.post("/ideas/{idea_id}/duplicate", response_model=IdeaResponse, status_code=201)
async def duplicate_idea(
    idea_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await idea_service.duplicate_idea(db, idea_id, current_user.id)
