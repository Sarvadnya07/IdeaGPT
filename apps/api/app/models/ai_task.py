import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

from sqlalchemy.dialects import postgresql

JSON_TYPE = JSON().with_variant(postgresql.JSONB, "postgresql")

class AiTask(Base):
    __tablename__ = "ai_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    idea_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("ideas.id", ondelete="SET NULL"), nullable=True)

    task_type: Mapped[str] = mapped_column(String(50), nullable=False, default="idea_evaluation")  # idea_evaluation, summary, roadmap_generation
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="auto")
    model: Mapped[str] = mapped_column(String(100), nullable=False, default="default")

    # Status: QUEUED | RUNNING | COMPLETED | FAILED | CANCELLED
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="QUEUED", index=True)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    input_payload: Mapped[Optional[dict]] = mapped_column(JSON_TYPE, nullable=True)
    result_payload: Mapped[Optional[dict]] = mapped_column(JSON_TYPE, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        Index("idx_ai_tasks_user_status", "user_id", "status"),
        Index("idx_ai_tasks_idempotency", "user_id", "idempotency_key"),
    )
