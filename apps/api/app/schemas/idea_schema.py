from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class IdeaBase(BaseModel):
    problem_statement: Optional[str] = None
    solution_description: Optional[str] = None
    target_audience: Optional[str] = None
    business_model: Optional[str] = None
    competitors: Optional[str] = None
    unique_selling_proposition: Optional[str] = None
    technology_stack: Optional[str] = None
    budget: Optional[str] = None
    timeline: Optional[str] = None
    additional_notes: Optional[str] = None

class IdeaCreate(IdeaBase):
    pass

class IdeaUpdate(IdeaBase):
    pass

class IdeaResponse(IdeaBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
