# Dautu adoption and migration plan

This document records the safe boundary between the reusable Server Platform and the existing Dautu investment application. It is a migration plan, not authorization to change or deploy the production Dautu service.

## Current Dautu responsibilities

The current Dautu backend in `app/api/main.py` contains both infrastructure concerns and investment-product behavior.

### Candidates for the shared platform

- FastAPI application construction and lifecycle.
- Environment parsing and logging.
- Standard security response headers, host validation, and CORS configuration (after behavior-compatible configuration is verified).
- Generic MongoDB client lifecycle and readiness helpers.
- Firebase ID-token verification as identity authentication only.
- Generic SMTP transport, with project-specific email templates and sender policy remaining in Dautu.
- Liveness/readiness conventions and common tests.

### Must remain Dautu-owned

- `require_user()` membership lookup in Firestore `allowed_users`.
- The Dautu admin identity and role policy.
- Subscription expiry enforcement and Dautu-specific rate limits.
- `/api/auth/send-verification` endpoint, Firebase action-link generation, Vietnamese email content, and its rate-limit policy.
- Stock, screener, simulation, history, financial-report, and AI-analysis routes.
- Dautu MongoDB collection names, indexes, repository queries, and data schema.
- All investment calculations, imports, scheduled jobs, and business workflows.

## Important compatibility differences discovered

1. Dautu's MongoDB module normalizes Atlas URIs, uses a 10-second default timeout, and owns `ensure_indexes()`. The platform helper does not currently implement URI normalization or Dautu's index set. Do not replace Dautu's MongoDB module wholesale.
2. Dautu's `/healthz` currently checks MongoDB and returns 503 if the database is unavailable. The platform separates process liveness (`/healthz`) from dependency readiness (`/readyz`). Before changing probes, update and verify Render's health-check path and monitoring expectations.
3. Dautu uses `SMTP_APP_PASSWORD`; the generic platform sender uses `SMTP_PASSWORD`. A migration must map configuration explicitly and preserve current Gmail STARTTLS behavior. Never rename or remove production environment variables as part of a code-only refactor.
4. Dautu's Firebase helper initializes the project app and verifies tokens, while its authorization layer also checks Firestore membership, role, and subscription. The shared helper must never replace those project authorization checks.
5. Dautu's API currently disables OpenAPI/docs and uses a narrow CORS method allowlist. Preserve these externally visible security settings during adoption.

## Staged migration

### Stage 1 — baseline (complete)

- Create the separate private `server-platform` repository.
- Add the FastAPI starter, optional integrations, template, Docker/Render examples, and CI.
- Confirm the platform test workflow passes on the current main commit.

### Stage 2 — compatibility adapter (next)

- Create a dedicated branch in Dautu; do not edit its production branch directly.
- Add the platform's generic modules only where behavior is equivalent.
- Keep Dautu's current MongoDB adapter and index initialization until a separate compatibility implementation has tests.
- Keep all Dautu routes and authorization logic unchanged.
- Add regression tests for route paths, auth outcomes, CORS, health checks, response projections, and startup index creation.
- Run the complete existing GitHub Actions suite.

### Stage 3 — review and merge

- Open a pull request with a file-by-file change summary and test evidence.
- Review the PR diff for accidental removal of business logic, changed API response shapes, or credential/configuration changes.
- Merge only after explicit approval.

### Stage 4 — production cutover (separate authorization required)

- Do not change the existing Render service, domains, environment variables, database, or deployment configuration until separately approved.
- Deploy the reviewed commit to a preview/staging service with isolated credentials.
- Smoke-test authentication, admin/user authorization, verification email, all read APIs, readiness, and existing scheduled workflows.
- Only then plan a controlled production deployment with rollback steps.

## Isolation rules

- `server-platform` is shared source code, not a shared multi-tenant API.
- Each application gets its own Render service, Firebase project/service account, SMTP credentials, and least-privilege database user/database.
- Dautu keeps its current data and credentials; future applications must not inherit them.
- No secrets belong in GitHub source files, templates, logs, or issue descriptions.
