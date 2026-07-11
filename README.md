<div align="center">
  <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 20px;">
    <div style="background: linear-gradient(to top right, #4f46e5, #8b5cf6); border-radius: 12px; width: 48px; height: 48px; display: flex; justify-content: center; align-items: center; box-shadow: 0 0 15px rgba(79,70,229,0.3);">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
    </div>
    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -1px;">IdeaGPT</h1>
  </div>

  <p><strong>Validate Concepts Instantly</strong></p>
  <p><em>Advanced Reasoning AI to evaluate technical feasibility, compute timelines, and assess startup risks.</em></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Next.js-black?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
    <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
    <img src="https://img.shields.io/badge/Turborepo-EF4444?style=for-the-badge&logo=turborepo&logoColor=white" alt="Turborepo" />
  </p>
</div>

---

## 📖 Overview

IdeaGPT is an AI-powered SaaS platform designed to evaluate startup ideas, generate product roadmaps, and recommend custom technology stacks for founders and engineers. It acts as a digital technical co-founder, providing data-driven "first pass" architectural blueprints to help teams move from concept to execution faster and with higher confidence.

## ✨ Key Features

- **Automated Idea Analysis:** Instantly evaluates technical complexity, Time-to-Market metrics, strengths, and weaknesses.
- **Isolated Workspaces:** Fully paginated and searchable project domains with local-draft auto-recovery.
- **Provider-Agnostic AI Orchestrator:** Securely interfaces with OpenAI, Gemini, and Ollama through a decoupled Backend Registry.
- **Visual Roadmaps (Upcoming):** Chronological milestones and priority checklists.
- **Enterprise-Grade Security:** Strict Tenant Isolation on PostgreSQL and immutable JWT validations via Clerk.

## 🏗 Architecture & Tech Stack

This project is structured as an enterprise-grade monorepo leveraging **Turborepo**:

- **Frontend (`apps/web`)**: Next.js 14 App Router, TailwindCSS, Framer Motion, TanStack React Query, Zustand, Zod.
- **Backend (`apps/api`)**: FastAPI, Python 3.11+, PostgreSQL (Asyncpg), SQLAlchemy, Alembic, Pydantic Settings.
- **State & Data**: Strict server-side pagination with query normalization, heavily utilizing localized React context.

```text
ideagpt/
├── apps/
│   ├── api/                # FastAPI Backend Application (Port 8000)
│   └── web/                # Next.js Frontend Application (Port 3000)
├── packages/               # Shared Monorepo Packages (Config, UI, Types)
├── docs/                   # Detailed Project Documentation
├── turbo.json              # Turborepo configuration
└── package.json            # Root workspace configuration
```

## 🚀 Setup & Installation

### Prerequisites
- Node.js (v18+) & pnpm (v9+)
- Python (3.11+)
- PostgreSQL (Local or Hosted)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sarvadnya07/IdeaGPT.git
   cd IdeaGPT
   ```

2. **Install Workspace Dependencies**
   ```bash
   pnpm install
   ```

3. **Environment Setup**
   Copy `.env.example` to `.env` in `apps/api` and `.env.local` in `apps/web`.
   Ensure you provide `DATABASE_URL` and `OPENAI_API_KEY`.

4. **Initialize Python Backend**
   ```bash
   cd apps/api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   alembic upgrade head      # Migrate Database
   cd ../..
   ```

## 🏃 Usage Instructions

Start the entire development ecosystem simultaneously via Turborepo:

```bash
pnpm run dev
```

- **Web UI:** `http://localhost:3000`
- **API Server:** `http://localhost:8000`
- **Swagger Docs:** `http://localhost:8000/docs`

## 📚 API Documentation

The backend is fully self-documenting via OpenAPI/Swagger. Access `http://localhost:8000/docs` while the server is running to view detailed payloads, schemas, and test routes.

## 🤝 Contributing & Scope

We welcome contributions! Please see our [FUTURE_SCOPE.md](./docs/FUTURE_SCOPE.md) for our long-term vision, upcoming scalability plans, and current roadmap.

---
<div align="center">
  <sub>Built with ❤️ by the IdeaGPT Engineering Team</sub>
</div>
