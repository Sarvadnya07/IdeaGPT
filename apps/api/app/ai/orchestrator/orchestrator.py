import time
import logging
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.orchestrator.factory import ProviderFactory
from app.ai.orchestrator.router import AIRouter
from app.ai.prompts.registry import prompt_registry
from app.ai.validators.output_validator import OutputValidator
from app.ai.pipelines.context import ContextBuilder
from app.services.cache_service import evaluation_cache

logger = logging.getLogger(__name__)

class AIOrchestrator:
    @staticmethod
    async def analyze_startup_idea(
        prompt: str = None,  # first argument for backward-compatibility
        db: AsyncSession = None,
        idea_id: str = None,
        prompt_version: str = "1.0",
        force_fresh: bool = False,
        preferred_provider: str = None,
        requested_model: str = None,
        strategy: str = "auto"
    ) -> dict:
        """
        AI Evaluation Pipeline:
        Context -> Prompt Resolver -> Cache Check -> LLM invocation -> Output Validator/Repair -> Cache Save.
        Gracefully falls back to DeterministicEvaluationEngine on upstream provider/model failure.
        """
        user_prompt = ""
        system_prompt = "You are a world-class AI Startup Analyst. You must return your analysis strictly as JSON matching the requested structure."
        p_version = prompt_version
        temp = 0.2
        max_t = 1500
        idea_obj = None

        # Resolve context if db & idea_id are provided
        if db and idea_id:
            from app.models.idea import Idea
            from sqlalchemy import select
            stmt = select(Idea).where(Idea.id == idea_id)
            res = await db.execute(stmt)
            idea_obj = res.scalars().first()

            context = await ContextBuilder.build_context(db, idea_id)
            idea_text = f"{context['idea_title']} {context['problem_statement']} {context['solution_description']}"
            prompt_config = prompt_registry.render_prompt("startup_evaluation", context, version=prompt_version)
            user_prompt = prompt_config["user_prompt"]
            system_prompt = prompt_config["system_prompt"]
            p_version = prompt_config["version"]
            temp = prompt_config["temperature"]
            max_t = prompt_config["max_tokens"]
        else:
            # Fallback for simple prompt integration
            user_prompt = prompt or "Analyze startup idea."
            idea_text = user_prompt

        # Router selection
        decision = AIRouter.route_task(
            task_type="idea_evaluation",
            requested_provider=preferred_provider or strategy,
            requested_model=requested_model
        )
        provider_name = decision["actual_provider"]
        target_model = decision["actual_model"]

        provider = ProviderFactory.create_provider(provider_name)

        # Cache Check
        if not force_fresh:
            cached_result = evaluation_cache.get(
                idea_text=idea_text,
                prompt_version=p_version,
                model=target_model,
                provider=provider_name
            )
            if cached_result:
                cached_result["metadata"]["cached"] = True
                return cached_result

        # LLM Invocation with Resilient Fallback
        try:
            start_time = time.time()
            raw_response = await provider.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                response_format="json",
                model_override=target_model
            )
            duration_ms = int((time.time() - start_time) * 1000)
            actual_model = raw_response.get("_actual_model") or target_model

            # Output Validator & Repair
            validated_model, error_msg = OutputValidator.validate_and_repair(raw_response)
            
            if not validated_model and error_msg:
                logger.warning(f"Initial AI response invalid: {error_msg}. Retrying with repair guidance...")
                repair_prompt = (
                    f"{user_prompt}\n\n"
                    f"Your previous response was malformed/invalid because: {error_msg}.\n"
                    f"Please fix and return valid JSON matching the requested schema exactly."
                )
                raw_response = await provider.generate(
                    prompt=repair_prompt,
                    system_prompt=system_prompt,
                    response_format="json"
                )
                validated_model, error_msg = OutputValidator.validate_and_repair(raw_response)

            if validated_model:
                result_dict = validated_model.model_dump()
                result_dict["metadata"] = {
                    "provider": provider_name,
                    "model": actual_model,
                    "prompt_version": p_version,
                    "temperature": temp,
                    "max_tokens": max_t,
                    "duration_ms": duration_ms,
                    "token_usage": raw_response.get("_usage", {}).get("total_tokens", 1500),
                    "estimated_cost": 0.003,
                    "cached": False
                }

                # Cache Save
                evaluation_cache.set(
                    idea_text=idea_text,
                    prompt_version=p_version,
                    model=actual_model,
                    provider=provider_name,
                    result_payload=result_dict
                )
                return result_dict

        except Exception as exc:
            logger.warning(f"Upstream AI provider '{provider_name}' failed ({exc}). Engaging deterministic fallback engine...")

        # Fallback Execution via DeterministicEvaluationEngine
        from app.evaluation.engine import DeterministicEvaluationEngine
        if idea_obj:
            fallback_payload = DeterministicEvaluationEngine.evaluate(idea_obj)
        else:
            dummy_idea = type("IdeaObj", (), {
                "title": (prompt or "Startup Idea")[:50],
                "problem_statement": user_prompt,
                "solution_description": user_prompt,
                "target_users": "Founders, Developers",
                "industry": "Technology",
                "business_model": "B2B SaaS",
                "stage": "Prototype",
                "tags": "ai, tech, saas",
                "notes": ""
            })()
            fallback_payload = DeterministicEvaluationEngine.evaluate(dummy_idea)

        fallback_payload["metadata"]["fallback_reason"] = f"Provider {provider_name} fallback"
        return fallback_payload

    @classmethod
    async def generate_dynamic_tool(
        cls,
        tool_name: str,
        user_prompt: str,
        system_prompt: str,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile",
        fallback_fn = None
    ) -> dict:
        """
        Generic dynamic LLM generator for deep tool synthesis across Roadmap, PRD, Pitch Deck, Tech Stack, Architecture.
        """
        import json
        import os
        from app.core.config import settings

        # In test mode without opt-in GROQ_E2E, immediately engage fast deterministic fallback to prevent external API calls and token consumption
        if settings.APP_ENV == "test" and os.getenv("GROQ_E2E") != "true":
            if fallback_fn:
                fb = fallback_fn()
                if isinstance(fb, dict):
                    fb["_execution_type"] = "DETERMINISTIC_ENGINE"
                    fb["_fallback_used"] = True
                return fb

        p_name = provider or "groq"
        m_name = model or "llama-3.3-70b-versatile"

        # Check Cache
        cached = evaluation_cache.get(
            idea_text=user_prompt,
            prompt_version=f"tool_{tool_name}",
            model=m_name,
            provider=p_name
        )
        if cached:
            cached["_cached"] = True
            cached["_execution_type"] = "CACHED_RESULT"
            cached["_fallback_used"] = False
            return cached

        try:
            prov = ProviderFactory.create_provider(p_name)
            raw = await prov.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                response_format="json",
                model_override=m_name
            )

            cleaned_text = OutputValidator.clean_json_string(raw if isinstance(raw, str) else json.dumps(raw))
            parsed = json.loads(cleaned_text)

            if isinstance(parsed, dict):
                parsed["_provider"] = p_name
                parsed["_model"] = m_name
                parsed["_execution_type"] = "REAL_PROVIDER"
                parsed["_fallback_used"] = False
                evaluation_cache.set(
                    idea_text=user_prompt,
                    prompt_version=f"tool_{tool_name}",
                    model=m_name,
                    provider=p_name,
                    result_payload=parsed
                )
                return parsed
        except Exception as e:
            logger.warning(f"Dynamic LLM generation failed for {tool_name} with {p_name}/{m_name}: {e}. Engaging fallback...")

        if fallback_fn:
            fb = fallback_fn()
            if isinstance(fb, dict):
                fb["_execution_type"] = "DETERMINISTIC_ENGINE"
                fb["_fallback_used"] = True
            return fb
        return {"_execution_type": "DETERMINISTIC_ENGINE", "_fallback_used": True}

    @classmethod
    async def generate_roadmap_ai(
        cls,
        title: str,
        category: str,
        problem_statement: str,
        solution_description: str,
        target_users: str,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile"
    ) -> list:
        user_prompt = (
            f"Generate a customized, domain-specific execution roadmap for this startup:\n"
            f"Title: {title}\n"
            f"Category: {category}\n"
            f"Problem: {problem_statement}\n"
            f"Solution: {solution_description}\n"
            f"Target Users: {target_users}\n\n"
            f"Provide strictly a JSON object with key 'milestones', an array of 4 sequential phase objects. "
            f"Each phase object must have 'title' (e.g. 'Phase 1: Native Audio Pipeline & Core Shell'), 'objective', "
            f"and 'tasks' (array of 3-4 specific technical tasks, each with 'title', 'description', 'estimated_days' (integer 1-7), and 'status' set to 'pending')."
        )
        system_prompt = (
            "You are an elite Principal Software Architect and Startup Technical Program Manager. "
            "Never generate generic tasks. Synthesize specific architectural steps, SDKs, protocols, and workflows tailored strictly to the startup idea."
        )

        from app.services.architecture_service import architecture_service
        fallback_fn = lambda: architecture_service.generate_ai_roadmap(
            title=title, category=category, problem_statement=problem_statement,
            solution_description=solution_description, target_users=target_users
        )

        result = await cls.generate_dynamic_tool(
            tool_name="roadmap",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            fallback_fn=lambda: {"milestones": fallback_fn()}
        )
        return result.get("milestones") or fallback_fn()

    @classmethod
    async def generate_tech_stack_ai(
        cls,
        title: str,
        category: str,
        focus: str = "balanced",
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile"
    ) -> dict:
        user_prompt = (
            f"Generate a modern, production-grade technology stack blueprint for this startup:\n"
            f"Title: {title}\nCategory: {category}\nFocus Strategy: {focus}\n\n"
            f"Return strictly a JSON object with keys: 'title', 'category', 'focus', "
            f"'frontend' (object with framework, styling, state_management, component_library, build_tooling), "
            f"'backend' (object with language, framework, api_protocol, validation, rate_limiting), "
            f"'database_and_caching' (object with primary_database, caching_layer, migrations, orm, vector_database), "
            f"'ai_and_ml' (object with inference_providers, orchestration, caching, output_validation), "
            f"'devops_and_security' (object with hosting, authentication, ci_cd, observability), and "
            f"'architectural_tradeoffs' (array of 3 tradeoff objects with 'decision', 'pros', 'cons')."
        )
        system_prompt = "You are a Principal Cloud & Systems Architect. Provide specific, cutting-edge, realistic technology stack recommendations."

        from app.services.architecture_service import architecture_service
        fallback_fn = lambda: architecture_service.generate_tech_stack(category=category, title=title, requirements_focus=focus)

        result = await cls.generate_dynamic_tool(
            tool_name="tech_stack",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            fallback_fn=fallback_fn
        )
        return result if "frontend" in result else fallback_fn()

    @classmethod
    async def generate_architecture_ai(
        cls,
        title: str,
        category: str,
        description: str,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile"
    ) -> dict:
        user_prompt = (
            f"Design an enterprise system architecture blueprint for this startup:\n"
            f"Title: {title}\nCategory: {category}\nDescription: {description}\n\n"
            f"Return strictly a JSON object with keys: 'title', 'category', 'description', "
            f"'topology' (object with client_layer, gateway_layer, compute_layer, data_layer, ai_inference_layer, caching_layer, background_workers), "
            f"'mermaid_diagram' (a valid Mermaid diagram string formatted as 'graph TD; ...'), "
            f"'api_endpoints' (array of 4-6 objects with 'method', 'path', 'description'), "
            f"'database_entities' (array of 3-5 objects with 'table', 'columns' (list of strings), 'description'), and "
            f"'security_specifications' (list of 4-6 specific security & compliance specifications)."
        )
        system_prompt = "You are a Principal Systems Architect. Create detailed, tailored system topology and data flow diagrams."

        from app.services.architecture_service import architecture_service
        fallback_fn = lambda: architecture_service.generate_architecture_blueprint(title=title, category=category, description=description)

        result = await cls.generate_dynamic_tool(
            tool_name="architecture",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            fallback_fn=fallback_fn
        )
        return result if "topology" in result else fallback_fn()

    @classmethod
    async def generate_prd_ai(
        cls,
        title: str,
        category: str,
        problem_statement: str,
        solution_description: str,
        target_users: str,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile"
    ) -> dict:
        user_prompt = (
            f"Author a comprehensive Product Requirements Document (PRD) for this startup:\n"
            f"Title: {title}\nCategory: {category}\nProblem: {problem_statement}\nSolution: {solution_description}\nTarget Users: {target_users}\n\n"
            f"Return strictly a JSON object with keys: 'title', 'version', 'status', 'category', 'target_users', 'executive_summary', "
            f"'problem_definition' (object with 'core_problem', 'current_alternatives' (list), 'why_now'), "
            f"'user_personas' (array of 2-3 objects with 'persona', 'need'), "
            f"'functional_requirements' (array of 4-6 objects with 'id', 'feature', 'priority', 'description'), "
            f"'non_functional_requirements' (array of 3-5 objects with 'id', 'category', 'target'), and "
            f"'success_metrics' (array of 3-5 objects with 'metric', 'target')."
        )
        system_prompt = "You are a Senior Product Leader (VP of Product). Produce highly actionable, crisp, domain-specific PRDs."

        from app.services.architecture_service import architecture_service
        fallback_fn = lambda: architecture_service.generate_prd(
            title=title, category=category, problem_statement=problem_statement,
            solution_description=solution_description, target_users=target_users
        )

        result = await cls.generate_dynamic_tool(
            tool_name="prd",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            fallback_fn=fallback_fn
        )
        res_dict = result if "executive_summary" in result else fallback_fn()
        if isinstance(res_dict, dict) and not str(res_dict.get("title", "")).startswith("PRD:"):
            res_dict["title"] = f"PRD: {title}"
        return res_dict

    @classmethod
    async def generate_pitch_deck_ai(
        cls,
        title: str,
        category: str,
        problem: str,
        solution: str,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile"
    ) -> list:
        user_prompt = (
            f"Create a high-converting 10-slide venture pitch deck outline for this startup:\n"
            f"Title: {title}\nCategory: {category}\nProblem: {problem}\nSolution: {solution}\n\n"
            f"Return strictly a JSON object with key 'slides', an array of 10 slide objects. "
            f"Each slide object must have 'slide_number' (1-10), 'title' (e.g. '1. Problem', '4. TAM / SAM / SOM', '6. Business Model'), "
            f"'headline' (a punchy investor headline), and 'bullet_points' (array of 3-4 specific narrative points tailored to the startup)."
        )
        system_prompt = "You are a Tier-1 Venture Capitalist & Pitch Deck Architect. Generate compelling, metrics-driven startup slide narratives."

        from app.services.architecture_service import architecture_service
        fallback_fn = lambda: architecture_service.generate_pitch_deck_outline(title=title, category=category, problem=problem, solution=solution)

        result = await cls.generate_dynamic_tool(
            tool_name="pitch_deck",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            fallback_fn=lambda: {"slides": fallback_fn()}
        )
        return result.get("slides") or fallback_fn()

    @classmethod
    async def generate_github_lab_ai(
        cls,
        title: str,
        category: str,
        tech_stack: Optional[str] = None,
        description: Optional[str] = None,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile"
    ) -> dict:
        user_prompt = (
            f"Generate a production GitHub repository blueprint for this startup codebase:\n"
            f"Title: {title}\nCategory: {category}\nTech Stack: {tech_stack or 'Modern Full-Stack'}\nDescription: {description or ''}\n\n"
            f"Return strictly a JSON object with keys: "
            f"'repository_name' (e.g. 'ideagpt-core'), 'description', 'license' (e.g. 'MIT'), "
            f"'directory_tree' (array of objects with 'path', 'type' ('file' or 'dir'), 'description'), "
            f"'ci_cd_workflow' (valid GitHub Actions YAML string with test, lint, and build jobs), "
            f"'dockerfile' (optimized multi-stage Dockerfile string), "
            f"'readme_content' (comprehensive Markdown README with architecture diagram, quickstart, environment variables table), "
            f"'recommended_open_source_libs' (array of 4-6 specific libraries/packages with 'name', 'purpose', 'url')."
        )
        system_prompt = "You are a Principal DevOps Engineer and Open Source Architect. Generate production-ready repository scaffolding and CI/CD pipelines."

        def fallback_fn():
            slug = title.lower().replace(" ", "-").replace("/", "-")
            return {
                "repository_name": slug,
                "description": f"Production repository for {title} ({category})",
                "license": "MIT",
                "directory_tree": [
                    {"path": "apps/web", "type": "dir", "description": "Next.js 16 frontend application"},
                    {"path": "apps/api", "type": "dir", "description": "FastAPI async Python backend"},
                    {"path": "packages/ui", "type": "dir", "description": "Shared design system components"},
                    {"path": ".github/workflows/ci.yml", "type": "file", "description": "Automated CI/CD validation pipeline"},
                    {"path": "Dockerfile", "type": "file", "description": "Multi-stage production container build"},
                    {"path": "docker-compose.yml", "type": "file", "description": "Local PostgreSQL & Redis orchestration"},
                    {"path": "README.md", "type": "file", "description": "Setup and developer documentation"}
                ],
                "ci_cd_workflow": "name: CI Pipeline\non: [push, pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - name: Run Tests\n        run: pnpm test",
                "dockerfile": "FROM node:20-alpine AS base\nWORKDIR /app\nCOPY package.json pnpm-lock.yaml ./\nRUN npm install -g pnpm && pnpm install\nCOPY . .\nRUN pnpm build\nEXPOSE 3000\nCMD [\"pnpm\", \"start\"]",
                "readme_content": f"# {title}\n\n> {category} — AI-Powered Architecture\n\n## Quickstart\n```bash\npnpm install\npnpm run dev\n```\n\n## Architecture\n- **Frontend**: Next.js 16 + Tailwind CSS\n- **Backend**: FastAPI + SQLAlchemy\n- **Database**: PostgreSQL 16 + Redis",
                "recommended_open_source_libs": [
                    {"name": "pydantic-v2", "purpose": "Type validation & schema enforcement", "url": "https://docs.pydantic.dev"},
                    {"name": "tanstack-query", "purpose": "Asynchronous state management", "url": "https://tanstack.com/query"},
                    {"name": "fastapi", "purpose": "High-performance async API server", "url": "https://fastapi.tiangolo.com"},
                    {"name": "lucide-react", "purpose": "Iconography system", "url": "https://lucide.dev"}
                ]
            }

        result = await cls.generate_dynamic_tool(
            tool_name="github_lab",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            fallback_fn=fallback_fn
        )
        return result if "directory_tree" in result else fallback_fn()

    @classmethod
    async def generate_investor_lab_ai(
        cls,
        title: str,
        category: str,
        market_size: Optional[str] = None,
        target_raise: Optional[str] = None,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile"
    ) -> dict:
        user_prompt = (
            f"Conduct an institutional venture capital investment analysis for this startup:\n"
            f"Title: {title}\nCategory: {category}\nMarket Size: {market_size or 'High-Growth Global TAM'}\nTarget Raise: {target_raise or '$1.5M Seed'}\n\n"
            f"Return strictly a JSON object with keys: "
            f"'valuation_range' (object with 'pre_money_min_usd', 'pre_money_max_usd', 'target_raise_usd', 'dilution_pct', 'methodology'), "
            f"'investor_scorecard' (object with integer scores 1-100 and brief comments for 'market_opportunity', 'team_and_execution', 'defensibility_moat', 'unit_economics', 'overall_investability'), "
            f"'funding_stages' (array of 3 objects with 'stage' (e.g. 'Pre-Seed', 'Seed', 'Series A'), 'target_arr', 'key_milestones' (list), 'valuation_benchmark'), "
            f"'cap_table_simulation' (array of objects with 'stakeholder', 'initial_equity_pct', 'post_seed_equity_pct', 'post_series_a_pct'), "
            f"'risk_matrix' (array of 3-4 objects with 'risk_factor', 'severity' ('LOW'|'MEDIUM'|'HIGH'), 'mitigation_strategy'), "
            f"'elevator_pitch' (a 2-sentence crisp institutional investment thesis)."
        )
        system_prompt = "You are a Partner at a Tier-1 Silicon Valley Venture Capital firm. Provide rigorous financial modeling, defensibility analysis, and term-sheet guidance."

        def fallback_fn():
            return {
                "valuation_range": {
                    "pre_money_min_usd": 6000000,
                    "pre_money_max_usd": 10000000,
                    "target_raise_usd": 1500000,
                    "dilution_pct": 15.0,
                    "methodology": "Scorecard Valuation + VC Multiples Method based on vertical SaaS comps"
                },
                "investor_scorecard": {
                    "market_opportunity": 88,
                    "team_and_execution": 82,
                    "defensibility_moat": 85,
                    "unit_economics": 80,
                    "overall_investability": 84
                },
                "funding_stages": [
                    {
                        "stage": "Seed ($1.5M)",
                        "target_arr": "$500k ARR",
                        "key_milestones": ["First 50 enterprise pilots", "Net revenue retention > 115%", "Automated onboarding pipeline"],
                        "valuation_benchmark": "$8M - $12M Post-Money"
                    },
                    {
                        "stage": "Series A ($6.0M)",
                        "target_arr": "$2.5M - $4.0M ARR",
                        "key_milestones": ["Scalable outbound motion", "Gross margins > 80%", "Zero to negative churn in core ICP"],
                        "valuation_benchmark": "$25M - $40M Post-Money"
                    }
                ],
                "cap_table_simulation": [
                    {"stakeholder": "Founders", "initial_equity_pct": 85.0, "post_seed_equity_pct": 70.0, "post_series_a_pct": 52.5},
                    {"stakeholder": "Employee Option Pool (ESOP)", "initial_equity_pct": 15.0, "post_seed_equity_pct": 12.0, "post_series_a_pct": 10.0},
                    {"stakeholder": "Seed Investors", "initial_equity_pct": 0.0, "post_seed_equity_pct": 18.0, "post_series_a_pct": 14.5},
                    {"stakeholder": "Series A Investors", "initial_equity_pct": 0.0, "post_seed_equity_pct": 0.0, "post_series_a_pct": 23.0}
                ],
                "risk_matrix": [
                    {"risk_factor": "Customer Acquisition Cost (CAC) Escalation", "severity": "MEDIUM", "mitigation_strategy": "Establish organic product-led referral loops before scaling paid acquisition."},
                    {"risk_factor": "Incumbent Fast-Follower Threat", "severity": "HIGH", "mitigation_strategy": "Build proprietary vertical workflows and high-friction switching costs into the core data layer."},
                    {"risk_factor": "Regulatory Compliance & Data Privacy", "severity": "LOW", "mitigation_strategy": "Implement SOC2 Type II and GDPR compliance controls from day one."}
                ],
                "elevator_pitch": f"{title} captures high-margin market share in {category} by deploying an AI-native operating model that drives 10x workflow efficiency over legacy incumbents."
            }

        result = await cls.generate_dynamic_tool(
            tool_name="investor_lab",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            fallback_fn=fallback_fn
        )
        return result if "investor_scorecard" in result else fallback_fn()

    @classmethod
    async def generate_mentor_lab_ai(
        cls,
        title: str,
        category: str,
        stage: Optional[str] = None,
        challenges: Optional[str] = None,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile"
    ) -> dict:
        user_prompt = (
            f"Synthesize an elite founder mentoring advisory session for this startup:\n"
            f"Title: {title}\nCategory: {category}\nStage: {stage or 'Early Idea / MVP'}\nKey Challenges: {challenges or 'Go-to-market distribution and initial technical velocity'}\n\n"
            f"Return strictly a JSON object with keys: "
            f"'mentor_persona' (object with 'name', 'role', 'philosophy'), "
            f"'executive_coaching_summary' (direct, candid founder advice), "
            f"'top_founder_blindspots' (array of 3 objects with 'blindspot', 'why_it_kills_startups', 'immediate_action'), "
            f"'applied_mental_models' (array of 3 objects with 'model_name' (e.g. 'Inversion', 'First Principles', 'Regret Minimization'), 'how_to_apply'), "
            f"'execution_plan_30_60_90' (object with 'days_30' (list), 'days_60' (list), 'days_90' (list)), "
            f"'critical_questions_for_the_founder' (array of 4 tough strategic questions)."
        )
        system_prompt = "You are a Legendary Startup Founder & Executive Coach (YC partner style). Be direct, pragmatic, and laser-focused on customer obsession and ruthless prioritization."

        def fallback_fn():
            return {
                "mentor_persona": {
                    "name": "Alex Vance",
                    "role": "2x Unicorn Founder & YC Advisory Partner",
                    "philosophy": "Talk to 10 customers every single week and write code every day. Everything else is a distraction."
                },
                "executive_coaching_summary": f"Your primary bottleneck for {title} is not technology; it is finding the acute, burning hair-on-fire problem for your first 10 true believers. Stop refining presentations and start shipping weekly customer experiments.",
                "top_founder_blindspots": [
                    {
                        "blindspot": "Building features before validating willingness-to-pay",
                        "why_it_kills_startups": "Founders spend 6 months building polished software that nobody will pay for.",
                        "immediate_action": "Secure 3 signed Letters of Intent (LOIs) or paid pre-orders before writing complex backend code."
                    },
                    {
                        "blindspot": "Premature scaling of marketing spend",
                        "why_it_kills_startups": "Pouring money into an unproven, leaky conversion funnel burns runway rapidly.",
                        "immediate_action": "Acquire first 50 users purely through manual, high-touch founder outreach."
                    },
                    {
                        "blindspot": "Diffusion of focus across multiple customer profiles",
                        "why_it_kills_startups": "Serving everybody means delighting nobody.",
                        "immediate_action": "Pick exactly ONE ICP (Ideal Customer Profile) and reject all out-of-scope requests."
                    }
                ],
                "applied_mental_models": [
                    {"model_name": "Inversion (Jacobi Principle)", "how_to_apply": "Ask: 'How could this startup guarantee failure in 90 days?' Avoid those exact traps."},
                    {"model_name": "First Principles Thinking", "how_to_apply": "Deconstruct your industry's core cost structure and rebuild it using modern AI leverage."},
                    {"model_name": "Regret Minimization Framework", "how_to_apply": "Make the high-conviction bet that you would regret not taking 10 years from now."}
                ],
                "execution_plan_30_60_90": {
                    "days_30": ["Conduct 25 structured user discovery interviews", "Ship MVP with core value loop only", "Get 5 active daily test users"],
                    "days_60": ["Refine onboarding to reach 'Aha!' moment in under 2 minutes", "Implement cohort retention tracking", "Achieve 40%+ weekly retention"],
                    "days_90": ["Launch paid tier with Stripe integration", "Close first $5,000 in recurring revenue", "Document repeatable sales playbook"]
                },
                "critical_questions_for_the_founder": [
                    "What is the single reason a user would switch from their current spreadsheet/tool to yours today?",
                    "If you could only build one single screen, what would that screen do?",
                    "What makes your unit economics 10x better than existing competitors?",
                    "Why are you the uniquely qualified founding team to win this vertical?"
                ]
            }

        result = await cls.generate_dynamic_tool(
            tool_name="mentor_lab",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            fallback_fn=fallback_fn
        )
        return result if "mentor_persona" in result else fallback_fn()

    @classmethod
    async def generate_recruiter_lab_ai(
        cls,
        title: str,
        category: str,
        current_team_size: Optional[str] = None,
        target_roles: Optional[str] = None,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile"
    ) -> dict:
        user_prompt = (
            f"Create an executive talent and hiring blueprint for this startup:\n"
            f"Title: {title}\nCategory: {category}\nCurrent Team: {current_team_size or 'Founders only (1-2)'}\nTarget Roles: {target_roles or 'Founding Engineer, Growth Lead, Product Designer'}\n\n"
            f"Return strictly a JSON object with keys: "
            f"'hiring_roadmap' (array of 2-3 phase objects with 'phase', 'headcount', 'roles' (list), 'key_milestone_trigger'), "
            f"'job_descriptions' (array of 2-3 detailed objects with 'role_title', 'level', 'mission', 'responsibilities' (list), 'required_skills' (list), 'compensation_range' (object with 'salary_usd', 'equity_pct')), "
            f"'interview_scorecard' (object with 'cultural_values' (list), 'technical_evaluation_probes' (list), 'red_flags_to_reject' (list)), "
            f"'talent_acquisition_strategy' (sourcing channels, founder outreach template)."
        )
        system_prompt = "You are a VP of People & Talent Acquisition for high-growth tech startups. Produce realistic compensation benchmarks, high-impact job descriptions, and rigorous hiring rubrics."

        def fallback_fn():
            return {
                "hiring_roadmap": [
                    {
                        "phase": "Phase 1: Seed / Founding Core (Months 0-6)",
                        "headcount": 3,
                        "roles": ["Lead Full-Stack Founding Engineer", "Full-Stack AI / ML Engineer"],
                        "key_milestone_trigger": "Initial MVP deployed and early user traction verified."
                    },
                    {
                        "phase": "Phase 2: Scale & Go-To-Market (Months 6-18)",
                        "headcount": 6,
                        "roles": ["Head of Product Design", "Growth Marketing Lead", "Senior Backend Engineer"],
                        "key_milestone_trigger": "Product-market fit verified with $20k+ MRR."
                    }
                ],
                "job_descriptions": [
                    {
                        "role_title": "Founding Full-Stack Engineer",
                        "level": "Staff / Founding",
                        "mission": "Take architectural ownership of the core web app and backend microservices, delivering high velocity feature shipping.",
                        "responsibilities": [
                            "Architect and build responsive frontend modules using Next.js 16 and TypeScript.",
                            "Design high-performance async API endpoints with FastAPI and PostgreSQL.",
                            "Implement secure authentication, caching, and background task pipelines."
                        ],
                        "required_skills": ["TypeScript / Next.js", "Python / FastAPI", "PostgreSQL / SQLAlchemy", "Cloud Deployments (Docker / AWS)"],
                        "compensation_range": {"salary_usd": "$120k - $160k", "equity_pct": "1.5% - 3.0%"}
                    },
                    {
                        "role_title": "Head of Growth & Developer Relations",
                        "level": "Lead / Head",
                        "mission": "Lead user acquisition loops, organic community growth, and developer documentation ecosystems.",
                        "responsibilities": [
                            "Design product-led viral loops and onboarding referral mechanics.",
                            "Execute technical content marketing and founder-led social distribution.",
                            "Manage analytics funnel, cohort conversion, and lifecycle retention campaigns."
                        ],
                        "required_skills": ["Product-Led Growth (PLG)", "Data Analytics (PostHog/Mixpanel)", "Technical Content Writing", "Community Sourcing"],
                        "compensation_range": {"salary_usd": "$100k - $140k", "equity_pct": "1.0% - 2.0%"}
                    }
                ],
                "interview_scorecard": {
                    "cultural_values": [
                        "Bias for Action & Extreme Ownership",
                        "Intellectual Honesty & Low Ego",
                        "Customer Obsession over Technical Perfection"
                    ],
                    "technical_evaluation_probes": [
                        "Pair programming on a real production-like feature in under 60 minutes.",
                        "System design walkthrough evaluating trade-offs between simplicity and scalability.",
                        "Debugging a real asynchronous concurrency race condition."
                    ],
                    "red_flags_to_reject": [
                        "Complaining about ambiguity or requiring micromanaged specifications.",
                        "Over-engineering simple requirements with unnecessary architectural bloat.",
                        "Inability to explain past failures and lessons learned honestly."
                    ]
                },
                "talent_acquisition_strategy": "Source directly from top open-source GitHub contributors, technical hackathon winners, and ex-founders looking for their next high-leverage build."
            }

        result = await cls.generate_dynamic_tool(
            tool_name="recruiter_lab",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            fallback_fn=fallback_fn
        )
        return result if "job_descriptions" in result else fallback_fn()

    @classmethod
    async def generate_strategy_lab_ai(
        cls,
        title: str,
        category: str,
        competitors: Optional[str] = None,
        value_proposition: Optional[str] = None,
        provider: str = "groq",
        model: str = "llama-3.3-70b-versatile"
    ) -> dict:
        user_prompt = (
            f"Conduct an advanced competitive strategy and business model analysis for this startup:\n"
            f"Title: {title}\nCategory: {category}\nKnown Competitors: {competitors or 'Legacy incumbents and fragmented point solutions'}\nValue Prop: {value_proposition or '10x faster workflow through vertical AI automation'}\n\n"
            f"Return strictly a JSON object with keys: "
            f"'porter_five_forces' (array of 5 objects with 'force_name', 'intensity' ('LOW'|'MEDIUM'|'HIGH'), 'analysis', 'strategic_defense'), "
            f"'blue_ocean_strategy' (object with 'eliminate' (list), 'reduce' (list), 'raise' (list), 'create' (list)), "
            f"'defensibility_moat_breakdown' (object with integer scores 1-100 and rationale for 'network_effects', 'switching_costs', 'data_flywheel', 'brand_and_distribution'), "
            f"'pricing_model_matrix' (array of 3 tier objects with 'tier_name', 'price_monthly_usd', 'target_persona', 'core_features' (list), 'estimated_gross_margin'), "
            f"'gtm_growth_engine' (object with 'primary_loop', 'viral_coefficient_target', 'payback_period_months')."
        )
        system_prompt = "You are a Principal Business Strategist (McKinsey/Bain & Company style). Deliver rigorous micro-economic competitive frameworks and actionable monetization models."

        def fallback_fn():
            return {
                "porter_five_forces": [
                    {"force_name": "Threat of New Entrants", "intensity": "MEDIUM", "analysis": "Low barrier to AI wrapper entry, but high barrier to proprietary vertical data integration.", "strategic_defense": "Build deep workflow integrations that accumulate proprietary user context over time."},
                    {"force_name": "Bargaining Power of Buyers", "intensity": "MEDIUM", "analysis": "Customers have alternative generic tools, but switching creates friction once teams are onboarded.", "strategic_defense": "Deliver demonstrable ROI that exceeds subscription cost by 10x."},
                    {"force_name": "Bargaining Power of Suppliers", "intensity": "LOW", "analysis": "Upstream LLM inference providers are highly commoditized with dropping token costs.", "strategic_defense": "Maintain multi-provider abstraction gateway (Groq, Gemini, Ollama, OpenAI) to prevent vendor lock-in."},
                    {"force_name": "Threat of Substitutes", "intensity": "HIGH", "analysis": "Manual spreadsheets, internal scripts, and generic chat LLMs compete for user mindshare.", "strategic_defense": "Provide end-to-end specialized output formats (PRD, Pitch Deck, Roadmap, Architecture) rather than plain text chat."},
                    {"force_name": "Competitive Rivalry", "intensity": "MEDIUM", "analysis": "Fragmented market with many early-stage experiments but few unified vertical leaders.", "strategic_defense": "Out-execute on speed, developer UX, and institutional quality analysis."}
                ],
                "blue_ocean_strategy": {
                    "eliminate": ["Manual copy-pasting between disparate AI tools", "Bloated enterprise sales cycles for early-stage founders"],
                    "reduce": ["Time required to evaluate technical feasibility from weeks to seconds", "Expensive initial consulting fees"],
                    "raise": ["Determinism and reproducibility of AI analysis", "Actionability of architecture blueprints"],
                    "create": ["Automated multi-stage lab personas (GitHub, Investor, Mentor, Recruiter, Strategy)", "Built-in BYOK encrypted key security vault"]
                },
                "defensibility_moat_breakdown": {
                    "network_effects": 75,
                    "switching_costs": 88,
                    "data_flywheel": 84,
                    "brand_and_distribution": 80
                },
                "pricing_model_matrix": [
                    {"tier_name": "Starter / Free", "price_monthly_usd": "$0", "target_persona": "Solo builders exploring new concepts", "core_features": ["3 Idea Evaluations / month", "Basic Roadmap generator", "Community Support"], "estimated_gross_margin": "90%"},
                    {"tier_name": "Pro Builder", "price_monthly_usd": "$29", "target_persona": "Active founders & technical product managers", "core_features": ["Unlimited Idea Evaluations", "Full Secondary Labs Suite", "BYOK Unthrottled Routing", "Priority AI Gateway"], "estimated_gross_margin": "85%"},
                    {"tier_name": "Venture Studio / Team", "price_monthly_usd": "$99", "target_persona": "Accelerators, incubators & startup studios", "core_features": ["Multi-seat workspace", "Custom Prompt Blueprints", "Direct GitHub Scaffolding", "Institutional Investor Export"], "estimated_gross_margin": "88%"}
                ],
                "gtm_growth_engine": {
                    "primary_loop": "Product-Led Viral Sharing: Founders generate and share public interactive evaluation reports with co-founders and investors.",
                    "viral_coefficient_target": "1.25",
                    "payback_period_months": "1.5"
                }
            }

        result = await cls.generate_dynamic_tool(
            tool_name="strategy_lab",
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            fallback_fn=fallback_fn
        )
        return result if "porter_five_forces" in result else fallback_fn()

    @classmethod
    async def generate_research_plan_ai(
        cls,
        task_type: str = "market_analysis",
        title: str = "Startup Idea",
        industry: str = "Technology",
        target_audience: Optional[str] = None
    ) -> Dict[str, Any]:
        from app.ai.gateway.evidence.planner import ResearchPlanner
        plan = ResearchPlanner.generate_plan(
            task_type=task_type,
            idea_title=title,
            industry=industry,
            target_audience=target_audience
        )
        return plan.model_dump()

    @classmethod
    async def generate_grounded_market_ai(
        cls,
        title: str,
        industry: str,
        problem_statement: str,
        target_audience: Optional[str] = None,
        provider: str = "auto",
        model: str = "auto",
        byok_key: Optional[str] = None,
        byok_tavily_key: Optional[str] = None
    ) -> Dict[str, Any]:
        from app.ai.gateway.evidence.pipeline import EvidenceAwareResearchPipeline
        result = await EvidenceAwareResearchPipeline.generate_grounded_market_analysis(
            idea_title=title,
            industry=industry,
            problem_statement=problem_statement,
            target_audience=target_audience,
            provider=provider,
            model=model,
            byok_key=byok_key,
            byok_tavily_key=byok_tavily_key
        )
        return result.model_dump()

    @classmethod
    async def generate_grounded_competitors_ai(
        cls,
        title: str,
        industry: str,
        solution_description: str,
        provider: str = "auto",
        model: str = "auto",
        byok_key: Optional[str] = None,
        byok_tavily_key: Optional[str] = None
    ) -> Dict[str, Any]:
        from app.ai.gateway.evidence.pipeline import EvidenceAwareResearchPipeline
        result = await EvidenceAwareResearchPipeline.generate_grounded_competitor_analysis(
            idea_title=title,
            industry=industry,
            solution_description=solution_description,
            provider=provider,
            model=model,
            byok_key=byok_key,
            byok_tavily_key=byok_tavily_key
        )
        return result.model_dump()

    @classmethod
    async def generate_grounded_risks_ai(
        cls,
        title: str,
        industry: str,
        tech_depth: Optional[str] = "High",
        provider: str = "auto",
        model: str = "auto",
        byok_key: Optional[str] = None,
        byok_tavily_key: Optional[str] = None
    ) -> Dict[str, Any]:
        from app.ai.gateway.evidence.pipeline import EvidenceAwareResearchPipeline
        result = await EvidenceAwareResearchPipeline.generate_grounded_risk_analysis(
            idea_title=title,
            industry=industry,
            tech_depth=tech_depth,
            provider=provider,
            model=model,
            byok_key=byok_key,
            byok_tavily_key=byok_tavily_key
        )
        return result.model_dump()

orchestrator = AIOrchestrator()

