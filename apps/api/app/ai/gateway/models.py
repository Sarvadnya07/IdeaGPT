"""
IdeaGPT AI Gateway v1 — Normalized Request, Result, Usage, Evidence, and Model Schemas.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from app.ai.gateway.contracts import (
    AICapability,
    CapabilityConfidence,
    ModelCategory,
    ModelStatus,
    ProviderState,
    EvidenceType,
)


class AIUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    duration_ms: int = 0
    estimated_cost: Optional[float] = None
    currency: str = "USD"
    pricing_source: Optional[str] = None


class ModelDescriptor(BaseModel):
    provider: str
    model_id: str
    display_name: str
    category: ModelCategory = ModelCategory.CHAT
    capabilities: List[AICapability] = Field(default_factory=list)
    capability_confidence: CapabilityConfidence = CapabilityConfidence.VERIFIED
    input_modalities: List[str] = Field(default_factory=lambda: ["text"])
    output_modalities: List[str] = Field(default_factory=lambda: ["text"])
    context_window: int = 131072
    supports_structured_output: bool = True
    supports_vision: bool = False
    supports_documents: bool = False
    supports_tools: bool = False
    supports_streaming: bool = True
    pricing: Optional[Dict[str, float]] = None
    currency: str = "USD"
    status: ModelStatus = ModelStatus.ACTIVE
    configured: bool = True
    available: bool = True
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deprecated_at: Optional[datetime] = None

    model_config = ConfigDict(use_enum_values=True)


class AIRequest(BaseModel):
    task_type: str = "idea_evaluation"
    capability: AICapability = AICapability.STRUCTURED_OUTPUT
    prompt: str
    system_prompt: str = ""
    messages: Optional[List[Dict[str, str]]] = None
    structured_schema: Optional[Dict[str, Any]] = None
    provider_override: Optional[str] = None
    model_override: Optional[str] = None
    temperature: float = 0.2
    max_output_tokens: int = 2048
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    byok_api_key: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)


class EvidenceItem(BaseModel):
    evidence_type: EvidenceType = EvidenceType.FACT
    claim: str
    value: Optional[Union[str, float, int, Dict[str, Any]]] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    assumptions: Optional[str] = None
    reasoning: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(use_enum_values=True)


class Citation(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    source: Optional[str] = None
    published_date: Optional[str] = None


class AIResult(BaseModel):
    text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    provider: str
    model: str
    usage: AIUsage = Field(default_factory=AIUsage)
    duration_ms: int = 0
    finish_reason: Optional[str] = "stop"
    confidence: float = 1.0
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    raw_metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(use_enum_values=True)


class ResearchRequest(BaseModel):
    query: str
    max_results: int = 5
    search_depth: str = "basic"  # basic | advanced
    include_domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None
    user_id: Optional[int] = None


class ResearchResult(BaseModel):
    query: str
    sources: List[Citation] = Field(default_factory=list)
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    duration_ms: int = 0
    provider: str = "tavily"
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProviderDescriptor(BaseModel):
    id: str
    name: str
    capabilities: List[AICapability] = Field(default_factory=list)
    state: ProviderState = ProviderState.NOT_CONFIGURED
    configured: bool = False
    enabled: bool = True
    byok_supported: bool = True
    latency_ms: int = 0
    models_count: int = 0
    error: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)
