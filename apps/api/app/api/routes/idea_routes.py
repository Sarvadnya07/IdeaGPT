from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.session import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.schemas.idea_schema import IdeaUpdate, IdeaResponse
from app.services.idea_service import idea_service

router = APIRouter()

@router.get("/{project_id}/idea", response_model=IdeaResponse)
async def get_idea(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    idea = await idea_service.get_idea_by_project(db, project_id, current_user.id)
    if not idea:
        # Return empty but successful 200, or let the frontend know it's empty
        return {"project_id": project_id}
    return idea

@router.post("/{project_id}/idea", response_model=IdeaResponse)
async def save_idea(
    project_id: int,
    payload: IdeaUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await idea_service.save_idea(db, project_id, payload, current_user.id)
