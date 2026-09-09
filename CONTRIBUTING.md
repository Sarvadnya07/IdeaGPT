# Contributing to IdeaGPT

Thank you for contributing to IdeaGPT!

---

## 🚀 Quick Start for Contributors

1. **Fork & Clone:** Fork the repository and create your feature branch (`git checkout -b feature/amazing-feature`).
2. **Bootstrap:** Run the automated setup workflow:
   ```bash
   pnpm install
   pnpm setup
   ```
3. **Develop:** Start local dev servers:
   ```bash
   pnpm dev
   ```

---

## 🧪 Pre-PR Verification

Before opening a pull request, ensure all local checks pass:

```bash
# 1. Run full test suite (Vitest + Pytest)
pnpm test

# 2. Verify static types
pnpm typecheck

# 3. Verify code quality (ESLint + Flake8)
pnpm lint

# 4. Verify production build
pnpm build
```

---

## 📖 Key Documentation

* [**Environment Setup Guide (`docs/SETUP.md`)**](./docs/SETUP.md)
* [**Daily Development Workflows (`docs/DEVELOPMENT.md`)**](./docs/DEVELOPMENT.md)
* [**Testing & Database Parity (`docs/TESTING.md`)**](./docs/TESTING.md)
* [**Architecture Blueprint (`docs/ARCHITECTURE.md`)**](./docs/ARCHITECTURE.md)
* [**REST API Specification (`docs/API.md`)**](./docs/API.md)

---

## 🔒 Security & Code Standards

* **TypeScript:** Strict mode is enforced across all frontend code.
* **Python:** Code must conform to Flake8 formatting and pass Pytest with zero regressions.
* **Authentication:** Never bypass Clerk or hardcode credentials.
* **Tenancy:** All database queries must be scoped strictly to `current_user.id`.

