# IdeaGPT — Vercel Deployment Guide

## Step-by-Step Production Deployment

### 1. Import Repository into Vercel
1. Open the [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New... $\to$ Project**.
2. Select your `IdeaGPT` Git repository (`https://github.com/Sarvadnya07/IdeaGPT.git`).

---

### 2. Configure Project Settings

| Setting Name | Value | Description |
| :--- | :--- | :--- |
| **Project Name** | `ideagpt` (or your chosen name) | Project identifier |
| **Framework Preset** | `Next.js` | Automatically configured by Vercel |
| **Root Directory** | `.` | Leave as root directory |
| **Build Command** | Default (`turbo build`) | Monorepo build step |
| **Output Directory** | Default | Managed by Next.js / Vercel functions |
| **Install Command** | Default (`pnpm install`) | Installs workspace packages; Python dependencies installed via root `requirements.txt` |

---

### 3. Configure Environment Variables

Add the following environment variables in **Project Settings $\to$ Environment Variables** for **Production** (and Preview if needed):

#### Frontend Variables
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
NEXT_PUBLIC_API_URL=/api/v1
```

#### Backend & Database Variables
```env
APP_ENV=production
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@db.YOUR_SUPABASE_ID.supabase.co:5432/postgres
CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
CORS_ORIGINS=https://your-domain.vercel.app
```

#### AI Provider Variables
```env
GROQ_API_KEY=gsk_...
ENABLE_GROQ=true
GROQ_DEFAULT_MODEL=llama-3.3-70b-versatile
```

---

### 4. Deploy & Verify
1. Click **Deploy**.
2. Wait for the build to complete.
3. Test endpoints:
   - Public Landing Page: `GET https://your-domain.vercel.app/`
   - Authentication Sign-In: `GET https://your-domain.vercel.app/sign-in`
   - FastAPI Liveness Check: `GET https://your-domain.vercel.app/api/health/live`
   - FastAPI Readiness Check: `GET https://your-domain.vercel.app/api/health/ready`
   - FastAPI Models Endpoint: `GET https://your-domain.vercel.app/api/v1/ai/models`
