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


# ---------------------------------------------------------------------------
# 1. Edge Case: Tech Stack Endpoint
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_tech_stack_edge_cases():
    headers = _make_auth_header("user_tech_stack_edge")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Case A: Unknown / Exotic Category fallback to robust standard stack
        res_exotic = await client.post(
            "/api/v1/ai/tech-stack",
            headers=headers,
            json={"title": "Quantum Blockchain AI", "category": "Quantum Web3 BioTech", "focus": "exotic_mode"}
        )
        assert res_exotic.status_code == 200
        data_exotic = res_exotic.json()
        assert "frontend" in data_exotic
        assert "backend" in data_exotic

        # Case B: FinTech / Security Category picks specialized security stack
        res_fintech = await client.post(
            "/api/v1/ai/tech-stack",
            headers=headers,
            json={"title": "BankGuard", "category": "FinTech / High-Security Banking", "focus": "high_scale"}
        )
        assert res_fintech.status_code == 200
        data_fintech = res_fintech.json()
        assert "PostgreSQL" in data_fintech["database_and_caching"]["primary_database"]
        assert "Clerk" in data_fintech["devops_and_security"]["authentication"]

        # Case C: HealthTech Category picks HIPAA-compliant layers
        res_health = await client.post(
            "/api/v1/ai/tech-stack",
            headers=headers,
            json={"title": "MedRecord", "category": "Healthcare Telehealth", "focus": "balanced"}
        )
        assert res_health.status_code == 200
        data_health = res_health.json()
        assert "HIPAA" in data_health["backend"]["framework"] or "HIPAA" in data_health["devops_and_security"]["authentication"]


# ---------------------------------------------------------------------------
# 2. Edge Case: PRD & Pitch Deck Endpoints (Long Text & Validation)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_prd_and_pitch_deck_edge_cases():
    headers = _make_auth_header("user_prd_edge")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Case A: Empty strings in optional fields
        res_empty = await client.post(
            "/api/v1/ai/prd",
            headers=headers,
            json={"title": "Blank PRD", "category": "SaaS", "problem_statement": "", "solution_description": ""}
        )
        assert res_empty.status_code == 200
        assert "PRD: Blank PRD" in res_empty.json()["title"]

        # Case B: Exceeding max length (100+ chars in title)
        res_oversized = await client.post(
            "/api/v1/ai/prd",
            headers=headers,
            json={"title": "A" * 150, "category": "SaaS"}
        )
        assert res_oversized.status_code == 422  # Pydantic validation rejection

        # Case C: Pitch deck with special characters and unicode
        res_pitch = await client.post(
            "/api/v1/ai/pitch-deck",
            headers=headers,
            json={"title": "Über-App 🚀 (Inc.)", "category": "B2C AI", "problem": "Difficulties with 100% multilingual support € / $ / ¥"}
        )
        assert res_pitch.status_code == 200
        deck = res_pitch.json()
        assert len(deck["slides"]) == 10
        assert "Über-App 🚀 (Inc.)" in deck["title"]


# ---------------------------------------------------------------------------
# 3. Security & Authorization: Export Endpoints Isolation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_export_security_isolation():
    headers_user_a = _make_auth_header("user_export_sec_a")
    headers_user_b = _make_auth_header("user_export_sec_b")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # User A creates project, idea, and evaluation
        p = (await client.post("/api/v1/projects/", headers=headers_user_a, json={"title": "User A Private Proj", "slug": "proj-sec-a"})).json()["id"]
        i = (await client.post(f"/api/v1/projects/{p}/ideas", headers=headers_user_a, json={
            "title": "Idea A",
            "problem_statement": "Valid problem statement over 10 chars",
            "solution_description": "Valid solution description over 10 chars"
        })).json()["id"]
        e = (await client.post(f"/api/v1/ideas/{i}/evaluations", headers=headers_user_a, json={"evaluation_type": "comprehensive"})).json()["id"]

        # User B attempts to export User A's evaluation via Markdown (Forbidden / 404)
        res_md_b = await client.post("/api/v1/exports/markdown", headers=headers_user_b, json={"evaluation_id": e})
        assert res_md_b.status_code in [403, 404]

        # User B attempts to export User A's evaluation via JSON (Forbidden / 404)
        res_json_b = await client.post("/api/v1/exports/json", headers=headers_user_b, json={"evaluation_id": e})
        assert res_json_b.status_code in [403, 404]

        # Non-existent evaluation ID (404)
        res_nonexistent = await client.post("/api/v1/exports/markdown", headers=headers_user_a, json={"evaluation_id": "non-existent-uuid"})
        assert res_nonexistent.status_code == 404


# ---------------------------------------------------------------------------
# 4. Failure Mode & Boundary: Compare Ideas Matrix
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_compare_ideas_boundary_and_isolation():
    headers_a = _make_auth_header("user_compare_bound_a")
    headers_b = _make_auth_header("user_compare_bound_b")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Project & Ideas for User A
        p_a = (await client.post("/api/v1/projects/", headers=headers_a, json={"title": "Compare Proj A", "slug": "cmp-p-a"})).json()["id"]
        ideas_a = []
        for idx in range(6):
            i_id = (await client.post(f"/api/v1/projects/{p_a}/ideas", headers=headers_a, json={
                "title": f"Idea A-{idx}",
                "problem_statement": f"Valid problem statement {idx} over 10 chars",
                "solution_description": f"Valid solution description {idx} over 10 chars"
            })).json()["id"]
            ideas_a.append(i_id)

        # Create Project & Idea for User B
        p_b = (await client.post("/api/v1/projects/", headers=headers_b, json={"title": "Compare Proj B", "slug": "cmp-p-b"})).json()["id"]
        i_b = (await client.post(f"/api/v1/projects/{p_b}/ideas", headers=headers_b, json={
            "title": "Idea B-0",
            "problem_statement": "Valid problem statement for B over 10 chars",
            "solution_description": "Valid solution description for B over 10 chars"
        })).json()["id"]

        # Boundary A: Less than 2 ideas rejected with 400/422
        res_too_few = await client.post("/api/v1/evaluations/compare", headers=headers_a, json={"idea_ids": [ideas_a[0]]})
        assert res_too_few.status_code in [400, 422]

        # Boundary B: More than 5 ideas rejected with 400/422
        res_too_many = await client.post("/api/v1/evaluations/compare", headers=headers_a, json={"idea_ids": ideas_a[:6]})
        assert res_too_many.status_code in [400, 422]

        # Security: User A tries to include User B's idea in comparison (Tenant boundary violation -> 404/403)
        res_cross_user = await client.post("/api/v1/evaluations/compare", headers=headers_a, json={"idea_ids": [ideas_a[0], i_b]})
        assert res_cross_user.status_code in [403, 404]


# ---------------------------------------------------------------------------
# 5. Reliability: Analytics Date Filtering & Project Scoping
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_analytics_filter_and_project_scoping():
    headers = _make_auth_header("user_analytics_scoping")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 2 distinct projects
        p1 = (await client.post("/api/v1/projects/", headers=headers, json={"title": "Alpha Project", "slug": "alpha-proj"})).json()["id"]
        p2 = (await client.post("/api/v1/projects/", headers=headers, json={"title": "Beta Project", "slug": "beta-proj"})).json()["id"]

        # Add 2 ideas to Alpha, 1 to Beta
        await client.post(f"/api/v1/projects/{p1}/ideas", headers=headers, json={
            "title": "Alpha 1",
            "problem_statement": "Valid problem statement for Alpha 1",
            "solution_description": "Valid solution description for Alpha 1"
        })
        await client.post(f"/api/v1/projects/{p1}/ideas", headers=headers, json={
            "title": "Alpha 2",
            "problem_statement": "Valid problem statement for Alpha 2",
            "solution_description": "Valid solution description for Alpha 2"
        })
        await client.post(f"/api/v1/projects/{p2}/ideas", headers=headers, json={
            "title": "Beta 1",
            "problem_statement": "Valid problem statement for Beta 1",
            "solution_description": "Valid solution description for Beta 1"
        })

        # Query all projects analytics
        res_all = await client.get("/api/v1/analytics?range=all", headers=headers)
        assert res_all.status_code == 200
        data_all = res_all.json()
        assert data_all["summary"]["total_projects"] == 2
        assert data_all["summary"]["total_ideas"] == 3

        # Query scoped to Alpha project only
        res_p1 = await client.get(f"/api/v1/analytics?range=all&project_id={p1}", headers=headers)
        assert res_p1.status_code == 200
        data_p1 = res_p1.json()
        assert data_p1["summary"]["total_ideas"] == 2

        # Query scoped to Beta project only
        res_p2 = await client.get(f"/api/v1/analytics?range=all&project_id={p2}", headers=headers)
        assert res_p2.status_code == 200
        data_p2 = res_p2.json()
        assert data_p2["summary"]["total_ideas"] == 1
