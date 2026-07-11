from fastapi import Depends, HTTPException, status
from typing import Annotated
from app.models.user import User
from app.api.dependencies.auth import get_current_user

def require_role(required_role: str):
    def role_checker(current_user: Annotated[User, Depends(get_current_user)]):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required role: {required_role}"
            )
        return current_user
    return role_checker

def get_current_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin privileges"
        )
    return current_user
