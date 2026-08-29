# Deployment Guide

IdeaGPT's decoupled architecture allows the frontend and backend to be deployed independently, optimizing for their specific compute requirements.

## 🌐 Frontend Deployment (Next.js)

The recommended hosting provider for the `apps/web` application is **Vercel**, which provides native support for Turborepo and Next.js App Router optimizations.

### Steps for Vercel Deployment

1. Connect your GitHub repository to Vercel.
2. Select the `IdeaGPT` repository.
3. Vercel automatically detects the Turborepo structure.
4. **Root Directory:** Keep it as the repository root.
5. **Build Command:** It should automatically default to `pnpm run build` or `turbo run build`.
6. **Environment Variables:** Add `NEXT_PUBLIC_API_URL` pointing to your production backend URL.
7. Deploy.

## ⚙️ Backend Deployment (FastAPI)

FastAPI requires a Python environment. Recommended hosts include **Render**, **Railway**, or **AWS ECS/AppRunner**. We'll outline deploying via Docker, which is universally supported.

### Dockerized Deployment (Recommended)

A `docker-compose.yml` (and corresponding `Dockerfile` in `apps/api`) should be used to containerize the application.

1. **Build the Image:**

   ```bash
   cd apps/api
   docker build -t ideagpt-api .
   ```

2. **Run the Container:**
   ```bash
   docker run -d -p 8000:8000 --env-file .env ideagpt-api
   ```

### Deploying to Render (Example)

1. Create a new "Web Service" on Render.
2. Point it to the GitHub repository.
3. **Root Directory:** `apps/api`
4. **Environment:** Python
5. **Build Command:** `pip install -r requirements.txt`
6. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Add environment variables (e.g., `OPENAI_API_KEY`, `CORS_ORIGINS`).

## 🔄 CI/CD Recommendations

We recommend setting up **GitHub Actions** to automate deployments.

1. **Lint & Test Workflow:** Triggered on every Pull Request to `main`. It should run `flake8`, `pytest`, and `eslint`.
2. **Deploy Workflow:** Triggered on pushing to `main`. It should build the Docker image and push it to a registry (e.g., AWS ECR) and trigger a Vercel deployment hook.
