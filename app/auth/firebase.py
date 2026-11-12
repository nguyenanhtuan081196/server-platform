"""Optional Firebase ID-token verification.

This module verifies identity only. Each consuming project must implement its own
membership, role, tenant, and subscription authorization policy. Use a dedicated
Firebase project and service account for each deployed application.
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from fastapi import Header, HTTPException

from app.core.config import get_settings


@lru_cache(maxsize=1)
def _firebase_app():
    import firebase_admin
    from firebase_admin import credentials

    raw = get_settings().firebase_service_account_json
    if not raw:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not configured")
    try:
        service_account = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON must contain valid JSON") from exc

    if not isinstance(service_account, dict) or not service_account.get("project_id"):
        raise RuntimeError("Firebase service-account JSON must include project_id")

    # A consuming app uses its own dedicated Firebase project. Do not silently
    # reuse a default app initialized with another project's credentials.
    try:
        app = firebase_admin.get_app()
    except ValueError:
        app = firebase_admin.initialize_app(credentials.Certificate(service_account))
    configured_project = service_account["project_id"]
    actual_project = getattr(app, "project_id", None)
    if actual_project and actual_project != configured_project:
        raise RuntimeError("Initialized Firebase app does not match configured project_id")
    return app


def verify_firebase_token(token: str) -> dict[str, Any]:
    from firebase_admin import auth

    try:
        claims = auth.verify_id_token(token, app=_firebase_app(), check_revoked=True)
    except RuntimeError:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired identity token") from exc

    if get_settings().auth_require_verified_email and claims.get("email_verified") is not True:
        raise HTTPException(status_code=403, detail="Email verification is required")
    return claims


def require_authenticated_user(
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        return verify_firebase_token(token)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication service unavailable") from exc
