"""
IdeaGPT AI Gateway v1 — BYOK Provider Credential Endpoints.
Authenticated user routes for managing personal AI provider keys.
"""

from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.schemas.credential_schema import (
    CredentialCreateRequest,
    CredentialResponse,
    CredentialVerifyResponse,
)
from app.services.credential_vault_service import CredentialVaultService

router = APIRouter(prefix="/ai/credentials", tags=["ai-credentials"])


@router.post("", response_model=CredentialResponse, summary="Store a BYOK provider API key")
async def save_credential(
    payload: CredentialCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Encrypts and saves a user-supplied provider API key.
    Returns masked key hint (e.g., 'gsk_...9a4b') and metadata. Plaintext is NEVER returned.
    """
    cred = await CredentialVaultService.save_credential(
        db=db,
        user=current_user,
        provider=payload.provider,
        api_key=payload.api_key
    )
    return cred


@router.get("", response_model=List[CredentialResponse], summary="List configured BYOK providers")
async def list_credentials(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all saved BYOK credentials for the current user with non-secret masked hints.
    """
    return await CredentialVaultService.get_user_credentials(db=db, user=current_user)


@router.post("/{provider}/verify", response_model=CredentialVerifyResponse, summary="Test connectivity of BYOK key")
async def verify_credential(
    provider: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Tests live authentication and connectivity using the user's stored BYOK key.
    """
    valid, message, latency_ms = await CredentialVaultService.verify_credential(
        db=db,
        user=current_user,
        provider=provider
    )
    return CredentialVerifyResponse(
        provider=provider,
        valid=valid,
        status="VALID" if valid else "INVALID",
        message=message,
        latency_ms=latency_ms
    )


@router.delete("/{provider}", summary="Revoke a BYOK provider key")
async def delete_credential(
    provider: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Permanently deletes a user's stored BYOK credential.
    """
    deleted = await CredentialVaultService.delete_credential(
        db=db,
        user=current_user,
        provider=provider
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credential for provider '{provider}' not found."
        )
    return {"message": f"Credential for '{provider}' revoked successfully."}
