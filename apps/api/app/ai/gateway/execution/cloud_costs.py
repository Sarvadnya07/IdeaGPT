"""
IdeaGPT — Cloud Cost Estimator (Feature 29).
Deterministic multi-cloud infrastructure cost modeling for AWS, Vercel, Supabase, and Cloudflare.
Labels all outputs as ESTIMATE and breaks down cost drivers transparently.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class CloudCostInput(BaseModel):
    monthly_active_users: int = Field(default=10000, ge=100)
    monthly_api_requests: int = Field(default=500000, ge=1000)
    database_storage_gb: float = Field(default=20.0, ge=1.0)
    file_storage_gb: float = Field(default=50.0, ge=0.0)
    ai_tokens_monthly: int = Field(default=10000000, ge=0)  # 10M tokens


class ProviderCostEstimate(BaseModel):
    provider_name: str  # AWS | Vercel | Supabase | Cloudflare
    tier_name: str
    monthly_cost_usd: float
    annual_cost_usd: float
    cost_breakdown: Dict[str, float]
    primary_cost_driver: str
    scalability_notes: str
    provenance: str = "DETERMINISTIC_CALCULATION"


class CloudCostResult(BaseModel):
    inputs: CloudCostInput
    recommended_stack: str
    monthly_min_estimate_usd: float
    monthly_max_estimate_usd: float
    providers: List[ProviderCostEstimate]
    cost_optimization_tips: List[str]


class CloudCostEngine:
    @staticmethod
    def estimate(inputs: CloudCostInput) -> CloudCostResult:
        mau = inputs.monthly_active_users
        reqs = inputs.monthly_api_requests
        db_gb = inputs.database_storage_gb
        file_gb = inputs.file_storage_gb
        tokens = inputs.ai_tokens_monthly

        # AI Token Cost (blended ~$0.60 / 1M tokens)
        ai_cost = round((tokens / 1_000_000.0) * 0.60, 2)

        # 1. Vercel (Frontend + Serverless)
        vercel_base = 20.0 if mau > 1000 else 0.0  # Pro plan
        vercel_bandwidth = round(max(0.0, (reqs * 0.00005) * 0.15), 2)  # Bandwidth overage
        vercel_total = round(vercel_base + vercel_bandwidth, 2)

        vercel_estimate = ProviderCostEstimate(
            provider_name="Vercel",
            tier_name="Pro Tier",
            monthly_cost_usd=vercel_total,
            annual_cost_usd=round(vercel_total * 12, 2),
            cost_breakdown={"Base Subscription": vercel_base, "Edge Bandwidth": vercel_bandwidth},
            primary_cost_driver="Team Seats & Serverless Invocations",
            scalability_notes="Zero DevOps overhead, fast global edge CDN."
        )

        # 2. Supabase (Managed PostgreSQL + Auth + Storage)
        supa_base = 25.0  # Pro plan
        supa_db = round(max(0.0, (db_gb - 8.0) * 0.125), 2)
        supa_storage = round(max(0.0, (file_gb - 100.0) * 0.021), 2)
        supa_total = round(supa_base + supa_db + supa_storage, 2)

        supa_estimate = ProviderCostEstimate(
            provider_name="Supabase",
            tier_name="Pro Database",
            monthly_cost_usd=supa_total,
            annual_cost_usd=round(supa_total * 12, 2),
            cost_breakdown={"Base Database": supa_base, "Disk Storage": supa_db, "Object Storage": supa_storage},
            primary_cost_driver="Database Disk & Egress",
            scalability_notes="PostgreSQL with built-in pgvector and connection pooling."
        )

        # 3. AWS ECS Fargate + RDS (Full Containerized Cloud)
        aws_compute = round(max(40.0, (mau / 5000.0) * 35.0), 2)
        aws_rds = round(max(35.0, db_gb * 1.5), 2)
        aws_nat = 32.0  # NAT Gateway
        aws_s3 = round(file_gb * 0.023, 2)
        aws_total = round(aws_compute + aws_rds + aws_nat + aws_s3, 2)

        aws_estimate = ProviderCostEstimate(
            provider_name="AWS (ECS Fargate + RDS)",
            tier_name="Production VPC",
            monthly_cost_usd=aws_total,
            annual_cost_usd=round(aws_total * 12, 2),
            cost_breakdown={"ECS Containers": aws_compute, "RDS PostgreSQL": aws_rds, "NAT Gateway": aws_nat, "S3 Storage": aws_s3},
            primary_cost_driver="NAT Gateway & Managed RDS Instance",
            scalability_notes="Enterprise-grade isolation, SOC 2 compliance ready."
        )

        # 4. Cloudflare (Workers + R2 + D1)
        cf_base = 5.0
        cf_r2 = round(file_gb * 0.015, 2)
        cf_total = round(cf_base + cf_r2, 2)

        cf_estimate = ProviderCostEstimate(
            provider_name="Cloudflare (Workers + R2)",
            tier_name="Workers Paid",
            monthly_cost_usd=cf_total,
            annual_cost_usd=round(cf_total * 12, 2),
            cost_breakdown={"Workers Paid": cf_base, "R2 Zero-Egress Storage": cf_r2},
            primary_cost_driver="Worker Requests",
            scalability_notes="Zero egress fees on object storage."
        )

        # Composite Recommended Modern Stack: Vercel ($20) + Supabase ($25) + AI Tokens
        composite_monthly = round(vercel_total + supa_total + ai_cost, 2)

        return CloudCostResult(
            inputs=inputs,
            recommended_stack="Vercel (Frontend) + Supabase (PostgreSQL) + Multi-Provider AI Gateway",
            monthly_min_estimate_usd=round(composite_monthly * 0.85, 2),
            monthly_max_estimate_usd=round(composite_monthly * 1.35, 2),
            providers=[vercel_estimate, supa_estimate, aws_estimate, cf_estimate],
            cost_optimization_tips=[
                "Enable 24h deterministic response caching to reduce AI token inference spend by up to 60%.",
                "Use Cloudflare R2 for user file attachments to avoid AWS S3 data egress penalties.",
                "Adopt connection pooling (PgBouncer/Supabase Pooler) to avoid RDS connection saturation."
            ]
        )
