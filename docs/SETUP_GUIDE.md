# Local Setup Guide

Follow this guide to get the complete IdeaGPT ecosystem running on your local machine for development and testing.

## Prerequisites

Ensure you have the following installed on your machine:
- [Node.js](https://nodejs.org/) (v18.17+ required for Next.js)
- [pnpm](https://pnpm.io/) (v9+ recommended, to manage the Turborepo workspace)
- [Python](https://www.python.org/downloads/) (3.11+ required for FastAPI)
- [Git](https://git-scm.com/)

## 1. Clone the Repository

```bash
git clone https://github.com/Sarvadnya07/IdeaGPT.git
cd IdeaGPT
```

## 2. Install Node Dependencies

At the root of the project, install the workspace dependencies using `pnpm`. This will install dependencies for the `web` app and all `packages/*`.

```bash
pnpm install
```

## 3. Setup Python Backend

The API requires its own virtual environment to prevent dependency conflicts.

```bash
# Navigate to the API directory
cd apps/api

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python requirements
pip install -r requirements.txt

# Return to root directory
cd ../..
```

## 4. Environment Variables

You need to set up environment variables for both the frontend and backend.

### Backend (`apps/api/.env`)
Create a `.env` file in `apps/api/`:
```env
# Required for LLM Reasoning
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# API Settings
CORS_ORIGINS=http://localhost:3000
```

### Frontend (`apps/web/.env.local`)
Create a `.env.local` file in `apps/web/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 5. Start the Development Servers

IdeaGPT uses Turborepo to run both the frontend and backend simultaneously with a single command from the root directory:

```bash
pnpm run dev
```

### What this does:
1. `apps/web` (Next.js) will start on [http://localhost:3000](http://localhost:3000)
2. `apps/api` (FastAPI) will start on [http://localhost:8000](http://localhost:8000)

## 6. Troubleshooting

**Python dependencies failing to install?**
Ensure you are using Python 3.11+. Some libraries may not have pre-built wheels for older versions.

**Next.js Cannot fetch from API?**
Ensure your `apps/api/.env` has `CORS_ORIGINS` correctly configured to allow requests from `http://localhost:3000`, and that `NEXT_PUBLIC_API_URL` is correct in `apps/web/.env.local`.

**Turborepo script failing?**
Sometimes `pnpm` workspace caches can get stuck. Run `pnpm clean` (if configured) or manually delete `node_modules` and `.turbo` folders and run `pnpm install` again.
