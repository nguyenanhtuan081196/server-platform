# Server Platform

A reusable, project-neutral backend foundation built with FastAPI. Use it to start independent applications without rebuilding the operational basics each time.

## Architecture and isolation

This repository is shared **source code**, not a shared multi-tenant production API. Deploy one backend service per application. Each deployment must use its own credentials and project data.

| Integration | Shared in source code | Separate for every project |
| --- | --- | --- |
| MongoDB | Connection helpers and lifecycle | Atlas database, database user, URI, backups and access policy |
| Firebase | Firebase Admin initialization and ID-token verification | Firebase project, service account, Auth users, Firestore and Security Rules |
| SMTP | Generic SMTP transport | Sender identity, app password/API key and sending limits |
| Render | Deployment pattern | Render service, environment variables, domains and access controls |

For MongoDB, a shared Atlas cluster can be a cost-conscious starting point, but create a separate database and least-privilege database user for every application. For stronger isolation, use separate Atlas clusters. Never give one project's credentials access to another project's database.

For Firebase, create a separate Firebase project per application. Each project owns its Authentication users, Firestore data, Security Rules and service account. Never copy service-account JSON between projects.

## What belongs here

- Application factory and standard health endpoints.
- Environment-based configuration and safe logging.
- Security response headers, host validation, and configurable CORS.
- Optional MongoDB connection lifecycle, collection helper and readiness checks.
- Optional Firebase ID-token verification.
- SMTP email transport.
- Docker and Render deployment starter files.
- Tests and a project template.

## What does not belong here

Business routes, project-specific schemas, stock/investment logic, customer data, Firebase project credentials, SMTP passwords, database URIs, and project-specific admin identities. Keep those in the consuming project and its own secret store.

## Quick start

1. Clone this private repository and copy the root `app/` platform package, `requirements.txt`, and the deployment starter files into a new project repository. The template folder contains the project entry point and setup notes.
2. Create a virtual environment and install `requirements.txt`.
3. Copy `.env.example` to `.env` and configure only the integrations you use.
4. Run `uvicorn app.main:app --reload` (or your project's own entry point).
5. Run `python -m unittest discover -s tests -v`.

The platform deliberately does not require MongoDB or Firebase just to start. Enable integrations with environment variables.

## Configuration

See [`.env.example`](.env.example). Never commit real credentials.

Important variables:

- `APP_NAME`: service display name.
- `APP_ENV`: development, test, or production.
- `API_ALLOWED_HOSTS`: comma-separated hostnames; include the Render hostname and custom domain.
- `CORS_ALLOWED_ORIGINS`: comma-separated exact origins.
- `MONGODB_URI` and `MONGODB_DATABASE`: optional MongoDB integration. Use a database-specific, least-privilege Atlas user per project.
- `FIREBASE_SERVICE_ACCOUNT_JSON`: optional Firebase Admin service-account JSON for this project's Firebase project.
- `AUTH_REQUIRE_VERIFIED_EMAIL`: whether Firebase users must have verified email.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`: optional SMTP transport.

## MongoDB usage

```python
from app.database.mongo import get_collection, get_database

db = get_database()
users = get_collection("users")
```

The client is lazy and cached for the process, and is closed by the FastAPI application lifespan on shutdown. `/readyz` pings MongoDB only when `MONGODB_URI` is configured. A missing optional integration does not prevent local startup.

## Firebase usage

```python
from fastapi import APIRouter, Depends
from app.auth.firebase import require_authenticated_user

router = APIRouter()

@router.get("/me")
def me(user=Depends(require_authenticated_user)):
    return {"uid": user["uid"], "email": user.get("email")}
```

The helper verifies Firebase identity and (by default) verified-email status. It does **not** decide project membership, subscription, or admin roles. Each project must implement those authorization checks against its own data. Never trust a client-supplied role or email as proof of admin access.

## Health endpoints

- `GET /healthz`: process liveness; no credentials or dependency details.
- `GET /readyz`: readiness; checks MongoDB only when `MONGODB_URI` is configured.

## Deployment and secrets

Deploy one Render web service per project. Set secrets in that service's environment settings, not in Git. Keep `MONGODB_URI`, Firebase service-account JSON, SMTP password, and other secrets out of source control, logs, client-side code, and issue reports. Restrict MongoDB network access and database users to the minimum required.

The included Dockerfile and `render.yaml` are starter examples. Review service name, region, plan, environment variables, and health-check path before deploying. Do not connect this repository to the existing Dautu production service until a separate migration is tested and explicitly approved.

## Existing Dautu adoption\n\nSee [the staged Dautu adoption plan](docs/dautu-adoption-plan.md) for the audited boundary between shared infrastructure and Dautu-specific authentication, data, API, and investment logic. It documents compatibility differences and explicitly separates code migration from production cutover.\n\n## Reuse and versioning

Projects can initially copy the platform source package. Once the API stabilizes, publish versioned releases and optionally package the shared modules for pinned dependency reuse. Avoid making production projects depend on an unpinned moving branch.
