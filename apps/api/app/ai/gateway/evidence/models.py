"""
IdeaGPT AI Gateway — Research & Evidence Domain Models.
Defines normalized schemas for Sources, Evidence, Citations, Research Plans, and Grounded Analysis.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class SourceType(str, Enum):
    OFFICIAL = "OFFICIAL"
    GOVERNMENT = "GOVERNMENT"
    ACADEMIC = "ACADEMIC"
    COMPANY = "COMPANY"
    INDUSTRY = "INDUSTRY"
    NEWS = "NEWS"
    COMMUNITY = "COMMUNITY"
    UNKNOWN = "UNKNOWN"


class EvidenceClassification(str, Enum):
    FACT = "FACT"
    ESTIMATE = "ESTIMATE"
    INFERENCE = "INFERENCE"
    RECOMMENDATION = "RECOMMENDATION"
    UNKNOWN = "UNKNOWN"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class NormalizedSource(BaseModel):
    id: str
    citation_id: str = "[1]"
    title: str
    url: str
    domain: str
    snippet: str
    content: Optional[str] = None
    published_at: Optional[str] = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_type: SourceType = SourceType.UNKNOWN
    relevance_score: float = Field(default=0.8, ge=0.0, le=1.0)
    is_authoritative: bool = False

    model_config = ConfigDict(use_enum_values=True)


class NormalizedEvidence(BaseModel):
    id: str
    claim: str
    classification: EvidenceClassification = EvidenceClassification.INFERENCE
    source_ids: List[str] = Field(default_factory=list)
    source_urls: List[str] = Field(default_factory=list)
    supporting_excerpt: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    confidence_score: float = Field(default=0.75, ge=0.0, le=1.0)
    assumptions: Optional[str] = None
    reasoning_notes: Optional[str] = None
    conflict_details: Optional[Dict[str, Any]] = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def evidence_type(self) -> EvidenceClassification:
        return self.classification

    @property
    def source_url(self) -> Optional[str]:
        return self.source_urls[0] if self.source_urls else None

    @property
    def source_title(self) -> Optional[str]:
        return None

    model_config = ConfigDict(use_enum_values=True)


class ResearchQueryPlan(BaseModel):
    task_type: str
    idea_title: str
    industry: str
    queries: List[str] = Field(default_factory=list, max_length=5)
    focus_areas: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(use_enum_values=True)


class GroundedMarketAnalysis(BaseModel):
    market_definition: str
    target_segment: str
    tam_estimate: Optional[str] = None
    sam_estimate: Optional[str] = None
    som_estimate: Optional[str] = None
    growth_cagr: Optional[str] = None
    key_market_drivers: List[str] = Field(default_factory=list)
    evidence_claims: List[NormalizedEvidence] = Field(default_factory=list)
    citations: List[NormalizedSource] = Field(default_factory=list)
    overall_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    status: str = "COMPLETED"

    model_config = ConfigDict(use_enum_values=True)


class GroundedCompetitorItem(BaseModel):
    name: str
    category: str  # Direct, Adjacent, Substitute
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    differentiation_gap: str
    evidence_claims: List[NormalizedEvidence] = Field(default_factory=list)
    citations: List[NormalizedSource] = Field(default_factory=list)


class GroundedCompetitorAnalysis(BaseModel):
    direct_competitors: List[GroundedCompetitorItem] = Field(default_factory=list)
    adjacent_alternatives: List[GroundedCompetitorItem] = Field(default_factory=list)
    competitive_moat: str
    pricing_landscape: Optional[str] = None
    evidence_claims: List[NormalizedEvidence] = Field(default_factory=list)
    citations: List[NormalizedSource] = Field(default_factory=list)
    overall_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    status: str = "COMPLETED"

    model_config = ConfigDict(use_enum_values=True)


class GroundedRiskItem(BaseModel):
    category: str  # Technical, Regulatory, Market, Financial, Operational
    title: str
    severity: str  # High, Medium, Low
    likelihood: str  # High, Medium, Low
    description: str
    mitigation_strategy: str
    classification: EvidenceClassification = EvidenceClassification.INFERENCE
    citations: List[NormalizedSource] = Field(default_factory=list)


class GroundedRiskAnalysis(BaseModel):
    risks: List[GroundedRiskItem] = Field(default_factory=list)
    critical_blockers: List[str] = Field(default_factory=list)
    regulatory_considerations: List[str] = Field(default_factory=list)
    overall_risk_score: int = Field(default=50, ge=0, le=100)
    overall_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    status: str = "COMPLETED"

    model_config = ConfigDict(use_enum_values=True)
