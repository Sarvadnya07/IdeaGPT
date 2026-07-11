from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Annotated

from app.db.session import get_db
from app.models.user import User
from app.core.security import ClerkAuth
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()
clerk_auth = ClerkAuth()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Validates the Clerk JWT, extracts the user ID, and synchronizes the user to PostgreSQL.
    """
    token = credentials.credentials
    try:
        # Decode and verify the JWT
        payload = await clerk_auth.verify_token(token)
        clerk_id: str = payload.get("sub")
        if not clerk_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Synchronize user to PostgreSQL
        result = await db.execute(select(User).where(User.clerk_id == clerk_id))
        user = result.scalar_one_or_none()

        if not user:
            # Create the user automatically on first backend hit
            # Note: Clerk JWT doesn't always contain email/name unless specifically added to session claims.
            # Usually, you'd rely on a Webhook or fetch from Clerk API. We'll use fallbacks.
            email = payload.get("email", f"{clerk_id}@placeholder.com")
            
            user = User(
                clerk_id=clerk_id,
                email=email,
                name=payload.get("name", "New User")
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Synchronized new user from Clerk: {clerk_id}")
            
        return user

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
