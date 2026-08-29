# IDEA GPT — RESEARCH & EVIDENCE ARCHITECTURE SPECIFICATION

**Architecture Version**: 2.0 (Phase B)  
**Layer**: AI Gateway / Research & Knowledge Grounding  
**Package**: `apps/api/app/ai/gateway/evidence`

---

## 1. System Topology & Data Flow

```
+-------------------------------------------------------------------------+
|                              USER PROMPT / IDEA                         |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  ResearchPlanner (Bounded Queries <= 4)                 |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|               ResearchCacheService (24h TTL, SHA-256 Key)               |
+------------------+------------------------------------+-----------------+
                   | (Cache Hit)                        | (Cache Miss)
                   v                                    v
     +---------------------------+       +-------------------------------+
     |  Return Cached Citations  |       | TavilyResearchProviderAdapter |
     +-------------+-------------+       +--------------+----------------+
                   |                                    |
                   |                                    v
                   |                     +-------------------------------+
                   |                     |  SourceNormalizer             |
                   |                     |  - Canonical URL (strip UTM)  |
                   |                     |  - Domain Trust Tier          |
                   |                     |  - Deduplication              |
                   |                     +--------------+----------------+
                   |                                    |
                   +-----------------+------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  Grounded Domain Analyzers (Isolated Block)             |
|  System Prompt + <untrusted_external_research_data> ... </...>          |
|  - GroundedMarketAnalyzer                                               |
|  - GroundedCompetitorAnalyzer                                           |
|  - GroundedRiskAnalyzer                                                 |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  EvidenceValidator & Taxonomy Engine                    |
|  - Downgrade uncited FACT -> INFERENCE / ESTIMATE                       |
|  - Require assumptions on ESTIMATE                                      |
|  - Detect conflicting sources & synthesize ranges                       |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                      Persisted Result & Frontend UI                     |
|  - Badges (FACT, ESTIMATE, INFERENCE, UNKNOWN, CONFLICT)                |
|  - Confidence Indicator (HIGH, MEDIUM, LOW)                             |
|  - Citations Drawer                                                     |
+-------------------------------------------------------------------------+
```

---

## 2. Core Modules and Contracts

### 2.1 Domain Models (`apps/api/app/ai/gateway/evidence/models.py`)

- `SourceType`: `GOVERNMENT`, `ACADEMIC`, `INDUSTRY`, `NEWS`, `COMPANY`, `COMMUNITY`, `UNKNOWN`.
- `EvidenceClassification`: `FACT`, `ESTIMATE`, `INFERENCE`, `RECOMMENDATION`, `UNKNOWN`, `CONFLICTING_EVIDENCE`.
- `ConfidenceLevel`: `HIGH`, `MEDIUM`, `LOW`.
- `NormalizedSource`: Canonical representation of web citation with relevance score and authoritative indicator.
- `NormalizedEvidence`: Fine-grained claim with taxonomy classification, supporting excerpt, assumptions, and source bindings.

### 2.2 Bounded Query Planner (`apps/api/app/ai/gateway/evidence/planner.py`)

- Enforces an invariant limit of at most 4 focused queries per task type (`market_analysis`, `competitor_analysis`, `risk_analysis`, `general_research`).

### 2.3 Source Normalization & Deduplication (`apps/api/app/ai/gateway/evidence/normalizer.py`)

- Strips URL tracking parameters (`utm_*`, `fbclid`, `ref`, `#anchors`).
- Classifies domain authority against government (`.gov`, `.mil`), academic (`.edu`, `arxiv.org`), industry research (`gartner.com`, `statista.com`, `mckinsey.com`), news, and community forums.
- Deduplicates identical content URLs across search queries.

### 2.4 Research Cache (`apps/api/app/ai/gateway/evidence/cache.py`)

- In-memory thread-safe cache with 24-hour TTL.
- Keys generated via SHA-256 hash: `sha256(f"{task_type}:{normalized_query}:{provider}")`.

### 2.5 Evidence Taxonomy & Downgrade Validator (`apps/api/app/ai/gateway/evidence/taxonomy.py`)

- **Downgrade Rule**: If an LLM returns `FACT` without a valid `source_url` or `source_id`, it is automatically downgraded to `INFERENCE`.
- **Numerical Claim Rule**: Uncited numerical metrics (e.g. `$4.5B TAM`) are converted to `ESTIMATE` with assumed speculative status.
- **Source Discrepancy Detection**: Identifies variance between sources on numerical claims and synthesizes a bounded composite range with `MEDIUM` confidence.

### 2.6 Grounded Domain Analyzers (`apps/api/app/ai/gateway/evidence/grounded_analyzers.py`)

- `GroundedMarketAnalyzer`: Evaluates TAM, target segments, CAGR, and drivers.
- `GroundedCompetitorAnalyzer`: Analyzes direct and adjacent competitors, defensibility moats, and pricing.
- `GroundedRiskAnalyzer`: Evaluates regulatory, technical, and execution risks with structured mitigations.
- Prompt injection defense: Wraps untrusted extracts in XML fences with system instructions preventing instruction override.
