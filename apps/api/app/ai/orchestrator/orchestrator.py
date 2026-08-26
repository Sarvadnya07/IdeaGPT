import time
import logging
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
            return fallback_fn()
        return {}

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
        return result if "executive_summary" in result else fallback_fn()

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

orchestrator = AIOrchestrator()
