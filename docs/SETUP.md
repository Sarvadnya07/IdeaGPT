# 🚀 IdeaGPT Environment Setup Guide

This guide describes the golden path for bootstrapping a complete local development environment for IdeaGPT.

---

## 📋 Prerequisites

Before running setup, ensure the following host tools are installed:

1. **Node.js** (>=22.13.0, recommended 22.23.2) — [https://nodejs.org/](https://nodejs.org/)
2. **pnpm** (11.1.1) — Install via: `npm install -g pnpm@11.1.1`
3. **Python** (3.12.x) — [https://www.python.org/downloads/](https://www.python.org/downloads/)
4. *(Optional but Recommended)* **Docker & Docker Compose** — [https://www.docker.com/](https://www.docker.com/) for local PostgreSQL 15+ & Redis 7.

---

## ⚡ The Golden Path: One-Command Setup

Run the following commands in sequence:

```bash
# 1. Clone repository
git clone https://github.com/Sarvadnya07/IdeaGPT.git
cd IdeaGPT

# 2. Install workspace dependencies
pnpm install

# 3. Bootstrap development environment
pnpm setup
```

### What `pnpm setup` does automatically:
* **Pre-flight Checks:** Verifies compatible Node (>=22.13.0), pnpm (11.1.1), and Python (3.12.x).
* **Environment Template Initialization:** Safely initializes `apps/api/.env`, `apps/web/.env.local`, and root `.env` from template examples without overwriting any existing secrets.
* **Virtual Environment Creation:** Automatically creates `apps/api/venv` and installs all development/testing dependencies (`requirements-dev.txt`).
* **Cross-Platform Python Detection:** Prepares the runner for Windows (`venv\Scripts\python.exe`) or POSIX (`venv/bin/python`).
* **Docker Probe:** Detects Docker Compose and provides instructions for optional containerized database services.

---

## 🏃 Running the Application

After running `pnpm setup`, start both the Next.js web application and FastAPI server concurrently:

```bash
pnpm dev
```

* **Next.js Web UI:** [http://localhost:3000](http://localhost:3000)
* **FastAPI Server:** [http://localhost:8000](http://localhost:8000)
* **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🗄️ Database & Infrastructure Setup (Optional)

Local unit tests and mock development operate out-of-the-box using SQLite. If you wish to run against real PostgreSQL and Redis locally:

```bash
# Start PostgreSQL 15 & Redis 7 in background
pnpm db:up

# Run Alembic database migrations against local PostgreSQL
pnpm db:migrate

# Stop local database containers when done
pnpm db:down
```

---

## 🔍 Verifying Your Setup

To verify that your local environment is correctly configured without running tests:

```bash
pnpm verify:env
```

This runs a rapid diagnostic check of Node, pnpm, Python virtualenv, FastAPI imports, environment files, and Docker readiness.
