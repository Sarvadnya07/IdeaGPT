# Architecture Overview

IdeaGPT is an AI-powered SaaS platform built as a **Turborepo monorepo** separating the Next.js presentation tier from the FastAPI backend and deterministic evaluation engine.

---

## 🏛️ Key Architectural Documents

- **[System Architecture Guide](../ARCHITECTURE.md)**: Detailed system design, C4 topologies, module boundaries, and sequence flows.
- **[Security Architecture](../SECURITY.md)**: Cryptographic token validation, multi-tenant isolation, and rate-limiting.
- **[Performance & Optimization](../PERFORMANCE.md)**: Async non-blocking execution, RSC rendering, and connection pooling.
- **[Deployment & Infrastructure](../DEPLOYMENT.md)**: Containerization, Docker configurations, and CI/CD pipelines.
- **[API Endpoints Reference](../api/endpoints.md)**: Comprehensive REST API endpoint inventory.

---

## 📚 Architecture Decision Records (ADRs)

1. [ADR-0001: Architecture Monorepo Setup](../ADR/0001-architecture.md)
2. [ADR-0002: Deterministic Evaluation Engine & State Machine](../ADR/0002-deterministic-evaluation-engine.md)
3. [ADR-0003: Clerk RS256 JWKS Key Verification & Multi-Tenancy](../ADR/0003-clerk-rs256-jwks-and-multi-tenancy.md)
4. [ADR-0004: Multi-Provider Dynamic Discovery & AI Routing](../ADR/0004-multi-provider-dynamic-discovery-routing.md)
5. [ADR-0005: Modular Monolith and Service Boundaries](../ADR/0005-modular-monolith-and-service-boundaries.md)
