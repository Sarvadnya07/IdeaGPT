from sqlalchemy import String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
import enum
from datetime import datetime, timezone
import uuid
from typing import Any, Optional

from app.db.base import Base

class RoadmapStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    archived = "archived"

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # JSONB blob representing the explicit Roadmap milestone structure
    milestones: Mapped[Any] = mapped_column(JSON, nullable=False, default=list)
    
    status: Mapped[RoadmapStatus] = mapped_column(Enum(RoadmapStatus), default=RoadmapStatus.draft, nullable=False)

    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


    # Relationships
    project = relationship("Project", backref=backref("roadmaps", passive_deletes=True), passive_deletes=True)
