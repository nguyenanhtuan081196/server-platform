import os
import unittest
from unittest.mock import MagicMock, patch

from fastapi import APIRouter, HTTPException
from fastapi.testclient import TestClient


class PlatformTests(unittest.TestCase):
    def setUp(self):
        from app.core.config import get_settings
        get_settings.cache_clear()

    def tearDown(self):
        from app.core.config import get_settings
        get_settings.cache_clear()
        from app.database.mongo import get_client
        get_client.cache_clear()

    def test_settings_defaults_are_safe_for_local_start(self):
        with patch.dict(os.environ, {}, clear=True):
            from app.core.config import get_settings
            settings = get_settings()
            self.assertEqual(settings.app_name, "Backend API")
            self.assertEqual(settings.mongodb_uri, "")
            self.assertTrue(settings.auth_require_verified_email)

    def test_liveness_does_not_require_database_or_credentials(self):
        with patch.dict(os.environ, {"API_ALLOWED_HOSTS": "testserver"}, clear=True):
            from app.core.config import get_settings
            get_settings.cache_clear()
            from app.main import create_app
            client = TestClient(create_app())
            response = client.get("/healthz")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "ok"})

    def test_project_router_can_be_injected(self):
        with patch.dict(os.environ, {"API_ALLOWED_HOSTS": "testserver"}, clear=True):
            from app.core.config import get_settings
            get_settings.cache_clear()
            router = APIRouter()

            @router.get("/project-check")
            def project_check():
                return {"project": "injected"}

            from app.main import create_app
            response = TestClient(create_app(routers=[router])).get("/project-check")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"project": "injected"})

    def test_database_is_optional(self):
        with patch.dict(os.environ, {}, clear=True):
            from app.core.config import get_settings
            get_settings.cache_clear()
            from app.database.mongo import get_database
            with self.assertRaisesRegex(RuntimeError, "MONGODB_URI"):
                get_database()

    def test_database_uses_configured_project_database(self):
        with patch.dict(os.environ, {
            "MONGODB_URI": "mongodb://example.invalid:27017",
            "MONGODB_DATABASE": "isolated_project_db",
        }, clear=True):
            from app.core.config import get_settings
            get_settings.cache_clear()
            from app.database.mongo import get_database
            fake_client = MagicMock()
            fake_database = object()
            fake_client.__getitem__.return_value = fake_database
            with patch("app.database.mongo.get_client", return_value=fake_client):
                self.assertIs(get_database(), fake_database)
            fake_client.__getitem__.assert_called_once_with("isolated_project_db")

    def test_readiness_does_not_require_optional_mongodb(self):
        with patch.dict(os.environ, {"API_ALLOWED_HOSTS": "testserver"}, clear=True):
            from app.core.config import get_settings
            get_settings.cache_clear()
            from app.main import create_app
            response = TestClient(create_app()).get("/readyz")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "ready"})

    def test_readiness_fails_closed_when_configured_mongodb_is_unavailable(self):
        with patch.dict(os.environ, {
            "API_ALLOWED_HOSTS": "testserver",
            "MONGODB_URI": "mongodb://example.invalid:27017",
        }, clear=True):
            from app.core.config import get_settings
            get_settings.cache_clear()
            from app.main import create_app
            with patch("app.health.ping_database", side_effect=TimeoutError()):
                response = TestClient(create_app()).get("/readyz")
            self.assertEqual(response.status_code, 503)

    def test_firebase_auth_requires_bearer_token(self):
        from app.auth.firebase import require_authenticated_user
        with self.assertRaises(HTTPException) as raised:
            require_authenticated_user(authorization=None)
        self.assertEqual(raised.exception.status_code, 401)

    def test_firebase_verified_email_policy_is_enforced(self):
        with patch.dict(os.environ, {"AUTH_REQUIRE_VERIFIED_EMAIL": "true"}, clear=True):
            from app.core.config import get_settings
            get_settings.cache_clear()
            from app.auth.firebase import verify_firebase_token
            with patch("firebase_admin.auth.verify_id_token", return_value={
                "uid": "user-123", "email_verified": False
            }):
                with patch("app.auth.firebase._firebase_app", return_value=object()):
                    with self.assertRaises(HTTPException) as raised:
                        verify_firebase_token("fake-token")
            self.assertEqual(raised.exception.status_code, 403)

    def test_firebase_identity_returns_claims_without_project_role_assumptions(self):
        with patch.dict(os.environ, {"AUTH_REQUIRE_VERIFIED_EMAIL": "true"}, clear=True):
            from app.core.config import get_settings
            get_settings.cache_clear()
            from app.auth.firebase import verify_firebase_token
            claims = {"uid": "user-123", "email_verified": True}
            with patch("firebase_admin.auth.verify_id_token", return_value=claims):
                with patch("app.auth.firebase._firebase_app", return_value=object()):
                    self.assertEqual(verify_firebase_token("fake-token"), claims)


if __name__ == "__main__":
    unittest.main()
