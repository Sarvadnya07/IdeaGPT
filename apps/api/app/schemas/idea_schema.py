from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class IdeaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    problem_statement: str = Field(..., min_length=10, max_length=5000)
    solution_description: str = Field(..., min_length=10, max_length=5000)
    target_users: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    business_model: Optional[str] = Field(None, max_length=200)
    stage: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=5000)
    is_draft: Optional[bool] = True

class IdeaCreate(IdeaBase):
    pass

class IdeaUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    problem_statement: Optional[str] = Field(None, min_length=10, max_length=5000)
    solution_description: Optional[str] = Field(None, min_length=10, max_length=5000)
    target_users: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    business_model: Optional[str] = Field(None, max_length=200)
    stage: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=5000)
    is_draft: Optional[bool] = None

class IdeaResponse(BaseModel):
    id: str
    project_id: str
    title: str
    problem_statement: str
    solution_description: str
    target_users: Optional[str] = None
    industry: Optional[str] = None
    business_model: Optional[str] = None
    stage: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    is_draft: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
