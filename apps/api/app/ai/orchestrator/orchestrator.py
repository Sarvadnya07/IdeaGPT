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
        strategy: str = "auto"
    ) -> dict:
        """
        AI Evaluation Pipeline:
        Context -> Prompt Resolver -> Cache Check -> LLM invocation -> Output Validator/Repair -> Cache Save.
        """
        user_prompt = ""
        system_prompt = "You are a world-class AI Startup Analyst. You must return your analysis strictly as JSON matching the requested structure."
        p_version = prompt_version
        temp = 0.2
        max_t = 1500

        # Resolve context if db & idea_id are provided
        if db and idea_id:
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
        provider_name = AIRouter.route(strategy=strategy, preferred=preferred_provider)
        provider = ProviderFactory.create_provider(provider_name)
        model_name = getattr(provider, "model", "default-model")

        # Cache Check
        if not force_fresh:
            cached_result = evaluation_cache.get(
                idea_text=idea_text,
                prompt_version=p_version,
                model=model_name,
                provider=provider_name
            )
            if cached_result:
                cached_result["metadata"]["cached"] = True
                return cached_result

        # LLM Invocation
        start_time = time.time()
        raw_response = await provider.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_format="json"
        )
        duration_ms = int((time.time() - start_time) * 1000)

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

        # Fallback if repair fails
        if not validated_model:
            result_dict = {
                "summary": "AI response was malformed and could not be repaired.",
                "score": 50,
                "strengths": ["Data safety fallback"],
                "weaknesses": ["Malformed response"],
                "recommendations": ["Retry the evaluation"],
                "confidence": 0.5,
                "dimensions": {
                    "innovation": 50,
                    "market_potential": 50,
                    "technical_feasibility": 50,
                    "business_viability": 50,
                    "scalability": 50,
                    "execution_complexity": 50,
                    "competitive_differentiation": 50
                },
                "architecture_breakdown": "Feasibility breakdown could not be generated."
            }
        else:
            result_dict = validated_model.model_dump()

        # Add metadata
        result_dict["metadata"] = {
            "provider": provider_name,
            "model": model_name,
            "prompt_version": p_version,
            "temperature": temp,
            "max_tokens": max_t,
            "duration_ms": duration_ms,
            "token_usage": 1500,
            "estimated_cost": 0.003,
            "cached": False
        }

        # Cache Save
        evaluation_cache.set(
            idea_text=idea_text,
            prompt_version=p_version,
            model=model_name,
            provider=provider_name,
            result_payload=result_dict
        )

        return result_dict

orchestrator = AIOrchestrator()
