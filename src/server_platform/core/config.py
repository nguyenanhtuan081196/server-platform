"""Small dependency-free environment configuration layer."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _csv_env(name: str, default: str = "") -> tuple[str, ...]:
    return tuple(part.strip() for part in os.getenv(name, default).split(",") if part.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    log_level: str
    allowed_hosts: tuple[str, ...]
    cors_allowed_origins: tuple[str, ...]
    mongodb_uri: str
    mongodb_database: str
    mongodb_server_selection_timeout_ms: int
    mongodb_connect_timeout_ms: int
    firebase_service_account_json: str
    auth_require_verified_email: bool
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_from_email: str
    smtp_use_starttls: bool

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Backend API").strip() or "Backend API",
        app_env=os.getenv("APP_ENV", "development").strip() or "development",
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        allowed_hosts=_csv_env("API_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver"),
        cors_allowed_origins=_csv_env("CORS_ALLOWED_ORIGINS"),
        mongodb_uri=os.getenv("MONGODB_URI", "").strip(),
        mongodb_database=os.getenv("MONGODB_DATABASE", "app").strip() or "app",
        mongodb_server_selection_timeout_ms=int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000")),
        mongodb_connect_timeout_ms=int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "5000")),
        firebase_service_account_json=os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip(),
        auth_require_verified_email=os.getenv("AUTH_REQUIRE_VERIFIED_EMAIL", "true").lower() in {"1", "true", "yes", "on"},
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com").strip(),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", "").strip(),
        smtp_password=os.getenv("SMTP_PASSWORD", "").strip(),
        smtp_from_email=os.getenv("SMTP_FROM_EMAIL", "").strip(),
        smtp_use_starttls=os.getenv("SMTP_USE_STARTTLS", "true").lower() in {"1", "true", "yes", "on"},
    )
