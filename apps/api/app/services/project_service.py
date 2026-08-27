from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
import uuid
import re
import logging

from app.models.project import Project
from app.models.user import User
from app.schemas.project_schema import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)

def _generate_slug(title: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    if not slug:
        slug = "project"
    random_suffix = str(uuid.uuid4())[:8]
    return f"{slug}-{random_suffix}"

class ProjectService:
    async def get_user_projects(self, db: AsyncSession, user_id: int, limit: int = 50, offset: int = 0, search: str = None, category: str = None, is_archived: bool = False, is_pinned: bool = None, sort_by: str = "newest"):
        query = select(Project).where(Project.user_id == user_id, Project.deleted_at.is_(None))
        
        if search:
            escaped_search = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            query = query.where(Project.title.ilike(f"%{escaped_search}%", escape="\\"))
        if category:
            query = query.where(Project.category == category)
        if is_archived is not None:
            query = query.where(Project.is_archived == is_archived)
        if is_pinned is not None:
            query = query.where(Project.is_pinned == is_pinned)
            
        if sort_by == "oldest":
            query = query.order_by(Project.created_at.asc())
        elif sort_by == "alphabetical":
            query = query.order_by(Project.title.asc())
        elif sort_by == "last_opened":
            query = query.order_by(Project.updated_at.desc())
        else:
            query = query.order_by(Project.created_at.desc())
            
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0
        
        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return {"items": items, "total": total}

    async def get_project(self, db: AsyncSession, project_id: str, user_id: int):
        result = await db.execute(
            select(Project).where(Project.id == project_id, Project.user_id == user_id, Project.deleted_at.is_(None))
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    async def create_project(self, db: AsyncSession, project_in: ProjectCreate, user_id: int):
        slug = _generate_slug(project_in.title)
        db_project = Project(
            **project_in.model_dump(),
            slug=slug,
            user_id=user_id
        )
        db.add(db_project)
        try:
            await db.commit()
            await db.refresh(db_project)
        except IntegrityError as exc:
            await db.rollback()
            logger.warning(
                "Project creation integrity error for user_id=%s slug=%s error_type=%s",
                user_id,
                slug,
                type(exc).__name__,
            )
            raise HTTPException(status_code=409, detail="Project already exists") from exc
        except SQLAlchemyError as exc:
            await db.rollback()
            logger.error(
                "Project creation database error for user_id=%s error_type=%s",
                user_id,
                type(exc).__name__,
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail="Could not create project") from exc
        return db_project

    async def update_project(self, db: AsyncSession, project_id: str, project_in: ProjectUpdate, user_id: int):
        db_project = await self.get_project(db, project_id, user_id)
        
        update_data = project_in.model_dump(exclude_unset=True)
        if "title" in update_data and update_data["title"] != db_project.title:
            db_project.slug = _generate_slug(update_data["title"])

        for field, value in update_data.items():
            setattr(db_project, field, value)
            
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return db_project

    async def delete_project(self, db: AsyncSession, project_id: str, user_id: int):
        db_project = await self.get_project(db, project_id, user_id)
        from sqlalchemy.sql import func
        db_project.deleted_at = func.now()
        db.add(db_project)
        await db.commit()
        return {"status": "deleted"}
        
    async def duplicate_project(self, db: AsyncSession, project_id: str, user_id: int):
        original = await self.get_project(db, project_id, user_id)
        slug = _generate_slug(f"{original.title} Copy")
        db_project = Project(
            title=f"{original.title} (Copy)",
            slug=slug,
            description=original.description,
            category=original.category,
            status="draft",
            visibility=original.visibility,
            color=original.color,
            icon=original.icon,
            user_id=user_id
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)

        # Clone all active ideas from the original project into the new project
        from app.models.idea import Idea
        result = await db.execute(
            select(Idea).where(Idea.project_id == original.id).order_by(Idea.created_at.asc())
        )
        original_ideas = result.scalars().all()
        for orig_idea in original_ideas:
            cloned_idea = Idea(
                id=str(uuid.uuid4()),
                project_id=db_project.id,
                title=orig_idea.title,
                problem_statement=orig_idea.problem_statement,
                solution_description=orig_idea.solution_description,
                target_users=orig_idea.target_users,
                industry=orig_idea.industry,
                business_model=orig_idea.business_model,
                stage=orig_idea.stage,
                tags=orig_idea.tags,
                notes=orig_idea.notes,
                is_draft=orig_idea.is_draft,
            )
            db.add(cloned_idea)

        if original_ideas:
            await db.commit()

        return db_project

project_service = ProjectService()
