"""
Provider Credential Model for Secure BYOK (Bring-Your-Own-Key) Storage.
Stores encrypted API keys per-user with non-secret masked hints.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.user import Base


class ProviderCredential(Base):
    __tablename__ = "provider_credentials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    encrypted_secret = Column(String(512), nullable=False)
    key_hint = Column(String(32), nullable=False)  # e.g., "gsk_...9a4b", "sk-...1c8d"
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE | INVALID | REVOKED
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="provider_credentials")

    __table_args__ = (
        Index("idx_user_provider_cred", "user_id", "provider", unique=True),
    )
