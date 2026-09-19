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
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.ai_artifact import AIArtifact
from sqlalchemy import select

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
        assert "artifact_id" in data
        assert data.get("schema_version") == 1


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
        assert "artifact_id" in data
        assert data.get("schema_version") == 1


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
        assert "artifact_id" in data
        assert data.get("schema_version") == 1


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
        assert "artifact_id" in data
        assert data.get("schema_version") == 1


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
        assert "artifact_id" in data
        assert data.get("schema_version") == 1


async def _seed_lab_user_and_project(user_sub: str, user_id: int, project_id: str):
    """Helper to seed a user and a project for tenant isolation testing."""
    async with AsyncSessionLocal() as db:
        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if not user:
            user = User(id=user_id, clerk_id=user_sub, email=f"{user_sub}@example.com", name=f"User {user_sub}")
            db.add(user)
            await db.commit()

        proj_res = await db.execute(select(Project).where(Project.id == project_id))
        proj = proj_res.scalar_one_or_none()
        if not proj:
            proj = Project(id=project_id, user_id=user_id, title="Test Lab Project", slug=f"test-lab-{project_id}")
            db.add(proj)
            await db.commit()


@pytest.mark.asyncio
async def test_secondary_labs_persistence_and_querying():
    """Verify generated lab artifacts persist in DB and can be retrieved via /ai/artifacts."""
    sub = "user_lab_persistence"
    user_id = 901
    project_id = "proj-lab-persist-01"
    await _seed_lab_user_and_project(sub, user_id, project_id)
    headers = _make_auth_header(sub=sub)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Generate investor lab with project_id
        post_res = await client.post(
            "/api/v1/ai/labs/investor",
            headers=headers,
            json={
                "project_id": project_id,
                "title": "FinTech Matrix",
                "category": "FinTech",
                "market_size": "$10B Market",
                "target_raise": "$1M Pre-Seed"
            }
        )
        assert post_res.status_code == 200
        post_data = post_res.json()
        artifact_id = post_data["artifact_id"]
        assert artifact_id is not None

        # Query back via GET /api/v1/ai/artifacts
        get_res = await client.get(
            f"/api/v1/ai/artifacts?project_id={project_id}&artifact_type=investor_lab&limit=1",
            headers=headers
        )
        assert get_res.status_code == 200
        artifacts = get_res.json()
        assert len(artifacts) >= 1
        latest = artifacts[0]
        assert latest["id"] == artifact_id
        assert latest["artifact_type"] == "investor_lab"
        assert latest["project_id"] == project_id
        assert "valuation_range" in latest["content_payload"]


@pytest.mark.asyncio
async def test_secondary_labs_tenant_isolation_403():
    """Verify that attempting to attach a lab artifact to another user's project returns 403."""
    owner_sub = "user_lab_owner"
    owner_id = 902
    victim_proj_id = "proj-lab-owner-01"
    await _seed_lab_user_and_project(owner_sub, owner_id, victim_proj_id)

    attacker_sub = "user_lab_attacker"
    attacker_id = 903
    attacker_proj_id = "proj-lab-attacker-01"
    await _seed_lab_user_and_project(attacker_sub, attacker_id, attacker_proj_id)

    attacker_headers = _make_auth_header(sub=attacker_sub)

    endpoints = [
        ("/api/v1/ai/labs/github", {"project_id": victim_proj_id, "title": "Test"}),
        ("/api/v1/ai/labs/investor", {"project_id": victim_proj_id, "title": "Test"}),
        ("/api/v1/ai/labs/mentor", {"project_id": victim_proj_id, "title": "Test"}),
        ("/api/v1/ai/labs/recruiter", {"project_id": victim_proj_id, "title": "Test"}),
        ("/api/v1/ai/labs/strategy", {"project_id": victim_proj_id, "title": "Test"}),
        ("/api/v1/ai/strategy/analyze", {"project_id": victim_proj_id, "title": "Test"}),
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for ep, body in endpoints:
            res = await client.post(ep, headers=attacker_headers, json=body)
            assert res.status_code == 403, f"Endpoint {ep} should have returned 403, got {res.status_code}"
