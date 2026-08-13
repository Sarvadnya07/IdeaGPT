from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import uuid

from app.models.roadmap import Roadmap
from app.models.project import Project
from app.schemas.roadmap_schema import RoadmapCreate, RoadmapUpdate

class RoadmapService:
    async def _verify_project_ownership(self, db: AsyncSession, project_id: str, user_id: int) -> Project:
        result = await db.execute(
            select(Project).where(Project.id == project_id, Project.user_id == user_id, Project.deleted_at.is_(None))
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found or you don't have access")
        return project

    async def _verify_roadmap_ownership(self, db: AsyncSession, roadmap_id: str, user_id: int) -> Roadmap:
        result = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
        roadmap = result.scalar_one_or_none()
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        
        await self._verify_project_ownership(db, roadmap.project_id, user_id)
        return roadmap

    async def get_project_roadmaps(self, db: AsyncSession, project_id: str, user_id: int):
        await self._verify_project_ownership(db, project_id, user_id)
        result = await db.execute(
            select(Roadmap).where(Roadmap.project_id == project_id).order_by(Roadmap.created_at.desc())
        )
        return result.scalars().all()

    async def get_roadmap(self, db: AsyncSession, roadmap_id: str, user_id: int):
        return await self._verify_roadmap_ownership(db, roadmap_id, user_id)

    async def create_roadmap(self, db: AsyncSession, project_id: str, roadmap_in: RoadmapCreate, user_id: int):
        await self._verify_project_ownership(db, project_id, user_id)
        
        # Serialize the Pydantic list of models into a list of dicts for JSONB
        milestones_data = [m.model_dump() for m in roadmap_in.milestones]
        
        db_roadmap = Roadmap(
            id=str(uuid.uuid4()),
            project_id=project_id,
            status=roadmap_in.status,
            milestones=milestones_data
        )
        db.add(db_roadmap)
        await db.commit()
        await db.refresh(db_roadmap)
        return db_roadmap

    async def update_roadmap(self, db: AsyncSession, roadmap_id: str, roadmap_in: RoadmapUpdate, user_id: int):
        db_roadmap = await self._verify_roadmap_ownership(db, roadmap_id, user_id)
        
        if roadmap_in.milestones is not None:
            db_roadmap.milestones = [m.model_dump() for m in roadmap_in.milestones]
        if roadmap_in.status is not None:
            db_roadmap.status = roadmap_in.status
            
        db.add(db_roadmap)
        await db.commit()
        await db.refresh(db_roadmap)
        return db_roadmap

    async def delete_roadmap(self, db: AsyncSession, roadmap_id: str, user_id: int):
        db_roadmap = await self._verify_roadmap_ownership(db, roadmap_id, user_id)
        await db.delete(db_roadmap)
        await db.commit()
        return {"status": "deleted"}

roadmap_service = RoadmapService()
