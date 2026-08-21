from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class TaskSchema(BaseModel):
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    estimated_days: Optional[int] = Field(None, description="Estimated effort in days")
    status: str = Field(default="pending", description="Status: pending, in_progress, completed")

class MilestoneSchema(BaseModel):
    title: str = Field(..., description="Title of the milestone")
    objective: str = Field(..., description="Objective of this milestone")
    tasks: List[TaskSchema] = Field(default_factory=list, description="List of tasks in this milestone")

class RoadmapBase(BaseModel):
    milestones: List[MilestoneSchema] = Field(default_factory=list, description="Validated JSON structure for roadmap milestones")
    status: str = Field(default="draft")

class RoadmapCreate(RoadmapBase):
    pass

class RoadmapUpdate(RoadmapBase):
    pass

class RoadmapResponse(RoadmapBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
