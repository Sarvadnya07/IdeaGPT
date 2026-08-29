"""
IdeaGPT AI Artifact Domain Model.
Durable PostgreSQL persistence for all generated blueprints, PRDs, pitch decks,
tech stacks, system architectures, research dossiers, and strategy labs.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class AIArtifact(Base):
    __tablename__ = "ai_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    idea_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("ideas.id", ondelete="CASCADE"), nullable=True, index=True)

    artifact_type: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(255), default="Untitled AI Artifact")

    # Execution truth metadata
    provider: Mapped[str] = mapped_column(String(50), default="groq")
    model: Mapped[str] = mapped_column(String(100), default="openai/gpt-oss-120b")
    requested_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    requested_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    execution_type: Mapped[str] = mapped_column(String(30), default="REAL_PROVIDER")  # REAL_PROVIDER | DETERMINISTIC_ENGINE | CACHED_RESULT

    # Durable payload
    content_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # Accounting & Performance
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token_usage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
