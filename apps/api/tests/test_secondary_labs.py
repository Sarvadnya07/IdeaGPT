"""
Integration and Deterministic Fallback Tests for the 5 Secondary Labs:
- GitHub Lab
- Investor Lab
- Mentor Lab
- Recruiter Lab
- Strategy Lab
"""

import pytest
import time
import jwt
from httpx import AsyncClient, ASGITransport
from app.main import app

TEST_SECRET = "test-secret-for-unit-tests-only-never-production"


def _make_auth_header(sub: str = "user_secondary_labs") -> dict:
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


@pytest.mark.asyncio
async def test_github_lab_generation():
    """Verify GitHub Lab repository scaffolding and CI/CD workflow generation."""
    headers = _make_auth_header()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/ai/labs/github",
            headers=headers,
            json={
                "title": "CloudPulse Monitoring",
                "category": "DevOps / Observability",
                "tech_stack": "Next.js, FastAPI, PostgreSQL, Redis"
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "repository_name" in data
        assert "directory_tree" in data
        assert len(data["directory_tree"]) > 0
        assert "ci_cd_workflow" in data
        assert "dockerfile" in data
        assert "readme_content" in data


@pytest.mark.asyncio
async def test_investor_lab_generation():
    """Verify Investor Lab institutional valuation and cap table generation."""
    headers = _make_auth_header()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/ai/labs/investor",
            headers=headers,
            json={
                "title": "MedRecord AI",
                "category": "HealthTech",
                "market_size": "$24B Global Market",
                "target_raise": "$2.0M Seed"
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "valuation_range" in data
        assert "investor_scorecard" in data
        assert data["investor_scorecard"]["market_opportunity"] > 0
        assert "funding_stages" in data
        assert "cap_table_simulation" in data
        assert "risk_matrix" in data


@pytest.mark.asyncio
async def test_mentor_lab_generation():
    """Verify Mentor Lab founder coaching and 30-60-90 day plan."""
    headers = _make_auth_header()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/ai/labs/mentor",
            headers=headers,
            json={
                "title": "FinGuard Payments",
                "category": "FinTech",
                "stage": "Seed Stage",
                "challenges": "Enterprise compliance onboarding and banking partner integration"
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "mentor_persona" in data
        assert "executive_coaching_summary" in data
        assert len(data["top_founder_blindspots"]) >= 3
        assert len(data["applied_mental_models"]) >= 3
        assert "execution_plan_30_60_90" in data
        assert len(data["execution_plan_30_60_90"]["days_30"]) > 0


@pytest.mark.asyncio
async def test_recruiter_lab_generation():
    """Verify Recruiter Lab hiring roadmap and compensation benchmarks."""
    headers = _make_auth_header()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/ai/labs/recruiter",
            headers=headers,
            json={
                "title": "DevPilot AI",
                "category": "Developer Tools",
                "current_team_size": "2 Founders",
                "target_roles": "Founding Engineer, Growth Lead"
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "hiring_roadmap" in data
        assert len(data["job_descriptions"]) >= 2
        assert "interview_scorecard" in data
        assert "compensation_range" in data["job_descriptions"][0]


@pytest.mark.asyncio
async def test_strategy_lab_generation():
    """Verify Strategy Lab Porter's Five Forces and Blue Ocean Canvas."""
    headers = _make_auth_header()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/ai/labs/strategy",
            headers=headers,
            json={
                "title": "OmniVoice AI",
                "category": "B2B Audio AI",
                "competitors": "Generic Voice Assistants",
                "value_proposition": "Sub-100ms real-time audio intelligence for medical encounters"
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert len(data["porter_five_forces"]) == 5
        assert "blue_ocean_strategy" in data
        assert "defensibility_moat_breakdown" in data
        assert len(data["pricing_model_matrix"]) >= 3
        assert "gtm_growth_engine" in data
