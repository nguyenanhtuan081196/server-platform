"""Optional MongoDB integration with one isolated database per app deployment.

Configure MONGODB_URI and MONGODB_DATABASE separately for every consuming project.
The client is lazy: importing or starting an app does not require MongoDB credentials.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

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
        retryWrites=True,
    )


def get_database() -> Database:
    settings = get_settings()
    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is not configured")
    if not settings.mongodb_database:
        raise RuntimeError("MONGODB_DATABASE is not configured")
    return get_client()[settings.mongodb_database]


def get_collection(name: str) -> Any:
    """Return a collection from this deployment's configured database."""
    if not name or name.startswith("$") or "\x00" in name:
        raise ValueError("A valid MongoDB collection name is required")
    return get_database()[name]


def ping_database() -> bool:
    get_client().admin.command("ping")
    return True


def close_client() -> None:
    """Close the cached client during application shutdown, if it was created."""
    if get_client.cache_info().currsize:
        get_client().close()
        get_client.cache_clear()
