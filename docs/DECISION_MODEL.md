# IDEA GPT — DECISION MODEL SPECIFICATION & MATHEMATICAL NORMALIZATION

**Standard**: Decision Intelligence Standard v1.0  
**Date**: August 27, 2026

---

## 1. Risk-Adjusted Decision Scoring

The platform rejects naive additive score subtractions in favor of a normalized, calibrated attenuation function:

$$\text{DecisionScore} = \text{Attractiveness} \times \left(1 - 0.5 \times \frac{R}{100}\right)$$

Where:
- $\text{Attractiveness} \in [0, 100]$: Deterministic sum of weighted criteria:
  $$\text{Attractiveness} = \sum_{i=1}^n (w_i \cdot s_i) \quad \text{with} \quad \sum w_i = 1.0$$
- $R \in [0, 100]$: Composite risk exposure factor.
- **Bounding Invariant**: For any valid input, $\text{DecisionScore} \in [0, 100]$. A zero-risk venture retains $100\%$ of its attractiveness; a maximum-risk venture ($R=100$) retains $50\%$ of its score.

---

## 2. Assumption Priority Normalization

To identify which underlying assumption a founder must validate first, assumptions are ranked via:

$$\text{PriorityScore} = \frac{\text{Impact} \times \text{Uncertainty}}{\text{EaseOfValidation}}$$

### Discrete Normalization Table:
| Factor | HIGH (3.0) | MEDIUM (2.0) | LOW (1.0) |
| :--- | :--- | :--- | :--- |
| **Impact** | Catastrophic / venture-ending | Significant friction | Minor inconvenience |
| **Uncertainty** | Zero empirical data | Secondary industry estimates | Verified customer telemetry |
| **Validation Ease** | Rapid / low-cost ($< 1$ wk) | Moderate prototype ($2-4$ wks) | Heavy clinical/hardware test ($> 2$ mo) |

### Tier Classification:
- $\text{Priority} \ge 4.5 \implies$ **`CRITICAL`** (Blocks capital allocation until tested)
- $3.0 \le \text{Priority} < 4.5 \implies$ **`HIGH`** (Execute in Phase 1)
- $1.5 \le \text{Priority} < 3.0 \implies$ **`MEDIUM`** (Execute in Phase 2)
- $\text{Priority} < 1.5 \implies$ **`LOW`** (Monitor passively)

---

## 3. Decision Gate Criteria

| Gate | Condition Trigger | Strategic Mandate |
| :--- | :--- | :--- |
| **`GO`** | $\text{Score} \ge 75.0$ and $R < 40.0$ | Proceed to full production development. |
| **`VALIDATE_FIRST`** | $\text{Score} \ge 60.0$ | Pause heavy development; execute founder validation experiments. |
| **`GO_WITH_CONDITIONS`**| $45.0 \le \text{Score} < 60.0$ | Proceed only after specific regulatory/technical gates clear. |
| **`PIVOT`** | $\text{Score} < 45.0$ | Reposition customer segment, value proposition, or monetization model. |
| **`STOP`** | Structural impasse | Archive venture to conserve founder runway. |
