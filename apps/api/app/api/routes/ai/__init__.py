"""
Aggregated AI Router: Combines modular AI sub-routers (tasks, artifacts, strategy, execution, ops, labs)
under prefix /ai with tag "ai", guaranteeing 100% route and contract compatibility.
"""

from fastapi import APIRouter
from app.api.routes.ai.tasks import router as tasks_router
from app.api.routes.ai.artifacts import router as artifacts_router
from app.api.routes.ai.strategy import router as strategy_router
from app.api.routes.ai.execution import router as execution_router
from app.api.routes.ai.ops import router as ops_router
from app.api.routes.ai.labs import router as labs_router

router = APIRouter(prefix="/ai", tags=["ai"])

# Include modular sub-routers
router.include_router(ops_router)
router.include_router(labs_router)
router.include_router(artifacts_router)
router.include_router(tasks_router)
router.include_router(strategy_router)
router.include_router(execution_router)
