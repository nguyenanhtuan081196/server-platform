# New project starter

This directory is the project-specific entry-point template. To create a working project:

1. Copy this template into a new project repository.
2. Copy the platform root `app/` package and `requirements.txt` from the Server Platform repository into that project (the template entry point imports `create_app` from the platform package).
3. Add your project's routers under `app/api/` and pass them to `create_app(routers=[...])`.
4. Add project-owned authorization, data models, tests and CI.
5. Configure a unique `APP_NAME`, allowed hosts, CORS origins and service credentials.
6. Deploy a separate Render service for this project.

## MongoDB

Create a database and a least-privilege MongoDB Atlas database user for this project. Set its own `MONGODB_URI` and `MONGODB_DATABASE` in the project's Render environment. A shared Atlas cluster is acceptable initially if database permissions prevent cross-project access; separate clusters provide stronger isolation.

## Firebase

Create a new Firebase project for this application. Enable only the required products, configure its own Authentication providers and Firestore Security Rules, then create a dedicated service account for backend verification. Set its JSON in `FIREBASE_SERVICE_ACCOUNT_JSON` in this project's secret environment. Do not reuse Dautu's Firebase project or service account.

## SMTP and secrets

Use a separate sender identity or credential where practical. Keep all secrets in the project's secret store, never in Git. Do not share production database credentials, Firebase service accounts, admin identities, or email credentials between projects.

The shared Firebase helper verifies identity only. Implement this project's membership and admin-role checks in this project.
