"""
Sprint 2.4 — Idea Domain Hardening Test Suite

Comprehensive tests for Idea model validation, CRUD lifecycle, draft workflow,
duplication contract, hard deletion, search integration, and cross-user authorization.
"""
import os
import time
import pytest
import jwt as pyjwt
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select

from app.main import app
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea

TEST_SECRET = os.environ.get("CLERK_JWT_TEST_SECRET", "test-secret-for-unit-tests-only-never-production")

def _make_token(sub: str, email: str = "test@domain.com") -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": email,
        "iat": now,
        "exp": now + 3600,
        "iss": "https://healthy-sunbeam-68.clerk.accounts.dev"
    }
    return pyjwt.encode(payload, TEST_SECRET, algorithm="HS256")


# ============================================================
# 1. PYDANTIC VALIDATION TESTS
# ============================================================

@pytest.mark.asyncio
async def test_idea_pydantic_validation_edge_cases():
    """Verify backend enforces length and type validation rules for idea creation and updates."""
    token = _make_token("user_val_idea_001")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create project first
        res_p = await ac.post("/api/v1/projects/", json={"title": "Validation Project"}, headers=headers)
        proj_id = res_p.json()["id"]

        # 1. Missing required title -> 422
        r1 = await ac.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "problem_statement": "Valid problem statement length 10",
                "solution_description": "Valid solution description length 10"
            },
            headers=headers
        )
        assert r1.status_code == 422

        # 2. Empty title -> 422
        r2 = await ac.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "",
                "problem_statement": "Valid problem statement length 10",
                "solution_description": "Valid solution description length 10"
            },
            headers=headers
        )
        assert r2.status_code == 422

        # 3. Excessive title length (> 100) -> 422
        r3 = await ac.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "T" * 105,
                "problem_statement": "Valid problem statement length 10",
                "solution_description": "Valid solution description length 10"
            },
            headers=headers
        )
        assert r3.status_code == 422

        # 4. Short problem_statement (< 10) -> 422
        r4 = await ac.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "Valid Title",
                "problem_statement": "Too short",
                "solution_description": "Valid solution description length 10"
            },
            headers=headers
        )
        assert r4.status_code == 422

        # 5. Short solution_description (< 10) -> 422
        r5 = await ac.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "Valid Title",
                "problem_statement": "Valid problem statement length 10",
                "solution_description": "Short"
            },
            headers=headers
        )
        assert r5.status_code == 422

        # 6. Valid complete idea payload -> 200
        valid_payload = {
            "title": "Complete Multi-Agent IDE",
            "problem_statement": "Developers spend hours orchestrating AI tools manually across terminals.",
            "solution_description": "An autonomous multi-agent background executor integrated directly into the workspace.",
            "target_users": "Full-Stack Developers",
            "industry": "Software Engineering",
            "business_model": "Freemium SaaS",
            "stage": "Beta",
            "tags": "ai,agents,developer-tools",
            "notes": "Internal design phase notes.",
            "is_draft": True
        }
        r_valid = await ac.post(f"/api/v1/projects/{proj_id}/ideas", json=valid_payload, headers=headers)
        assert r_valid.status_code == 200
        assert r_valid.json()["target_users"] == "Full-Stack Developers"


# ============================================================
# 2. DRAFT WORKFLOW & UPDATE IMMUTABILITY TESTS
# ============================================================

@pytest.mark.asyncio
async def test_idea_draft_workflow_and_immutability():
    """Verify draft workflow (is_draft True -> False) and protect immutable fields (project_id, id)."""
    token = _make_token("user_draft_001")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_p = await ac.post("/api/v1/projects/", json={"title": "Draft Workflow Project"}, headers=headers)
        proj_id = res_p.json()["id"]

        # Step 1: Create draft idea (is_draft=True)
        res_c = await ac.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "Draft Idea Version 1",
                "problem_statement": "Initial problem definition for draft idea.",
                "solution_description": "Initial solution definition for draft idea.",
                "is_draft": True
            },
            headers=headers
        )
        assert res_c.status_code == 200
        idea_data = res_c.json()
        idea_id = idea_data["id"]
        assert idea_data["is_draft"] is True

        # Step 2: Retrieve draft
        res_g1 = await ac.get(f"/api/v1/ideas/{idea_id}", headers=headers)
        assert res_g1.json()["is_draft"] is True

        # Step 3: Update draft to non-draft (is_draft=False) + attempt malicious project_id re-assignment
        res_u = await ac.patch(
            f"/api/v1/ideas/{idea_id}",
            json={
                "title": "Finalized Idea Version 1",
                "is_draft": False,
                "project_id": "malicious-fake-project-id"  # Must be ignored/protected
            },
            headers=headers
        )
        assert res_u.status_code == 200
        updated = res_u.json()
        assert updated["title"] == "Finalized Idea Version 1"
        assert updated["is_draft"] is False
        assert updated["project_id"] == proj_id  # project_id remained original

        # Verify SQL DB persistence
        async with AsyncSessionLocal() as db:
            db_idea = (await db.execute(select(Idea).where(Idea.id == idea_id))).scalar_one_or_none()
            assert db_idea.is_draft is False
            assert db_idea.project_id == proj_id


# ============================================================
# 3. IDEA DUPLICATION CONTRACT TESTS
# ============================================================

@pytest.mark.asyncio
async def test_idea_duplication_contract():
    """
    Verify duplication contract:
      - Original remains unchanged.
      - Duplicate receives fresh UUID id.
      - Duplicate belongs to same project_id.
      - Title is copied as `title (Copy)`.
      - Duplicate has is_draft=True.
      - Fresh timestamps.
      - Original and duplicate are 100% independent.
    """
    token = _make_token("user_dup_idea_001")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_p = await ac.post("/api/v1/projects/", json={"title": "Duplication Project"}, headers=headers)
        proj_id = res_p.json()["id"]

        res_c = await ac.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "Original Idea Title",
                "problem_statement": "Original problem statement long enough.",
                "solution_description": "Original solution description long enough.",
                "target_users": "Architects",
                "is_draft": False  # Original is non-draft
            },
            headers=headers
        )
        orig_id = res_c.json()["id"]

        # Duplicate the idea
        res_dup = await ac.post(f"/api/v1/ideas/{orig_id}/duplicate", headers=headers)
        assert res_dup.status_code == 200
        dup = res_dup.json()

        # Contract assertions
        assert dup["id"] != orig_id
        assert dup["project_id"] == proj_id
        assert dup["title"] == "Original Idea Title (Copy)"
        assert dup["problem_statement"] == "Original problem statement long enough."
        assert dup["is_draft"] is True  # Duplicate MUST start as draft

        # Verify SQL DB holds both rows independently
        async with AsyncSessionLocal() as db:
            orig_db = (await db.execute(select(Idea).where(Idea.id == orig_id))).scalar_one_or_none()
            dup_db = (await db.execute(select(Idea).where(Idea.id == dup["id"]))).scalar_one_or_none()
            assert orig_db.title == "Original Idea Title"
            assert orig_db.is_draft is False
            assert dup_db.title == "Original Idea Title (Copy)"
            assert dup_db.is_draft is True


# ============================================================
# 4. IDEA HARD DELETION CONTRACT TESTS
# ============================================================

@pytest.mark.asyncio
async def test_idea_hard_deletion_contract():
    """Verify hard delete removes row completely from PostgreSQL ideas table."""
    token = _make_token("user_hard_del_001")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_p = await ac.post("/api/v1/projects/", json={"title": "Hard Delete Project"}, headers=headers)
        proj_id = res_p.json()["id"]

        res_c = await ac.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "Idea To Delete",
                "problem_statement": "Problem statement for deletion testing.",
                "solution_description": "Solution description for deletion testing."
            },
            headers=headers
        )
        idea_id = res_c.json()["id"]

        # Delete the idea
        res_del = await ac.delete(f"/api/v1/ideas/{idea_id}", headers=headers)
        assert res_del.status_code == 200

        # Verify GET returns 404
        res_g = await ac.get(f"/api/v1/ideas/{idea_id}", headers=headers)
        assert res_g.status_code == 404

        # Verify SQL DB row is removed
        async with AsyncSessionLocal() as db:
            db_idea = (await db.execute(select(Idea).where(Idea.id == idea_id))).scalar_one_or_none()
            assert db_idea is None, "Hard delete must remove idea row from ideas table"


# ============================================================
# 5. GLOBAL SEARCH INTEGRATION & ISOLATION TESTS
# ============================================================

@pytest.mark.asyncio
async def test_global_search_idea_matching_and_user_isolation():
    """
    GET /api/v1/search?q=...
    Verifies matching across title, problem, solution, tags.
    Verifies User A search results NEVER include User B's ideas.
    Verifies ideas in soft-deleted projects are excluded.
    """
    token_a = _make_token("user_search_a", "search_a@domain.com")
    token_b = _make_token("user_search_b", "search_b@domain.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create Project A & Idea A (with unique tag 'quantum-fusion')
        res_pa = await ac.post("/api/v1/projects/", json={"title": "Search Project A"}, headers=headers_a)
        proj_a_id = res_pa.json()["id"]

        await ac.post(
            f"/api/v1/projects/{proj_a_id}/ideas",
            json={
                "title": "Quantum Fusion Reactor",
                "problem_statement": "Plasma containment stability issues.",
                "solution_description": "Magnetic field alignment via neural network feedback.",
                "tags": "quantum-fusion,clean-energy"
            },
            headers=headers_a
        )

        # Create Project B & Idea B (also matching 'quantum-fusion')
        res_pb = await ac.post("/api/v1/projects/", json={"title": "Search Project B"}, headers=headers_b)
        proj_b_id = res_pb.json()["id"]

        await ac.post(
            f"/api/v1/projects/{proj_b_id}/ideas",
            json={
                "title": "Quantum Fusion Secret B",
                "problem_statement": "Confidential research on fusion power.",
                "solution_description": "Confidential tokamak design details.",
                "tags": "quantum-fusion,secret"
            },
            headers=headers_b
        )

        # User A searches 'quantum-fusion'
        res_sa = await ac.get("/api/v1/search?q=quantum-fusion", headers=headers_a)
        assert res_sa.status_code == 200
        data_a = res_sa.json()
        results_a = data_a["results"]
        titles_a = [r["title"] for r in results_a]

        assert "Quantum Fusion Reactor" in titles_a
        assert "Quantum Fusion Secret B" not in titles_a, "User A must NEVER see User B's search results"

        # User B searches 'quantum-fusion'
        res_sb = await ac.get("/api/v1/search?q=quantum-fusion", headers=headers_b)
        assert res_sb.status_code == 200
        results_b = res_sb.json()["results"]
        titles_b = [r["title"] for r in results_b]

        assert "Quantum Fusion Secret B" in titles_b
        assert "Quantum Fusion Reactor" not in titles_b, "User B must NEVER see User A's search results"

        # Soft delete Project A
        await ac.delete(f"/api/v1/projects/{proj_a_id}", headers=headers_a)

        # User A searches again -> soft-deleted project ideas must NOT be returned
        res_sa2 = await ac.get("/api/v1/search?q=quantum-fusion", headers=headers_a)
        results_a2 = res_sa2.json()["results"]
        titles_a2 = [r["title"] for r in results_a2]
        assert "Quantum Fusion Reactor" not in titles_a2, "Soft-deleted project ideas must be excluded from search"


# ============================================================
# 6. CQ-01 STRUCTURED METADATA PERSISTENCE & EVALUATION CONTEXT
# ============================================================

@pytest.mark.asyncio
async def test_idea_cq01_structured_metadata_persistence_and_evaluation_context():
    """
    CQ-01 Regression Test:
    Verifies that structured idea definitions (including custom USP, tech stack,
    budget, timeline serialized into notes JSON) are:
      1. Successfully persisted via POST /api/v1/projects/{id}/ideas
      2. Accurately retrieved via GET /api/v1/ideas/{id}
      3. Accurately updated via PATCH /api/v1/ideas/{id}
      4. Fully retained upon POST /api/v1/ideas/{id}/duplicate
      5. Accessible to ContextBuilder for AI evaluation pipeline
    """
    import json
    from app.ai.pipelines.context import ContextBuilder

    token = _make_token("user_cq01_test_001")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create parent project
        res_p = await ac.post("/api/v1/projects/", json={"title": "CQ-01 Test Project"}, headers=headers)
        proj_id = res_p.json()["id"]

        custom_notes = json.dumps({
            "usp": "10x faster deterministic evaluation engine",
            "tech_stack": "Next.js 14, FastAPI, PostgreSQL, Asyncpg",
            "budget": "$15,000",
            "timeline": "Q4 2026"
        })

        # 1. Create Idea with structured notes metadata
        res_create = await ac.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "Autonomous DevOps Agent",
                "problem_statement": "Infrastructure deployment requires manual configuration and debugging.",
                "solution_description": "An autonomous AI agent managing Terraform, Docker, and Kubernetes deployment workflows.",
                "target_users": "DevOps Engineers and Platform Architects",
                "industry": "DevOps / Cloud Infrastructure",
                "business_model": "Usage-based B2B SaaS",
                "stage": "MVP",
                "tags": "devops,ai-agents,cloud",
                "notes": custom_notes,
                "is_draft": True
            },
            headers=headers
        )
        assert res_create.status_code == 200
        created_data = res_create.json()
        idea_id = created_data["id"]

        # Verify initial persistence
        assert created_data["title"] == "Autonomous DevOps Agent"
        assert created_data["target_users"] == "DevOps Engineers and Platform Architects"
        assert created_data["notes"] == custom_notes

        # 2. Retrieve Idea
        res_get = await ac.get(f"/api/v1/ideas/{idea_id}", headers=headers)
        assert res_get.status_code == 200
        get_data = res_get.json()
        parsed_notes = json.loads(get_data["notes"])
        assert parsed_notes["usp"] == "10x faster deterministic evaluation engine"
        assert parsed_notes["tech_stack"] == "Next.js 14, FastAPI, PostgreSQL, Asyncpg"
        assert parsed_notes["budget"] == "$15,000"
        assert parsed_notes["timeline"] == "Q4 2026"

        # 3. Update Idea
        updated_notes = json.dumps({
            "usp": "10x faster deterministic evaluation engine with real-time audit",
            "tech_stack": "Next.js 14, FastAPI, PostgreSQL, Asyncpg, Redis",
            "budget": "$25,000",
            "timeline": "Q1 2027"
        })
        res_patch = await ac.patch(
            f"/api/v1/ideas/{idea_id}",
            json={
                "notes": updated_notes,
                "stage": "Beta"
            },
            headers=headers
        )
        assert res_patch.status_code == 200
        patch_data = res_patch.json()
        assert patch_data["stage"] == "Beta"
        assert patch_data["notes"] == updated_notes

        # 4. Duplicate Idea
        res_dup = await ac.post(f"/api/v1/ideas/{idea_id}/duplicate", headers=headers)
        assert res_dup.status_code == 200
        dup_data = res_dup.json()
        assert dup_data["id"] != idea_id
        assert dup_data["title"] == "Autonomous DevOps Agent (Copy)"
        assert dup_data["notes"] == updated_notes, "Duplication must retain full structured notes metadata"
        assert dup_data["target_users"] == "DevOps Engineers and Platform Architects"

        # 5. Verify ContextBuilder evaluation context integration
        async with AsyncSessionLocal() as db:
            context = await ContextBuilder.build_context(db, idea_id)
            assert context["idea_id"] == idea_id
            assert context["idea_title"] == "Autonomous DevOps Agent"
            assert context["target_users"] == "DevOps Engineers and Platform Architects"
            assert context["notes"] == updated_notes
            parsed_eval_notes = json.loads(context["notes"])
            assert parsed_eval_notes["budget"] == "$25,000"
