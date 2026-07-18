from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

from app.db.base import Base

class EvaluationJob(Base):
    __tablename__ = "evaluation_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    idea_id: Mapped[str] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), index=True)
    
    # Status: 'draft', 'queued', 'processing', 'completed', 'failed', 'cancelled'
    status: Mapped[str] = mapped_column(String, default="draft", index=True)
    
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Evaluation(Base):
    """
    Stores the final structured output from the AI.
    """
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("evaluation_jobs.id", ondelete="CASCADE"), unique=True, index=True)
    
    # We use JSONB/JSON to store the structured AI response 
    # (e.g. scores, metrics, feedback arrays)
    result_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
