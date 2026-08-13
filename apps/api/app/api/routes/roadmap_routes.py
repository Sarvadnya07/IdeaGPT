from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.roadmap_schema import RoadmapCreate, RoadmapUpdate, RoadmapResponse
from app.services.roadmap_service import roadmap_service

router = APIRouter()

@router.post("/projects/{project_id}/roadmaps", response_model=RoadmapResponse)
async def create_roadmap(
    project_id: str,
    roadmap_in: RoadmapCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    return await roadmap_service.create_roadmap(db, project_id, roadmap_in, user_id)

@router.get("/projects/{project_id}/roadmaps", response_model=List[RoadmapResponse])
async def get_project_roadmaps(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    return await roadmap_service.get_project_roadmaps(db, project_id, user_id)

@router.get("/roadmaps/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap(
    roadmap_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    return await roadmap_service.get_roadmap(db, roadmap_id, user_id)

@router.patch("/roadmaps/{roadmap_id}", response_model=RoadmapResponse)
async def update_roadmap(
    roadmap_id: str,
    roadmap_in: RoadmapUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    return await roadmap_service.update_roadmap(db, roadmap_id, roadmap_in, user_id)

@router.delete("/roadmaps/{roadmap_id}")
async def delete_roadmap(
    roadmap_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    return await roadmap_service.delete_roadmap(db, roadmap_id, user_id)
