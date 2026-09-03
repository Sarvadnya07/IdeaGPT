import pytest
import time
import jwt
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

settings.APP_ENV = "test"
settings.CLERK_JWT_TEST_SECRET = "test-secret-for-unit-tests-only-never-production"

TEST_SECRET = "test-secret-for-unit-tests-only-never-production"

def _make_auth_header(sub: str, email: str = None) -> dict:
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": email or f"{sub}@example.com",
        "iat": now,
        "exp": now + 3600,
        "iss": "https://healthy-sunbeam-68.clerk.accounts.dev"
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_analytics_zero_data():
    headers = _make_auth_header("user_analytics_zero")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/analytics", headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["time_range"] == "all"
        assert data["summary"]["total_projects"] == 0
        assert data["summary"]["total_ideas"] == 0
        assert data["summary"]["total_evaluations"] == 0
        assert data["summary"]["average_overall_score"] is None

        assert data["projects"]["total"] == 0
        assert data["ideas"]["total"] == 0
        assert data["evaluations"]["total"] == 0
        assert data["trends"] == []

@pytest.mark.asyncio
async def test_analytics_populated_reconciliation():
    headers = _make_auth_header("user_analytics_pop")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Project 1
        p1 = (await client.post(
            "/api/v1/projects/",
            json={"title": "Analytics Proj 1", "slug": "an-p1", "category": "SaaS"},
            headers=headers
        )).json()["id"]

        # Create Idea 1 in Proj 1
        i1 = (await client.post(
            f"/api/v1/projects/{p1}/ideas",
            json={
                "title": "SaaS Idea Alpha",
                "problem_statement": "Problem statement for Alpha",
                "solution_description": "Solution description for Alpha",
                "is_draft": False
            },
            headers=headers
        )).json()["id"]

        # Create Idea 2 (Draft) in Proj 1
        i2 = (await client.post(
            f"/api/v1/projects/{p1}/ideas",
            json={
                "title": "SaaS Idea Draft",
                "problem_statement": "Problem statement for Draft",
                "solution_description": "Solution description for Draft",
                "is_draft": True
            },
            headers=headers
        )).json()["id"]

        # Evaluate Idea 1
        e1 = await client.post(
            f"/api/v1/ideas/{i1}/evaluations",
            json={"evaluation_type": "full"},
            headers=headers
        )
        assert e1.status_code == 201

        # Query Analytics
        res = await client.get("/api/v1/analytics", headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["summary"]["total_projects"] == 1
        assert data["summary"]["total_ideas"] == 2
        assert data["summary"]["total_evaluations"] == 1
        assert data["summary"]["completed_evaluations"] == 1
        assert data["summary"]["average_overall_score"] is not None

        assert data["ideas"]["drafts"] == 1
        assert data["ideas"]["published"] == 1

        assert data["evaluations"]["completed"] == 1
        assert len(data["trends"]) >= 1

@pytest.mark.asyncio
async def test_analytics_user_isolation():
    headers_a = _make_auth_header("user_analytics_user_a")
    headers_b = _make_auth_header("user_analytics_user_b")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # User A creates data
        p_a = (await client.post(
            "/api/v1/projects/",
            json={"title": "Private Proj A", "slug": "priv-pa"},
            headers=headers_a
        )).json()["id"]

        await client.post(
            f"/api/v1/projects/{p_a}/ideas",
            json={"title": "Idea A", "problem_statement": "Problem statement for Idea A", "solution_description": "Solution description for Idea A"},
            headers=headers_a
        )

        # User B queries analytics -> receives 0 totals
        res_b = await client.get("/api/v1/analytics", headers=headers_b)
        assert res_b.status_code == 200
        data_b = res_b.json()

        assert data_b["summary"]["total_projects"] == 0
        assert data_b["summary"]["total_ideas"] == 0
        assert data_b["summary"]["total_evaluations"] == 0
