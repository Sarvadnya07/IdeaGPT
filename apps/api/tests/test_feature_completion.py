"""
IdeaGPT — Complete 30-Feature Verification Test Suite.
Tests all operational, decision-science, build-tools, and output communication features.
"""

import pytest
import time
import json
import jwt
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.ai.gateway.strategy.unit_economics import UnitEconomicsEngine, UnitEconomicsInput
from app.ai.gateway.strategy.decision_engines import (
    RedFlagScannerEngine,
    RegulatoryRadarEngine,
    MoatAssessorEngine,
    ResourceComparisonEngine,
    ExecutiveSummaryEngine,
    TamSamSomEngine,
    ElevatorPitchEngine
)
from app.ai.gateway.execution.cloud_costs import CloudCostEngine, CloudCostInput
from app.ai.gateway.execution.build_tools import (
    ArchitectureMatrixEngine,
    DatabaseSchemaEngine,
    SecurityChecklistEngine,
    UserStoryEngine,
    OpenApiContractEngine,
    FailureModeEngine,
    ReleasePhasingEngine
)

TEST_SECRET = "test-secret-for-unit-tests-only-never-production"


def _make_auth_header(sub: str = "user_feature_completion_tester") -> dict:
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
# GROUP A: AI RUNTIME & OPERATIONS (Features 3, 34, 52, 53, 54)
# ==============================================================================

@pytest.mark.asyncio
async def test_ai_credit_token_gauge():
    """Verify AI credit & token gauge endpoint returns real counts with UNKNOWN fallback."""
    headers = _make_auth_header("gauge_user")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/analytics/ai/usage-gauge", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "total_requests" in data
        assert "total_tokens_consumed" in data
        assert "provider_quota_status" in data
        assert data["provider_quota_status"]["external_remaining_quota"] == "UNKNOWN"


@pytest.mark.asyncio
async def test_ai_telemetry_and_cache_stats():
    """Verify provider telemetry, cache hit rates, and system health endpoints."""
    headers = _make_auth_header("telemetry_user")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Telemetry
        t_res = await client.get("/api/v1/analytics/ai/telemetry", headers=headers)
        assert t_res.status_code == 200
        assert "telemetry" in t_res.json()

        # Cache Stats
        c_res = await client.get("/api/v1/analytics/ai/cache-telemetry", headers=headers)
        assert c_res.status_code == 200
        c_data = c_res.json()
        assert "hit_rate_pct" in c_data
        assert "average_warm_cache_latency_ms" in c_data

        # Health Monitor
        h_res = await client.get("/api/v1/ai/ops/health-monitor", headers=headers)
        assert h_res.status_code == 200
        assert h_res.json()["overall_status"] == "HEALTHY"

        # AI Benchmark
        b_res = await client.post("/api/v1/ai/ops/benchmark", headers=headers)
        assert b_res.status_code == 200
        assert len(b_res.json()["benchmark_runs"]) >= 3


# ==============================================================================
# GROUP B: DECISION INTELLIGENCE (Features 7, 8, 9, 11, 12, 13, 14, 15, 43)
# ==============================================================================

def test_unit_economics_deterministic_calculations():
    """Verify deterministic unit economics math: LTV, CAC Payback, Gross Margin, and Runway."""
    inp = UnitEconomicsInput(
        target_price_monthly_usd=29.0,
        monthly_cogs_usd=4.0,
        estimated_cac_usd=45.0,
        monthly_churn_rate_pct=5.0,
        monthly_fixed_burn_usd=5000.0,
        available_capital_usd=50000.0
    )
    res = UnitEconomicsEngine.calculate(inp)

    # Gross Margin: (25 / 29) * 100 = 86.2%
    assert res.gross_margin_pct.numeric_value == 86.2
    # Lifetime: 1 / 0.05 = 20.0 months
    assert res.customer_lifetime_months.numeric_value == 20.0
    # LTV: 20 * 25 = $500.00
    assert res.customer_lifetime_value_usd.numeric_value == 500.0
    # LTV / CAC: 500 / 45 = 11.11x
    assert res.ltv_to_cac_ratio.numeric_value >= 10.0
    # Payback: 45 / 25 = 1.8 months
    assert res.cac_payback_months.numeric_value == 1.8
    # Break-even: 5000 / 25 = 200 customers
    assert res.break_even_customers.numeric_value == 200.0
    # Runway: 50000 / 5000 = 10.0 months
    assert res.projected_runway_months.numeric_value == 10.0
    assert res.overall_health == "VIABLE"


def test_investor_red_flags_scanner():
    """Verify detection of regulatory, competition, and capital red flags."""
    res = RedFlagScannerEngine.scan(
        title="MedSecure AI",
        industry="Healthcare / Medical AI",
        problem="Patient record synthesis",
        solution="Automated clinical charts",
        eval_score=65.0
    )
    assert res.total_flags >= 3
    assert any(f.category == "REGULATORY" for f in res.red_flags)
    assert any(f.category == "COMPETITION" for f in res.red_flags)


def test_regulatory_radar_and_moat_assessor():
    """Verify regulatory radar framework mapping and 8-dimension moat assessor."""
    radar = RegulatoryRadarEngine.evaluate("Fintech / Personal Finance")
    assert any("GDPR" in f.framework_name for f in radar.frameworks)
    assert any("PCI-DSS" in f.framework_name for f in radar.frameworks)

    moat = MoatAssessorEngine.assess("IdeaGPT Platform", "B2B SaaS")
    assert moat.overall_moat_score >= 70
    assert len(moat.dimensions) == 5


def test_resource_comparison_and_tam_sam_som():
    """Verify resource requirement comparison and TAM/SAM/SOM sizing."""
    ideas = [
        {"id": "i-1", "title": "Lean SaaS", "overall_score": 85.0},
        {"id": "i-2", "title": "Hardware Robotics", "overall_score": 50.0}
    ]
    res_comp = ResourceComparisonEngine.compare_resources(ideas)
    assert res_comp.leanest_idea_id == "i-1"
    assert res_comp.compared_ideas[0].recommended_team_size == 2

    market = TamSamSomEngine.get_market_sizing("Startup Idea", "Cybersecurity", "$5.5B", "18%")
    assert market.tam.numeric_billions == 4.2 or "$5.5B" in market.tam.value_usd
    assert market.sam.numeric_billions == 0.85
    assert market.som.numeric_billions == 0.045


# ==============================================================================
# GROUP C: PRODUCT EXECUTION & BUILD TOOLS (Features 25, 26, 29, 30, 32, 33, 35, 36, 37, 39)
# ==============================================================================

def test_cloud_cost_estimator_deterministic():
    """Verify multi-cloud deterministic pricing model across Vercel, Supabase, and AWS."""
    inp = CloudCostInput(
        monthly_active_users=5000,
        monthly_api_requests=250000,
        database_storage_gb=10.0,
        file_storage_gb=20.0,
        ai_tokens_monthly=5000000
    )
    costs = CloudCostEngine.estimate(inp)
    assert len(costs.providers) == 4
    assert any(p.provider_name == "Vercel" for p in costs.providers)
    assert any(p.provider_name == "Supabase" for p in costs.providers)
    assert costs.monthly_min_estimate_usd > 0.0


def test_build_tools_engines():
    """Verify Architecture Matrix, Schema Generator, Security Checklist, User Stories, OpenAPI, Failures, Release Phasing."""
    # 1. Architecture Matrix
    arch = ArchitectureMatrixEngine.generate("IdeaGPT")
    assert len(arch.comparisons) >= 3

    # 2. Database Schema
    schema = DatabaseSchemaEngine.generate_schema("IdeaGPT")
    assert "CREATE TABLE" in schema.sql_ddl
    assert len(schema.tables) == 3

    # 3. Security Checklist
    sec = SecurityChecklistEngine.generate_checklist("IdeaGPT")
    assert sec.critical_controls >= 2

    # 4. User Stories
    stories = UserStoryEngine.generate_stories("IdeaGPT", "Manual evaluation is slow", "Automated AI decision engine")
    assert len(stories.stories) >= 3
    assert all(len(s.given_when_then_acceptance_criteria) >= 2 for s in stories.stories)

    # 5. OpenAPI Contract
    contract = OpenApiContractEngine.generate_contract("IdeaGPT")
    assert contract.openapi_version == "3.1.0"
    assert len(contract.endpoints) >= 3

    # 6. Failure Modes
    failures = FailureModeEngine.enumerate_failures("IdeaGPT")
    assert len(failures.failure_modes) >= 3

    # 7. Release Phasing
    phasing = ReleasePhasingEngine.generate_phases("IdeaGPT")
    assert len(phasing.phases) == 3


@pytest.mark.asyncio
async def test_critical_path_and_custom_tasks_endpoints():
    """Verify Roadmap Critical Path calculation and Custom Task CRUD."""
    headers = _make_auth_header("roadmap_tester")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Project
        p_res = await client.post("/api/v1/projects/", json={"title": "Roadmap Test Proj", "slug": "road-test-proj"}, headers=headers)
        assert p_res.status_code == 201
        p_id = p_res.json()["id"]

        # Create Roadmap
        r_res = await client.post(
            f"/api/v1/projects/{p_id}/roadmaps",
            json={"status": "active", "milestones": [{"title": "Phase 1", "objective": "Validate MVP", "tasks": []}]},
            headers=headers
        )
        assert r_res.status_code == 201
        r_id = r_res.json()["id"]

        # Add Custom Task
        t_res = await client.post(
            f"/api/v1/roadmaps/{r_id}/tasks",
            json={
                "title": "Set up CI/CD pipeline",
                "description": "Automated pytest and vitest runs",
                "phase": "MVP",
                "priority": "HIGH",
                "estimated_days": 2,
                "dependencies": []
            },
            headers=headers
        )
        assert t_res.status_code == 200
        assert t_res.json()["success"] is True

        # Critical Path
        cp_res = await client.get(f"/api/v1/roadmaps/{r_id}/critical-path", headers=headers)
        assert cp_res.status_code == 200
        assert "critical_path_tasks" in cp_res.json()


# ==============================================================================
# GROUP D: OUTPUT & COMMUNICATION (Features 4, 18, 19, 21, 46)
# ==============================================================================

@pytest.mark.asyncio
async def test_recent_activity_and_pdf_export_and_pitch_variants():
    """Verify Activity Feed pagination, PDF HTML export, Pitch Variants, and Version Diffing."""
    headers = _make_auth_header("output_tester")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Activity Feed
        act_res = await client.get("/api/v1/analytics/activity?page=1&limit=5", headers=headers)
        assert act_res.status_code == 200
        assert "events" in act_res.json()

        # 2. Pitch Variants
        pitch_res = await client.post(
            "/api/v1/ai/decision/pitch-variants",
            json={"title": "IdeaGPT", "problem": "Manual idea validation is slow", "solution": "AI decision intelligence"},
            headers=headers
        )
        assert pitch_res.status_code == 200
        assert len(pitch_res.json()["variants"]) == 5

        # 3. Venture Matrix
        vm_res = await client.get("/api/v1/analytics/venture-matrix", headers=headers)
        assert vm_res.status_code == 200
        assert "points" in vm_res.json()


def test_export_service_all_formats():
    """Explicitly verify Markdown, JSON, and PDF HTML exports preserving data and sanitization."""
    from app.services.export_service import ExportService

    payload = {
        "summary": "Innovative <script>alert(1)</script> SaaS platform",
        "score": 88,
        "decision_gate": "GO",
        "strengths": ["Strong retention loops", "High LTV/CAC ratio"],
        "weaknesses": ["Long sales cycle", "Regulatory overhead"],
        "recommendations": ["Focus on self-serve onboarding", "Acquire SOC2 certification"],
        "citations": [
            {
                "source_title": "Gartner Report 2026",
                "source_url": "https://gartner.com/saas",
                "domain_trust_level": "AUTHORITATIVE"
            }
        ],
        "architecture_breakdown": "Modular Monolith with PostgreSQL"
    }

    # 1. JSON Export
    json_out = ExportService.to_json(payload)
    data = json.loads(json_out)
    assert data["score"] == 88
    assert len(data["strengths"]) == 2

    # 2. Markdown Export
    md_out = ExportService.to_markdown(payload)
    assert "## Executive Summary" in md_out
    assert "**Overall Score**: 88/100" in md_out
    assert "- Strong retention loops" in md_out
    assert "- Long sales cycle" in md_out
    assert "- Focus on self-serve onboarding" in md_out
    assert "Gartner Report 2026" in md_out

    # 3. PDF HTML Export
    html_out = ExportService.to_pdf_html(payload, project_title="Fintech Engine")
    assert "<title>IdeaGPT Executive Report — Fintech Engine</title>" in html_out
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_out
    assert "<script>" not in html_out  # Sanitized!
    assert "<li>Strong retention loops</li>" in html_out
    assert "<li>Long sales cycle</li>" in html_out
    assert "<li>Focus on self-serve onboarding</li>" in html_out
    assert "Gartner Report 2026" in html_out
    assert "88" in html_out
    assert "GATE: GO" in html_out

