import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea
from app.models.evaluation import Evaluation

# Mock users for tests
mock_user_a = User(id=1, clerk_id="user_a", email="a@test.com", name="User A")
mock_user_b = User(id=2, clerk_id="user_b", email="b@test.com", name="User B")

current_mock_user = mock_user_a

async def override_get_current_user():
    return current_mock_user

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
async def seed_users():
    async with AsyncSessionLocal() as db:
        # Check if users already exist
        res = await db.execute(select(User).where(User.id.in_([1, 2])))
        existing = res.scalars().all()
        ids = {u.id for u in existing}
        
        if 1 not in ids:
            db.add(mock_user_a)
        if 2 not in ids:
            db.add(mock_user_b)
            
        await db.commit()

@pytest.mark.anyio
async def test_workspace_project_and_idea_lifecycle():
    global current_mock_user
    current_mock_user = mock_user_a

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create project
        proj_payload = {"title": "Test Startup", "description": "A testing project", "category": "SaaS"}
        res = await ac.post("/api/v1/projects/", json=proj_payload)
        assert res.status_code == 201
        proj_data = res.json()
        assert "id" in proj_data
        proj_id = proj_data["id"]

        # 2. List projects
        list_res = await ac.get("/api/v1/projects/")
        assert list_res.status_code == 200
        assert any(p["id"] == proj_id for p in list_res.json()["items"])

        # 3. Create Idea under project
        idea_payload = {
            "title": "Clean AI Idea",
            "problem_statement": "The existing tools are way too complex and slow for standard workflows.",
            "solution_description": "We build a streamlined agent-focused AI assistant that manages builds.",
            "target_users": "Developers",
            "is_draft": True
        }
        res_idea = await ac.post(f"/api/v1/projects/{proj_id}/ideas", json=idea_payload)
        assert res_idea.status_code == 201
        idea_data = res_idea.json()
        assert "id" in idea_data
        idea_id = idea_data["id"]

        # 4. List Ideas
        res_list_ideas = await ac.get(f"/api/v1/projects/{proj_id}/ideas")
        assert res_list_ideas.status_code == 200
        assert len(res_list_ideas.json()) > 0
        assert res_list_ideas.json()[0]["id"] == idea_id

        # 5. Trigger evaluation (should start as QUEUED)
        res_eval = await ac.post(f"/api/v1/ideas/{idea_id}/evaluations", json={"evaluation_type": "startup_evaluation"})
        assert res_eval.status_code == 201
        eval_data = res_eval.json()
        assert eval_data["status"] in ["PENDING", "QUEUED", "RUNNING", "COMPLETED"]
        eval_id = eval_data["id"]

        # 6. Check evaluation status
        res_status = await ac.get(f"/api/v1/evaluations/{eval_id}")
        assert res_status.status_code == 200
        assert res_status.json()["status"] in ["QUEUED", "RUNNING", "COMPLETED"]

        # 7. Soft delete project
        res_del = await ac.delete(f"/api/v1/projects/{proj_id}")
        assert res_del.status_code == 200

        # Verify project is hidden from lists
        list_res2 = await ac.get("/api/v1/projects/")
        assert list_res2.status_code == 200
        assert not any(p["id"] == proj_id for p in list_res2.json()["items"])

@pytest.mark.anyio
async def test_ownership_validation():
    global current_mock_user
    # Seed a project owned by User B
    async with AsyncSessionLocal() as db:
        proj = Project(
            id="test-proj-b",
            user_id=mock_user_b.id,
            title="User B Project",
            slug="user-b-project"
        )
        db.add(proj)
        await db.commit()

        idea = Idea(
            id="test-idea-b",
            project_id="test-proj-b",
            title="User B Idea",
            problem_statement="Too many bugs in our systems.",
            solution_description="AI that fixes bugs automatically.",
            is_draft=False
        )
        db.add(idea)
        await db.commit()

    # Now verify User A cannot access User B's project or idea
    current_mock_user = mock_user_a
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Check Project access
        res = await ac.get("/api/v1/projects/test-proj-b")
        assert res.status_code == 404  # Service returns 404 on not owned

        # Check Idea access
        res_idea = await ac.get(f"/api/v1/projects/test-proj-b/ideas")
        assert res_idea.status_code == 404

        # Check Trigger Evaluation access
        res_eval = await ac.post("/api/v1/ideas/test-idea-b/evaluations", json={"evaluation_type": "startup_evaluation"})
        assert res_eval.status_code == 403 # Access denied
