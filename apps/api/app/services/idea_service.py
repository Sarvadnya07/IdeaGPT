from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import uuid

from app.models.idea import Idea
from app.models.project import Project
from app.schemas.idea_schema import IdeaCreate, IdeaUpdate

class IdeaService:
    async def _verify_project_ownership(self, db: AsyncSession, project_id: str, user_id: int) -> Project:
        result = await db.execute(select(Project).where(Project.id == project_id, Project.user_id == user_id, Project.deleted_at.is_(None)))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found or you don't have access")
        return project

    async def _verify_idea_ownership(self, db: AsyncSession, idea_id: str, user_id: int) -> Idea:
        result = await db.execute(select(Idea).where(Idea.id == idea_id))
        idea = result.scalar_one_or_none()
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
        
        # Verify ownership of parent project
        await self._verify_project_ownership(db, idea.project_id, user_id)
        return idea

    async def get_project_ideas(self, db: AsyncSession, project_id: str, user_id: int):
        await self._verify_project_ownership(db, project_id, user_id)
        result = await db.execute(select(Idea).where(Idea.project_id == project_id).order_by(Idea.created_at.desc()))
        return result.scalars().all()

    async def get_idea(self, db: AsyncSession, idea_id: str, user_id: int):
        return await self._verify_idea_ownership(db, idea_id, user_id)

    async def create_idea(self, db: AsyncSession, project_id: str, idea_in: IdeaCreate, user_id: int):
        await self._verify_project_ownership(db, project_id, user_id)
        
        db_idea = Idea(
            id=str(uuid.uuid4()),
            project_id=project_id,
            **idea_in.model_dump()
        )
        db.add(db_idea)
        await db.commit()
        await db.refresh(db_idea)
        return db_idea

    async def update_idea(self, db: AsyncSession, idea_id: str, idea_in: IdeaUpdate, user_id: int):
        db_idea = await self._verify_idea_ownership(db, idea_id, user_id)
        
        update_data = idea_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_idea, field, value)
            
        db.add(db_idea)
        await db.commit()
        await db.refresh(db_idea)
        return db_idea

    async def delete_idea(self, db: AsyncSession, idea_id: str, user_id: int):
        db_idea = await self._verify_idea_ownership(db, idea_id, user_id)
        await db.delete(db_idea)
        await db.commit()
        return {"status": "deleted"}

    async def duplicate_idea(self, db: AsyncSession, idea_id: str, user_id: int):
        original = await self._verify_idea_ownership(db, idea_id, user_id)
        db_idea = Idea(
            id=str(uuid.uuid4()),
            project_id=original.project_id,
            title=f"{original.title} (Copy)",
            problem_statement=original.problem_statement,
            solution_description=original.solution_description,
            target_users=original.target_users,
            industry=original.industry,
            business_model=original.business_model,
            stage=original.stage,
            tags=original.tags,
            notes=original.notes,
            is_draft=True
        )
        db.add(db_idea)
        await db.commit()
        await db.refresh(db_idea)
        return db_idea

idea_service = IdeaService()
