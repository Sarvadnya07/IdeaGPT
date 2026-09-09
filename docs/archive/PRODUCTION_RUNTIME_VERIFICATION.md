# IdeaGPT — Production Runtime Verification Runbook

## Post-Deployment Verification Probes

Run these commands using `curl` or your browser to verify the production system:

### 1. Frontend Liveness Probe
```bash
curl -I https://<your-domain>.vercel.app/
# Expected: HTTP 200 OK
# Content-Type: text/html; charset=utf-8
```

### 2. Frontend Auth Interface Probe
```bash
curl -I https://<your-domain>.vercel.app/sign-in
# Expected: HTTP 200 OK
# Content-Type: text/html; charset=utf-8
```

### 3. FastAPI Backend Liveness (No DB required)
```bash
curl -s https://<your-domain>.vercel.app/api/health/live
# Expected: {"status": "live", "service": "IdeaGPT API"}
```

### 4. FastAPI Backend Readiness (Database connected)
```bash
curl -s https://<your-domain>.vercel.app/api/health/ready
# Expected: {"status": "ready", "database": "connected"}
```

### 5. AI Gateway Model Discovery
```bash
curl -s https://<your-domain>.vercel.app/api/v1/ai/models
# Expected: JSON array containing active and available models (Groq, Gemini, Tavily, etc.)
```

### 6. Protected Route Enforcement
```bash
curl -I https://<your-domain>.vercel.app/dashboard
# Expected: HTTP 307 / 308 redirect to /sign-in (Clerk middleware protection)
```
