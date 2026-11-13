# Server Platform

A reusable, project-neutral FastAPI backend foundation distributed as the Python package `server-platform`. Use it to start independent applications without rebuilding operational infrastructure each time.

## Architecture and isolation

This repository is shared **library source**, not a shared multi-tenant production API. Deploy one backend service per application. Each deployment must use its own credentials and project data.

| Integration | Shared in this package | Separate for every project |
| --- | --- | --- |
| MongoDB | Connection helpers and lifecycle | Atlas database, database user, URI, backups and access policy |
| Firebase | Firebase Admin initialization and ID-token verification | Firebase project, service account, Auth users, Firestore and Security Rules |
| SMTP | Generic SMTP transport | Sender identity, app password/API key and sending limits |
| Render | Deployment pattern | Render service, environment variables, domains and access controls |

For MongoDB, a shared Atlas cluster can be a cost-conscious starting point, but create a separate database and least-privilege database user for every application. For stronger isolation, use separate Atlas clusters. Never give one project's credentials access to another project's database.

For Firebase, create a separate Firebase project per application. Each project owns its Authentication users, Firestore data, Security Rules and service account. Never copy service-account JSON between projects.

## What belongs here

- FastAPI application factory and standard health endpoints.
- Environment-based configuration and safe logging.
- Security response headers, host validation, and configurable CORS.
- Optional MongoDB connection lifecycle, URI normalization, collection helper and readiness checks.
- Optional Firebase ID-token verification.
- Generic SMTP email transport.
- Docker and Render deployment starter files.
- Tests and a project template.

Business routes, project-specific schemas, investment logic, customer data, Firebase credentials, SMTP passwords, database URIs, and project-specific admin identities belong in each consuming project.

## Install from source

For local development of this repository:

```bash
python -m venv .venv
# Activate the virtual environment, then:
python -m pip install -e ".[test]"
python -m unittest discover -s tests -v
```

The package uses a `src/server_platform` layout and is imported as `server_platform`, avoiding collisions with a consuming project's own `app` package.

After a reviewed release tag is published, a consuming project's dependency can be pinned to that immutable tag:

```toml
[project]
dependencies = [
  "server-platform @ git+https://github.com/nguyenanhtuan081196/server-platform.git@v0.1.0"
]
```

If repository access is restricted, configure a read-only GitHub deploy key or token in the build environment. Never embed credentials in dependency URLs or commit them to source control. Do not depend on an unpinned `main` branch.

## Quick start for a new project

1. Copy `templates/fastapi-project/` into a new project repository.
2. Add the pinned `server-platform` dependency to that project's `pyproject.toml` and install the project dependencies.
3. Add project-owned routers under the new project's `app/api/` and pass them to `create_app(routers=[...])`.
4. Add project-owned authorization, data models, tests and CI.
5. Configure a unique `APP_NAME`, allowed hosts, CORS origins and service credentials.
6. Deploy a separate Render service using the starter Dockerfile/Blueprint as a reference.

The platform deliberately does not require MongoDB or Firebase just to start. Enable integrations with environment variables.

## Configuration

See [`.env.example`](.env.example). Never commit real credentials.

Important variables:

- `APP_NAME`: service display name.
- `APP_ENV`: development, test, or production.
- `API_ALLOWED_HOSTS`: comma-separated hostnames; include the Render hostname and custom domain.
- `CORS_ALLOWED_ORIGINS`: comma-separated exact origins.
- `MONGODB_URI` and `MONGODB_DATABASE`: optional MongoDB integration. Use a database-specific, least-privilege Atlas user per project.
- `MONGODB_SERVER_SELECTION_TIMEOUT_MS`: maximum time to wait for server selection.
- `MONGODB_CONNECT_TIMEOUT_MS`: maximum time to establish an individual socket connection.
- `FIREBASE_SERVICE_ACCOUNT_JSON`: optional Firebase Admin service-account JSON for this project's Firebase project.
- `AUTH_REQUIRE_VERIFIED_EMAIL`: whether Firebase users must have verified email.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`: optional SMTP transport.

## MongoDB usage

```python
from server_platform.database.mongo import get_collection, get_database

db = get_database()
users = get_collection("users")
```

The client is lazy and cached for the process. The URI helper validates the MongoDB scheme and host, removes empty query options, and adds `retryWrites=true` only when it is not already explicitly configured. Separate server-selection and socket-connect timeouts are configurable. The application lifespan closes the cached client at shutdown. `/readyz` pings MongoDB only when `MONGODB_URI` is configured. A missing optional integration does not prevent local startup.

## Firebase usage

```python
from fastapi import APIRouter, Depends
from server_platform.auth.firebase import require_authenticated_user

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

## Existing Dautu adoption

See [the staged Dautu adoption plan](docs/dautu-adoption-plan.md) for the audited boundary between shared infrastructure and Dautu-specific authentication, data, API, and investment logic. A package release does not itself authorize changing Dautu's production runtime.
