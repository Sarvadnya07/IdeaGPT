"""
AI Artifacts Sub-Router: Durable artifacts listing and retrieval.
"""

from typing import Optional, Any, Dict, List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.ai_artifact_service import AIArtifactService

router = APIRouter()


class AIArtifactResponse(BaseModel):
    """Typed schema for artifact list items."""
    id: str
    artifact_type: str
    title: Optional[str] = None
    project_id: Optional[str] = None
    idea_id: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    execution_type: Optional[str] = None
    fallback_used: bool = False
    content_payload: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


class AIArtifactDetailResponse(AIArtifactResponse):
    """Typed schema for single artifact detail (superset of list view)."""
    fallback_reason: Optional[str] = None


@router.get("/artifacts", response_model=List[AIArtifactResponse], summary="List durable AI artifacts for current user")
async def list_user_artifacts(
    current_user: Annotated[User, Depends(get_current_user)],
    artifact_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves all durably persisted AI blueprints, PRDs, roadmaps, and analysis dossiers.
    """
    artifacts = await AIArtifactService.list_artifacts_by_user(db=db, user=current_user, artifact_type=artifact_type)
    return [
        AIArtifactResponse(
            id=str(a.id),
            artifact_type=a.artifact_type,
            title=a.title,
            project_id=str(a.project_id) if a.project_id else None,
            idea_id=str(a.idea_id) if a.idea_id else None,
            provider=a.provider,
            model=a.model,
            execution_type=a.execution_type,
            fallback_used=bool(a.fallback_used),
            content_payload=a.content_payload,
            created_at=a.created_at.isoformat() if a.created_at else None,
        )
        for a in artifacts
    ]


@router.get("/artifacts/{artifact_id}", response_model=AIArtifactDetailResponse, summary="Get a specific durable AI artifact by ID")
async def get_artifact_by_id(
    artifact_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a single durable artifact, enforcing tenant boundaries.
    """
    artifact = await AIArtifactService.get_artifact_by_id(db=db, user=current_user, artifact_id=artifact_id)
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"AI Artifact '{artifact_id}' not found.")
    return AIArtifactDetailResponse(
        id=str(artifact.id),
        artifact_type=artifact.artifact_type,
        title=artifact.title,
        project_id=str(artifact.project_id) if artifact.project_id else None,
        idea_id=str(artifact.idea_id) if artifact.idea_id else None,
        provider=artifact.provider,
        model=artifact.model,
        execution_type=artifact.execution_type,
        fallback_used=bool(artifact.fallback_used),
        fallback_reason=artifact.fallback_reason,
        content_payload=artifact.content_payload,
        created_at=artifact.created_at.isoformat() if artifact.created_at else None,
    )
