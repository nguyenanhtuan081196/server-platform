"""Optional lazy MongoDB integration; importing the platform needs no DB."""
from __future__ import annotations

from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    settings = get_settings()
    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is not configured")
    return MongoClient(
        settings.mongodb_uri,
        appname=settings.app_name,
        serverSelectionTimeoutMS=settings.mongodb_server_selection_timeout_ms,
        connectTimeoutMS=settings.mongodb_server_selection_timeout_ms,
    )


def get_database() -> Database:
    settings = get_settings()
    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is not configured")
    return get_client()[settings.mongodb_database]


def ping_database() -> bool:
    get_client().admin.command("ping")
    return True


def close_client() -> None:
    if get_client.cache_info().currsize:
        get_client().close()
        get_client.cache_clear()
