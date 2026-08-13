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
async def test_compare_2_ideas_success():
    headers = _make_auth_header("user_comp_succ")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        p_res = await client.post(
            "/api/v1/projects/",
            json={"title": "Compare Proj A", "slug": "compare-proj-a"},
            headers=headers
        )
        assert p_res.status_code == 200
        proj_id = p_res.json()["id"]

        i1_res = await client.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "Alpha Platform",
                "problem_statement": "Problem statement for Alpha",
                "solution_description": "Solution description for Alpha",
                "target_users": "Developers",
                "industry": "Developer Tools",
                "business_model": "SaaS Subscription",
                "stage": "MVP",
                "is_draft": False
            },
            headers=headers
        )
        assert i1_res.status_code == 200
        idea1_id = i1_res.json()["id"]

        i2_res = await client.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "Beta App",
                "problem_statement": "Problem statement for Beta",
                "solution_description": "Solution description for Beta",
                "is_draft": False
            },
            headers=headers
        )
        assert i2_res.status_code == 200
        idea2_id = i2_res.json()["id"]

        e1_res = await client.post(
            f"/api/v1/ideas/{idea1_id}/evaluations",
            json={"evaluation_type": "full"},
            headers=headers
        )
        assert e1_res.status_code == 200

        comp_res = await client.post(
            "/api/v1/evaluations/compare",
            json={"idea_ids": [idea1_id, idea2_id]},
            headers=headers
        )
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert comp_data["compared_count"] == 2
        assert comp_data["highest_score_idea_id"] == idea1_id

        items = comp_data["ideas"]
        assert len(items) == 2
        assert items[0]["idea_id"] == idea1_id
        assert items[0]["evaluation_status"] == "evaluated"
        assert items[0]["overall_score"] is not None

        assert items[1]["idea_id"] == idea2_id
        assert items[1]["evaluation_status"] == "unevaluated"
        assert items[1]["overall_score"] is None

@pytest.mark.asyncio
async def test_compare_validation_rejections():
    headers = _make_auth_header("user_comp_rej")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        p_res = await client.post("/api/v1/projects/", json={"title": "P", "slug": "p-rej"}, headers=headers)
        proj_id = p_res.json()["id"]
        i_res = await client.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={"title": "Idea Rej", "problem_statement": "Problem statement long enough", "solution_description": "Solution description long enough"},
            headers=headers
        )
        assert i_res.status_code == 200
        idea_id = i_res.json()["id"]

        # Less than 2 ideas -> 400
        res_less = await client.post("/api/v1/evaluations/compare", json={"idea_ids": [idea_id]}, headers=headers)
        assert res_less.status_code == 400

        # Duplicate ideas -> 400
        res_dup = await client.post("/api/v1/evaluations/compare", json={"idea_ids": [idea_id, idea_id]}, headers=headers)
        assert res_dup.status_code == 400

@pytest.mark.asyncio
async def test_compare_unauthorized_idea_matrix():
    headers_a = _make_auth_header("user_comp_sec_a")
    headers_b = _make_auth_header("user_comp_sec_b")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        pa = (await client.post("/api/v1/projects/", json={"title": "PA", "slug": "pa-sec"}, headers=headers_a)).json()["id"]
        ia = (await client.post(
            f"/api/v1/projects/{pa}/ideas",
            json={"title": "IA", "problem_statement": "Problem statement long enough", "solution_description": "Solution description long enough"},
            headers=headers_a
        )).json()["id"]

        pb = (await client.post("/api/v1/projects/", json={"title": "PB", "slug": "pb-sec"}, headers=headers_b)).json()["id"]
        ib = (await client.post(
            f"/api/v1/projects/{pb}/ideas",
            json={"title": "IB", "problem_statement": "Problem statement long enough", "solution_description": "Solution description long enough"},
            headers=headers_b
        )).json()["id"]

        # User B trying to compare User A's idea -> 403 Forbidden
        res_unauth = await client.post("/api/v1/evaluations/compare", json={"idea_ids": [ia, ib]}, headers=headers_b)
        assert res_unauth.status_code == 403
