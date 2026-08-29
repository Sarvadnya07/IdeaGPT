<div align="center">
  <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 20px;">
    <div style="background: linear-gradient(to top right, #4f46e5, #8b5cf6); border-radius: 12px; width: 48px; height: 48px; display: flex; justify-content: center; align-items: center; box-shadow: 0 0 15px rgba(79,70,229,0.3);">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
    </div>
    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -1px;">IdeaGPT</h1>
  </div>

  <p><strong>Validate Concepts Instantly</strong></p>
  <p><em>Advanced AI co-founder for technical feasibility, architectural blueprints, and timeline evaluation.</em></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Next.js-black?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
    <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
    <img src="https://img.shields.io/badge/Turborepo-EF4444?style=for-the-badge&logo=turborepo&logoColor=white" alt="Turborepo" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  </p>
</div>

---

## 📖 Overview

**IdeaGPT** is an AI-powered SaaS platform designed to bridge the gap between ideation and execution. Tailored for founders, product managers, and software engineers, IdeaGPT acts as an automated technical co-founder. By evaluating startup concepts, generating precise product roadmaps, and recommending custom technology stacks, it provides data-driven architectural blueprints that minimize risk and accelerate time-to-market.

---

## ✨ Features

- **🧠 Automated Idea Analysis:** Instantly evaluate technical complexity, time-to-market metrics, and strategic strengths/weaknesses.
- **📂 Isolated Workspaces:** Fully paginated, searchable, and isolated project domains.
- **🤖 Provider-Agnostic AI Orchestrator:** Seamlessly integrates with Groq (Llama 3.3), OpenAI, Gemini, and Ollama with dynamic model discovery and cached fallback routing.
- **⚖️ Idea Benchmarking Engine:** Side-by-side comparative matrices evaluating 2–5 ideas with score deltas and ranking.
- **📊 Platform Analytics & Velocity:** Real-time metrics on project velocity, evaluation score distributions, and dimensional criteria averages.
- **🛠️ Tech Stack Architect:** 5-layer tailored recommendations across Frontend, Backend, Database, AI, and DevOps with architectural trade-offs.
- **🏛️ Architecture Blueprints Studio:** System topologies, Mermaid data flow diagrams, RESTful API registries, and database ER models.
- **📋 PRD & Pitch Deck Generator:** Automated Product Requirements Documents and 10-slide VC pitch deck outlines with Markdown/JSON exports.
- **📑 Saved Reports & Exports Hub:** Instant preview, clipboard copy, and `.md` / `.json` downloads for all evaluations.
- **🗺️ Intelligent Roadmapping:** Project-specific milestone timelines, objectives, and task trackers backed by PostgreSQL.
- **🔒 Enterprise-Grade Security:** Strict multi-tenant data isolation via PostgreSQL and secure JWT-based session management through Clerk.

### 🚧 Future Vision & Roadmap

- **🤝 Extended Simulations:** AI Mentor, Recruiter Sim, GitHub Lab, and Strategy Lab (see [FUTURE_SCOPE.md](./FUTURE_SCOPE.md)).

---

## 📸 Screenshots & Demo

_(Note: Replace placeholder links with actual demo screenshots when ready)_

|                                                      Dashboard Overview                                                       |                                              Idea Analysis & Insights                                               |
| :---------------------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------: |
| <img src="https://via.placeholder.com/600x350/0c0c0e/ffffff?text=Dashboard+Overview" alt="Dashboard Overview" width="100%" /> | <img src="https://via.placeholder.com/600x350/0c0c0e/ffffff?text=Idea+Analysis" alt="Idea Analysis" width="100%" /> |

---

## 🛠️ Tech Stack

**Frontend Environment:**

- **Framework:** Next.js 16+ (React 19, App Router, Turbopack)
- **Language:** TypeScript
- **Styling:** TailwindCSS, Framer Motion
- **State Management:** TanStack React Query v5, Zustand
- **Authentication:** Clerk

**Backend Environment:**

- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Database:** PostgreSQL (with Asyncpg & SQLAlchemy)
- **Migrations:** Alembic
- **Validation:** Pydantic

**Infrastructure & Tooling:**

- **Monorepo Management:** Turborepo
- **Package Manager:** pnpm

---

## 🏗️ Architecture

IdeaGPT is structured as an enterprise-ready **Turborepo** monorepo, strictly separating frontend presentation layers from robust backend inference and data APIs. The Next.js client handles session states and optimistic UI updates while the Python-based FastAPI backend orchestrates heavy LLM inference, schema generation, and asynchronous PostgreSQL persistence.

---

## 🚀 Installation Guide

### Prerequisites

- [Node.js (v18+)](https://nodejs.org/) & [pnpm (v9+)](https://pnpm.io/)
- [Python (3.11+)](https://www.python.org/)
- [PostgreSQL (v14+)](https://www.postgresql.org/)

### Step-by-Step Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Sarvadnya07/IdeaGPT.git
   cd IdeaGPT
   ```

2. **Install Workspace Dependencies**

   ```bash
   pnpm install
   ```

3. **Backend Environment Setup**

   ```bash
   cd apps/api
   python -m venv venv
   # macOS/Linux: source venv/bin/activate
   # Windows: .\venv\Scripts\activate

   pip install -r requirements.txt
   alembic upgrade head
   cd ../..
   ```

---

## 🏃 Usage Instructions

Once dependencies are installed and environments are configured, start the complete development ecosystem using Turborepo:

```bash
pnpm run dev
```

- **Next.js Web UI:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Server:** [http://localhost:8000](http://localhost:8000)
- **OpenAPI Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ⚙️ Configuration

Copy the provided example environment files and populate them with your credentials.

**1. Frontend (`apps/web/.env.local`)**

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**2. Backend (`apps/api/.env`)**

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ideagpt
OPENAI_API_KEY=sk-...
CLERK_SECRET_KEY=sk_test_...
```

---

## 📁 Folder Structure

```text
IdeaGPT/
├── apps/
│   ├── api/                    # FastAPI Backend Application (Python)
│   │   ├── alembic/            # Database Migrations
│   │   ├── app/                # Core API Logic & Routers
│   │   └── requirements.txt    # Python Dependencies
│   └── web/                    # Next.js Frontend Application (TypeScript)
│       ├── app/                # Next.js App Router Pages
│       ├── components/         # Reusable UI Components
│       └── lib/                # Client Utilities & Hooks
├── packages/                   # Shared Monorepo Packages
│   ├── @ideagpt/typescript-config
│   └── @ideagpt/ui
├── docs/                       # Project Documentation
├── turbo.json                  # Turborepo Configuration
└── pnpm-workspace.yaml         # Monorepo Workspace Config
```

---

## 📚 API Documentation

The FastAPI backend is fully self-documenting. When running the API server, navigate to `http://localhost:8000/docs` to interact with the interactive Swagger UI. This provides full schema definitions, endpoint payloads, and real-time route testing.

---

## ⚡ Performance / Optimization Notes

- **Query Caching:** Heavily utilizes TanStack React Query on the frontend to minimize redundant API calls.
- **Asynchronous DB:** The backend leverages `asyncpg` for non-blocking, high-concurrency database transactions.
- **Turborepo Caching:** Intelligent build and execution caching drastically reduces local build times and CI/CD pipeline durations.

---

## 🛡️ Security Considerations

- **Authentication:** Managed externally by Clerk, ensuring secure JWT minting without locally storing raw passwords.
- **Data Isolation:** All PostgreSQL queries are strictly filtered by Tenant/User ID at the ORM level.
- **Rate Limiting:** FastAPI endpoints are actively wrapped in `slowapi` to prevent abuse of downstream LLM inference APIs.

---

## 🤝 Contributing Guidelines

We welcome community contributions!

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

For future roadmap items, refer to our [FUTURE_SCOPE.md](./FUTURE_SCOPE.md).

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## ✍️ Author / Credits

Built with ❤️ by the **IdeaGPT Engineering Team** (Sarvadnya07).
