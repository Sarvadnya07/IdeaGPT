# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in IdeaGPT, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

### How to Report

1. **Email:** Send a detailed report to the repository maintainer via GitHub's private vulnerability reporting feature.
2. **GitHub Security Advisories:** Use [GitHub's private vulnerability reporting](https://github.com/Sarvadnya07/IdeaGPT/security/advisories/new) to submit a report directly.

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial Assessment:** Within 5 business days
- **Resolution Target:** Within 30 days for critical issues

### Scope

The following are in scope:

- Authentication and authorization bypasses
- Injection vulnerabilities (SQL, command, template)
- Sensitive data exposure
- CI/CD and supply-chain risks
- API security issues

### Out of Scope

- Social engineering attacks
- Denial of service (unless trivially exploitable)
- Issues in dependencies that are already patched upstream
- Theoretical vulnerabilities without proof of concept

## Security Practices

- All dependencies are monitored via Dependabot
- CI pipeline includes dependency auditing
- Authentication uses Clerk JWT (RS256/JWKS)
- All data endpoints enforce user-scoped ownership
- Security-sensitive code paths require CODEOWNERS review
