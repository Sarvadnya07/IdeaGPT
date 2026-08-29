# IdeaGPT — Final Remaining Work & Pre-Production Boundary

**Date**: August 2026  
**Scope**: Classification of Remaining Tasks for Private Beta & Public Launch  

---

## 1. Classification of Remaining Work

### Category A: Fixed in Code (Completed in Pre-Production Sprint)
- [x] Clerk RS256 cryptography dependency installed & declared in `requirements.txt`.
- [x] Database connection pool resilience (`pool_pre_ping`, recycle, timeout, sizing).
- [x] Transactional rollback safety on route exceptions in `get_db`.
- [x] Startup lifespan cleanup sweeps for stale evaluations and background AI tasks.
- [x] Structured JSON log query scrubber to redact URL parameters containing secrets.
- [x] Frontend Axios interceptor enhanced to display explicit rate limit / quota / validation errors.

### Category B: Requires External Configuration (Deploy-Time Tasks)
- [ ] Configure live Production Clerk Publishable Key (`pk_live_...`) and custom domain in DNS.
- [ ] Configure Production CORS origins list matching exact production domains (`https://app.ideagpt.dev`).
- [ ] Configure Groq Cloud production billing / tier thresholds in Groq console.

### Category C: Requires Infrastructure Setup (DevOps / Cloud Hosting)
- [ ] Setup managed PostgreSQL instance (e.g. AWS RDS PostgreSQL 16+ or Supabase) with automated daily backups & 7-day point-in-time recovery.
- [ ] Setup container orchestrator (AWS ECS Fargate / Render / Vercel) with liveness (`/health/live`) and readiness (`/health/ready`) probe checks.
- [ ] Optional: Redis instance configuration if centralized multi-pod rate limiting is required.

### Category D: Future Enhancements (Phase 10+ Roadmap)
- [ ] Interactive AI Mentor simulation (`/mentor`).
- [ ] Recruiter & Team hiring planner simulation (`/recruiter`).
- [ ] GitHub Lab automated scaffolding repo generation (`/github-lab`).
- [ ] Strategy Lab deep venture war-gaming (`/strategy-lab`).
- [ ] Investor matchmaker network (`/investor`).

---

## 2. Beta Gate Decision

All code-fixable blockers are **100% resolved**. The remaining tasks are standard hosting infrastructure and credential provisioning actions documented in the [Deployment Checklist](./PRODUCTION_DEPLOYMENT_CHECKLIST.md).
