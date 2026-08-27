"""
Pydantic Schemas for BYOK Provider Credentials.
Strictly ensures raw secret values are accepted on write, but NEVER exposed in responses.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CredentialCreateRequest(BaseModel):
    provider: str = Field(..., description="Provider identifier (groq, gemini, openai, tavily)")
    api_key: str = Field(..., min_length=8, max_length=512, description="Provider API Key")

    model_config = ConfigDict(extra="forbid")


class CredentialResponse(BaseModel):
    id: str
    provider: str
    key_hint: str
    status: str
    configured: bool = True
    verified: bool = True
    last_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CredentialVerifyResponse(BaseModel):
    provider: str
    valid: bool
    status: str
    message: str
    latency_ms: int = 0
