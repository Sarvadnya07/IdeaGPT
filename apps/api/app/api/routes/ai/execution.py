"""
AI Execution Sub-Router: Build tools, cloud costs, database schema, security checklist, and contracts.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Body

from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/execution/cloud-costs", summary="Deterministic multi-cloud infrastructure cost estimation")
async def estimate_cloud_costs(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.execution.cloud_costs import CloudCostEngine, CloudCostInput
    inp = CloudCostInput(**payload)
    return CloudCostEngine.estimate(inp)


@router.post("/execution/architecture-tradeoffs", summary="Evaluate architecture stack trade-offs (FastAPI vs Node, Monolith vs Microservices)")
async def evaluate_architecture_tradeoffs(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.execution.build_tools import ArchitectureMatrixEngine
    return ArchitectureMatrixEngine.generate(
        title=payload.get("title", "Startup Concept"),
        category=payload.get("category", "B2B SaaS")
    )


@router.post("/execution/database-schema", summary="Generate validated PostgreSQL DDL schema recommendations")
async def generate_database_schema(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.execution.build_tools import DatabaseSchemaEngine
    return DatabaseSchemaEngine.generate_schema(
        title=payload.get("title", "Startup Concept"),
        domain=payload.get("domain", "SaaS")
    )


@router.post("/execution/security-checklist", summary="Generate production security best-practices checklist")
async def generate_security_checklist(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.execution.build_tools import SecurityChecklistEngine
    return SecurityChecklistEngine.generate_checklist(
        title=payload.get("title", "Startup Concept")
    )


@router.post("/execution/user-stories", summary="Generate structured user stories and Given/When/Then acceptance criteria")
async def generate_user_stories(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.execution.build_tools import UserStoryEngine
    return UserStoryEngine.generate_stories(
        title=payload.get("title", "Startup Concept"),
        problem=payload.get("problem", ""),
        solution=payload.get("solution", "")
    )


@router.post("/execution/openapi-contract", summary="Synthesize validated OpenAPI 3.1 contract specifications")
async def generate_openapi_contract(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.execution.build_tools import OpenApiContractEngine
    return OpenApiContractEngine.generate_contract(
        title=payload.get("title", "Startup Concept")
    )


@router.post("/execution/failure-modes", summary="Enumerate edge-case failure modes and mitigation strategies")
async def enumerate_failure_modes(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.execution.build_tools import FailureModeEngine
    return FailureModeEngine.enumerate_failures(
        title=payload.get("title", "Startup Concept")
    )


@router.post("/execution/release-phasing", summary="Classify features into MVP, V1, and V1.1 release phases")
async def generate_release_phasing(
    payload: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user)
):
    from app.ai.gateway.execution.build_tools import ReleasePhasingEngine
    return ReleasePhasingEngine.generate_phases(
        title=payload.get("title", "Startup Concept")
    )
