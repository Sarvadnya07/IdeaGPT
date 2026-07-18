import pytest
from sqlalchemy.future import select
from app.ai.prompts.registry import prompt_registry
from app.ai.validators.output_validator import OutputValidator
from app.ai.pipelines.context import ContextBuilder
from app.services.cache_service import evaluation_cache
from app.ai.orchestrator.orchestrator import orchestrator
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea

@pytest.mark.anyio
async def test_prompt_registry_discovery():
    # Registry should find startup_evaluation and v1.0
    prompts = prompt_registry.list_prompts()
    assert len(prompts) > 0
    assert any(p["id"] == "startup_evaluation" for p in prompts)
    
    versions = prompt_registry.list_versions("startup_evaluation")
    assert "1.0" in versions

@pytest.mark.anyio
async def test_context_builder_and_prompt_rendering(setup_test_db):
    async with AsyncSessionLocal() as db:
        # Seed test user, project, and idea
        user = User(id=10, clerk_id="user_10", email="test10@test.com", name="Test User 10")
        db.add(user)
        await db.commit()

        project = Project(id="proj_10", user_id=10, title="Context Project", slug="context-project")
        db.add(project)
        await db.commit()

        idea = Idea(
            id="idea_10",
            project_id="proj_10",
            title="Registry Idea",
            problem_statement="Problem context",
            solution_description="Solution details",
            is_draft=False
        )
        db.add(idea)
        await db.commit()

        # Build context
        context = await ContextBuilder.build_context(db, "idea_10")
        assert context["project_title"] == "Context Project"
        assert context["idea_title"] == "Registry Idea"
        
        # Render prompt
        rendered = prompt_registry.render_prompt("startup_evaluation", context, version="1.0")
        assert "Registry Idea" in rendered["user_prompt"]
        assert rendered["version"] == "1.0"

@pytest.mark.anyio
async def test_output_validator_repair():
    # Valid JSON test
    raw = '{"summary": "Clean concept", "score": 85, "strengths": ["a"], "weaknesses": ["b"], "recommendations": ["c"], "confidence": 0.9, "dimensions": {"innovation": 80, "market_potential": 85, "technical_feasibility": 70, "business_viability": 75, "scalability": 80, "execution_complexity": 70, "competitive_differentiation": 85}}'
    model, err = OutputValidator.validate_and_repair(raw)
    assert err is None
    assert model.score == 85
    
    # Broken JSON repair test
    broken_markdown = '```json\n{"summary": "Markdown wrapper", "score": 90, "strengths": [], "weaknesses": [], "recommendations": [], "confidence": 0.9, "dimensions": {"innovation": 90, "market_potential": 90, "technical_feasibility": 90, "business_viability": 90, "scalability": 90, "execution_complexity": 90, "competitive_differentiation": 90}}\n```'
    model2, err2 = OutputValidator.validate_and_repair(broken_markdown)
    assert err2 is None
    assert model2.score == 90

@pytest.mark.anyio
async def test_cache_hits_and_misses():
    idea_text = "Unique idea text representation"
    # Clear local cache map for reliability
    evaluation_cache.local_cache.clear()
    
    res = evaluation_cache.get(idea_text, "1.0", "mock-model", "mock-provider")
    assert res is None # Cache miss
    
    payload = {"score": 95, "metadata": {"prompt_version": "1.0"}}
    evaluation_cache.set(idea_text, "1.0", "mock-model", "mock-provider", payload)
    
    cached = evaluation_cache.get(idea_text, "1.0", "mock-model", "mock-provider")
    assert cached is not None
    assert cached["score"] == 95
