from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = "user"
    timezone: Optional[str] = None
    locale: Optional[str] = None
    onboarding_completed: Optional[bool] = False

class UserCreate(UserBase):
    clerk_id: str
    email: Optional[str] = None

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    clerk_id: str
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
