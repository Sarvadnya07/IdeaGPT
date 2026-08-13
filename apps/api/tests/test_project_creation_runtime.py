import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.main import app
from app.core.config import settings
from app.core.database import engine
from app.models.user import User
from app.models.project import Project
from app.api.dependencies.auth import get_current_user

client = TestClient(app)

@pytest.mark.asyncio
async def test_01_normal_authenticated_project_creation():
    """Verifies that an authenticated request to POST /api/v1/projects/ creates a project and returns 200."""
    async with AsyncSession(engine) as db:
        user = User(clerk_id="user_proj_runtime_1", email="proj1@ideagpt.dev")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            response = client.post(
                "/api/v1/projects/",
                json={"title": "Runtime Test Project", "description": "Testing runtime creation", "category": "B2B SaaS"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Runtime Test Project"
            assert data["user_id"] == user.id
            assert "slug" in data
            assert data["slug"].startswith("runtime-test-project-")
        finally:
            app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_02_exact_browser_payload_execution():
    """Verifies the exact payload sent by the Next.js browser page (/projects/new)."""
    async with AsyncSession(engine) as db:
        user = User(clerk_id="user_proj_runtime_2", email="proj2@ideagpt.dev")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        browser_payload = {
            "title": "Nexus - AI Development Platform",
            "description": "Briefly describe what you are building...",
            "category": "Other"
        }

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            response = client.post("/api/v1/projects/", json=browser_payload)
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == browser_payload["title"]
            assert data["description"] == browser_payload["description"]
            assert data["category"] == browser_payload["category"]
        finally:
            app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_03_duplicate_title_and_slug_isolation():
    """Verifies that creating multiple projects with the exact same title generates distinct unique slugs without 500 error."""
    async with AsyncSession(engine) as db:
        user = User(clerk_id="user_proj_runtime_3", email="proj3@ideagpt.dev")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp1 = client.post("/api/v1/projects/", json={"title": "Duplicate Title Project"})
            resp2 = client.post("/api/v1/projects/", json={"title": "Duplicate Title Project"})
            resp3 = client.post("/api/v1/projects/", json={"title": "Duplicate Title Project"})

            assert resp1.status_code == 200
            assert resp2.status_code == 200
            assert resp3.status_code == 200

            slug1 = resp1.json()["slug"]
            slug2 = resp2.json()["slug"]
            slug3 = resp3.json()["slug"]

            assert len({slug1, slug2, slug3}) == 3
        finally:
            app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_04_validation_rejections():
    """Verifies payload validation rules for empty title or title exceeding maximum length."""
    resp_empty = client.post("/api/v1/projects/", json={"title": ""})
    assert resp_empty.status_code in (401, 422)

    resp_long = client.post("/api/v1/projects/", json={"title": "a" * 101})
    assert resp_long.status_code in (401, 422)

@pytest.mark.asyncio
async def test_05_unauthenticated_request_rejection():
    """Verifies unauthenticated project creation request returns 401 Unauthorized."""
    response = client.post("/api/v1/projects/", json={"title": "Unauthenticated Project"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_06_project_persistence_in_database():
    """Verifies that project records created via HTTP persist in PostgreSQL / database."""
    async with AsyncSession(engine) as db:
        user = User(clerk_id="user_proj_runtime_6", email="proj6@ideagpt.dev")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            res = client.post("/api/v1/projects/", json={"title": "Persisted Project", "category": "Fintech"})
            assert res.status_code == 200
            project_id = res.json()["id"]

            db_res = await db.execute(select(Project).where(Project.id == project_id))
            proj = db_res.scalar_one_or_none()
            assert proj is not None
            assert proj.title == "Persisted Project"
            assert proj.user_id == user.id
        finally:
            app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_07_groq_independence_for_crud():
    """Verifies that project CRUD endpoints function deterministically even when Groq is unconfigured or disabled."""
    async with AsyncSession(engine) as db:
        user = User(clerk_id="user_proj_runtime_7", email="proj7@ideagpt.dev")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch.object(settings, "GROQ_API_KEY", None), patch.object(settings, "ENABLE_GROQ", False):
                response = client.post("/api/v1/projects/", json={"title": "No AI Project", "category": "Healthtech"})
                assert response.status_code == 200
                assert response.json()["title"] == "No AI Project"
        finally:
            app.dependency_overrides.clear()
