from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.models.idea import Idea
from app.models.project import Project
from app.schemas.idea_schema import IdeaCreate, IdeaUpdate

class IdeaService:
    async def _verify_project_ownership(self, db: AsyncSession, project_id: int, user_id: int):
        result = await db.execute(select(Project).where(Project.id == project_id, Project.user_id == user_id))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found or you don't have access")
        return project

    async def get_idea_by_project(self, db: AsyncSession, project_id: int, user_id: int):
        await self._verify_project_ownership(db, project_id, user_id)
        
        result = await db.execute(select(Idea).where(Idea.project_id == project_id))
        idea = result.scalar_one_or_none()
        return idea

    async def save_idea(self, db: AsyncSession, project_id: int, idea_in: IdeaUpdate, user_id: int):
        await self._verify_project_ownership(db, project_id, user_id)
        
        result = await db.execute(select(Idea).where(Idea.project_id == project_id))
        db_idea = result.scalar_one_or_none()
        
        update_data = idea_in.model_dump(exclude_unset=True)
        
        if not db_idea:
            db_idea = Idea(project_id=project_id, **update_data)
            db.add(db_idea)
        else:
            for field, value in update_data.items():
                setattr(db_idea, field, value)
            db.add(db_idea)
            
        await db.commit()
        await db.refresh(db_idea)
        return db_idea

idea_service = IdeaService()
