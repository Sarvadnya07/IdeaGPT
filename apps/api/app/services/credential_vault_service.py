"""
IdeaGPT AI Gateway v1 — BYOK Credential Vault & Encryption Service.
Implements authenticated encryption for user-supplied provider API keys.
"""

import base64
import hashlib
import logging
import time
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from app.core.config import settings
from app.models.provider_credential import ProviderCredential
from app.models.user import User
from app.ai.gateway.registry import gateway_registry
from app.ai.exceptions.ai_exceptions import AIAuthenticationException

logger = logging.getLogger(__name__)


def _get_encryption_cipher() -> Fernet:
    """
    Derive a 32-byte urlsafe base64 key from configuration or deterministic development fallback.
    """
    raw_key = getattr(settings, "CREDENTIAL_ENCRYPTION_KEY", None) or "ideagpt-development-master-encryption-key-32-bytes!"
    # Ensure key is 32 url-safe base64 bytes for Fernet
    digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
    fernet_key = base64.urlsafe_b64encode(digest)
    return Fernet(fernet_key)


def mask_api_key(raw_key: str) -> str:
    """Generate safe, non-secret display hint (e.g. 'gsk_...9a4b')."""
    if not raw_key:
        return "..."
    if len(raw_key) <= 8:
        return f"{raw_key[:2]}...{raw_key[-2:]}"
    prefix = raw_key[:4]
    suffix = raw_key[-4:]
    return f"{prefix}...{suffix}"


class CredentialVaultService:
    @classmethod
    def encrypt_secret(cls, plain_text: str) -> str:
        cipher = _get_encryption_cipher()
        encrypted_bytes = cipher.encrypt(plain_text.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    @classmethod
    def decrypt_secret(cls, encrypted_text: str) -> str:
        cipher = _get_encryption_cipher()
        decrypted_bytes = cipher.decrypt(encrypted_text.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")

    @classmethod
    async def save_credential(
        cls,
        db: AsyncSession,
        user: User,
        provider: str,
        api_key: str
    ) -> ProviderCredential:
        """
        Encrypts and upserts a user provider credential.
        """
        p_id = provider.lower().strip()
        encrypted = cls.encrypt_secret(api_key.strip())
        hint = mask_api_key(api_key.strip())

        # Check existing
        stmt = select(ProviderCredential).where(
            and_(
                ProviderCredential.user_id == user.id,
                ProviderCredential.provider == p_id
            )
        )
        res = await db.execute(stmt)
        cred = res.scalars().first()

        now = datetime.now(timezone.utc)
        if cred:
            cred.encrypted_secret = encrypted
            cred.key_hint = hint
            cred.status = "ACTIVE"
            cred.last_verified_at = now
            cred.updated_at = now
        else:
            cred = ProviderCredential(
                user_id=user.id,
                provider=p_id,
                encrypted_secret=encrypted,
                key_hint=hint,
                status="ACTIVE",
                last_verified_at=now,
                created_at=now,
                updated_at=now
            )
            db.add(cred)

        await db.commit()
        await db.refresh(cred)
        return cred

    @classmethod
    async def get_user_credentials(
        cls,
        db: AsyncSession,
        user: User
    ) -> List[ProviderCredential]:
        """
        List all saved BYOK credentials for the current user.
        """
        stmt = select(ProviderCredential).where(
            ProviderCredential.user_id == user.id
        ).order_by(ProviderCredential.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def get_decrypted_key(
        cls,
        db: AsyncSession,
        user_id: int,
        provider: str
    ) -> Optional[str]:
        """
        Internal resolver to decrypt a user's API key for execution.
        """
        stmt = select(ProviderCredential).where(
            and_(
                ProviderCredential.user_id == user_id,
                ProviderCredential.provider == provider.lower().strip(),
                ProviderCredential.status == "ACTIVE"
            )
        )
        res = await db.execute(stmt)
        cred = res.scalars().first()
        if not cred:
            return None
        try:
            return cls.decrypt_secret(cred.encrypted_secret)
        except Exception as exc:
            logger.error(f"Failed to decrypt credential for user {user_id}: {exc}")
            return None

    @classmethod
    async def verify_credential(
        cls,
        db: AsyncSession,
        user: User,
        provider: str
    ) -> Tuple[bool, str, int]:
        """
        Tests live connectivity for user's stored BYOK key against provider health endpoint.
        """
        p_id = provider.lower().strip()
        key = await cls.get_decrypted_key(db, user.id, p_id)
        if not key:
            return False, f"No active credential found for provider '{provider}'.", 0

        adapter = gateway_registry.get_adapter(p_id)
        if not adapter:
            return False, f"Provider '{provider}' is not supported.", 0

        start = time.time()
        try:
            health_desc = await adapter.health(byok_key=key)
            latency = int((time.time() - start) * 1000)
            if health_desc.state in ("AVAILABLE", "BYOK_CONNECTED"):
                return True, f"Successfully verified connectivity to {adapter.display_name} ({health_desc.models_count} models discovered).", latency
            return False, f"Verification failed: {health_desc.error or 'Service unavailable'}", latency
        except Exception as exc:
            latency = int((time.time() - start) * 1000)
            return False, f"Verification error: {str(exc)}", latency

    @classmethod
    async def revoke_credential(
        cls,
        db: AsyncSession,
        user: User,
        provider: str
    ) -> bool:
        """
        Transitions a user's credential state to REVOKED. Future requests fail safely.
        """
        stmt = select(ProviderCredential).where(
            and_(
                ProviderCredential.user_id == user.id,
                ProviderCredential.provider == provider.lower().strip()
            )
        )
        res = await db.execute(stmt)
        cred = res.scalars().first()
        if not cred:
            return False

        cred.status = "REVOKED"
        cred.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return True

    @classmethod
    async def delete_credential(
        cls,
        db: AsyncSession,
        user: User,
        provider: str
    ) -> bool:
        """
        Revokes and permanently deletes a user provider credential.
        """
        stmt = delete(ProviderCredential).where(
            and_(
                ProviderCredential.user_id == user.id,
                ProviderCredential.provider == provider.lower().strip()
            )
        )
        res = await db.execute(stmt)
        await db.commit()
        return res.rowcount > 0
