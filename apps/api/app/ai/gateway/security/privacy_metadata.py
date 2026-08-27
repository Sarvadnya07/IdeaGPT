"""
IdeaGPT AI Gateway — Provider Privacy & Data Policy Metadata.
Explicitly documents training, data retention, zero-retention support, and data residency regions.
"""

from typing import Dict, Any
from pydantic import BaseModel

class ProviderPrivacyMetadata(BaseModel):
    provider: str
    training_on_user_data: bool
    data_retention_days: int
    zero_retention_available: bool
    data_residency_region: str
    hipaa_compliant: bool
    soc2_certified: bool

PROVIDER_PRIVACY_REGISTRY: Dict[str, ProviderPrivacyMetadata] = {
    "groq": ProviderPrivacyMetadata(
        provider="groq",
        training_on_user_data=False,
        data_retention_days=0,
        zero_retention_available=True,
        data_residency_region="US-West (Direct LPU Inference)",
        hipaa_compliant=True,
        soc2_certified=True
    ),
    "gemini": ProviderPrivacyMetadata(
        provider="gemini",
        training_on_user_data=False,  # Paid/Enterprise Tier
        data_retention_days=30,
        zero_retention_available=True,
        data_residency_region="Global / Multi-Region",
        hipaa_compliant=True,
        soc2_certified=True
    ),
    "openai": ProviderPrivacyMetadata(
        provider="openai",
        training_on_user_data=False,  # API tier
        data_retention_days=30,
        zero_retention_available=True,
        data_residency_region="US-East / Multi-Region",
        hipaa_compliant=True,
        soc2_certified=True
    ),
    "ollama": ProviderPrivacyMetadata(
        provider="ollama",
        training_on_user_data=False,
        data_retention_days=0,
        zero_retention_available=True,
        data_residency_region="Local / On-Premise",
        hipaa_compliant=True,
        soc2_certified=True
    ),
    "tavily": ProviderPrivacyMetadata(
        provider="tavily",
        training_on_user_data=False,
        data_retention_days=0,
        zero_retention_available=True,
        data_residency_region="US-East",
        hipaa_compliant=False,
        soc2_certified=True
    ),
    "mock": ProviderPrivacyMetadata(
        provider="mock",
        training_on_user_data=False,
        data_retention_days=0,
        zero_retention_available=True,
        data_residency_region="In-Memory Test",
        hipaa_compliant=True,
        soc2_certified=True
    )
}
