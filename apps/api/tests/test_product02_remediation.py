"""
PRODUCT-02 remediation regression tests.

Each test guards a specific finding from
``docs/audits/PRODUCT_01_FEATURE_COMPLETENESS_AUDIT.md``. These are written to be
meaningful (they assert observable behaviour), not merely present.

Covered:
  * P-07 — the DB-free context path must produce the SAME prompt inputs as the
           db-backed path (the F-07 connection fix must not change model input).
  * P-08 — the concurrency indexes created by migration e3f4a5b6c7d8 must also be
           declared on the ORM models, or ``alembic check`` fails in CI.
  * P-01 — the durable artifact store must be readable, project-scoped and
           owner-scoped.
  * P-02 — artifact writes must be linked to the caller's own project.
"""
import time

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea
from app.models.evaluation import Evaluation
from app.models.ai_task import AiTask
from app.services.ai_artifact_service import AIArtifactService
from app.ai.pipelines.context import ContextBuilder
from app.ai.prompts.registry import prompt_registry

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
        "iss": "https://healthy-sunbeam-68.clerk.accounts.dev",
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


async def _get_user_id(clerk_id: str) -> int:
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.clerk_id == clerk_id))
        user = res.scalars().first()
        assert user is not None, f"user {clerk_id} was not provisioned"
        return user.id


# ---------------------------------------------------------------------------
# P-08 — schema/metadata alignment (guards the CI `alembic check` gate)
# ---------------------------------------------------------------------------

def test_concurrency_indexes_are_declared_on_the_models():
    """
    Migration e3f4a5b6c7d8 creates these indexes. If the ORM metadata does not
    declare them, `alembic check` reports drift and the CI job fails.
    """
    eval_indexes = {i.name for i in Evaluation.__table__.indexes}
    assert "uq_evaluations_active_per_idea" in eval_indexes
    assert "ix_evaluations_idea_id_status" in eval_indexes

    task_indexes = {i.name for i in AiTask.__table__.indexes}
    assert "uq_ai_tasks_user_idempotency" in task_indexes
    assert "ix_ai_tasks_user_id_created_at" in task_indexes


def test_active_evaluation_index_is_partial_and_unique():
    """The invariant must be a PARTIAL unique index, not a blanket unique one."""
    index = next(
        i for i in Evaluation.__table__.indexes
        if i.name == "uq_evaluations_active_per_idea"
    )
    assert index.unique is True
    # A blanket UNIQUE(idea_id) would block re-evaluating a completed idea, so the
    # index must carry a partial predicate.
    assert "postgresql_where" in index.dialect_kwargs
    assert "PENDING" in str(index.dialect_kwargs["postgresql_where"])


# ---------------------------------------------------------------------------
# P-07 — prompt fidelity on the DB-free path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_compile_context_matches_build_context():
    """
    The detached path (compile_context) must produce a byte-identical context to
    the db-backed path (build_context). If these diverge, the F-07 fix silently
    changes the prompt, the prompt version, and therefore the cache key.
    """
    headers = _make_auth_header("user_ctx_equiv")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        proj = await client.post(
            "/api/v1/projects/",
            json={"title": "Context Equivalence", "slug": "context-equivalence"},
            headers=headers,
        )
        assert proj.status_code == 201
        project_id = proj.json()["id"]

        idea_res = await client.post(
            f"/api/v1/projects/{project_id}/ideas",
            json={
                "title": "Sentinel",
                "problem_statement": "Founders cannot validate ideas quickly.",
                "solution_description": "Automated feasibility analysis.",
                "target_users": "Founders",
                "industry": "Developer Tools",
                "business_model": "SaaS Subscription",
                "stage": "MVP",
                "is_draft": False,
            },
            headers=headers,
        )
        assert idea_res.status_code == 201
        idea_id = idea_res.json()["id"]

    async with AsyncSessionLocal() as db:
        idea = (
            await db.execute(select(Idea).where(Idea.id == idea_id))
        ).scalars().first()
        project = (
            await db.execute(select(Project).where(Project.id == project_id))
        ).scalars().first()
        assert idea is not None and project is not None

        detached = ContextBuilder.compile_context(idea, project)
        from_db = await ContextBuilder.build_context(db, idea_id)

    assert detached == from_db

    # The rendered prompt is therefore identical on both paths.
    rendered_detached = prompt_registry.render_prompt("startup_evaluation", detached)
    rendered_db = prompt_registry.render_prompt("startup_evaluation", from_db)
    assert rendered_detached == rendered_db

    # And it is genuinely the registry prompt, not the bare-prompt fallback.
    registry_config = prompt_registry.get_prompt("startup_evaluation")
    assert registry_config is not None
    assert rendered_detached["version"] == registry_config["version"]
    assert rendered_detached["system_prompt"] == registry_config["system_prompt"]
    assert rendered_detached["max_tokens"] == registry_config.get("max_tokens", 1000)


# ---------------------------------------------------------------------------
# P-01 / P-02 — artifact retrieval, project scoping and ownership
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_artifacts_are_readable_scoped_and_owner_isolated():
    """
    A persisted artifact must be retrievable by its owner, filterable by project,
    and invisible to another user.
    """
    headers_a = _make_auth_header("user_artifact_owner")
    headers_b = _make_auth_header("user_artifact_other")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        proj_a = await client.post(
            "/api/v1/projects/",
            json={"title": "Artifact Owner Proj", "slug": "artifact-owner-proj"},
            headers=headers_a,
        )
        assert proj_a.status_code == 201
        project_a_id = proj_a.json()["id"]

        # A second project for the same user, to prove the filter actually filters.
        proj_a2 = await client.post(
            "/api/v1/projects/",
            json={"title": "Artifact Other Proj", "slug": "artifact-other-proj"},
            headers=headers_a,
        )
        assert proj_a2.status_code == 201
        project_a2_id = proj_a2.json()["id"]

        # Sanity: user B is provisioned too.
        me_b = await client.get("/api/v1/users/me", headers=headers_b)

        user_a_id = await _get_user_id("user_artifact_owner")

        # Persist an artifact against project A (owner-linked).
        async with AsyncSessionLocal() as db:
            await AIArtifactService.save_artifact(
                db=db,
                user_id=user_a_id,
                artifact_type="tech_stack",
                title="Tech Stack: Artifact Owner Proj",
                content_payload={"frontend": "Next.js"},
                project_id=project_a_id,
            )

        # 1. Owner sees it, scoped to the right project.
        res_scoped = await client.get(
            "/api/v1/ai/artifacts",
            params={"project_id": project_a_id},
            headers=headers_a,
        )
        assert res_scoped.status_code == 200
        scoped = res_scoped.json()
        assert len(scoped) == 1
        assert scoped[0]["artifact_type"] == "tech_stack"
        assert scoped[0]["project_id"] == project_a_id
        assert scoped[0]["content_payload"]["frontend"] == "Next.js"

        # 2. Scoping by the other project returns nothing (filter is real).
        res_other = await client.get(
            "/api/v1/ai/artifacts",
            params={"project_id": project_a2_id},
            headers=headers_a,
        )
        assert res_other.status_code == 200
        assert res_other.json() == []

        # 3. A different user cannot see it.
        res_b = await client.get(
            "/api/v1/ai/artifacts",
            params={"project_id": project_a_id},
            headers=headers_b,
        )
        assert res_b.status_code == 200
        assert res_b.json() == []

        # 4. Detail endpoint is owner-scoped too (404, not 403 — no existence leak).
        artifact_id = scoped[0]["id"]
        detail_owner = await client.get(
            f"/api/v1/ai/artifacts/{artifact_id}", headers=headers_a
        )
        assert detail_owner.status_code == 200
        detail_other = await client.get(
            f"/api/v1/ai/artifacts/{artifact_id}", headers=headers_b
        )
        assert detail_other.status_code == 404


@pytest.mark.asyncio
async def test_cross_tenant_artifact_link_is_rejected():
    """
    P-02: writing an artifact that references another user's project must fail
    closed (403) rather than creating an unattributable cross-tenant row.
    """
    headers_a = _make_auth_header("user_link_victim")
    headers_b = _make_auth_header("user_link_attacker")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        proj = await client.post(
            "/api/v1/projects/",
            json={"title": "Victim Project", "slug": "victim-project"},
            headers=headers_a,
        )
        assert proj.status_code == 201
        victim_project_id = proj.json()["id"]
        await client.get("/api/v1/users/me", headers=headers_b)

    attacker_id = await _get_user_id("user_link_attacker")

    from fastapi import HTTPException

    async with AsyncSessionLocal() as db:
        with pytest.raises(HTTPException) as exc_info:
            await AIArtifactService.save_artifact(
                db=db,
                user_id=attacker_id,
                artifact_type="prd",
                title="Should not be persisted",
                content_payload={"leak": True},
                project_id=victim_project_id,
            )
    assert exc_info.value.status_code == 403
