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

orchestrator = AIOrchestrator()
