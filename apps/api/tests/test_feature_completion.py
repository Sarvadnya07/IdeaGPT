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
async def test_tech_stack_generation_endpoint():
    """
    Verifies that POST /api/v1/ai/tech-stack generates comprehensive 5-layer tech stack recommendations.
    """
    headers = _make_auth_header("user_tech_stack_test")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/ai/tech-stack",
            headers=headers,
            json={
                "title": "FinTech Ledger",
                "category": "FinTech / Security",
                "focus": "high_scale"
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["title"] == "FinTech Ledger"
        assert "frontend" in data
        assert "backend" in data
        assert "database_and_caching" in data
        assert "ai_and_ml" in data
        assert "devops_and_security" in data
        assert len(data["architectural_tradeoffs"]) > 0


@pytest.mark.asyncio
async def test_architecture_blueprint_endpoint():
    """
    Verifies that POST /api/v1/ai/architecture generates system topology, Mermaid diagram, and database entity models.
    """
    headers = _make_auth_header("user_arch_test")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/ai/architecture",
            headers=headers,
            json={
                "title": "HealthTech Platform",
                "category": "Healthcare SaaS",
                "description": "HIPAA-compliant telehealth platform"
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["title"] == "HealthTech Platform"
        assert "topology" in data
        assert "mermaid_diagram" in data
        assert "api_endpoints" in data
        assert "database_entities" in data
        assert "security_specifications" in data
        assert len(data["api_endpoints"]) >= 5


@pytest.mark.asyncio
async def test_prd_generation_endpoint():
    """
    Verifies that POST /api/v1/ai/prd generates a structured PRD with user personas and functional requirements.
    """
    headers = _make_auth_header("user_prd_test")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/ai/prd",
            headers=headers,
            json={
                "title": "AI Code Reviewer",
                "category": "Developer Tools",
                "problem_statement": "Manual code review is slow and error-prone.",
                "solution_description": "Automated AI code reviewer with instant semantic feedback.",
                "target_users": "Software Engineers"
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "PRD: AI Code Reviewer" in data["title"]
        assert "executive_summary" in data
        assert len(data["user_personas"]) >= 2
        assert len(data["functional_requirements"]) >= 3
        assert len(data["success_metrics"]) >= 2


@pytest.mark.asyncio
async def test_pitch_deck_generation_endpoint():
    """
    Verifies that POST /api/v1/ai/pitch-deck generates a 10-slide venture pitch deck outline.
    """
    headers = _make_auth_header("user_pitch_test")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/ai/pitch-deck",
            headers=headers,
            json={
                "title": "CloudOptimizer",
                "category": "DevOps / Infrastructure",
                "problem": "Companies waste millions on unoptimized cloud instances.",
                "solution": "Autonomous cloud instance optimizer."
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["title"] == "CloudOptimizer"
        assert len(data["slides"]) == 10
        assert data["slides"][0]["slide_number"] == 1
        assert data["slides"][9]["slide_number"] == 10


@pytest.mark.asyncio
async def test_export_markdown_and_json():
    """
    Verifies exporting evaluation payloads as Markdown and JSON.
    """
    headers = _make_auth_header("user_export_test")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Project
        p_res = await client.post(
            "/api/v1/projects/",
            headers=headers,
            json={"title": "Export Project", "slug": "export-proj-slug", "category": "SaaS"}
        )
        assert p_res.status_code in [200, 201]
        p_id = p_res.json()["id"]

        # Create Idea
        i_res = await client.post(
            f"/api/v1/projects/{p_id}/ideas",
            headers=headers,
            json={"title": "Export Idea", "problem_statement": "Export test problem", "solution_description": "Export test solution"}
        )
        assert i_res.status_code in [200, 201]
        i_id = i_res.json()["id"]

        # Trigger Evaluation
        e_res = await client.post(
            f"/api/v1/ideas/{i_id}/evaluations",
            headers=headers,
            json={"evaluation_type": "comprehensive"}
        )
        assert e_res.status_code == 200
        e_id = e_res.json()["id"]

        # Test Markdown Export
        res_md = await client.post(
            "/api/v1/exports/markdown",
            headers=headers,
            json={"evaluation_id": e_id}
        )
        assert res_md.status_code == 200
        md_data = res_md.json()
        assert "filename" in md_data
        assert "AI Idea Evaluation Report" in md_data["content"]

        # Test JSON Export
        res_json = await client.post(
            "/api/v1/exports/json",
            headers=headers,
            json={"evaluation_id": e_id}
        )
        assert res_json.status_code == 200
        json_data = res_json.json()
        assert "filename" in json_data
        assert "content" in json_data
