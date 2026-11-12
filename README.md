# Server Platform

A reusable, project-neutral backend foundation built with FastAPI. Use it to start independent applications without rebuilding the operational basics each time.

## What belongs here

- Application factory and standard health endpoints.
- Environment-based configuration and safe logging.
- Security response headers, host validation, and configurable CORS.
- Optional MongoDB connection lifecycle and readiness checks.
- Optional Firebase ID-token verification.
- SMTP email transport.
- Docker and Render deployment starter files.
- Tests and a project template.

## What does not belong here

Business routes, project-specific schemas, stock/investment logic, customer data, Firebase project credentials, SMTP passwords, database URIs, and project-specific admin identities. Keep those in the consuming project and its own secret store.

## Quick start

1. Copy `templates/fastapi-project/` to a new project repository.
2. Create a virtual environment and install `requirements.txt`.
3. Copy `.env.example` to `.env` and configure only the integrations you use.
4. Run `uvicorn app.main:app --reload`.
5. Run `python -m unittest discover -s tests -v`.

The platform deliberately does not require MongoDB or Firebase just to start. Enable integrations with environment variables.

## Configuration

See [`.env.example`](.env.example). Never commit real credentials.

Important variables:

- `APP_NAME`: service display name.
- `APP_ENV`: development, test, or production.
- `API_ALLOWED_HOSTS`: comma-separated hostnames; include the Render hostname and custom domain.
- `CORS_ALLOWED_ORIGINS`: comma-separated exact origins.
- `MONGODB_URI` and `MONGODB_DATABASE`: optional MongoDB integration.
- `FIREBASE_SERVICE_ACCOUNT_JSON`: optional Firebase Admin service-account JSON.
- `AUTH_REQUIRE_VERIFIED_EMAIL`: whether Firebase users must have verified email.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`: optional SMTP transport.

## Health endpoints

- `GET /healthz`: process liveness; no credentials or dependency details.
- `GET /readyz`: readiness; checks MongoDB only when `MONGODB_URI` is configured.

## Extend the application

Create routers in your project, then pass them to `create_app(routers=[...])`. Keep business logic and authorization policies in that project. The Firebase helper verifies identity; it does not decide project membership, subscription, or admin roles.

## Deployment

The included Dockerfile and `render.yaml` are safe starting points. Review service name, region, plan, environment variables, and health-check path before deploying. Do not connect this repository to the existing Dautu production service until a separate migration is tested and explicitly approved.

## Reuse and versioning

Projects can initially copy the starter template. Once the platform API stabilizes, publish versioned releases and optionally package the shared modules for pinned dependency reuse. Avoid making production projects depend on an unpinned moving branch.
