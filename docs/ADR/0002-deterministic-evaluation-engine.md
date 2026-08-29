# 2. Deterministic Evaluation Engine & State Machine Lifecycle

Date: 2026-08-15

## Status

Accepted

## Context

Initial technical evaluations for startup ideas required high reliability, zero latency jitter, and 100% reproducible results. Relying exclusively on third-party LLMs for foundational scoring introduced rate-limit vulnerabilities, non-deterministic drift, network latency (3–10s), and cost overhead for basic validation.

## Decision

We implemented a 100% offline, deterministic rule-based evaluation engine (`DeterministicEvaluationEngine` v2.6) coupled with a persistent Finite State Machine (`EvaluationCoordinator` and `EvaluationExecutor`) and lifecycle event auditing (`EvaluationHistory`).

- Deterministic scoring across 7 dimensional axes: Innovation, Market Potential, Technical Feasibility, Business Viability, Scalability, Execution Complexity, and Competitive Differentiation.
- Isolated database transactions for state transitions (`PENDING` -> `RUNNING` -> `COMPLETED`/`FAILED`).
- Stale job recovery sweep for interrupted processes.

## Consequences

### Pros:

- Sub-50ms execution speed with zero external network dependencies.
- Perfect reproducibility and zero cost per basic evaluation.
- High resilience: Core platform functionality remains 100% available even during total external AI provider outages.
- Immutable lifecycle audit trail for all evaluations.

### Cons:

- Rule-based heuristics require code updates to adjust dimensional weighting.
