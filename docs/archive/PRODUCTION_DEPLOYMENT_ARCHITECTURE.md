# IdeaGPT — Production Deployment Architecture

## 1. Architectural Model

IdeaGPT is designed as a unified Monorepo Root Deployment conforming to official Vercel Next.js + Python serverless deployment standards.

```
                  ┌─────────────────────────────────────┐
                  │          Vercel Platform            │
                  │   Root Deployment (Root Dir: .)     │
                  └──────────────────┬──────────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           │                                                   │
  HTTP Traffic: /*                                    HTTP Traffic: /api/*
           │                                                   │
           ▼                                                   ▼
┌──────────────────────┐                             ┌──────────────────────┐
│  Next.js 16 Frontend │                             │    FastAPI Backend   │
│     (apps/web)       │                             │    (api/index.py)    │
└──────────┬───────────┘                             └──────────┬───────────┘
           │                                                    │
           │ JWT / RS256 Validation                             │ Async Queries (asyncpg)
           ▼                                                    ▼
┌──────────────────────┐                             ┌──────────────────────┐
│      Clerk Auth      │                             │   PostgreSQL / DB    │
│  (accounts.dev JWKS) │                             │      (Supabase)      │
└──────────────────────┘                             └──────────┬───────────┘
                                                                │
                                                                │ AI Gateway (Async)
                                                                ▼
                                                     ┌──────────────────────┐
                                                     │    Groq LPU Cloud    │
                                                     │ (llama-3.3-70b / etc)│
                                                     └──────────────────────┘
```

---

## 2. Directory Layout & Routing Boundaries

| Path | Purpose | Vercel Function / Build Target |
| :--- | :--- | :--- |
| `api/index.py` | Python ASGI Entrypoint | `@vercel/python` serverless handler exposed at `/api/*` |
| `requirements.txt` | Root Python Dependency Manifest | Automatically installed by `@vercel/python` builder via `pip` |
| `.python-version` | Python Version Pinning | Locks Vercel runtime to Python `3.12` |
| `apps/web/` | Next.js Frontend Application | Built with Turborepo (`turbo build` / `next build`) |
| `apps/api/` | FastAPI Core Application Source | Imported directly by `api/index.py` via normalized `sys.path` |
| `packages/` | Shared TypeScript Configs & UI Components | Monorepo workspace packages |

---

## 3. Key Design Decisions

1. **Root-Based Monorepo Pattern**:
   - Vercel's zero-config Next.js framework builder discovers `api/index.py` automatically.
   - Eliminates packaging failures where a standalone `apps/api` project was misidentified as a Node.js project due to `apps/api/package.json`.
2. **Single Canonical FastAPI Instance**:
   - `api/index.py` forwards requests directly to `apps/api/app/main.py:app`.
   - Zero duplicated routing, zero duplicated middleware configurations.
3. **Strict Secret Scoping**:
   - `NEXT_PUBLIC_*` variables are strictly limited to the public frontend (`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `NEXT_PUBLIC_API_URL`).
   - Server-side secrets (`DATABASE_URL`, `CLERK_SECRET_KEY`, `GROQ_API_KEY`) remain strictly in the backend execution environment and are never bundled into client JS.
