from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.session import get_db
from app.models.user import User
from app.schemas.user_schema import UserResponse, UserUpdate
from app.api.dependencies.auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get the currently authenticated user synchronized from Clerk.
    """
    return current_user

ALLOWED_USER_UPDATE_FIELDS = {
    "name",
    "username",
    "full_name",
    "avatar",
    "timezone",
    "locale",
    "onboarding_completed",
}

@router.patch("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update the current user's profile metadata.
    Enforces strict field whitelist to prevent mass-assignment privilege escalation.
    """
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for key, value in update_dict.items():
        if key in ALLOWED_USER_UPDATE_FIELDS:
            setattr(current_user, key, value)
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return current_user
