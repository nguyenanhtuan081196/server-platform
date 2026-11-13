"""Identity verification helpers. Membership and roles remain project-owned."""

from app.auth.firebase import require_authenticated_user, verify_firebase_token

__all__ = ["require_authenticated_user", "verify_firebase_token"]
