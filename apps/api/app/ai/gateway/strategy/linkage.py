"""
IdeaGPT Phase C — Strategy Linkage Service.
Connects strategic validation experiments directly to persisted Roadmap milestones/tasks,
PRD requirement modules, and Architecture decision records.
"""

import uuid
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models.roadmap import Roadmap, RoadmapStatus
from app.models.project import Project

logger = logging.getLogger(__name__)


class StrategyLinkageService:
    @classmethod
    async def add_strategy_experiment_to_roadmap(
        cls,
        db: AsyncSession,
        project_id: str,
        user_id: int,
        action_title: str,
        rationale: str,
        target_metric: str,
        success_threshold: str,
        milestone_title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates or updates a Roadmap milestone with an actionable validation task
        directly linked to the strategic decision experiment.
        """
        # 1. Verify project ownership
        proj_res = await db.execute(
            select(Project).where(Project.id == project_id, Project.user_id == user_id, Project.deleted_at.is_(None))
        )
        project = proj_res.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")

        # 2. Fetch or create Roadmap for project
        road_res = await db.execute(
            select(Roadmap).where(Roadmap.project_id == project_id).order_by(Roadmap.created_at.desc())
        )
        roadmap = road_res.scalars().first()

        if not roadmap:
            roadmap = Roadmap(
                id=str(uuid.uuid4()),
                project_id=project_id,
                status=RoadmapStatus.active,
                milestones=[],
                created_at=datetime.now(timezone.utc),
            )
            db.add(roadmap)

        # 3. Create the strategic milestone / task payload
        target_ms_name = milestone_title or "Phase 1: Strategic Validation Experiments"
        new_task = {
            "id": f"strat-task-{uuid.uuid4().hex[:8]}",
            "title": action_title,
            "description": f"Strategic Rationale: {rationale}\nTarget Metric: {target_metric}\nSuccess Threshold: {success_threshold}",
            "status": "pending",
            "task_type": "STRATEGY_VALIDATION_EXPERIMENT",
            "source": "STRATEGY_LAB_DECISION_ENGINE",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Find existing milestone or append new one
        existing_milestones = list(roadmap.milestones or [])
        matched = False
        for ms in existing_milestones:
            if ms.get("title") == target_ms_name:
                tasks = ms.get("tasks", [])
                tasks.append(new_task)
                ms["tasks"] = tasks
                matched = True
                break

        if not matched:
            existing_milestones.append({
                "id": f"strat-ms-{uuid.uuid4().hex[:6]}",
                "title": target_ms_name,
                "description": "Validation milestones synthesized by Strategy Lab Decision Engine",
                "phase": "Validation",
                "tasks": [new_task]
            })

        roadmap.milestones = existing_milestones
        roadmap.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(roadmap)

        return {
            "success": True,
            "roadmap_id": roadmap.id,
            "project_id": project_id,
            "created_task": new_task,
            "milestone_title": target_ms_name,
        }
