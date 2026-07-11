# 1. Architecture Monorepo Setup

Date: 2026-07-11

## Status
Accepted

## Context
We need a highly scalable platform that separates frontend rendering from backend AI orchestration while maintaining a single source of truth for deployments.

## Decision
We chose a TurboRepo-inspired monorepo structure utilizing Next.js (App Router) in `apps/web` for frontend interactions and FastAPI in `apps/api` for asynchronous orchestration of OpenAI models and heavy PostgreSQL queries.

## Consequences
Pros:
- Unified linting and testing strategy.
- Clear separation of concerns between client and server.
Cons:
- Deployment requires monorepo awareness (e.g., Vercel / Docker targeting specific subdirectories).
