"""
IdeaGPT AI Service Abstraction

Primary AI services are modularized across:
  - app.services.ai_task_service.AiTaskService: Asynchronous AI task queue & execution
  - app.services.ai_registry_service.AIRegistryService: Dynamic provider & model discovery
  - app.services.architecture_service.ArchitectureService: Tech stack, blueprints, PRD & pitch deck generation
  - app.ai.orchestrator.router.AIRouter: Provider-agnostic task routing
"""
from app.services.ai_task_service import AiTaskService
from app.services.ai_registry_service import AIRegistryService
from app.services.architecture_service import architecture_service

__all__ = ["AiTaskService", "AIRegistryService", "architecture_service"]
