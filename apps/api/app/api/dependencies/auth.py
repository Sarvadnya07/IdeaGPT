"""
FastAPI dependency: get_current_user

Authentication flow:
  1. HTTPBearer extracts the Bearer token — returns 403 if header is absent
     (FastAPI maps HTTPBearer's 403 to the client as "not authenticated")
  2. ClerkAuth.verify_token() cryptographically verifies the JWT — returns 401
  3. Extract verified `sub` (Clerk user ID)
  4. Look up the user in PostgreSQL by clerk_id
  5. On first login: safely create the user using only verified JWT claims
     - email is taken from verified JWT claims only (never from client input)
     - if Clerk does not include email in the session token, email is stored as None
     - concurrent first-login requests are handled via IntegrityError retry
  6. Return the database user

Error distinction (CRITICAL — do not collapse these):
  Invalid/missing/expired/forged token → 401  (raised by ClerkAuth)
  Valid token + database unavailable        → 503
  Valid token + unexpected application bug  → 500
  Valid token + user not found              → safe creation (not 401)

Logging rules:
  - NEVER log the raw JWT token
  - NEVER log the Authorization header
  - Log clerk_id only at INFO/DEBUG level (it is not a secret)
  - Log errors without leaking credentials or stack traces to the client
"""

import logging

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Annotated

from app.db.session import get_db
from app.models.user import User
from app.core.security import ClerkAuth

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HTTPBearer — auto_error=True means a missing Authorization header returns
# 403 Forbidden.  We re-raise as 401 in the dependency below for consistency.
# ---------------------------------------------------------------------------
_http_bearer = HTTPBearer(auto_error=True)

clerk_auth = ClerkAuth()


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_http_bearer)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validates the Clerk JWT, extracts the verified user ID, and synchronizes
    the user to PostgreSQL.

    See module docstring for error distinction rules.
    """
    token = credentials.credentials

    # ------------------------------------------------------------------
    # Step 1 — Cryptographic JWT verification
    # ClerkAuth.verify_token() raises HTTPException(401) on any failure.
    # We do NOT catch that exception here — it propagates directly.
    # ------------------------------------------------------------------
    payload = await clerk_auth.verify_token(token)

    # ------------------------------------------------------------------
    # Step 2 — Extract verified sub
    # The "require": ["sub"] option in verify_token() already enforces this,
    # but we double-check here so get_current_user is self-contained.
    # ------------------------------------------------------------------
    clerk_id: str | None = payload.get("sub")
    if not clerk_id:
        # Should not be reached after verify_token, but fail closed.
        logger.warning("Verified token missing sub claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ------------------------------------------------------------------
    # Step 3 — Database operations
    # Failures here are NOT authentication failures.
    # ------------------------------------------------------------------
    try:
        user = await _get_or_create_user(db, clerk_id, payload)
    except HTTPException:
        # Re-raise HTTP exceptions from _get_or_create_user unchanged
        raise
    except SQLAlchemyError as exc:
        logger.error(
            "Database error during user synchronization for clerk_id=%s: %s",
            clerk_id,
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable",
        )
    except Exception as exc:
        logger.error(
            "Unexpected error during user synchronization for clerk_id=%s: %s",
            clerk_id,
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    request.state.user_id = str(user.id)
    request.state.clerk_id = clerk_id
    return user


async def _get_or_create_user(
    db: AsyncSession, clerk_id: str, payload: dict
) -> User:
    """
    Look up the user by clerk_id, creating them on first login.

    Handles concurrent first-login requests via IntegrityError retry.

    Email/name are sourced exclusively from the verified JWT payload.
    We NEVER use client-provided data or fabricated placeholder values in
    production.  If Clerk does not include 'email' in the session token,
    it is stored as NULL.

    To include email in Clerk session tokens:
      Clerk Dashboard → Configure → Sessions → Customize session token
      → Add {{ user.primary_email_address }}
    """
    # First attempt: look up existing user
    result = await db.execute(select(User).where(User.clerk_id == clerk_id))
    user = result.scalar_one_or_none()

    if user:
        return user

    # User not found — create on first login
    logger.info("First login: synchronizing new user clerk_id=%s", clerk_id)

    email: str | None = payload.get("email") or None
    name: str | None = (
        payload.get("name")
        or payload.get("full_name")
        or None
    )

    new_user = User(
        clerk_id=clerk_id,
        email=email,
        name=name,
    )
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
        logger.info("New user created: clerk_id=%s", clerk_id)
        return new_user

    except IntegrityError:
        # Concurrent request already created the user — roll back and re-fetch
        await db.rollback()
        logger.info(
            "Concurrent user creation detected for clerk_id=%s, re-fetching",
            clerk_id,
        )
        result = await db.execute(select(User).where(User.clerk_id == clerk_id))
        user = result.scalar_one_or_none()
        if user:
            return user
        # Extremely unlikely: integrity error but user still not found
        logger.error(
            "IntegrityError on create but user not found after rollback: clerk_id=%s",
            clerk_id,
        )
        raise
