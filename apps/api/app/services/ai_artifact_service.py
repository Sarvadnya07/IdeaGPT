"""
IdeaGPT AI Artifact Service.
Durable persistence, retrieval, and lifecycle management for all AI-generated blueprints,
PRDs, tech stacks, pitch decks, research dossiers, and strategy labs.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.ai_artifact import AIArtifact
from app.models.user import User

logger = logging.getLogger(__name__)


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
        limit: int = 50
    ) -> List[AIArtifact]:
        """
        Lists artifacts owned by current user.
        """
        conditions = [AIArtifact.user_id == user.id]
        if artifact_type:
            conditions.append(AIArtifact.artifact_type == artifact_type)

        stmt = select(AIArtifact).where(and_(*conditions)).order_by(desc(AIArtifact.created_at)).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

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
