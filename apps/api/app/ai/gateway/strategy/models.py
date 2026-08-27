"""
Domain models for IdeaGPT Phase C — Deep Reasoning & Comparative Strategy Lab.
Enforces strict provenance, deterministic normalization, assumption taxonomy,
decision gates, reversibility, and cross-artifact consistency contracts.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


# ==============================================================================
# 1. PROVENANCE TAXONOMY
# ==============================================================================

class DataProvenance(str, Enum):
    """
    Guarantees transparent data lineage across all Strategy Lab outputs.
    """
    USER_INPUT = "USER_INPUT"
    DETERMINISTIC_CALCULATION = "DETERMINISTIC_CALCULATION"
    RESEARCH_EVIDENCE = "RESEARCH_EVIDENCE"
    MODEL_INFERENCE = "MODEL_INFERENCE"
    RECOMMENDATION = "RECOMMENDATION"


# ==============================================================================
# 2. ASSUMPTION & DECISION ENUMS
# ==============================================================================

class AssumptionClass(str, Enum):
    EXPLICIT_USER_ASSUMPTION = "EXPLICIT_USER_ASSUMPTION"
    EVIDENCE_SUPPORTED = "EVIDENCE_SUPPORTED"
    MODEL_INFERENCE = "MODEL_INFERENCE"
    UNVERIFIED = "UNVERIFIED"
    HIGH_RISK = "HIGH_RISK"


class SeverityLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ValidationEase(str, Enum):
    HIGH = "HIGH"    # Fast/inexpensive (e.g. 15 user interviews, landing page test)
    MEDIUM = "MEDIUM"  # Moderate effort (e.g. prototype test, paid ad validation)
    LOW = "LOW"       # Difficult/expensive (e.g. clinical trial, hardware lab testing)


class Reversibility(str, Enum):
    REVERSIBLE = "REVERSIBLE"                  # Two-way door decision (low regret)
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"  # Moderate cost to unwind
    HARD_TO_REVERSE = "HARD_TO_REVERSE"        # One-way door decision (high regret)


class DecisionGate(str, Enum):
    GO = "GO"
    GO_WITH_CONDITIONS = "GO_WITH_CONDITIONS"
    VALIDATE_FIRST = "VALIDATE_FIRST"
    PIVOT = "PIVOT"
    STOP = "STOP"


class DecisionConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ScenarioVariant(str, Enum):
    BASELINE = "BASELINE"
    OPTIMISTIC = "OPTIMISTIC"
    CONSERVATIVE = "CONSERVATIVE"
    ADVERSE = "ADVERSE"


# ==============================================================================
# 3. STRUCTURED DOMAIN MODELS
# ==============================================================================

class AssumptionItem(BaseModel):
    id: str = Field(description="Unique assumption identifier")
    claim: str = Field(description="The underlying premise or assumption")
    classification: AssumptionClass = Field(default=AssumptionClass.UNVERIFIED)
    impact: SeverityLevel = Field(default=SeverityLevel.HIGH, description="Potential damage if assumption is false")
    uncertainty: SeverityLevel = Field(default=SeverityLevel.HIGH, description="Degree of empirical unknown")
    validation_ease: ValidationEase = Field(default=ValidationEase.HIGH, description="Ease of running a fast experiment")
    priority_score: float = Field(default=4.5, description="Deterministic normalized priority score [0.33, 9.0]")
    priority_tier: str = Field(default="CRITICAL", description="CRITICAL | HIGH | MEDIUM | LOW")
    recommended_experiment: str = Field(description="Specific actionable experiment to validate this assumption")
    provenance: DataProvenance = Field(default=DataProvenance.MODEL_INFERENCE)

    model_config = ConfigDict(use_enum_values=True)


class DecisionCriterion(BaseModel):
    id: str
    name: str
    weight: float = Field(ge=0.0, le=1.0, description="Normalized criterion weight sum <= 1.0")
    raw_score: float = Field(ge=0.0, le=100.0, description="Raw performance score 0-100")
    weighted_score: float = Field(ge=0.0, le=100.0, description="raw_score * weight")
    rationale: str
    evidence_refs: List[str] = Field(default_factory=list)
    confidence: DecisionConfidence = Field(default=DecisionConfidence.MEDIUM)
    provenance: DataProvenance = Field(default=DataProvenance.DETERMINISTIC_CALCULATION)

    model_config = ConfigDict(use_enum_values=True)


class Tradeoff(BaseModel):
    id: str
    dimension: str
    option_a_name: str
    option_b_name: str
    difference: str
    consequence: str
    reversibility: Reversibility
    evidence_citations: List[str] = Field(default_factory=list)
    confidence: DecisionConfidence = Field(default=DecisionConfidence.MEDIUM)
    provenance: DataProvenance = Field(default=DataProvenance.MODEL_INFERENCE)

    model_config = ConfigDict(use_enum_values=True)


class ContradictionWarning(BaseModel):
    id: str
    contradiction_type: str = Field(description="E.g. MARKET_VS_STRATEGY, ARCHITECTURE_VS_ROADMAP")
    sections_involved: List[str]
    claim_a: str
    claim_b: str
    severity: SeverityLevel
    resolution_guidance: str

    model_config = ConfigDict(use_enum_values=True)


class CrossArtifactConsistencyWarning(BaseModel):
    id: str
    artifact_pair: str = Field(description="E.g. ROADMAP_TIMELINE_VS_TECH_COMPLEXITY")
    issue: str
    severity: SeverityLevel
    suggested_alignment: str

    model_config = ConfigDict(use_enum_values=True)


class ScenarioParameterInput(BaseModel):
    budget_usd: Optional[float] = Field(default=None, description="Available runway budget in USD")
    timeline_months: Optional[float] = Field(default=None, description="Target timeline to launch in months")
    team_size: Optional[int] = Field(default=None, description="Active full-time builders")
    monthly_burn_rate_usd: Optional[float] = Field(default=None, description="Estimated monthly burn")
    target_pricing_usd: Optional[float] = Field(default=None, description="Target price per subscriber/user per month")
    tam_reduction_pct: Optional[float] = Field(default=0.0, description="Simulated percentage TAM contraction")


class ScenarioResult(BaseModel):
    variant: ScenarioVariant
    runway_months: float = Field(description="Deterministic runway calculation: budget / burn")
    projected_time_to_mvp_months: float = Field(description="Estimated MVP completion timeline")
    feasibility_score: float = Field(ge=0.0, le=100.0)
    risk_profile: SeverityLevel
    key_bottleneck: str
    mitigation: str
    provenance: DataProvenance = Field(default=DataProvenance.DETERMINISTIC_CALCULATION)

    model_config = ConfigDict(use_enum_values=True)


class SensitivityMetric(BaseModel):
    variable_name: str
    baseline_value: str
    perturbed_value: str
    affected_dimensions: List[str]
    elasticity_rating: SeverityLevel = Field(description="HIGH: Material impact; LOW: Negligible change")
    direction: str = Field(description="POSITIVE | NEGATIVE | NEUTRAL")
    explanation: str
    confidence: DecisionConfidence = Field(default=DecisionConfidence.MEDIUM)
    provenance: DataProvenance = Field(default=DataProvenance.DETERMINISTIC_CALCULATION)

    model_config = ConfigDict(use_enum_values=True)


class StrategicNextAction(BaseModel):
    id: str
    action_title: str
    action_type: str = Field(description="VALIDATION_EXPERIMENT | ROADMAP_TASK | PRD_REQUIREMENT | ARCHITECTURE_DECISION")
    rationale: str
    target_metric: str
    success_threshold: str
    reversibility: Reversibility
    target_roadmap_milestone: Optional[str] = None
    provenance: DataProvenance = Field(default=DataProvenance.RECOMMENDATION)

    model_config = ConfigDict(use_enum_values=True)


class DeepStrategyAnalysis(BaseModel):
    idea_id: Optional[str] = None
    idea_title: str
    decision_gate: DecisionGate
    gate_rationale: str
    raw_attractiveness_score: float = Field(ge=0.0, le=100.0, description="Sum of weighted decision criteria")
    normalized_risk_exposure: float = Field(ge=0.0, le=100.0, description="Composite risk factor R in [0, 100]")
    risk_adjusted_decision_score: float = Field(ge=0.0, le=100.0, description="Score = Attractiveness * (1 - 0.5 * (R/100))")
    scoring_formula_description: str = Field(
        default="DecisionScore = Attractiveness * (1 - 0.5 * (RiskExposure / 100)). Preserves 0-100 scale with calibrated penalty."
    )
    overall_confidence: DecisionConfidence
    key_assumptions: List[AssumptionItem]
    decision_criteria: List[DecisionCriterion]
    tradeoffs: List[Tradeoff]
    scenarios: List[ScenarioResult]
    sensitivity_analysis: List[SensitivityMetric]
    contradictions: List[ContradictionWarning]
    cross_artifact_warnings: List[CrossArtifactConsistencyWarning]
    next_actions: List[StrategicNextAction]
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(use_enum_values=True)


class MultiIdeaComparisonResult(BaseModel):
    compared_idea_ids: List[str]
    winner_idea_id: str
    winner_idea_title: str
    winner_rationale: str
    strongest_alternative_id: Optional[str] = None
    idea_decision_scores: Dict[str, float]
    criteria_winners: Dict[str, str] = Field(description="Criterion name -> Winning Idea Title")
    critical_tradeoffs: List[Tradeoff]
    comparative_confidence: DecisionConfidence
    provenance: DataProvenance = Field(default=DataProvenance.DETERMINISTIC_CALCULATION)

    model_config = ConfigDict(use_enum_values=True)
