import uuid
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.evaluation_history import EvaluationHistory

class Evaluation(Base):
    """
    Consolidated Evaluation Job and Report state.
    """
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    idea_id: Mapped[str] = mapped_column(String(36), ForeignKey("ideas.id", ondelete="CASCADE"), index=True)
    
    provider: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    evaluation_type: Mapped[str] = mapped_column(String, default="startup_evaluation", index=True)
    
    # Status: 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'
    status: Mapped[str] = mapped_column(String, default="PENDING", index=True)
    
    # Progress stage: 'PENDING', 'VALIDATION', 'RULE_EXECUTION', 'SCORING', 'INSIGHTS', 'SAVING', 'COMPLETED', 'FAILED', 'CANCELLED'
    progress: Mapped[str] = mapped_column(String, default="PENDING", index=True)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token_usage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # JSON analysis payload
    result_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Audit history relationship
    history_events: Mapped[List["EvaluationHistory"]] = relationship("EvaluationHistory", back_populates="evaluation", cascade="all, delete-orphan", order_by="EvaluationHistory.created_at.asc()")

