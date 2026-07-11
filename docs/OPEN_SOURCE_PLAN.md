# Open Source Improvement Plan

To transition IdeaGPT from a personal/internal project to a thriving open-source community asset, the repository should implement standard GitHub community workflows.

## 1. Issue Templates (`.github/ISSUE_TEMPLATE/`)

Creating structured issue templates ensures that incoming bug reports and feature requests contain actionable information.

- **`bug_report.yml`:** Form requesting OS, browser, Steps to Reproduce, Expected Behavior, and actual Logs.
- **`feature_request.yml`:** Form requesting the Problem statement, Proposed Solution, and Alternatives considered.

## 2. Pull Request Template (`.github/pull_request_template.md`)

A checklist for contributors before they submit a PR:
- [ ] Have you run `pnpm lint` and `flake8`?
- [ ] Is your branch based on the latest `main`?
- [ ] Have you added tests for your changes?
- [ ] Does this PR introduce a breaking change? (If yes, explain).

## 3. GitHub Actions CI/CD (`.github/workflows/`)

Automate the validation of PRs.

- **`ci.yml`:**
  - On Pull Request to `main`.
  - Runs `pnpm install`.
  - Runs `pnpm lint` (Frontend).
  - Sets up Python 3.11, runs `pip install -r requirements.txt`.
  - Runs `flake8` and `pytest` (Backend).
  - Fails the PR if any check fails.

## 4. Code of Conduct (`CODE_OF_CONDUCT.md`)

Adopt the [Contributor Covenant](https://www.contributor-covenant.org/) to set clear expectations for community behavior and provide reporting mechanisms for harassment.

## 5. Security Policy (`SECURITY.md` in root)

Add a standard policy for reporting vulnerabilities responsibly without opening a public issue. (e.g., "Please email security@ideagpt.com instead of opening an issue.")

## 6. Release Workflow

Utilize **Changesets** or **Release Please** to automate semantic versioning and changelog generation based on conventional commits. This ensures that every new release on GitHub automatically includes detailed release notes.
