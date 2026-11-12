# New project starter

Copy this directory's structure into a new project repository, then:

1. Install the shared platform requirements from the platform repository (or pin a released package once published).
2. Add your project's routers under `app/api/`.
3. Add project-owned authorization and data models.
4. Set a unique `APP_NAME`, allowed hosts, CORS origins, database, Firebase project, and SMTP sender.
5. Add a project-specific `render.yaml` and CI tests.

Do not share production database credentials, Firebase service accounts, admin identities, or email credentials between projects.
