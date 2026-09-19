"""
IdeaGPT AI Artifact Service.
Durable persistence, retrieval, and lifecycle management for all AI-generated blueprints,
PRDs, tech stacks, pitch decks, research dossiers, and strategy labs.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from fastapi import HTTPException, status

from app.models.ai_artifact import AIArtifact
from app.models.user import User

logger = logging.getLogger(__name__)


async def assert_tenant_links(
    db: AsyncSession,
    user_id: int,
    project_id: Optional[str] = None,
    idea_id: Optional[str] = None,
) -> None:
    """
    F-02 remediation — verify that a supplied project_id / idea_id belongs to the
    authenticated user before writing a cross-referencing row.

    Fail closed with 403 whenever a referenced parent does not exist or is owned by
    someone else.
    """
    if not project_id and not idea_id:
        return

    from app.models.project import Project
    from app.models.idea import Idea

    if project_id:
        proj_res = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == user_id,
                Project.deleted_at.is_(None),
            )
        )
        if not proj_res.scalar_one_or_none():
            logger.warning(
                "Tenant link denied: project_id=%s not owned by user_id=%s",
                project_id,
                user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Referenced project does not exist or access is denied.",
            )

    if idea_id:
        idea_res = await db.execute(select(Idea).where(Idea.id == idea_id))
        idea = idea_res.scalar_one_or_none()
        if not idea:
            logger.warning(
                "Tenant link denied: idea_id=%s not found (user_id=%s)",
                idea_id,
                user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Referenced idea does not exist or access is denied.",
            )

        # Idea must belong to the same project when both are supplied, and both
        # must be owned by the caller.
        if project_id and idea.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Referenced idea does not belong to the referenced project.",
            )

        proj_res = await db.execute(
            select(Project).where(
                Project.id == idea.project_id,
                Project.user_id == user_id,
                Project.deleted_at.is_(None),
            )
        )
        if not proj_res.scalar_one_or_none():
            logger.warning(
                "Tenant link denied: idea_id=%s parent project not owned by user_id=%s",
                idea_id,
                user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Referenced idea does not exist or access is denied.",
            )


class AIArtifactService:
    @classmethod
    async def save_artifact(
        cls,
        db: AsyncSession,
        user_id: int,
        artifact_type: str,
        title: str,
        content_payload: Dict[str, Any],
        project_id: Optional[str] = None,
        idea_id: Optional[str] = None,
        provider: str = "groq",
        model: str = "openai/gpt-oss-120b",
        requested_provider: Optional[str] = None,
        requested_model: Optional[str] = None,
        fallback_used: bool = False,
        fallback_reason: Optional[str] = None,
        execution_type: str = "REAL_PROVIDER",
        duration_ms: Optional[int] = None,
        token_usage: Optional[int] = None,
        estimated_cost: Optional[float] = None,
    ) -> AIArtifact:
        """
        Durably persists an AI-generated artifact in PostgreSQL before returning to client.
        """
        await assert_tenant_links(db, user_id, project_id, idea_id)

        artifact = AIArtifact(
            user_id=user_id,
            project_id=project_id,
            idea_id=idea_id,
            artifact_type=artifact_type,
            title=title,
            provider=provider,
            model=model,
            requested_provider=requested_provider,
            requested_model=requested_model,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            execution_type=execution_type,
            content_payload=content_payload,
            duration_ms=duration_ms,
            token_usage=token_usage,
            estimated_cost=estimated_cost,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(artifact)
        await db.commit()
        await db.refresh(artifact)
        logger.info(f"Persisted AI artifact {artifact.id} ({artifact_type}) for user {user_id}")
        return artifact

    @classmethod
    async def get_artifact_by_id(
        cls,
        db: AsyncSession,
        user: User,
        artifact_id: str
    ) -> Optional[AIArtifact]:
        """
        Retrieves a durable artifact enforcing tenant boundary.
        """
        stmt = select(AIArtifact).where(
            and_(
                AIArtifact.id == artifact_id,
                AIArtifact.user_id == user.id
            )
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    @classmethod
    async def list_artifacts_by_user(
        cls,
        db: AsyncSession,
        user: User,
        artifact_type: Optional[str] = None,
        limit: int = 50,
        project_id: Optional[str] = None,
        idea_id: Optional[str] = None,
        offset: int = 0,
    ) -> List[AIArtifact]:
        """
        Lists artifacts owned by current user.

        PRODUCT-01 P-01: previously hard-limited to 50 rows with no project or
        idea scoping, which is why a durable store with no UI could not be
        surfaced per-project. Ownership is always enforced; project_id/idea_id
        narrow the result set rather than widening access.
        """
        conditions = [AIArtifact.user_id == user.id]
        if artifact_type:
            conditions.append(AIArtifact.artifact_type == artifact_type)
        if project_id:
            conditions.append(AIArtifact.project_id == project_id)
        if idea_id:
            conditions.append(AIArtifact.idea_id == idea_id)

        stmt = (
            select(AIArtifact)
            .where(and_(*conditions))
            .order_by(desc(AIArtifact.created_at))
            .offset(max(0, offset))
            .limit(max(1, min(limit, 100)))
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def count_artifacts_by_user(
        cls,
        db: AsyncSession,
        user: User,
        artifact_type: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> int:
        """Total count for the same filter set, so callers can paginate honestly."""
        conditions = [AIArtifact.user_id == user.id]
        if artifact_type:
            conditions.append(AIArtifact.artifact_type == artifact_type)
        if project_id:
            conditions.append(AIArtifact.project_id == project_id)

        stmt = select(func.count(AIArtifact.id)).where(and_(*conditions))
        res = await db.execute(stmt)
        return int(res.scalar() or 0)

    @classmethod
    async def get_latest_project_artifact(
        cls,
        db: AsyncSession,
        user: User,
        project_id: str,
        artifact_type: str
    ) -> Optional[AIArtifact]:
        """
        Retrieves the latest generated artifact of a specific type for a project.
        """
        stmt = select(AIArtifact).where(
            and_(
                AIArtifact.user_id == user.id,
                AIArtifact.project_id == project_id,
                AIArtifact.artifact_type == artifact_type
            )
        ).order_by(desc(AIArtifact.created_at)).limit(1)
        res = await db.execute(stmt)
        return res.scalars().first()
