import os
import unittest
from unittest.mock import patch

from fastapi import APIRouter
from fastapi.testclient import TestClient


class PlatformTests(unittest.TestCase):
    def setUp(self):
        from app.core.config import get_settings
        get_settings.cache_clear()

    def tearDown(self):
        from app.core.config import get_settings
        get_settings.cache_clear()

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


if __name__ == "__main__":
    unittest.main()
