# Contributing to IdeaGPT

First off, thanks for taking the time to contribute!

## Getting Started

1. Fork the repo and create your branch from `main`.
2. Run `pnpm install` in the root.
3. Ensure `.env.local` is set up.
4. Run tests before submitting a PR.

## Code Standards
- We strictly adhere to TypeScript strict mode.
- All Python code must pass `flake8` and `pytest`.
- Ensure Husky hooks pass locally (`pnpm run lint`, `pnpm run typecheck`).

## Pull Requests
Fill out the Pull Request template completely. Ensure all GitHub Action CI checks pass before requesting a review.
