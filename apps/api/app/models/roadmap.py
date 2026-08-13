from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
import uuid

from app.db.base import Base

class RoadmapStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    archived = "archived"

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # JSONB blob representing the explicit Roadmap milestone structure
    milestones = Column(JSON, nullable=False, default=list)
    
    status = Column(Enum(RoadmapStatus), default=RoadmapStatus.draft, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", backref="roadmaps")
