# Testing Guide

Quality assurance is highly prioritized. Given the complexities of LLM integrations and monorepo architectures, we maintain distinct testing layers.

## Backend Testing (FastAPI)

We use `pytest` as our testing framework for the Python backend. Tests are located in `apps/api/tests/`.

### Running Tests

```bash
cd apps/api
pytest
```

To run with coverage:
```bash
pytest --cov=app tests/
```

### Strategy
- **Unit Tests:** Focus on parsing logic, Pydantic schema validations, and internal service functions.
- **Mocking LLMs:** We NEVER hit the actual OpenAI/Anthropic APIs during standard testing to save costs and execution time. We use `unittest.mock` to intercept LLM client calls and return deterministic JSON fixture data.
- **Integration Tests:** Spin up the FastAPI `TestClient` to ensure endpoints resolve properly and return correct HTTP status codes.

## Frontend Testing (Next.js)

We utilize **Vitest** and **React Testing Library** for frontend components. (Currently being implemented).

### Strategy
- **Unit Testing Components:** Reusable components in `packages/ui` should have 100% test coverage.
- **State Management:** Ensure Zustand stores act deterministically when mock data is injected.

## End-to-End (E2E) Testing

*Future Implementation:* We plan to integrate **Playwright** or **Cypress** to handle full user flows:
1. User logs in.
2. Submits a startup idea.
3. System waits for the simulated API response.
4. UI renders the dynamic roadmap correctly.

## Manual Testing & Edge Cases

Before merging major features, ensure you manually test these edge cases:
- Extremely short or nonsensical startup idea inputs (ensure the LLM handles it gracefully or the frontend blocks it).
- Long inputs exceeding character limits.
- API timeouts (simulate a slow internet connection using Chrome DevTools).
