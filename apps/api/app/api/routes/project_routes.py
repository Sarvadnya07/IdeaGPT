from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from app.db.session import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectResponse, PaginatedProjectResponse
from app.services.project_service import project_service

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    payload: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await project_service.create_project(db, payload, current_user.id)

@router.get("/", response_model=PaginatedProjectResponse)
async def get_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100, description="Page size limit (1-100)"),
    offset: int = Query(0, ge=0, description="Page offset"),
    search: str = None,
    category: str = None,
    is_archived: bool = False,
    is_pinned: bool = None,
    sort_by: str = "newest"
):
    return await project_service.get_user_projects(db, current_user.id, limit, offset, search, category, is_archived, is_pinned, sort_by)

@router.post("/{project_id}/duplicate", response_model=ProjectResponse, status_code=201)
async def duplicate_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await project_service.duplicate_project(db, project_id, current_user.id)
 
@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await project_service.get_project(db, project_id, current_user.id)
 
@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await project_service.update_project(db, project_id, payload, current_user.id)
 
@router.patch("/{project_id}/pin", response_model=ProjectResponse)
async def pin_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    project = await project_service.get_project(db, project_id, current_user.id)
    update_data = ProjectUpdate(is_pinned=not project.is_pinned)
    return await project_service.update_project(db, project_id, update_data, current_user.id)
 
@router.patch("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    project = await project_service.get_project(db, project_id, current_user.id)
    update_data = ProjectUpdate(is_archived=not project.is_archived)
    return await project_service.update_project(db, project_id, update_data, current_user.id)
 
@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    return await project_service.delete_project(db, project_id, current_user.id)
