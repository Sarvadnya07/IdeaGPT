# IDEA GPT — STRATEGY & DECISION ARCHITECTURE

**Author**: Principal AI Reasoning Architect & Decision-Science Engineer  
**Status**: Active Architecture Standard (Phase C)  
**Date**: August 27, 2026

---

## 1. System Topology & Data Flow

```
                      IDEA
                       │
              ┌────────┴────────┐
              │                 │
      RESEARCH EVIDENCE     ASSUMPTIONS
      (Phase B Citations)  (Classified Tiers)
              │                 │
              └────────┬────────┘
                       ▼
              DEEP REASONING LAYER
           (Traceable Claim Synthesis)
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     OPTIONS       TRADE-OFFS       RISKS
   (Strategic)   (Reversibility) (Exposure)
        │              │              │
        └──────────────┼──────────────┘
                       ▼
            SCENARIO & SENSITIVITY
        (Baseline / Optimistic / Adverse)
                       │
                       ▼
            WEIGHTED DECISION MODEL
      (Attractiveness - Risk Adjustment)
                       │
                       ▼
          STRATEGIC RECOMMENDATION
         (Decision Gate: GO / PIVOT / etc.)
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       ROADMAP    ARCHITECTURE     PRD
    (Validation)  (Constraints) (Requirements)
```

---

## 2. Provenance Guarantees

Every data point rendered across Strategy Lab carries an immutable provenance stamp:
- `USER_INPUT`: Ground truth supplied by the founder (e.g. Budget, Target Segment).
- `DETERMINISTIC_CALCULATION`: Arithmetic calculated outside the LLM (e.g. Runway = Budget / Burn, Weighted Decision Score).
- `RESEARCH_EVIDENCE`: Fact citation retrieved from verified Phase B search indices.
- `MODEL_INFERENCE`: Qualitative synthesis derived via deep reasoning.
- `RECOMMENDATION`: Actionable guidance generated for roadmap or PRD execution.

---

## 3. Directory Layout & Module Responsibilities

```
apps/api/app/ai/gateway/strategy/
├── models.py          # Domain schemas, provenance enums, decision gates, assumption items
├── reasoning.py       # Assumption extraction, prioritization formula, contradiction audits
├── scenario.py        # Deterministic financial scenario engine and sensitivity analyzer
├── comparative.py     # Multi-idea weighted criteria decision matrix
├── linkage.py         # Strategy experiment to PostgreSQL Roadmap persistence linkage
└── pipeline.py        # Gateway facade coordinating strategy workflows
```
