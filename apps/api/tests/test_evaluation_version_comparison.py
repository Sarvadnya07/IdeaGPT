import os
import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient, ASGITransport
import jwt as pyjwt

from app.main import app
from app.core.config import settings
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea
from app.models.evaluation import Evaluation
from app.db.session import AsyncSessionLocal
from app.services.evaluation_version_comparison_service import (
    evaluation_version_comparison_service,
    EvaluationVersionComparisonService,
)

TEST_SECRET = os.environ.get("CLERK_JWT_TEST_SECRET", "test-secret-for-unit-tests-only-never-production")


def _make_token(sub: str = "test_eval_user_001") -> str:
    payload = {
        "sub": sub,
        "exp": 9999999999,
        "iat": 1000000000,
        "iss": settings.clerk_issuer or "https://clerk.test",
    }
    return pyjwt.encode(payload, TEST_SECRET, algorithm="HS256")


# ===========================================================================
# 1. PURE COMPARISON SERVICE TESTS (ZERO DB, ZERO AI, ZERO SIDE-EFFECTS)
# ===========================================================================

def test_pure_comparison_positive_delta():
    """Verify overall score and higher-is-better metrics show positive delta and 'improved' status."""
    eval_a = Evaluation(
        id=str(uuid.uuid4()),
        idea_id="test-idea-1",
        project_id="test-proj-1",
        status="COMPLETED",
        created_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        result_payload={
            "score": 70,
            "confidence": 0.80,
            "dimensions": {
                "innovation": 65,
                "market_potential": 70,
                "technical_feasibility": 75,
                "business_viability": 60,
                "scalability": 70,
                "execution_complexity": 80,
                "competitive_differentiation": 65,
            },
            "strengths": ["Strong founder pedigree"],
            "weaknesses": ["Unclear pricing model"],
            "recommendations": ["Conduct 10 customer interviews"],
        },
    )

    eval_b = Evaluation(
        id=str(uuid.uuid4()),
        idea_id="test-idea-1",
        project_id="test-proj-1",
        status="COMPLETED",
        created_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
        result_payload={
            "score": 85,
            "confidence": 0.90,
            "dimensions": {
                "innovation": 80,
                "market_potential": 85,
                "technical_feasibility": 80,
                "business_viability": 75,
                "scalability": 85,
                "execution_complexity": 60,  # Lower complexity is better!
                "competitive_differentiation": 80,
            },
            "strengths": ["Strong founder pedigree", "Proprietary AI dataset"],
            "weaknesses": [],
            "recommendations": ["Scale paid ad campaigns"],
        },
    )

    res = evaluation_version_comparison_service.compare_evaluation_versions(eval_a, eval_b)

    assert res.idea_id == "test-idea-1"
    assert res.overall_score.value_a == 70.0
    assert res.overall_score.value_b == 85.0
    assert res.overall_score.delta == 15.0
    assert res.overall_score.formatted_delta == "+15.00"
    assert res.overall_score.status == "improved"

    # Higher is better dimension: innovation (65 -> 80)
    inno = next(d for d in res.dimensions if d.key == "innovation")
    assert inno.delta == 15.0
    assert inno.formatted_delta == "+15.00"
    assert inno.status == "improved"

    # Lower is better dimension: execution_complexity (80 -> 60)
    # Reduced complexity is an IMPROVEMENT
    exec_comp = next(d for d in res.dimensions if d.key == "execution_complexity")
    assert exec_comp.delta == -20.0
    assert exec_comp.formatted_delta == "-20.00"
    assert exec_comp.direction == "lower_is_better"
    assert exec_comp.status == "improved"


def test_pure_comparison_negative_delta():
    """Verify overall score and higher-is-better metrics show negative delta and 'declined' status."""
    eval_a = Evaluation(
        id="eval-a",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={
            "score": 88.5,
            "dimensions": {
                "market_potential": 90,
                "execution_complexity": 50,
            },
        },
    )

    eval_b = Evaluation(
        id="eval-b",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={
            "score": 75.0,
            "dimensions": {
                "market_potential": 70,
                "execution_complexity": 85,  # Higher complexity is a DECLINE
            },
        },
    )

    res = evaluation_version_comparison_service.compare_evaluation_versions(eval_a, eval_b)

    assert res.overall_score.delta == -13.5
    assert res.overall_score.formatted_delta == "-13.50"
    assert res.overall_score.status == "declined"

    mkt = next(d for d in res.dimensions if d.key == "market_potential")
    assert mkt.delta == -20.0
    assert mkt.status == "declined"

    exec_comp = next(d for d in res.dimensions if d.key == "execution_complexity")
    assert exec_comp.delta == 35.0
    assert exec_comp.status == "declined"


def test_pure_comparison_zero_delta():
    """Verify identical scores return delta 0.00 and 'unchanged' status."""
    eval_a = Evaluation(
        id="eval-a",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={"score": 80, "dimensions": {"innovation": 75}},
    )
    eval_b = Evaluation(
        id="eval-b",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={"score": 80, "dimensions": {"innovation": 75}},
    )

    res = evaluation_version_comparison_service.compare_evaluation_versions(eval_a, eval_b)

    assert res.overall_score.delta == 0.0
    assert res.overall_score.formatted_delta == "0.00"
    assert res.overall_score.status == "unchanged"

    inno = next(d for d in res.dimensions if d.key == "innovation")
    assert inno.delta == 0.0
    assert inno.formatted_delta == "0.00"
    assert inno.status == "unchanged"


def test_pure_comparison_missing_values_no_zero_fabrication():
    """Missing metric values must yield delta=None and status='unavailable' without fabricating zeroes."""
    eval_a = Evaluation(
        id="eval-a",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={"score": 75, "dimensions": {"innovation": 70}},
    )
    eval_b = Evaluation(
        id="eval-b",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={"score": None, "dimensions": {}},  # innovation absent in B
    )

    res = evaluation_version_comparison_service.compare_evaluation_versions(eval_a, eval_b)

    assert res.overall_score.value_a == 75.0
    assert res.overall_score.value_b is None
    assert res.overall_score.delta is None
    assert res.overall_score.formatted_delta is None
    assert res.overall_score.status == "unavailable"

    inno = next(d for d in res.dimensions if d.key == "innovation")
    assert inno.value_a == 70.0
    assert inno.value_b is None
    assert inno.delta is None
    assert inno.status == "unavailable"


def test_pure_comparison_numeric_precision():
    """Verify exact 2 decimal precision without binary floating point drift."""
    eval_a = Evaluation(
        id="eval-a",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={"score": 10.10, "dimensions": {"innovation": 12.33}},
    )
    eval_b = Evaluation(
        id="eval-b",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={"score": 12.60, "dimensions": {"innovation": 10.33}},
    )

    res = evaluation_version_comparison_service.compare_evaluation_versions(eval_a, eval_b)

    assert res.overall_score.delta == 2.50
    assert res.overall_score.formatted_delta == "+2.50"

    inno = next(d for d in res.dimensions if d.key == "innovation")
    assert inno.delta == -2.00
    assert inno.formatted_delta == "-2.00"


def test_pure_comparison_swot_lists_normalization_and_preservation():
    """Verify SWOT lists identify added, removed, and retained items deterministically with text preservation."""
    eval_a = Evaluation(
        id="eval-a",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={
            "strengths": ["  Strong Market Need  ", "Proprietary Algorithm"],
            "weaknesses": ["High Burn Rate", "Regulatory Hurdles"],
            "recommendations": ["Hire Compliance Officer"],
        },
    )
    eval_b = Evaluation(
        id="eval-b",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={
            "strengths": ["strong market need", "Experienced Team"],  # Added team, retained market need
            "weaknesses": ["Regulatory Hurdles"],                    # Resolved burn rate
            "recommendations": ["Hire Compliance Officer", "Launch MVP"],
        },
    )

    res = evaluation_version_comparison_service.compare_evaluation_versions(eval_a, eval_b)

    strengths = res.swot["strengths"]
    assert "Experienced Team" in strengths.added
    assert "Proprietary Algorithm" in strengths.removed
    assert any("strong market need" in item.lower() for item in strengths.retained)

    weaknesses = res.swot["weaknesses"]
    assert "High Burn Rate" in weaknesses.removed
    assert "Regulatory Hurdles" in weaknesses.retained


def test_pure_comparison_sections():
    """Verify structured section comparison for architecture, market fit, financials, and risks."""
    eval_a = Evaluation(
        id="eval-a",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={
            "architecture_breakdown": "### Architecture v1\nMonolithic FastAPI",
            "risks": ["Cold start latency"],
        },
    )
    eval_b = Evaluation(
        id="eval-b",
        idea_id="test-idea-1",
        status="COMPLETED",
        result_payload={
            "architecture_breakdown": "### Architecture v2\nMicroservices on Railway",
            "financial_projections": {"arr_y1": 50000},
            "risks": ["Cold start latency"],
        },
    )

    res = evaluation_version_comparison_service.compare_evaluation_versions(eval_a, eval_b)

    arch = next(s for s in res.sections if s.section_key == "architecture_breakdown")
    assert arch.present_in_a is True
    assert arch.present_in_b is True
    assert arch.status == "changed"

    fin = next(s for s in res.sections if s.section_key == "financial_projections")
    assert fin.present_in_a is False
    assert fin.present_in_b is True
    assert fin.status == "added"

    risks = next(s for s in res.sections if s.section_key == "risks")
    assert risks.present_in_a is True
    assert risks.present_in_b is True
    assert risks.status == "unchanged"

    mkt = next(s for s in res.sections if s.section_key == "market_fit")
    assert mkt.present_in_a is False
    assert mkt.present_in_b is False
    assert mkt.status == "unavailable"


# ===========================================================================
# 2. HTTP ROUTE & AUTHORIZATION TESTS
# ===========================================================================

@pytest.mark.asyncio
async def test_compare_route_unauthenticated_returns_401():
    """Route without Bearer token must return 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/evaluations/idea-123/compare?a=eval-1&b=eval-2")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_compare_route_same_id_rejected_400():
    """Comparing an evaluation with itself (a == b) must return 400 Bad Request."""
    auth_hdr = {"Authorization": f"Bearer {_make_token('test_same_id_user')}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/evaluations/idea-123/compare?a=eval-same&b=eval-same", headers=auth_hdr)
        assert res.status_code == 400
        assert "Cannot compare an evaluation with itself" in res.json()["detail"]


@pytest.mark.asyncio
async def test_compare_route_cross_tenant_rejected_403():
    """Attempting to compare evaluations for an idea owned by another user must return 403."""
    user_owner_sub = "test_owner_user"
    user_attacker_sub = "test_attacker_user"

    async with AsyncSessionLocal() as db:
        # Create Owner User
        owner = User(clerk_id=user_owner_sub, email="owner@test.com", name="Owner")
        db.add(owner)
        await db.flush()

        # Create Owner Project & Idea
        proj = Project(user_id=owner.id, title="Owner Project", slug="owner-project")
        db.add(proj)
        await db.flush()

        idea = Idea(project_id=proj.id, title="Owner Idea", problem_statement="Prob", solution_description="Sol")
        db.add(idea)
        await db.flush()

        eval_1 = Evaluation(id=str(uuid.uuid4()), project_id=proj.id, idea_id=idea.id, status="COMPLETED", result_payload={"score": 70})
        eval_2 = Evaluation(id=str(uuid.uuid4()), project_id=proj.id, idea_id=idea.id, status="COMPLETED", result_payload={"score": 80})
        db.add_all([eval_1, eval_2])
        await db.commit()

        target_idea_id = str(idea.id)
        e1_id = str(eval_1.id)
        e2_id = str(eval_2.id)

    # Attacker tries to compare owner's evaluations
    auth_hdr = {"Authorization": f"Bearer {_make_token(user_attacker_sub)}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            f"/api/v1/evaluations/{target_idea_id}/compare?a={e1_id}&b={e2_id}",
            headers=auth_hdr,
        )
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_compare_route_missing_or_unrelated_evaluation_404():
    """Requesting an evaluation that does not belong to the idea must return 404 (IDOR defense)."""
    user_sub = "test_idor_user"

    async with AsyncSessionLocal() as db:
        user = User(clerk_id=user_sub, email="idor@test.com", name="IDOR Tester")
        db.add(user)
        await db.flush()

        proj = Project(user_id=user.id, title="Proj", slug="proj-idor")
        db.add(proj)
        await db.flush()

        idea_1 = Idea(project_id=proj.id, title="Idea 1", problem_statement="P1", solution_description="S1")
        idea_2 = Idea(project_id=proj.id, title="Idea 2", problem_statement="P2", solution_description="S2")
        db.add_all([idea_1, idea_2])
        await db.flush()

        # eval_1 on idea_1, eval_2 on idea_2
        eval_1 = Evaluation(id=str(uuid.uuid4()), project_id=proj.id, idea_id=idea_1.id, status="COMPLETED", result_payload={"score": 75})
        eval_2 = Evaluation(id=str(uuid.uuid4()), project_id=proj.id, idea_id=idea_2.id, status="COMPLETED", result_payload={"score": 85})
        db.add_all([eval_1, eval_2])
        await db.commit()

        i1_id = str(idea_1.id)
        e1_id = str(eval_1.id)
        e2_id = str(eval_2.id)

    auth_hdr = {"Authorization": f"Bearer {_make_token(user_sub)}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # e2 does not belong to i1 -> must return 404
        res = await client.get(
            f"/api/v1/evaluations/{i1_id}/compare?a={e1_id}&b={e2_id}",
            headers=auth_hdr,
        )
        assert res.status_code == 404
        assert f"Evaluation '{e2_id}' not found for this idea" in res.json()["detail"]


@pytest.mark.asyncio
async def test_compare_route_incomplete_evaluation_rejected_400():
    """Evaluations not in COMPLETED status must be rejected with 400."""
    user_sub = "test_incomplete_eval_user"

    async with AsyncSessionLocal() as db:
        user = User(clerk_id=user_sub, email="inc@test.com", name="Inc Tester")
        db.add(user)
        await db.flush()

        proj = Project(user_id=user.id, title="Proj", slug="proj-inc")
        db.add(proj)
        await db.flush()

        idea = Idea(project_id=proj.id, title="Idea Inc", problem_statement="P", solution_description="S")
        db.add(idea)
        await db.flush()

        eval_1 = Evaluation(id=str(uuid.uuid4()), project_id=proj.id, idea_id=idea.id, status="COMPLETED", result_payload={"score": 75})
        eval_2 = Evaluation(id=str(uuid.uuid4()), project_id=proj.id, idea_id=idea.id, status="RUNNING", result_payload={})
        db.add_all([eval_1, eval_2])
        await db.commit()

        i_id = str(idea.id)
        e1_id = str(eval_1.id)
        e2_id = str(eval_2.id)

    auth_hdr = {"Authorization": f"Bearer {_make_token(user_sub)}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            f"/api/v1/evaluations/{i_id}/compare?a={e1_id}&b={e2_id}",
            headers=auth_hdr,
        )
        assert res.status_code == 400
        assert "Only COMPLETED evaluations can be compared" in res.json()["detail"]


@pytest.mark.asyncio
async def test_compare_route_success_both_endpoints():
    """Verify successful comparison across both primary and alias endpoints."""
    user_sub = "test_success_compare_user"

    async with AsyncSessionLocal() as db:
        user = User(clerk_id=user_sub, email="succ@test.com", name="Success Tester")
        db.add(user)
        await db.flush()

        proj = Project(user_id=user.id, title="Success Proj", slug="proj-success")
        db.add(proj)
        await db.flush()

        idea = Idea(project_id=proj.id, title="Success Idea", problem_statement="P", solution_description="S")
        db.add(idea)
        await db.flush()

        eval_1 = Evaluation(
            id=str(uuid.uuid4()),
            project_id=proj.id,
            idea_id=idea.id,
            status="COMPLETED",
            provider="groq",
            model="llama-3.3-70b-versatile",
            duration_ms=1200,
            token_usage=1450,
            estimated_cost=0.002,
            result_payload={
                "score": 72,
                "confidence": 0.85,
                "dimensions": {
                    "innovation": 70,
                    "market_potential": 75,
                    "technical_feasibility": 80,
                    "business_viability": 65,
                    "scalability": 70,
                    "execution_complexity": 85,
                    "competitive_differentiation": 68,
                },
                "strengths": ["Clear problem statement"],
                "weaknesses": ["Undefined pricing"],
                "recommendations": ["Talk to 10 customers"],
            },
        )
        eval_2 = Evaluation(
            id=str(uuid.uuid4()),
            project_id=proj.id,
            idea_id=idea.id,
            status="COMPLETED",
            provider="groq",
            model="llama-3.3-70b-versatile",
            duration_ms=950,
            token_usage=1600,
            estimated_cost=0.0025,
            result_payload={
                "score": 84,
                "confidence": 0.92,
                "dimensions": {
                    "innovation": 85,
                    "market_potential": 85,
                    "technical_feasibility": 82,
                    "business_viability": 80,
                    "scalability": 88,
                    "execution_complexity": 65,  # Lower complexity = improved!
                    "competitive_differentiation": 82,
                },
                "strengths": ["Clear problem statement", "Validated revenue model"],
                "weaknesses": [],
                "recommendations": ["Scale MVP pilot"],
            },
        )
        db.add_all([eval_1, eval_2])
        await db.commit()

        i_id = str(idea.id)
        e1_id = str(eval_1.id)
        e2_id = str(eval_2.id)

    auth_hdr = {"Authorization": f"Bearer {_make_token(user_sub)}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Primary endpoint: /api/v1/evaluations/{idea_id}/compare
        res1 = await client.get(
            f"/api/v1/evaluations/{i_id}/compare?a={e1_id}&b={e2_id}",
            headers=auth_hdr,
        )
        assert res1.status_code == 200
        data1 = res1.json()

        assert data1["idea_id"] == i_id
        assert data1["overall_score"]["delta"] == 12.0
        assert data1["overall_score"]["formatted_delta"] == "+12.00"
        assert data1["overall_score"]["status"] == "improved"
        assert data1["evaluation_a"]["id"] == e1_id
        assert data1["evaluation_b"]["id"] == e2_id

        # 2. Alias endpoint: /api/v1/ideas/{idea_id}/evaluations/compare
        res2 = await client.get(
            f"/api/v1/ideas/{i_id}/evaluations/compare?a={e1_id}&b={e2_id}",
            headers=auth_hdr,
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["overall_score"]["delta"] == 12.0
        assert data2["overall_score"]["formatted_delta"] == "+12.00"
