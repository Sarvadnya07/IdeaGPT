# IdeaGPT — Vercel Environment Reference & Project Separation

**Product**: IdeaGPT Monorepo  
**Target Platform**: Vercel Serverless (Next.js App Router + FastAPI Python Runtime)  
**Security Classification**: OPERATIONAL DEPLOYMENT REFERENCE  

---

## 1. Vercel Project Architecture

IdeaGPT is deployed on Vercel as two dedicated, isolated projects:

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                            VERCEL DEPLOYMENT                             │
├──────────────────────────┬───────────────────────────────────────────────┤
│ API Backend Project      │ idea-gpt-api (Root Directory: apps/api)       │
├──────────────────────────┼───────────────────────────────────────────────┤
│ Frontend Web Project     │ idea-gpt     (Root Directory: apps/web)       │
└──────────────────────────┴───────────────────────────────────────────────┘
```

---

## 2. API Project Configuration (`idea-gpt-api`)

- **Root Directory**: `apps/api`
- **Framework Preset**: `Other` (detected as Python Serverless via `apps/api/vercel.json` and `index.py`)
- **Build Command**: Leave empty (handled by Vercel Python builder)
- **Output Directory**: Leave empty

### Required Environment Variables (Production & Preview)

| Variable | Scope | Status / Value Description |
| :--- | :--- | :--- |
| `APP_ENV` | Production, Preview | Set to `production` (or `staging` for preview) |
| `DATABASE_URL` | Production, Preview | `postgresql+asyncpg://...` (Cloud PostgreSQL e.g. AWS RDS / Supabase / Neon) |
| `CORS_ORIGINS` | Production, Preview | `https://idea-gpt.vercel.app,https://app.ideagpt.dev` (Match exact frontend URLs) |
| `CLERK_PUBLISHABLE_KEY` | Production, Preview | `pk_live_...` (or `pk_test_...` during private beta) |
| `GROQ_API_KEY` | Production, Preview | `gsk_...` (Valid Groq API key) |
| `ENABLE_GROQ` | Production, Preview | `true` |
| `OPENAI_API_KEY` | Production, Preview | Optional fallback key |
| `GEMINI_API_KEY` | Production, Preview | Optional fallback key |
| `REDIS_URL` | Production, Preview | Optional distributed rate limiting cache |

---

## 3. Web Project Configuration (`idea-gpt`)

- **Root Directory**: `apps/web` (or monorepo root with Framework Preset: `Next.js`)
- **Framework Preset**: `Next.js`
- **Build Command**: `pnpm run build` (or Turborepo standard)
- **Output Directory**: `.next`

### Required Environment Variables (Production & Preview)

| Variable | Scope | Status / Value Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Production, Preview | `pk_live_...` |
| `CLERK_SECRET_KEY` | Production, Preview | `sk_live_...` |
| `NEXT_PUBLIC_API_URL` | Production, Preview | `https://idea-gpt-api.vercel.app/api/v1` |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | Production, Preview | `/sign-in` |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | Production, Preview | `/sign-up` |
| `NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL` | Production, Preview | `/` |
| `NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL` | Production, Preview | `/` |

---

## 4. Security Invariants

1. **Zero Secret Sharing**: `DATABASE_URL` and `GROQ_API_KEY` are configured ONLY in `idea-gpt-api`. They must never be added to `idea-gpt` (Web).
2. **CORS Alignment**: `CORS_ORIGINS` in `idea-gpt-api` must exactly match the deployed domain of `idea-gpt`.
