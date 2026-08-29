from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.roadmap_schema import RoadmapCreate, RoadmapUpdate, RoadmapResponse
from app.services.roadmap_service import roadmap_service

router = APIRouter()


class CustomTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    phase: str = Field(default="MVP", max_length=50)
    priority: str = Field(default="HIGH", max_length=20)
    estimated_days: int = Field(default=3, ge=1, le=180)
    dependencies: Optional[List[str]] = Field(default_factory=list)
    milestone_title: Optional[str] = None


class TaskStatusUpdateRequest(BaseModel):
    status: str = Field(pattern="^(PENDING|IN_PROGRESS|COMPLETED)$")


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


# ==============================================================================
# FEATURE 26: CUSTOM TASK ADDITION & STATUS MANAGEMENT
# ==============================================================================

@router.post("/roadmaps/{roadmap_id}/tasks", summary="Add custom milestone task to roadmap")
async def add_custom_task(
    roadmap_id: str,
    payload: CustomTaskRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await roadmap_service.add_custom_task(
        db=db,
        roadmap_id=roadmap_id,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        phase=payload.phase,
        priority=payload.priority,
        estimated_days=payload.estimated_days,
        dependencies=payload.dependencies,
        milestone_title=payload.milestone_title
    )


@router.put("/roadmaps/{roadmap_id}/tasks/{task_id}/status", summary="Update roadmap task status (PENDING | IN_PROGRESS | COMPLETED)")
async def update_task_status(
    roadmap_id: str,
    task_id: str,
    payload: TaskStatusUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await roadmap_service.update_task_status(
        db=db,
        roadmap_id=roadmap_id,
        task_id=task_id,
        new_status=payload.status,
        user_id=current_user.id
    )


# ==============================================================================
# FEATURE 25: CRITICAL PATH HIGHLIGHTING
# ==============================================================================

@router.get("/roadmaps/{roadmap_id}/critical-path", summary="Analyze roadmap dependency graph and compute critical chain")
async def get_critical_path(
    roadmap_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await roadmap_service.get_critical_path(
        db=db,
        roadmap_id=roadmap_id,
        user_id=current_user.id
    )
