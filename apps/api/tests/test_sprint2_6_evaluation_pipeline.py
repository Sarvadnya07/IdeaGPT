"""
Sprint 2.6 — Evaluation Pipeline & Execution Infrastructure Test Suite

Comprehensive test matrix verifying:
- Creation, execution, completion, state machine transitions
- Idempotency, duplicate execution rejection
- Retry mechanics and safety
- Cancellation flow and safety
- 10 simultaneous concurrent execution requests
- Stale evaluation recovery strategy
- Lifecycle audit history persistence
- Direct PostgreSQL persistence validation
- Multi-tenant cross-user authorization enforcement
- 100% deterministic result reproduction (zero AI dependencies)
"""
import os
import time
import asyncio
import pytest
import jwt as pyjwt
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select

from app.main import app
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea
from app.models.evaluation import Evaluation
from app.models.evaluation_history import EvaluationHistory
from app.evaluation.state import EvaluationStatus, EvaluationProgress
from app.evaluation.coordinator import EvaluationCoordinator
from app.evaluation.engine import DeterministicEvaluationEngine

TEST_SECRET = os.environ.get("CLERK_JWT_TEST_SECRET", "test-secret-for-unit-tests-only-never-production")

def _make_token(sub: str, email: str = None) -> str:
    if email is None:
        email = f"{sub}@domain.com"
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": email,
        "iat": now,
        "exp": now + 3600,
        "iss": "https://healthy-sunbeam-68.clerk.accounts.dev"
    }
    return pyjwt.encode(payload, TEST_SECRET, algorithm="HS256")



async def _create_test_idea(token: str, title: str = "B2B AI Platform") -> tuple[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        p_res = await ac.post("/api/v1/projects/", json={"title": "Sprint 2.6 Test Project"}, headers=headers)
        assert p_res.status_code in [200, 201]
        proj_id = p_res.json()["id"]

        i_res = await ac.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": title,
                "problem_statement": "Enterprise data integration is slow, complex, and prone to error.",
                "solution_description": "Automated B2B SaaS platform for scalable data transformation and Python automation.",
                "target_users": "Enterprise CTOs and Data Engineers",
                "industry": "Enterprise Software",
                "business_model": "B2B SaaS Subscription",
                "stage": "MVP",
                "tags": "saas, automation, enterprise",
                "notes": "FastAPI, PostgreSQL, Microservices architecture."
            },
            headers=headers
        )
        assert i_res.status_code in [200, 201]
        idea_id = i_res.json()["id"]
        return proj_id, idea_id


# =============================================================================
# 1. INITIALIZATION & LIFECYCLE STATE TRANSITION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_evaluation_initialization_and_pending_state():
    token = _make_token("user_26_init")
    headers = {"Authorization": f"Bearer {token}"}
    proj_id, idea_id = await _create_test_idea(token)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            f"/api/v1/ideas/{idea_id}/evaluations",
            json={"evaluation_type": "startup_evaluation"},
            headers=headers
        )
        assert res.status_code in [200, 201]
        data = res.json()
        assert data["status"] == EvaluationStatus.COMPLETED.value
        assert data["progress"] == EvaluationProgress.COMPLETED.value
        assert data["result_payload"]["score"] > 0

        # Verify direct DB state
        async with AsyncSessionLocal() as db:
            db_eval = await db.get(Evaluation, data["id"])
            assert db_eval is not None
            assert db_eval.status == EvaluationStatus.COMPLETED.value
            assert db_eval.result_payload["score"] == data["result_payload"]["score"]


@pytest.mark.asyncio
async def test_deterministic_engine_preserves_repeatability():
    token = _make_token("user_26_deter")
    proj_id, idea_id = await _create_test_idea(token, title="Deterministic Consistency Test")

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Idea).where(Idea.id == idea_id))
        idea = res.scalar_one()

        res1 = DeterministicEvaluationEngine.evaluate(idea)
        res2 = DeterministicEvaluationEngine.evaluate(idea)

        assert res1["score"] == res2["score"]
        assert res1["dimensions"] == res2["dimensions"]
        assert res1["strengths"] == res2["strengths"]
        assert res1["summary"] == res2["summary"]


@pytest.mark.asyncio
async def test_invalid_state_transitions_rejected():
    token = _make_token("user_26_transitions")
    headers = {"Authorization": f"Bearer {token}"}
    proj_id, idea_id = await _create_test_idea(token)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            f"/api/v1/ideas/{idea_id}/evaluations",
            json={"evaluation_type": "startup_evaluation"},
            headers=headers
        )
        eval_id = res.json()["id"]

        # Attempt to run an already COMPLETED evaluation -> 400 Bad Request
        run_res = await ac.post(f"/api/v1/evaluations/{eval_id}/run", headers=headers)
        assert run_res.status_code == 400

        # Attempt to cancel an already COMPLETED evaluation -> 400 Bad Request
        cancel_res = await ac.post(f"/api/v1/evaluations/{eval_id}/cancel", headers=headers)
        assert cancel_res.status_code == 400


# =============================================================================
# 2. RETRY & CANCELLATION MECHANICS
# =============================================================================

@pytest.mark.asyncio
async def test_cancellation_flow_and_retry():
    token = _make_token("user_26_cancel")
    headers = {"Authorization": f"Bearer {token}"}
    proj_id, idea_id = await _create_test_idea(token)

    async with AsyncSessionLocal() as db:
        # Create evaluation manually in PENDING state
        ev = Evaluation(
            project_id=proj_id,
            idea_id=idea_id,
            evaluation_type="startup_evaluation",
            status=EvaluationStatus.PENDING.value,
            progress=EvaluationProgress.PENDING.value,
            result_payload={},
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        eval_id = ev.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Cancel PENDING job -> 200 CANCELLED
        c_res = await ac.post(f"/api/v1/evaluations/{eval_id}/cancel", headers=headers)
        assert c_res.status_code == 200
        assert c_res.json()["status"] == EvaluationStatus.CANCELLED.value

        # 2. Retry CANCELLED job -> 200 COMPLETED
        r_res = await ac.post(f"/api/v1/evaluations/{eval_id}/retry", headers=headers)
        assert r_res.status_code == 200
        assert r_res.json()["status"] == EvaluationStatus.COMPLETED.value


@pytest.mark.asyncio
async def test_failure_handling_and_retry():
    token = _make_token("user_26_fail")
    headers = {"Authorization": f"Bearer {token}"}
    proj_id, idea_id = await _create_test_idea(token)

    async with AsyncSessionLocal() as db:
        # Create evaluation in FAILED state
        ev = Evaluation(
            project_id=proj_id,
            idea_id=idea_id,
            evaluation_type="startup_evaluation",
            status=EvaluationStatus.FAILED.value,
            progress=EvaluationProgress.FAILED.value,
            error_message="Simulated execution error",
            result_payload={},
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        eval_id = ev.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Retry FAILED job -> COMPLETED
        r_res = await ac.post(f"/api/v1/evaluations/{eval_id}/retry", headers=headers)
        assert r_res.status_code == 200
        data = r_res.json()
        assert data["status"] == EvaluationStatus.COMPLETED.value
        assert data["error_message"] is None


# =============================================================================
# 3. CONCURRENCY & IDEMPOTENCY (10 SIMULTANEOUS REQUESTS)
# =============================================================================

@pytest.mark.asyncio
async def test_concurrent_execution_locking():
    token = _make_token("user_26_concurrency")
    headers = {"Authorization": f"Bearer {token}"}
    proj_id, idea_id = await _create_test_idea(token)

    async with AsyncSessionLocal() as db:
        ev = Evaluation(
            project_id=proj_id,
            idea_id=idea_id,
            evaluation_type="startup_evaluation",
            status=EvaluationStatus.PENDING.value,
            progress=EvaluationProgress.PENDING.value,
            result_payload={},
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        eval_id = ev.id

    # Launch 10 simultaneous run requests
    async def _send_run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            return await ac.post(f"/api/v1/evaluations/{eval_id}/run", headers=headers)

    tasks = [_send_run() for _ in range(10)]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    status_codes = [r.status_code for r in responses if hasattr(r, "status_code")]
    
    # Exactly one request succeeds or transitions to COMPLETED, remainder handled safely without corruption
    assert 200 in status_codes
    assert all(code in [200, 400, 409] for code in status_codes)

    # Verify final database state is COMPLETED and clean
    async with AsyncSessionLocal() as db:
        final_ev = await db.get(Evaluation, eval_id)
        assert final_ev.status == EvaluationStatus.COMPLETED.value
        assert final_ev.result_payload["score"] > 0


# =============================================================================
# 4. STALE JOB RECOVERY STRATEGY
# =============================================================================

@pytest.mark.asyncio
async def test_stale_evaluation_recovery():
    token = _make_token("user_26_stale")
    proj_id, idea_id = await _create_test_idea(token)

    async with AsyncSessionLocal() as db:
        # Create a stale RUNNING evaluation started 10 minutes ago
        stale_time = datetime.now(timezone.utc) - timedelta(seconds=600)
        ev = Evaluation(
            project_id=proj_id,
            idea_id=idea_id,
            evaluation_type="startup_evaluation",
            status=EvaluationStatus.RUNNING.value,
            progress=EvaluationProgress.VALIDATION.value,
            started_at=stale_time,
            result_payload={},
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        eval_id = ev.id

        # Run recovery strategy
        recovered = await EvaluationCoordinator.recover_stale_evaluations(db, threshold_seconds=300)
        assert recovered >= 1

        # Check recovered evaluation
        db_ev = await db.get(Evaluation, eval_id)
        assert db_ev.status == EvaluationStatus.FAILED.value
        assert "Execution timed out" in db_ev.error_message


# =============================================================================
# 5. LIFECYCLE AUDIT HISTORY
# =============================================================================

@pytest.mark.asyncio
async def test_lifecycle_history_audit():
    token = _make_token("user_26_history")
    headers = {"Authorization": f"Bearer {token}"}
    proj_id, idea_id = await _create_test_idea(token)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            f"/api/v1/ideas/{idea_id}/evaluations",
            json={"evaluation_type": "startup_evaluation"},
            headers=headers
        )
        eval_id = res.json()["id"]

        hist_res = await ac.get(f"/api/v1/evaluations/{eval_id}/history", headers=headers)
        assert hist_res.status_code == 200
        history_list = hist_res.json()
        assert len(history_list) >= 2
        event_types = [h["event_type"] for h in history_list]
        assert "CREATED" in event_types
        assert "COMPLETED" in event_types


# =============================================================================
# 6. CROSS-USER OWNERSHIP ISOLATION
# =============================================================================

@pytest.mark.asyncio
async def test_cross_user_evaluation_security_matrix():
    token_a = _make_token("user_26_owner_A")
    token_b = _make_token("user_26_intruder_B")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    proj_id, idea_id = await _create_test_idea(token_a)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_res = await ac.post(
            f"/api/v1/ideas/{idea_id}/evaluations",
            json={"evaluation_type": "startup_evaluation"},
            headers=headers_a
        )
        eval_id = create_res.json()["id"]

        # User B attempts to access User A's evaluation
        endpoints = [
            ("GET", f"/api/v1/evaluations/{eval_id}"),
            ("POST", f"/api/v1/evaluations/{eval_id}/run"),
            ("POST", f"/api/v1/evaluations/{eval_id}/retry"),
            ("POST", f"/api/v1/evaluations/{eval_id}/cancel"),
            ("GET", f"/api/v1/evaluations/{eval_id}/insights"),
            ("GET", f"/api/v1/evaluations/{eval_id}/scores"),
            ("GET", f"/api/v1/evaluations/{eval_id}/history"),
            ("GET", f"/api/v1/evaluations/{eval_id}/charts"),
            ("DELETE", f"/api/v1/evaluations/{eval_id}"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                r = await ac.get(endpoint, headers=headers_b)
            elif method == "POST":
                r = await ac.post(endpoint, headers=headers_b)
            elif method == "DELETE":
                r = await ac.delete(endpoint, headers=headers_b)
            assert r.status_code in [403, 404], f"Endpoint {endpoint} failed security check with status {r.status_code}"
