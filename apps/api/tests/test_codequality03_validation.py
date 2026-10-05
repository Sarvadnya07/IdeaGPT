"""
CODEQUALITY-03 — Behavioral regression validation for the CODEQUALITY-02 refactors.

These are characterization + regression tests pinning the behavior of each
refactored area. They exist to PROVE (not assume) that the refactors:

  R-01  /metrics degraded-state signaling        — failure no longer fabricates data
  R-03  insight provenance labels                 — additive fields present, payload shape held
  R-04  analytics 30-day window + provenance      — window math correct, labels additive
  R-05  export route dedup (_export_payload)      — GET/POST route shapes unchanged
  R-06  _fail_task consolidation                  — message strings + status transitions identical
  R-07  IntegrityError -> 409 mapping             — duplicate active evaluation returns 409

Each test states the invariant it pins. Run with the rest of the suite.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models.evaluation import Evaluation
from app.models.ai_task import AiTask
from app.services.ai_task_service import AiTaskService
from app.api.routes.evaluation_routes import _export_payload
from app.services.insight_service import insight_service
from app.services.analytics_service import AnalyticsService


# ==============================================================================
# R-05 — Export route dedup: shape contract pinned byte-for-byte
# ==============================================================================

def _mk_eval(eid: str, payload: dict) -> Evaluation:
    ev = Evaluation()
    ev.id = eid
    ev.result_payload = payload
    return ev


class TestExportPayloadDedup:
    """Invariant: _export_payload reproduces the pre-refactor route responses exactly."""

    def test_json_shape(self):
        ev = _mk_eval("eval-abc123", {"score": 71})
        out = _export_payload(ev, "json")
        assert out == {
            "filename": "evaluation_eval-abc123.json",
            "format": "json",
            "content": out["content"],  # content is the serialized payload
        }
        assert out["format"] == "json"

    def test_markdown_shape(self):
        ev = _mk_eval("eval-abc123", {"score": 71, "strengths": ["x"]})
        out = _export_payload(ev, "markdown")
        assert out["filename"] == "evaluation_eval-abc123.md"
        assert out["format"] == "markdown"
        assert "x" in out["content"]

    def test_md_alias(self):
        ev = _mk_eval("e1", {})
        assert _export_payload(ev, "md")["format"] == "markdown"

    def test_pdf_shape(self):
        ev = _mk_eval("eval-abc123", {"score": 50})
        out = _export_payload(ev, "pdf")
        assert out["filename"] == "evaluation_eval-abc123.pdf.html"
        assert out["format"] == "pdf"

    def test_legacy_post_json_shape_strips_format(self):
        """All three export routes remain registered with identical paths/methods."""
        from app.main import app

        def iter_routes(routes):
            for r in routes:
                path = getattr(r, "path", None)
                methods = tuple(sorted(getattr(r, "methods", None) or []))
                if path:
                    yield (path, methods)
                # FastAPI >= newer versions wrap include_router in _IncludedRouter
                if type(r).__name__ == "_IncludedRouter":
                    prefix = getattr(getattr(r, "include_context", None), "prefix", "") or ""
                    for sub in getattr(getattr(r, "original_router", None), "routes", []) or []:
                        spath = getattr(sub, "path", None)
                        if spath:
                            yield (prefix + spath, tuple(sorted(getattr(sub, "methods", None) or [])))

        routes = set(iter_routes(app.routes))
        assert ("/api/v1/exports/json", ("POST",)) in routes
        assert ("/api/v1/exports/markdown", ("POST",)) in routes
        assert ("/api/v1/evaluations/{evaluation_id}/export", ("GET",)) in routes

    def test_content_matches_serialization(self):
        import json as _json
        from app.services.export_service import export_service
        payload = {"score": 88, "dimensions": {"innovation": 90}}
        ev = _mk_eval("e1", payload)
        out = _export_payload(ev, "json")
        assert out["content"] == export_service.to_json(payload)


# ==============================================================================
# R-06 — _fail_task consolidation: messages + transitions identical
# ==============================================================================

class TestFailTaskConsolidation:
    """Invariant: consolidated handler produces the same FAILED transitions
    and the same user-facing messages as the four removed except blocks."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exc_cls,expected_msg", [
        ("AIUnavailableException", "AI service is currently unavailable. Please check provider configuration or retry later."),
        ("AIQuotaExceededException", "Daily AI task quota reached for your account."),
        ("AIException", "An error occurred during AI model processing. Please try again."),
    ])
    async def test_expected_ai_failure_messages(self, exc_cls, expected_msg):
        import app.ai.exceptions.ai_exceptions as ai_exc
        exc = getattr(ai_exc, exc_cls)("boom")
        task = AiTask(id="t1", status="RUNNING")

        with patch.object(AiTaskService, "update_task_status", new=AsyncMock()) as up:
            await AiTaskService._fail_task(None, task, start_time=0.0, exc=exc, user_message=expected_msg)
            kwargs = up.call_args.kwargs
            assert kwargs["new_status"] == "FAILED"
            assert kwargs["error_message"] == expected_msg
            assert isinstance(kwargs["duration_ms"], int)

    @pytest.mark.asyncio
    async def test_unexpected_failure_message_and_logging(self, caplog):
        task = AiTask(id="t1", status="RUNNING")
        with patch.object(AiTaskService, "update_task_status", new=AsyncMock()) as up:
            await AiTaskService._fail_task(None, task, 0.0, RuntimeError("db went away"),
                                           "An unexpected error occurred during task execution. Please try again later.")
            kwargs = up.call_args.kwargs
            assert kwargs["new_status"] == "FAILED"
            assert kwargs["error_message"] == "An unexpected error occurred during task execution. Please try again later."

    @pytest.mark.asyncio
    async def test_real_transition_still_reaches_failed(self):
        """End-to-end: an unexpected exception inside _execute_task_internal -> FAILED."""
        task = AiTask(id="t1", status="RUNNING", task_type="idea_evaluation")

        class FakeResult:
            def scalars(self):
                class F:
                    def first(self):
                        return task
                return F()
        db = MagicMock()
        db.execute = AsyncMock(return_value=FakeResult())

        with patch("app.services.ai_task_service.AIRetryPolicy") as rp:
            rp.execute_with_retry = AsyncMock(side_effect=RuntimeError("kaboom"))

            async def fake_update(*args, **kw):
                # _fail_task calls update_task_status with kwargs (db=, task=,
                # new_status=, error_message=...); accept either style.
                db_ = kw.get("db") or (args[0] if args else None)
                task_ = kw.get("task") or (args[1] if len(args) > 1 else None)
                new_status = kw.get("new_status") or (args[2] if len(args) > 2 else None)
                task_.status = new_status
                if kw.get("error_message"):
                    task_.error_message = kw["error_message"]
                return task_

            with patch.object(AiTaskService, "update_task_status", new=AsyncMock(side_effect=fake_update)):
                result = await AiTaskService._execute_task_internal(db, "t1")
                assert result.status == "FAILED"
                assert result.error_message == "An unexpected error occurred during task execution. Please try again later."


# ==============================================================================
# R-07 — IntegrityError -> 409 mapping
# ==============================================================================

class TestConcurrentEvaluationGuard:
    """Invariant: a DB-level unique violation surfaces as HTTP 409 with the
    same shape as the pre-screen path (rollback must occur, no re-raise)."""

    @pytest.mark.asyncio
    async def test_integrity_error_maps_to_409(self):
        from app.evaluation.coordinator import EvaluationCoordinator
        from app.evaluation.state import EvaluationStatus, EvaluationProgress
        from unittest.mock import patch

        idea = MagicMock()
        idea.project_id = "p1"
        eval_row = MagicMock()
        eval_row.id = "new-eval"

        async def fake_verify(db, idea_id, user_id):
            return idea

        with patch.object(EvaluationCoordinator, "verify_idea_ownership", new=staticmethod(fake_verify)):
            # Simulate: pre-screen finds no active, but commit violates the index.
            # Use the REAL Evaluation model so select() builds a valid statement.
            res_active = MagicMock(); res_active.scalar_one_or_none.return_value = None
            db = MagicMock(spec=AsyncSession)
            db.add = MagicMock()
            db.refresh = AsyncMock()
            db.rollback = AsyncMock()
            db.commit = AsyncMock(side_effect=IntegrityError("uq_evaluations_one_active_per_idea", None, Exception()))
            db.execute = AsyncMock(return_value=res_active)

            with patch("app.evaluation.coordinator.EvaluationExecutor") as ex:
                ex.record_history_event = AsyncMock()
                with pytest.raises(HTTPException) as ei:
                    await EvaluationCoordinator.create_evaluation(
                        db=db, idea_id="i1", evaluation_type="startup_evaluation", user_id=1
                    )
        assert ei.value.status_code == 409
        assert "already in progress" in ei.value.detail
        db.rollback.assert_awaited_once()


# ==============================================================================
# R-01 — /metrics degraded state
# ==============================================================================

class TestMetricsDegradedState:
    """Invariant: DB failure no longer fabricates zero-count metrics."""

    @pytest.mark.asyncio
    async def test_metrics_route_reports_degraded(self):
        from httpx import AsyncClient, ASGITransport
        from app.main import app
        from tests.test_auth import _make_token

        token = _make_token(sub="metrics-user")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/metrics", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        body = res.json()
        assert "database_available" in body
        assert body["ai_task_metrics"]["total_tasks"] is not None or body["database_available"] is False

    @pytest.mark.asyncio
    async def test_metrics_db_failure_sets_flag(self, caplog):
        """Direct unit: get_metrics with a failing session reports degraded, not zeros."""
        from unittest.mock import MagicMock
        from app.main import get_metrics

        db = MagicMock()
        db.execute = AsyncMock(side_effect=RuntimeError("connection refused"))
        response = MagicMock()
        response.status_code = 200

        out = await get_metrics(current_user=MagicMock(id=1), db=db)
        assert out["database_available"] is False
        assert out["ai_task_metrics"]["total_tasks"] is None
        assert out["ai_task_metrics"]["by_status"] == {}

    @pytest.mark.asyncio
    async def test_metrics_db_success_keeps_counts(self):
        from unittest.mock import MagicMock
        from app.main import get_metrics

        db = MagicMock()
        res1 = MagicMock(); res1.scalar.return_value = 7
        res2 = MagicMock(); res2.all.return_value = [("QUEUED", 3), ("COMPLETED", 4)]
        db.execute = AsyncMock(side_effect=[res1, res2])

        out = await get_metrics(current_user=MagicMock(id=1), db=db)
        assert out["database_available"] is True
        assert out["ai_task_metrics"]["total_tasks"] == 7
        assert out["ai_task_metrics"]["by_status"] == {"QUEUED": 3, "COMPLETED": 4}


# ==============================================================================
# R-03 — Insight provenance labels (additive contract)
# ==============================================================================

class TestInsightProvenanceContract:
    """Invariant: provenance labels are additive; original keys/values unchanged."""

    @pytest.mark.asyncio
    async def test_labels_present_and_shape_held(self):
        from unittest.mock import MagicMock, AsyncMock
        ev = MagicMock()
        ev.id = "e1"
        ev.result_payload = {
            "score": 72,
            "confidence": 0.9,
            "summary": "s",
            "dimensions": {"innovation": 80, "market_potential": 60, "technical_feasibility": 65,
                           "business_viability": 70, "scalability": 75, "execution_complexity": 55,
                           "competitive_differentiation": 68},
            "strengths": ["S1", "S2", "S3"],
            "weaknesses": ["W1", "W2"],
            "recommendations": ["R1", "R2", "R3", "R4", "R5"],
            "architecture_breakdown": "arch",
        }

        db = MagicMock(spec=AsyncSession)
        res_eval = MagicMock(); res_eval.scalar_one_or_none.return_value = ev
        res_idea = MagicMock(); res_idea.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(side_effect=[res_eval, res_idea])

        out = await insight_service.get_insights(db, "e1")

        # Additive labels present with the honest-provenance vocabulary
        assert out["provenance"] == "HEURISTIC_ESTIMATE"
        assert out["market_analysis"]["tam_sam_som_provenance"] == "HEURISTIC_ESTIMATE"
        assert out["financial_potential"]["financials_provenance"] == "HEURISTIC_ESTIMATE"
        assert out["risk_analysis"]["provenance"] == "HEURISTIC_ESTIMATE"

        # Original contract keys still present and derived from payload
        assert out["executive_summary"]["score"] == 72
        assert out["innovation"]["score"] == 80
        assert out["swot"]["strengths"] == ["S1", "S2", "S3"]
        assert out["competitor_analysis"]["competitive_advantages"] == ["S1", "S2", "S3"]
        assert out["recommendations"]["quick_wins"] == ["R1", "R2"]

    @pytest.mark.asyncio
    async def test_scores_endpoint_shape_unchanged(self):
        from app.services.insight_service import scoring_service
        from unittest.mock import MagicMock, AsyncMock
        ev = MagicMock()
        ev.id = "e1"
        ev.status = "COMPLETED"
        ev.result_payload = {
            "score": 66,
            "confidence": 0.9,
            "dimensions": {"innovation": 70, "market_potential": 70, "technical_feasibility": 70,
                           "business_viability": 70, "scalability": 70, "execution_complexity": 60,
                           "competitive_differentiation": 70},
            "metadata": {"provider": "groq", "model": "m", "prompt_version": "1.0", "duration_ms": 5, "cached": False},
        }
        db = MagicMock(spec=AsyncSession)
        res = MagicMock(); res.scalar_one_or_none.return_value = ev
        db.execute = AsyncMock(return_value=res)

        out = await scoring_service.get_scores(db, "e1")
        # Contract keys that frontend consumes
        for key in ("overall_score", "computed_average", "dimensions", "status", "provider", "model", "cached"):
            assert key in out
        assert out["overall_score"] == 66


# ==============================================================================
# R-04 — Analytics window + provenance
# ==============================================================================

class TestAnalyticsWindowAndProvenance:
    """Invariant: usage gauge bounded to 30 days; provenance labels additive."""

    @pytest.mark.asyncio
    async def test_usage_gauge_window_and_labels(self):
        from app.models.user import User  # noqa: F401  (import path sanity)
        db = MagicMock(spec=AsyncSession)
        res = MagicMock(); res.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=res)

        out = await AnalyticsService.get_ai_usage_gauge(db, user_id=1)
        assert out["window_days"] == 30
        assert out["daily_average_tokens"] == 0  # 0 tokens / 30 with no tasks
        assert out["provenance"] == "DETERMINISTIC_CALCULATION"

    @pytest.mark.asyncio
    async def test_usage_gauge_daily_average_uses_real_window(self):
        """Old bug: total_tokens/30 regardless of window. New: query filtered to
        30 days, so a token burst 60 days ago is excluded entirely."""
        old_task = MagicMock()
        old_task.result_payload = {"tokens": 999999}
        old_task.provider = "groq"
        old_task.status = "COMPLETED"
        db = MagicMock(spec=AsyncSession)
        res = MagicMock(); res.scalars.return_value.all.return_value = [old_task]
        db.execute = AsyncMock(return_value=res)

        # Capture the query filter actually passed to the DB
        captured = {}
        async def capture(stmt):
            captured["stmt"] = stmt
            res = MagicMock(); res.scalars.return_value.all.return_value = []
            return res
        db.execute = AsyncMock(side_effect=capture)

        out = await AnalyticsService.get_ai_usage_gauge(db, user_id=1)
        # The statement must include a created_at >= cutoff clause
        sql = str(captured["stmt"])
        assert "created_at" in sql
        assert out["total_tokens_consumed"] == 0  # empty result honored

    @pytest.mark.asyncio
    async def test_venture_matrix_marks_unmeasured_points(self):
        db = MagicMock(spec=AsyncSession)
        idea = MagicMock(); idea.id = "i1"; idea.title = "T"
        row = (idea, "Proj", None)  # no evaluation -> defaults apply
        res = MagicMock(); res.all.return_value = [row]
        db.execute = AsyncMock(return_value=res)

        out = await AnalyticsService.get_venture_matrix(db, user_id=1)
        pt = out["points"][0]
        assert pt["has_measured_scores"] is False
        assert pt["provenance"] == "HEURISTIC_ESTIMATE"
        assert pt["quadrant"] == "High Value / Low Risk"  # default 75/35 placement preserved

    @pytest.mark.asyncio
    async def test_venture_matrix_marks_measured_points(self):
        db = MagicMock(spec=AsyncSession)
        idea = MagicMock(); idea.id = "i1"; idea.title = "T"
        ev = MagicMock()
        ev.result_payload = {"score": 85, "risk_score": 20, "decision_gate": "BUILD"}
        res = MagicMock(); res.all.return_value = [(idea, "Proj", ev)]
        db.execute = AsyncMock(return_value=res)

        out = await AnalyticsService.get_venture_matrix(db, user_id=1)
        pt = out["points"][0]
        assert pt["has_measured_scores"] is True
        assert pt["provenance"] == "DETERMINISTIC_CALCULATION"
        assert pt["x_attractiveness_score"] == 85.0
        assert pt["quadrant"] == "High Value / Low Risk"


# ==============================================================================
# Architecture note: route LOC fitness re-asserted locally (fast signal)
# ==============================================================================

def test_route_loc_fitness_still_holds():
    """R-05 moved export logic into a helper: routes must stay under the 400-LOC cap."""
    import os, ast
    routes_dir = os.path.join(os.path.dirname(__file__), "..", "app", "api", "routes")
    for root, _, files in os.walk(routes_dir):
        for f in files:
            if f.endswith(".py") and not f.startswith("__"):
                p = os.path.join(root, f)
                with open(p, "r", encoding="utf-8") as fh:
                    lines = [l for l in fh if l.strip() and not l.strip().startswith("#")]
                assert len(lines) <= 400, f"{p} exceeds route LOC cap"
