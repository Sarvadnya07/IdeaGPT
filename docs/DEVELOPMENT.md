# 💻 IdeaGPT Daily Development Guide

This guide details everyday engineering workflows, canonical commands, debugging, code standards, and monorepo conventions.

---

## 🛠️ Canonical Root Commands

All primary engineering tasks are exposed through root workspace commands:

| Command | Purpose | Output / Action |
| :--- | :--- | :--- |
| `pnpm setup` | Bootstrap environment | Checks runtimes, builds `apps/api/venv`, installs pip dependencies, and sets up safe `.env` files. |
| `pnpm dev` | Start development servers | Concurrently launches Next.js (port 3000) and FastAPI (port 8000) via Turborepo. |
| `pnpm test` | Run full test suite | Concurrently executes frontend Vitest tests and backend Pytest tests. |
| `pnpm typecheck` | Static type checking | Runs `tsc --noEmit` on frontend and validates backend schemas. |
| `pnpm lint` | Monorepo linting | Executes ESLint across web/packages and Flake8 on backend. |
| `pnpm build` | Production build | Builds Next.js production bundles and validates static routes. |
| `pnpm clean` | Clean artifacts | Removes `.turbo`, `.next`, cache files, and SQLite test databases. |
| `pnpm clean:deep` | Full reset | Removes build artifacts, caches, `node_modules`, and Python `venv`. |
| `pnpm verify:env` | Environment diagnostic | Quickly verifies Node, pnpm, Python venv, and environment files. |
| `pnpm db:up` | Start local containers | Boots local PostgreSQL 15 & Redis 7 via Docker Compose. |
| `pnpm db:down` | Stop local containers | Halts PostgreSQL and Redis containers. |
| `pnpm db:migrate` | Run migrations | Executes `alembic upgrade head` via the virtual environment. |

---

## 🐍 Python Virtual Environment & Runner Architecture

You **never need to manually activate** `apps/api/venv` before running project commands.

The backend uses a cross-platform runner (`apps/api/run-python.js`):
* **On Windows:** Resolves to `apps/api/venv/Scripts/python.exe`.
* **On Linux/macOS:** Resolves to `apps/api/venv/bin/python`.
* **Missing venv:** If the virtualenv is missing, the runner outputs a clear diagnostic prompting you to run `pnpm setup`.

---

## 🐞 Debugging in VS Code

Pre-configured launch profiles exist in `.vscode/launch.json`:
1. **Next.js: debug server-side:** Launches Next.js dev server with Node debugger attached.
2. **FastAPI: debug:** Launches Uvicorn server (`app.main:app`) on port 8000 with Python debugger attached.

### Recommended Extensions:
Install recommended extensions prompted by VS Code (configured in `.vscode/extensions.json`):
* Python (`ms-python.python`)
* Pylance (`ms-python.vscode-pylance`)
* ESLint (`dbaeumer.vscode-eslint`)
* Prettier (`esbenp.prettier-vscode`)
* Tailwind CSS IntelliSense (`bradlc.vscode-tailwindcss`)

---

## 🧹 Code Quality & Git Hooks

A pre-commit hook is installed via Husky (`.husky/pre-commit`):
* Runs `pnpm run lint` on commit.
* Code style is enforced using Prettier (`pnpm run format`).
