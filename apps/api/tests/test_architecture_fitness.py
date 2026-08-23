"""
IdeaGPT — Automated Architecture Fitness Function Suite

Continuously validates architectural invariants:
  1. Dependency Direction: Low-level layers (core, models, schemas) must not import API routes.
  2. Pure Engine Isolation: DeterministicEvaluationEngine must have zero database, API, or network dependencies.
  3. Pydantic v2 Standardization: All schemas must use ConfigDict(from_attributes=True) with 0 legacy Config classes.
  4. Multi-Tenant Scoping: Domain services and coordinators must enforce user isolation.
  5. Security Fail-Closed: Production settings validator must reject insecure configurations.
  6. SSE Streaming API Contract: Real-time event streaming endpoint contract validation.
"""
import ast
import inspect
import os
import sys
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.config import Settings
from app.evaluation.engine import DeterministicEvaluationEngine
from app.evaluation.coordinator import EvaluationCoordinator
from app.services.ai_task_service import AiTaskService
from app.services.comparison_service import ComparisonService
from app.services.analytics_service import AnalyticsService

# Base directory for app source code
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))


def _get_python_files(subfolder: str):
    folder_path = os.path.join(APP_DIR, subfolder)
    py_files = []
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.endswith(".py") and not f.startswith("__"):
                py_files.append(os.path.join(root, f))
    return py_files


# ===========================================================================
# 1. Dependency Direction & Layer Integrity
# ===========================================================================
def test_dependency_direction_core_and_models_do_not_import_routes():
    """
    Fitness Rule: Stable lower layers (core, models, schemas) MUST NOT import
    from outer application/controller layers (app.api.routes).
    """
    forbidden_import_targets = ["app.api.routes", "app.api.dependencies"]
    checked_folders = ["core", "models", "schemas", "db"]

    for folder in checked_folders:
        for filepath in _get_python_files(folder):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=filepath)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for forbidden in forbidden_import_targets:
                            assert not alias.name.startswith(forbidden), (
                                f"Architecture Violation in {filepath}: Lower layer imports {alias.name}"
                            )
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for forbidden in forbidden_import_targets:
                        assert not module.startswith(forbidden), (
                            f"Architecture Violation in {filepath}: Lower layer imports from {module}"
                        )


# ===========================================================================
# 2. Pure Engine Isolation Invariant
# ===========================================================================
def test_deterministic_engine_zero_external_dependencies():
    """
    Fitness Rule: DeterministicEvaluationEngine MUST remain 100% pure, offline,
    and free from database connections, network clients, or LLM SDK imports.
    """
    engine_file = os.path.join(APP_DIR, "evaluation", "engine.py")
    with open(engine_file, "r", encoding="utf-8") as f:
        content = f.read()
        tree = ast.parse(content, filename=engine_file)

    forbidden_modules = ["sqlalchemy", "asyncpg", "httpx", "requests", "openai", "groq", "app.db", "app.api"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in forbidden_modules:
                    assert not alias.name.startswith(forbidden), (
                        f"Purity Violation in engine.py: imported {alias.name}"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for forbidden in forbidden_modules:
                assert not module.startswith(forbidden), (
                    f"Purity Violation in engine.py: imported from {module}"
                )


# ===========================================================================
# 3. Pydantic v2 Schema Conformity
# ===========================================================================
def test_pydantic_v2_schema_standards():
    """
    Fitness Rule: All API schemas must use Pydantic v2 ConfigDict and contain
    ZERO legacy 'class Config:' declarations.
    """
    schema_files = _get_python_files("schemas")
    assert len(schema_files) > 0, "No schema files found"

    for filepath in schema_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content, filename=filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Config":
                pytest.fail(f"Pydantic v2 Violation in {filepath}: found deprecated 'class Config:'")


# ===========================================================================
# 4. Multi-Tenant Scoping Invariant
# ===========================================================================
def test_domain_services_enforce_user_isolation_parameter():
    """
    Fitness Rule: Domain services and coordinators handling private user entities
    must require user_id or User parameter in their public access interfaces.
    """
    # EvaluationCoordinator verification methods
    verify_sig = inspect.signature(EvaluationCoordinator.verify_idea_ownership)
    assert "user_id" in verify_sig.parameters, "verify_idea_ownership must enforce user_id parameter"

    get_eval_sig = inspect.signature(EvaluationCoordinator.get_evaluation)
    assert "user_id" in get_eval_sig.parameters, "get_evaluation must enforce user_id parameter"

    # ComparisonService
    compare_sig = inspect.signature(ComparisonService.compare_ideas)
    assert "user_id" in compare_sig.parameters, "compare_ideas must enforce user_id parameter"

    # AnalyticsService
    analytics_sig = inspect.signature(AnalyticsService.get_user_analytics)
    assert "user_id" in analytics_sig.parameters, "get_user_analytics must enforce user_id parameter"

    # AiTaskService
    create_task_sig = inspect.signature(AiTaskService.create_task)
    assert "user" in create_task_sig.parameters, "create_task must enforce user parameter"


# ===========================================================================
# 5. Security Fail-Closed Production Configuration Check
# ===========================================================================
def test_production_configuration_fail_fast():
    """
    Fitness Rule: In production mode (APP_ENV=production), Settings must
    fail-fast with RuntimeError if insecure or missing parameters are present.
    """
    # Case 1: Missing Clerk issuer in production
    s1 = Settings(APP_ENV="production", CLERK_PUBLISHABLE_KEY="", CLERK_JWT_ISSUER="", CLERK_JWT_TEST_SECRET=None)
    with pytest.raises(RuntimeError, match="PRODUCTION CONFIG ERROR"):
        s1.validate_production_config()

    # Case 2: Insecure test secret set in production
    s2 = Settings(
        APP_ENV="production",
        CLERK_PUBLISHABLE_KEY="pk_test_dGVzdC5jbGVyay5hY2NvdW50cy5kZXYk",
        CLERK_JWT_TEST_SECRET="should-never-be-in-prod-32bytes!"
    )
    with pytest.raises(RuntimeError, match="PRODUCTION CONFIG SECURITY ERROR"):
        s2.validate_production_config()

    # Case 3: Wildcard CORS origin in production
    s3 = Settings(
        APP_ENV="production",
        CLERK_PUBLISHABLE_KEY="pk_test_dGVzdC5jbGVyay5hY2NvdW50cy5kZXYk",
        CLERK_JWT_TEST_SECRET=None,
        CORS_ORIGINS="*"
    )
    with pytest.raises(RuntimeError, match="CORS_ORIGINS cannot contain wildcard"):
        s3.validate_production_config()

    # Case 4: SQLite database in production
    s4 = Settings(
        APP_ENV="production",
        CLERK_PUBLISHABLE_KEY="pk_test_dGVzdC5jbGVyay5hY2NvdW50cy5kZXYk",
        CLERK_JWT_TEST_SECRET=None,
        DATABASE_URL="sqlite+aiosqlite:///./prod.db"
    )
    with pytest.raises(RuntimeError, match="SQLite DATABASE_URL cannot be used in production"):
        s4.validate_production_config()


# ===========================================================================
# 6. SSE Real-Time Streaming Endpoint Contract
# ===========================================================================
@pytest.mark.asyncio
async def test_sse_streaming_endpoint_contract():
    """
    Fitness Rule: The SSE streaming endpoint GET /api/v1/ai/tasks/{task_id}/stream
    must respond with 'text/event-stream' content-type.
    """
    from tests.test_auth import _make_token
    token = _make_token(sub="user_fitness_001")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Request stream for a non-existent/test task ID
        res = await ac.get(
            "/api/v1/ai/tasks/non-existent-task-id/stream",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200
        assert "text/event-stream" in res.headers.get("content-type", "")
        # Should yield error event for non-existent task
        assert "event: error" in res.text or "event: task_update" in res.text
