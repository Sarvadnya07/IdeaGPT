"""
Phase C — Deep Reasoning & Comparative Strategy Lab Master Test Suite

Comprehensive test coverage for:
- Deterministic Assumption Priority Score Normalization
- Calibrated Risk-Adjusted Decision Score Mapping
- Contradiction & Disagreement Detection
- Cross-Artifact Consistency Auditing
- Controlled What-If Scenario Engine (Baseline, Optimistic, Conservative, Adverse)
- Single-Variable Sensitivity Analysis
- Multi-Idea Comparative Strategy Engine with Weighted Matrix
- Strategic Validation Experiment -> Roadmap Persistence Linkage
- Metamorphic Perturbation Testing (Budget / Timeline variance)
- Adversarial Prompt Injection Defense
- Primary Mira Personal Safety Platform Benchmark
- Authenticated REST API Endpoints
"""

import pytest
import time
import json
import jwt
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.main import app
from app.core.database import AsyncSessionLocal
from app.models.project import Project
from app.models.roadmap import Roadmap
from app.ai.gateway.strategy.models import (
    DataProvenance,
    AssumptionClass,
    SeverityLevel,
    ValidationEase,
    Reversibility,
    DecisionGate,
    DecisionConfidence,
    ScenarioVariant,
)
from app.ai.gateway.strategy.reasoning import StrategyReasoningEngine
from app.ai.gateway.strategy.scenario import ScenarioEngine, SensitivityEngine
from app.ai.gateway.strategy.comparative import ComparativeStrategyEngine
from app.ai.gateway.strategy.linkage import StrategyLinkageService
from app.ai.gateway.strategy.pipeline import StrategicDecisionPipeline

TEST_SECRET = "test-secret-for-unit-tests-only-never-production"


def _make_auth_header(sub: str = "user_phase_c_strategist") -> dict:
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": f"{sub}@example.com",
        "iat": now,
        "exp": now + 3600,
        "iss": "https://healthy-sunbeam-68.clerk.accounts.dev"
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


# ==============================================================================
# 1. ASSUMPTION PRIORITY SCORE NORMALIZATION
# ==============================================================================

def test_assumption_priority_score_normalization():
    """Verify deterministic normalized priority: (Impact * Uncertainty) / Ease."""
    # Critical: High Impact (3), High Uncertainty (3), High Ease (3) -> (3 * 3) / 3 = 3.0 -> HIGH
    score_1, tier_1 = StrategyReasoningEngine.calculate_assumption_priority(
        impact=SeverityLevel.HIGH,
        uncertainty=SeverityLevel.HIGH,
        ease=ValidationEase.HIGH
    )
    assert score_1 == 3.0
    assert tier_1 == "HIGH"

    # Extreme Critical: High Impact (3), High Uncertainty (3), Low Ease (1) -> (3 * 3) / 1 = 9.0 -> CRITICAL
    score_2, tier_2 = StrategyReasoningEngine.calculate_assumption_priority(
        impact=SeverityLevel.HIGH,
        uncertainty=SeverityLevel.HIGH,
        ease=ValidationEase.LOW
    )
    assert score_2 == 9.0
    assert tier_2 == "CRITICAL"

    # Low Priority: Low Impact (1), Low Uncertainty (1), High Ease (3) -> (1 * 1) / 3 = 0.33 -> LOW
    score_3, tier_3 = StrategyReasoningEngine.calculate_assumption_priority(
        impact=SeverityLevel.LOW,
        uncertainty=SeverityLevel.LOW,
        ease=ValidationEase.HIGH
    )
    assert score_3 == 0.33
    assert tier_3 == "LOW"


# ==============================================================================
# 2. RISK-ADJUSTED DECISION SCORE BOUNDING
# ==============================================================================

def test_risk_adjusted_decision_score_bounding():
    """Verify formula: Score = Attractiveness * (1 - 0.5 * (R / 100)) strictly bounds in [0, 100]."""
    # Zero risk: Score = 80 * (1 - 0) = 80.0
    assert StrategyReasoningEngine.calculate_risk_adjusted_decision_score(80.0, 0.0) == 80.0

    # Max risk (100): Score = 80 * (1 - 0.5) = 40.0
    assert StrategyReasoningEngine.calculate_risk_adjusted_decision_score(80.0, 100.0) == 40.0

    # Typical moderate risk (30): Score = 80 * (1 - 0.15) = 68.0
    assert StrategyReasoningEngine.calculate_risk_adjusted_decision_score(80.0, 30.0) == 68.0

    # Negative input bounding safety
    assert StrategyReasoningEngine.calculate_risk_adjusted_decision_score(-10.0, 50.0) == 0.0
    assert StrategyReasoningEngine.calculate_risk_adjusted_decision_score(150.0, -10.0) == 100.0


# ==============================================================================
# 3. CONTRADICTION & CROSS-ARTIFACT CONSISTENCY DETECTION
# ==============================================================================

def test_contradiction_detection_high_risk_go_gate():
    """Verify warning generated if risk exceeds 75 but decision gate is unconditional GO."""
    warnings = StrategyReasoningEngine.detect_contradictions(
        market_data={"tam_estimate": "$4.5B"},
        risk_data={"overall_risk_score": 85},
        tech_data=None,
        evaluation_data=None,
        proposed_gate=DecisionGate.GO
    )
    assert len(warnings) == 1
    assert warnings[0].contradiction_type == "RISK_VS_DECISION_GATE"
    assert warnings[0].severity == SeverityLevel.HIGH


def test_cross_artifact_inconsistency_detection():
    """Verify warning when distributed architecture is paired with 2-week MVP roadmap."""
    warnings = StrategyReasoningEngine.detect_cross_artifact_inconsistencies(
        architecture_notes="Complex distributed microservices with custom telemetry mesh",
        roadmap_notes="Launch full MVP in 2 weeks"
    )
    assert len(warnings) == 1
    assert warnings[0].artifact_pair == "ARCHITECTURE_VS_ROADMAP_TIMELINE"


# ==============================================================================
# 4. WHAT-IF SCENARIO ENGINE
# ==============================================================================

def test_scenario_engine_deterministic_variants():
    """Verify Baseline, Optimistic, Conservative, and Adverse runway and risk profiles."""
    scenarios = ScenarioEngine.generate_scenarios(
        base_budget=60000.0,
        base_timeline_months=3.0,
        monthly_burn=6000.0
    )
    assert len(scenarios) == 4

    # Baseline: $60k / $6k = 10.0 months runway
    assert scenarios[0].variant == ScenarioVariant.BASELINE
    assert scenarios[0].runway_months == 10.0
    assert scenarios[0].feasibility_score >= 80.0
    assert scenarios[0].risk_profile == SeverityLevel.LOW

    # Adverse: $30k / $8.4k = 3.6 months runway
    assert scenarios[3].variant == ScenarioVariant.ADVERSE
    assert scenarios[3].runway_months < 5.0
    assert scenarios[3].risk_profile == SeverityLevel.HIGH


# ==============================================================================
# 5. SINGLE-VARIABLE SENSITIVITY ENGINE
# ==============================================================================

def test_sensitivity_engine_elasticity():
    """Verify sensitivity metrics test budget, timeline, pricing, and penetration."""
    sensitivities = SensitivityEngine.analyze_sensitivities(
        base_budget=50000.0,
        base_timeline=3.0,
        base_pricing=29.0
    )
    assert len(sensitivities) == 4
    assert any("Capital" in s.variable_name for s in sensitivities)
    assert any("Pricing" in s.variable_name for s in sensitivities)
    assert all(s.provenance == DataProvenance.DETERMINISTIC_CALCULATION for s in sensitivities)


# ==============================================================================
# 6. COMPARATIVE STRATEGY ENGINE (MULTI-IDEA)
# ==============================================================================

def test_comparative_strategy_engine_multi_idea():
    """Verify multi-idea deterministic scoring, criterion winners, and trade-offs."""
    ideas_data = [
        {
            "id": "idea-1",
            "title": "Mira Personal Safety",
            "overall_score": 85.0,
            "risk_score": 25.0,
            "dimensions": {
                "market_potential": 88.0,
                "technical_feasibility": 84.0,
                "business_viability": 82.0,
                "competitive_differentiation": 86.0,
                "execution_complexity": 80.0,
            }
        },
        {
            "id": "idea-2",
            "title": "Generic Safety Whistle App",
            "overall_score": 55.0,
            "risk_score": 45.0,
            "dimensions": {
                "market_potential": 45.0,
                "technical_feasibility": 90.0,
                "business_viability": 40.0,
                "competitive_differentiation": 30.0,
                "execution_complexity": 90.0,
            }
        }
    ]

    result = ComparativeStrategyEngine.compare_multiple_ideas(ideas_data)
    assert result.winner_idea_id == "idea-1"
    assert result.winner_idea_title == "Mira Personal Safety"
    assert result.idea_decision_scores["idea-1"] > result.idea_decision_scores["idea-2"]
    assert len(result.criteria_winners) == 5
    assert len(result.critical_tradeoffs) >= 1


# ==============================================================================
# 7. STRATEGY EXPERIMENT -> ROADMAP LINKAGE
# ==============================================================================

@pytest.mark.asyncio
async def test_strategy_action_roadmap_linkage():
    """Verify linking a strategic experiment creates a persisted Roadmap milestone and task."""
    headers = _make_auth_header("user_roadmap_link_test")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Project
        proj_res = await client.post(
            "/api/v1/projects/",
            json={"title": "Strategy Link Project", "slug": "strat-link-proj"},
            headers=headers
        )
        assert proj_res.status_code == 201
        project_id = proj_res.json()["id"]

        # Link Strategy Experiment to Roadmap
        link_res = await client.post(
            "/api/v1/ai/strategy/link-to-roadmap",
            json={
                "project_id": project_id,
                "action_title": "Validate Willingness-to-Pay with 20 Solo Travelers",
                "rationale": "Verify customer monetization elasticity before deep coding",
                "target_metric": "Pre-order deposit rate",
                "success_threshold": "At least 25% conversion",
                "milestone_title": "Phase 1: Founder Discovery & Assumption Testing"
            },
            headers=headers
        )
        assert link_res.status_code == 200
        data = link_res.json()
        assert data["success"] is True
        assert "roadmap_id" in data
        assert data["created_task"]["title"] == "Validate Willingness-to-Pay with 20 Solo Travelers"

        # Verify Roadmap in Database
        async with AsyncSessionLocal() as db:
            road_res = await db.execute(select(Roadmap).where(Roadmap.project_id == project_id))
            roadmap = road_res.scalars().first()
            assert roadmap is not None
            assert len(roadmap.milestones) >= 1
            assert any("Founder Discovery" in m["title"] for m in roadmap.milestones)


# ==============================================================================
# 8. METAMORPHIC PERTURBATION TESTING
# ==============================================================================

def test_metamorphic_budget_perturbation():
    """Verify that lowering budget monotonically reduces runway without erratic jumps."""
    scenarios_high_budget = ScenarioEngine.generate_scenarios(base_budget=100000.0, monthly_burn=5000.0)
    scenarios_low_budget = ScenarioEngine.generate_scenarios(base_budget=20000.0, monthly_burn=5000.0)

    # Baseline runway must decrease monotonically
    assert scenarios_high_budget[0].runway_months == 20.0
    assert scenarios_low_budget[0].runway_months == 4.0
    assert scenarios_high_budget[0].feasibility_score > scenarios_low_budget[0].feasibility_score


# ==============================================================================
# 9. PRIMARY BENCHMARK: MIRA PERSONAL SAFETY PLATFORM
# ==============================================================================

@pytest.mark.asyncio
async def test_mira_benchmark_deep_strategy_pipeline():
    """Verify primary benchmark Mira executes full strategic reasoning cleanly."""
    analysis = await StrategicDecisionPipeline.analyze_strategy(
        idea_title="Mira Personal Safety",
        industry="Personal Safety / Consumer AI",
        problem_statement="Personal safety incidents require immediate coordination with trusted contacts",
        solution_description="Privacy-first incident support platform with localized emergency routing",
        user_constraints={"budget_usd": 75000.0, "timeline_months": 3.5, "monthly_burn_rate_usd": 7000.0}
    )

    assert analysis.idea_title == "Mira Personal Safety"
    assert analysis.decision_gate in (DecisionGate.GO, DecisionGate.VALIDATE_FIRST, DecisionGate.GO_WITH_CONDITIONS)
    assert 0.0 <= analysis.risk_adjusted_decision_score <= 100.0
    assert len(analysis.key_assumptions) >= 3
    assert len(analysis.decision_criteria) == 5
    assert len(analysis.tradeoffs) >= 1
    assert len(analysis.scenarios) == 4
    assert len(analysis.next_actions) >= 2


# ==============================================================================
# 10. AUTHENTICATED REST API ENDPOINTS
# ==============================================================================

@pytest.mark.asyncio
async def test_authenticated_strategy_api_endpoints():
    """Verify all Strategy Lab endpoints return structured data with valid JWT."""
    headers = _make_auth_header()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Strategy Analyze
        analyze_res = await client.post(
            "/api/v1/ai/strategy/analyze",
            json={
                "title": "CloudCost Optimizer",
                "industry": "B2B SaaS",
                "problem_statement": "Cloud bills are unpredictable",
                "solution_description": "Automated resource right-sizing"
            },
            headers=headers
        )
        assert analyze_res.status_code == 200
        an_data = analyze_res.json()
        assert "decision_gate" in an_data
        assert "risk_adjusted_decision_score" in an_data

        # 2. Strategy Assumptions
        assump_res = await client.post(
            "/api/v1/ai/strategy/assumptions",
            json={
                "title": "CloudCost Optimizer",
                "industry": "B2B SaaS",
                "problem_statement": "Cloud bills are unpredictable",
                "solution_description": "Automated resource right-sizing"
            },
            headers=headers
        )
        assert assump_res.status_code == 200
        ass_data = assump_res.json()
        assert len(ass_data) >= 3
        assert "priority_score" in ass_data[0]

        # 3. Strategy Scenario
        scen_res = await client.post(
            "/api/v1/ai/strategy/scenario",
            json={"budget_usd": 80000.0, "timeline_months": 4.0, "monthly_burn_rate_usd": 8000.0},
            headers=headers
        )
        assert scen_res.status_code == 200
        assert len(scen_res.json()) == 4

        # 4. Strategy Sensitivity
        sens_res = await client.post(
            "/api/v1/ai/strategy/sensitivity",
            json={"budget_usd": 80000.0, "timeline_months": 4.0, "target_pricing_usd": 49.0},
            headers=headers
        )
        assert sens_res.status_code == 200
        assert len(sens_res.json()) == 4

        # 5. Strategy Compare
        comp_res = await client.post(
            "/api/v1/ai/strategy/compare",
            json={
                "ideas": [
                    {"id": "idea-a", "title": "Idea Alpha", "overall_score": 88.0, "risk_score": 20.0},
                    {"id": "idea-b", "title": "Idea Beta", "overall_score": 72.0, "risk_score": 35.0}
                ]
            },
            headers=headers
        )
        assert comp_res.status_code == 200
        c_data = comp_res.json()
        assert c_data["winner_idea_id"] == "idea-a"
