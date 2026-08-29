# IdeaGPT — Production Deployment & Release Checklist

**Product**: IdeaGPT  
**Version**: 1.0.0-rc1  
**Target Environment**: AWS ECS Fargate / Vercel Edge / Render / Managed Kubernetes  

---

## 1. Pre-Deployment Environment Variables Matrix

### Backend (`apps/api`)
| Variable | Required | Example / Description |
| :--- | :---: | :--- |
| `APP_ENV` | Yes | `production` |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://user:pass@db-host:5432/ideagpt_prod` |
| `CLERK_PUBLISHABLE_KEY` | Yes | `pk_live_...` (or `pk_test_...` during private beta) |
| `CLERK_JWT_ISSUER` | Optional | `https://clerk.ideagpt.dev` (overrides derived issuer) |
| `CLERK_SECRET_KEY` | Optional | `sk_live_...` (only if backend Clerk SDK is called) |
| `CLERK_JWT_TEST_SECRET` | **PROHIBITED** | Must NOT be present in production |
| `CORS_ORIGINS` | Yes | `https://app.ideagpt.dev,https://ideagpt.dev` |
| `GROQ_API_KEY` | Yes | `gsk_...` (primary AI provider) |
| `ENABLE_GROQ` | Optional | `true` |
| `OPENAI_API_KEY` | Optional | `sk-proj-...` (fallback provider) |
| `GEMINI_API_KEY` | Optional | `AIzaSy...` (fallback provider) |
| `REDIS_URL` | Optional | `redis://redis-host:6379/0` (for distributed rate limits) |

### Frontend (`apps/web`)
| Variable | Required | Example / Description |
| :--- | :---: | :--- |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes | `pk_live_...` |
| `CLERK_SECRET_KEY` | Yes | `sk_live_...` (server-side Next.js middleware) |
| `NEXT_PUBLIC_API_URL` | Yes | `https://api.ideagpt.dev/api/v1` |

---

## 2. Step-by-Step Deployment Runbook

### Step 1: Database Migration
```bash
cd apps/api
# Ensure 0 schema drift
alembic check
# Run pending migrations
alembic upgrade head
```

### Step 2: Backend Container Build & Deployment
```bash
# Build Docker image
docker build -t ideagpt-api:1.0.0 apps/api/
# Verify liveness & readiness probes
curl -f https://api.ideagpt.dev/health/live
curl -f https://api.ideagpt.dev/health/ready
```

### Step 3: Frontend Deployment (Vercel / Node Container)
```bash
pnpm install --frozen-lockfile
pnpm run build
# Ensure all 28 routes compiled
```

### Step 4: Post-Deployment Smoke Verification
- [ ] Sign in with Clerk user account
- [ ] Create test project workspace
- [ ] Create test startup idea
- [ ] Run AI evaluation (verify sub-second Groq execution)
- [ ] View Tech Stack & PRD generator tabs
- [ ] Export markdown report and verify download

---

## 3. Rollback Strategy

1. **Frontend**: Instant rollback to previous Vercel deployment deployment hash / container tag.
2. **Backend**: Rollback container image to previous release tag.
3. **Database**: Backward-compatible migrations ensure schema rollback safety without dropping active columns.
