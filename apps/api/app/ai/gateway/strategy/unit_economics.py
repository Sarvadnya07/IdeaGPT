"""
IdeaGPT — Unit Economics Deterministic Calculator (Feature 9).
Provides mathematical calculations for CAC, LTV, LTV/CAC Ratio, Gross Margin,
ARPU, Payback Period, Monthly Burn, Runway, and Break-Even Volume.
Enforces strict provenance: USER_INPUT vs ASSUMPTION vs DETERMINISTIC_CALCULATION.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class UnitEconomicsInput(BaseModel):
    target_price_monthly_usd: float = Field(default=29.0, ge=0.0, description="Monthly subscription / ARPU ($)")
    monthly_cogs_usd: float = Field(default=4.0, ge=0.0, description="Direct monthly cost to serve ($)")
    estimated_cac_usd: float = Field(default=45.0, ge=0.0, description="Customer Acquisition Cost ($)")
    monthly_churn_rate_pct: float = Field(default=5.0, ge=0.1, le=100.0, description="Expected monthly churn (%)")
    monthly_fixed_burn_usd: float = Field(default=5000.0, ge=0.0, description="Fixed monthly operating burn ($)")
    available_capital_usd: float = Field(default=50000.0, ge=0.0, description="Current bank balance / capital ($)")


class MetricItem(BaseModel):
    name: str
    value: str
    numeric_value: float
    unit: str
    provenance: str = "DETERMINISTIC_CALCULATION"
    interpretation: str
    health_status: str = "HEALTHY"  # HEALTHY | CAUTION | CRITICAL


class UnitEconomicsResult(BaseModel):
    gross_margin_pct: MetricItem
    arpu_monthly: MetricItem
    customer_lifetime_months: MetricItem
    customer_lifetime_value_usd: MetricItem
    ltv_to_cac_ratio: MetricItem
    cac_payback_months: MetricItem
    break_even_customers: MetricItem
    projected_runway_months: MetricItem
    overall_health: str = "VIABLE"  # VIABLE | FRAGILE | UNPROFITABLE
    strategic_summary: str

    model_config = ConfigDict(use_enum_values=True)


class UnitEconomicsEngine:
    @staticmethod
    def calculate(inputs: UnitEconomicsInput) -> UnitEconomicsResult:
        price = max(0.0, inputs.target_price_monthly_usd)
        cogs = max(0.0, inputs.monthly_cogs_usd)
        cac = max(0.01, inputs.estimated_cac_usd)
        churn_rate = max(0.001, min(1.0, inputs.monthly_churn_rate_pct / 100.0))
        fixed_burn = max(0.0, inputs.monthly_fixed_burn_usd)
        capital = max(0.0, inputs.available_capital_usd)

        # 1. Gross Margin (%)
        gross_profit_per_sub = price - cogs
        margin_pct = round((gross_profit_per_sub / price) * 100.0, 1) if price > 0 else 0.0
        margin_status = "HEALTHY" if margin_pct >= 70.0 else ("CAUTION" if margin_pct >= 50.0 else "CRITICAL")
        margin_item = MetricItem(
            name="Gross Margin",
            value=f"{margin_pct}%",
            numeric_value=margin_pct,
            unit="%",
            provenance="DETERMINISTIC_CALCULATION",
            interpretation=f"${gross_profit_per_sub:.2f} contribution margin per user after hosting and AI inference costs.",
            health_status=margin_status
        )

        # 2. ARPU
        arpu_item = MetricItem(
            name="Average Revenue Per User (Monthly)",
            value=f"${price:.2f}",
            numeric_value=price,
            unit="USD/mo",
            provenance="USER_INPUT",
            interpretation="Base monthly subscription price.",
            health_status="HEALTHY"
        )

        # 3. Customer Lifetime (Months) = 1 / churn_rate
        lifetime_months = round(1.0 / churn_rate, 1)
        lifetime_item = MetricItem(
            name="Expected Customer Lifetime",
            value=f"{lifetime_months} months",
            numeric_value=lifetime_months,
            unit="months",
            provenance="DETERMINISTIC_CALCULATION",
            interpretation=f"Based on {inputs.monthly_churn_rate_pct}% monthly churn rate.",
            health_status="HEALTHY" if lifetime_months >= 18.0 else ("CAUTION" if lifetime_months >= 10.0 else "CRITICAL")
        )

        # 4. Customer Lifetime Value (LTV) = Lifetime * Gross Profit
        ltv = round(lifetime_months * gross_profit_per_sub, 2)
        ltv_status = "HEALTHY" if ltv >= (cac * 3.0) else ("CAUTION" if ltv >= (cac * 1.5) else "CRITICAL")
        ltv_item = MetricItem(
            name="Customer Lifetime Value (LTV)",
            value=f"${ltv:,.2f}",
            numeric_value=ltv,
            unit="USD",
            provenance="DETERMINISTIC_CALCULATION",
            interpretation="Total gross profit expected across customer tenure.",
            health_status=ltv_status
        )

        # 5. LTV / CAC Ratio
        ltv_cac = round(ltv / cac, 2)
        ltv_cac_status = "HEALTHY" if ltv_cac >= 3.0 else ("CAUTION" if ltv_cac >= 1.5 else "CRITICAL")
        ltv_cac_item = MetricItem(
            name="LTV to CAC Ratio",
            value=f"{ltv_cac}x",
            numeric_value=ltv_cac,
            unit="ratio",
            provenance="DETERMINISTIC_CALCULATION",
            interpretation="Institutional target is >= 3.0x for venture-scalable unit economics.",
            health_status=ltv_cac_status
        )

        # 6. CAC Payback Period (Months) = CAC / Gross Profit Monthly
        payback_months = round(cac / gross_profit_per_sub, 1) if gross_profit_per_sub > 0 else 999.0
        payback_status = "HEALTHY" if payback_months <= 12.0 else ("CAUTION" if payback_months <= 18.0 else "CRITICAL")
        payback_item = MetricItem(
            name="CAC Payback Period",
            value=f"{payback_months} months",
            numeric_value=payback_months,
            unit="months",
            provenance="DETERMINISTIC_CALCULATION",
            interpretation="Months required to recoup customer acquisition capital.",
            health_status=payback_status
        )

        # 7. Break-Even Active Customers = Fixed Burn / Gross Profit Monthly
        be_customers = int(round(fixed_burn / gross_profit_per_sub)) if gross_profit_per_sub > 0 else 999999
        be_item = MetricItem(
            name="Break-Even Active Subscriptions",
            value=f"{be_customers:,} users",
            numeric_value=float(be_customers),
            unit="subscribers",
            provenance="DETERMINISTIC_CALCULATION",
            interpretation=f"Active paying users needed to cover ${fixed_burn:,.0f}/mo fixed burn.",
            health_status="HEALTHY" if be_customers <= 1000 else "CAUTION"
        )

        # 8. Projected Zero-Revenue Runway
        runway_months = round(capital / fixed_burn, 1) if fixed_burn > 0 else 99.0
        runway_status = "HEALTHY" if runway_months >= 12.0 else ("CAUTION" if runway_months >= 6.0 else "CRITICAL")
        runway_item = MetricItem(
            name="Zero-Revenue Runway",
            value=f"{runway_months} months",
            numeric_value=runway_months,
            unit="months",
            provenance="DETERMINISTIC_CALCULATION",
            interpretation=f"Calculated from ${capital:,.0f} available capital at current burn.",
            health_status=runway_status
        )

        # Overall Health Rating
        if ltv_cac >= 3.0 and payback_months <= 12.0 and margin_pct >= 70.0:
            overall = "VIABLE"
            summary = f"Strong unit economics with {ltv_cac}x LTV/CAC and {payback_months}-month payback. The business model generates healthy cash flows at scale."
        elif ltv_cac >= 1.5 and margin_pct >= 50.0:
            overall = "FRAGILE"
            summary = f"Marginal unit economics ({ltv_cac}x LTV/CAC). Focus on improving retention or reducing acquisition spend to reach venture thresholds."
        else:
            overall = "UNPROFITABLE"
            summary = f"Unfavorable unit economics ({ltv_cac}x LTV/CAC). Acquisition costs exceed customer lifetime gross profit; model requires structural pricing/CAC overhaul."

        return UnitEconomicsResult(
            gross_margin_pct=margin_item,
            arpu_monthly=arpu_item,
            customer_lifetime_months=lifetime_item,
            customer_lifetime_value_usd=ltv_item,
            ltv_to_cac_ratio=ltv_cac_item,
            cac_payback_months=payback_item,
            break_even_customers=be_item,
            projected_runway_months=runway_item,
            overall_health=overall,
            strategic_summary=summary
        )
