from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default="", max_length=2000)
    category: Optional[str] = Field(default="B2B SaaS", max_length=100)
    color: Optional[str] = None
    icon: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None

    model_config = ConfigDict(extra="ignore")

class ProjectResponse(ProjectBase):
    id: str
    user_id: int
    slug: str
    status: str
    visibility: str
    is_pinned: bool
    is_archived: bool
    is_favorite: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from typing import List

class PaginatedProjectResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    limit: int
    offset: int
    has_more: bool
