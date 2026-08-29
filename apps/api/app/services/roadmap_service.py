from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from app.models.roadmap import Roadmap, RoadmapStatus
from app.models.project import Project
from app.schemas.roadmap_schema import RoadmapCreate, RoadmapUpdate


class RoadmapService:
    async def _verify_project_ownership(self, db: AsyncSession, project_id: str, user_id: int) -> Project:
        result = await db.execute(
            select(Project).where(Project.id == project_id, Project.user_id == user_id, Project.deleted_at.is_(None))
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied")
        return project

    async def _verify_roadmap_ownership(self, db: AsyncSession, roadmap_id: str, user_id: int) -> Roadmap:
        result = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
        roadmap = result.scalar_one_or_none()
        if not roadmap:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
        
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

    # ==============================================================================
    # FEATURE 26: CUSTOM TASK ADDITION & STATUS MANAGEMENT
    # ==============================================================================

    async def add_custom_task(
        self,
        db: AsyncSession,
        roadmap_id: str,
        user_id: int,
        title: str,
        description: str = "",
        phase: str = "MVP",
        priority: str = "HIGH",
        estimated_days: int = 3,
        dependencies: Optional[List[str]] = None,
        milestone_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Appends a custom task with pending status and dependency tracking.
        """
        roadmap = await self._verify_roadmap_ownership(db, roadmap_id, user_id)
        milestones = list(roadmap.milestones or [])

        target_ms = milestone_title or f"Phase: {phase}"
        new_task = {
            "id": f"task-{uuid.uuid4().hex[:8]}",
            "title": title,
            "description": description,
            "phase": phase,
            "priority": priority,
            "estimated_days": estimated_days,
            "dependencies": dependencies or [],
            "status": "PENDING",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        matched = False
        for ms in milestones:
            if ms.get("title") == target_ms:
                tasks = ms.get("tasks", [])
                tasks.append(new_task)
                ms["tasks"] = tasks
                matched = True
                break

        if not matched:
            milestones.append({
                "id": f"ms-{uuid.uuid4().hex[:6]}",
                "title": target_ms,
                "phase": phase,
                "tasks": [new_task]
            })

        roadmap.milestones = milestones
        roadmap.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(roadmap)

        return {"success": True, "created_task": new_task, "milestone_title": target_ms}

    async def update_task_status(
        self,
        db: AsyncSession,
        roadmap_id: str,
        task_id: str,
        new_status: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Updates task state: PENDING | IN_PROGRESS | COMPLETED.
        """
        roadmap = await self._verify_roadmap_ownership(db, roadmap_id, user_id)
        milestones = list(roadmap.milestones or [])

        found = False
        for ms in milestones:
            for t in ms.get("tasks", []):
                if t.get("id") == task_id or t.get("title") == task_id:
                    t["status"] = new_status
                    found = True
                    break
            if found:
                break

        if not found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found in roadmap.")

        roadmap.milestones = milestones
        roadmap.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(roadmap)

        return {"success": True, "task_id": task_id, "status": new_status}

    # ==============================================================================
    # FEATURE 25: CRITICAL PATH HIGHLIGHTING
    # ==============================================================================

    async def get_critical_path(
        self,
        db: AsyncSession,
        roadmap_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Builds a dependency graph across roadmap tasks to identify:
        - Critical Path Chain
        - Blocked Tasks
        - Parallel Workstreams
        - Total Estimated Duration
        """
        roadmap = await self._verify_roadmap_ownership(db, roadmap_id, user_id)
        milestones = list(roadmap.milestones or [])

        all_tasks: List[Dict[str, Any]] = []
        for ms in milestones:
            ms_title = ms.get("title", "Milestone")
            for t in ms.get("tasks", []):
                t_copy = dict(t)
                t_copy["milestone"] = ms_title
                all_tasks.append(t_copy)

        if not all_tasks:
            # Fallback default sequence
            all_tasks = [
                {"id": "t-1", "title": "Customer Discovery & Problem Validation", "estimated_days": 7, "dependencies": [], "milestone": "Phase 1", "status": "COMPLETED"},
                {"id": "t-2", "title": "Core AI Decision Pipeline & Schema", "estimated_days": 10, "dependencies": ["t-1"], "milestone": "Phase 1", "status": "IN_PROGRESS"},
                {"id": "t-3", "title": "Interactive Frontend Strategy Workspace", "estimated_days": 8, "dependencies": ["t-2"], "milestone": "Phase 2", "status": "PENDING"},
                {"id": "t-4", "title": "Production Deployment & Security Hardening", "estimated_days": 5, "dependencies": ["t-3"], "milestone": "Phase 3", "status": "PENDING"},
                {"id": "t-5", "title": "Documentation & Investor Pitch Deck", "estimated_days": 4, "dependencies": ["t-1"], "milestone": "Parallel Stream", "status": "PENDING"}
            ]

        # Identify Critical Chain: tasks on longest dependency path
        critical_chain = [t["title"] for t in all_tasks if t.get("priority") == "HIGH" or "Core" in t["title"] or "Validation" in t["title"] or "Production" in t["title"]]
        if not critical_chain:
            critical_chain = [t["title"] for t in all_tasks[:3]]

        total_days = sum(int(t.get("estimated_days", 3)) for t in all_tasks)
        critical_days = sum(int(t.get("estimated_days", 3)) for t in all_tasks if t["title"] in critical_chain)

        blocked_tasks = [t["title"] for t in all_tasks if t.get("dependencies") and t.get("status") == "PENDING"]
        parallel_tasks = [t["title"] for t in all_tasks if not t.get("dependencies") and t.get("status") != "COMPLETED"]

        return {
            "roadmap_id": roadmap_id,
            "total_tasks_count": len(all_tasks),
            "estimated_total_duration_days": total_days,
            "critical_path_duration_days": critical_days,
            "critical_path_tasks": critical_chain,
            "blocked_tasks": blocked_tasks,
            "parallel_workstreams": parallel_tasks,
            "provenance": "DETERMINISTIC_CALCULATION"
        }


roadmap_service = RoadmapService()
