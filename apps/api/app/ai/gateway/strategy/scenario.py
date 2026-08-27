"""
IdeaGPT Phase C — Scenario & Sensitivity Engine.
Provides deterministic financial and operational what-if simulation models,
runway calculations, and single-variable sensitivity analyses.
"""

from typing import Any, Dict, List, Optional
from app.ai.gateway.strategy.models import (
    DataProvenance,
    SeverityLevel,
    DecisionConfidence,
    ScenarioVariant,
    ScenarioResult,
    SensitivityMetric,
    ScenarioParameterInput,
)


class ScenarioEngine:
    """
    Simulates controlled operational and financial scenario variants (Baseline, Optimistic, Conservative, Adverse)
    with explicit deterministic arithmetic and transparent assumptions.
    """

    @classmethod
    def generate_scenarios(
        cls,
        base_budget: float = 50000.0,
        base_timeline_months: float = 3.0,
        monthly_burn: float = 6000.0,
    ) -> List[ScenarioResult]:
        budget = max(1000.0, float(base_budget))
        burn = max(500.0, float(monthly_burn))
        timeline = max(0.5, float(base_timeline_months))

        # 1. BASELINE SCENARIO
        baseline_runway = round(budget / burn, 1)
        baseline_feasibility = 85.0 if baseline_runway >= (timeline * 1.5) else (65.0 if baseline_runway >= timeline else 40.0)
        baseline_risk = SeverityLevel.LOW if baseline_runway >= (timeline * 1.5) else (SeverityLevel.MEDIUM if baseline_runway >= timeline else SeverityLevel.HIGH)

        baseline = ScenarioResult(
            variant=ScenarioVariant.BASELINE,
            runway_months=baseline_runway,
            projected_time_to_mvp_months=timeline,
            feasibility_score=baseline_feasibility,
            risk_profile=baseline_risk,
            key_bottleneck="Standard development cadence and initial customer recruitment",
            mitigation="Follow weekly sprint milestones and begin customer interviews in Sprint 1",
            provenance=DataProvenance.DETERMINISTIC_CALCULATION
        )

        # 2. OPTIMISTIC SCENARIO (Capital +30%, Burn -10%, Timeline -15%)
        opt_budget = budget * 1.3
        opt_burn = burn * 0.9
        opt_runway = round(opt_budget / opt_burn, 1)
        opt_timeline = round(timeline * 0.85, 1)
        opt_feasibility = min(98.0, baseline_feasibility + 12.0)

        optimistic = ScenarioResult(
            variant=ScenarioVariant.OPTIMISTIC,
            runway_months=opt_runway,
            projected_time_to_mvp_months=opt_timeline,
            feasibility_score=opt_feasibility,
            risk_profile=SeverityLevel.LOW,
            key_bottleneck="Managing rapid early adoption and server concurrency",
            mitigation="Deploy auto-scaling and leverage multi-provider gateway fallbacks",
            provenance=DataProvenance.DETERMINISTIC_CALCULATION
        )

        # 3. CONSERVATIVE SCENARIO (Capital -25%, Burn +20%, Timeline +30%)
        con_budget = budget * 0.75
        con_burn = burn * 1.2
        con_runway = round(con_budget / con_burn, 1)
        con_timeline = round(timeline * 1.3, 1)
        con_feasibility = max(30.0, baseline_feasibility - 20.0)
        con_risk = SeverityLevel.MEDIUM if con_runway >= con_timeline else SeverityLevel.HIGH

        conservative = ScenarioResult(
            variant=ScenarioVariant.CONSERVATIVE,
            runway_months=con_runway,
            projected_time_to_mvp_months=con_timeline,
            feasibility_score=con_feasibility,
            risk_profile=con_risk,
            key_bottleneck="Narrow runway window before MVP monetization",
            mitigation="Cut discretionary tooling expenses and focus strictly on core MVP value path",
            provenance=DataProvenance.DETERMINISTIC_CALCULATION
        )

        # 4. ADVERSE SCENARIO (Capital -50%, Burn +40%, Timeline +60%)
        adv_budget = budget * 0.50
        adv_burn = burn * 1.4
        adv_runway = round(adv_budget / adv_burn, 1)
        adv_timeline = round(timeline * 1.6, 1)
        adv_feasibility = max(15.0, baseline_feasibility - 45.0)

        adverse = ScenarioResult(
            variant=ScenarioVariant.ADVERSE,
            runway_months=adv_runway,
            projected_time_to_mvp_months=adv_timeline,
            feasibility_score=adv_feasibility,
            risk_profile=SeverityLevel.HIGH,
            key_bottleneck="Runway exhausts before achieving problem-solution fit",
            mitigation="Pivot to low-code validation prototype or secure bridge grant funding immediately",
            provenance=DataProvenance.DETERMINISTIC_CALCULATION
        )

        return [baseline, optimistic, conservative, adverse]


class SensitivityEngine:
    """
    Performs single-variable sensitivity perturbations while holding all other parameters constant.
    """

    @classmethod
    def analyze_sensitivities(
        cls,
        base_budget: float = 50000.0,
        base_timeline: float = 3.0,
        base_pricing: float = 29.0,
    ) -> List[SensitivityMetric]:
        return [
            SensitivityMetric(
                variable_name="Available Capital / Budget",
                baseline_value=f"${int(base_budget):,}",
                perturbed_value=f"${int(base_budget * 0.5):,}",
                affected_dimensions=["Runway Months", "Hiring Flexibility", "Ad Budget"],
                elasticity_rating=SeverityLevel.HIGH,
                direction="NEGATIVE",
                explanation="A 50% capital reduction halves runway, escalating execution urgency and narrowing margin for product error.",
                confidence=DecisionConfidence.HIGH,
                provenance=DataProvenance.DETERMINISTIC_CALCULATION
            ),
            SensitivityMetric(
                variable_name="Time to MVP Launch",
                baseline_value=f"{base_timeline:.1f} months",
                perturbed_value=f"{base_timeline * 2.0:.1f} months",
                affected_dimensions=["Burn Rate Accumulation", "First-Mover Moat"],
                elasticity_rating=SeverityLevel.HIGH,
                direction="NEGATIVE",
                explanation="Doubling delivery timeline doubles pre-revenue burn and exposes the venture to faster competitor encroachment.",
                confidence=DecisionConfidence.HIGH,
                provenance=DataProvenance.DETERMINISTIC_CALCULATION
            ),
            SensitivityMetric(
                variable_name="Subscription Pricing Model",
                baseline_value=f"${int(base_pricing)}/mo",
                perturbed_value=f"${int(base_pricing * 0.65)}/mo",
                affected_dimensions=["Gross Margin", "CAC Payback Period", "Customer Volume Needed"],
                elasticity_rating=SeverityLevel.MEDIUM,
                direction="NEGATIVE",
                explanation="A 35% price cut improves top-of-funnel conversion but increases customer volume needed for profitability by 54%.",
                confidence=DecisionConfidence.MEDIUM,
                provenance=DataProvenance.DETERMINISTIC_CALCULATION
            ),
            SensitivityMetric(
                variable_name="Target Market Penetration Rate",
                baseline_value="1.0% SAM Capture",
                perturbed_value="0.3% SAM Capture",
                affected_dimensions=["Year 2 ARR", "Valuation Ceiling"],
                elasticity_rating=SeverityLevel.MEDIUM,
                direction="NEGATIVE",
                explanation="Lower market capture requires higher retention or B2B enterprise tier expansion to reach sustainable scale.",
                confidence=DecisionConfidence.MEDIUM,
                provenance=DataProvenance.DETERMINISTIC_CALCULATION
            ),
        ]
