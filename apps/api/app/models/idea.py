from sqlalchemy import String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from app.db.base import Base

class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), unique=True, index=True)
    
    # Form fields
    problem_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    solution_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_audience: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    business_model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    competitors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unique_selling_proposition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    technology_stack: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    budget: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timeline: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    additional_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
