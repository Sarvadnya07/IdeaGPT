# 5. Modular Monolith and Service Boundaries

Date: 2026-08-18

## Status
Accepted

## Context
As IdeaGPT expanded to include roadmaps, comparisons, PRD generators, pitch deck builders, and analytics, an architectural baseline was needed to govern modularity and prevent the accumulation of unmanaged distributed systems complexity.

## Decision
We adopted a **Decoupled Modular Monolith** within a Turborepo monorepo:
1. **Frontend Presentation (`apps/web`)**: Next.js 16 App Router using React Server Components for SEO and initial load speed, alongside TanStack React Query v5 for client state management.
2. **Backend API & Processing (`apps/api`)**: Layered architecture strictly dividing Routers -> Domain Services -> Execution Engines -> SQLAlchemy Models.
3. **Database Ownership**: Single PostgreSQL database with shared schema and row-level tenant isolation, rejecting premature microservice database splitting.
4. **Service Extraction Policy**: Microservices are explicitly rejected until team organization divergence, divergent scale requirements (>10k concurrent evaluations/sec), or independent failure domains strictly justify the operational overhead.

## Consequences
### Pros:
- High cohesion and change locality across related features.
- Zero network serialization overhead or distributed transaction complexity.
- Unified CI/CD testing, single-command bootstrapping, and fast build caching.
- Low total cost of ownership (TCO) and low operational complexity.

### Cons:
- Large monorepo requires disciplined linting and automated fitness tests to prevent layer violations.
