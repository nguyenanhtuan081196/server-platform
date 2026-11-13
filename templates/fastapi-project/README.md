# New project starter

This directory contains a minimal project-owned FastAPI entry point. The reusable infrastructure is installed as the separately versioned `server-platform` Python dependency.

1. Copy this template into a new project repository.
2. Add `server-platform` to the new project's `pyproject.toml`, pinned to a reviewed release tag (for example, `server-platform @ git+https://github.com/nguyenanhtuan081196/server-platform.git@v0.1.0`).
3. Install the project's dependencies. If the platform repository is access-restricted, configure a read-only GitHub deploy key/token in the build environment; never commit credentials.
4. Add project-owned routers under `app/api/` and pass them to `create_app(routers=[...])`.
5. Add project-owned authorization, data models, tests and CI.
6. Configure a unique `APP_NAME`, allowed hosts, CORS origins and service credentials.
7. Deploy a separate Render service for this project.

The project imports shared infrastructure from `server_platform`, while its own API code remains under `app`.

## MongoDB

Create a database and a least-privilege MongoDB Atlas database user for this project. Set its own `MONGODB_URI` and `MONGODB_DATABASE` in the project's Render environment. A shared Atlas cluster is acceptable initially if database permissions prevent cross-project access; separate clusters provide stronger isolation.

## Firebase

Create a new Firebase project for this application. Enable only the required products, configure its own Authentication providers and Firestore Security Rules, then create a dedicated service account for backend verification. Set its JSON in `FIREBASE_SERVICE_ACCOUNT_JSON` in this project's secret environment. Do not reuse Dautu's Firebase project or service account.

## SMTP and secrets

Use a separate sender identity or credential where practical. Keep all secrets in the project's secret store, never in Git. Do not share production database credentials, Firebase service accounts, admin identities, or email credentials between projects.

The shared Firebase helper verifies identity only. Implement this project's membership and admin-role checks in this project.
