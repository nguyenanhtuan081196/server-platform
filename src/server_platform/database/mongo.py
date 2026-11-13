"""Optional MongoDB integration with one isolated database per app deployment.

Configure MONGODB_URI and MONGODB_DATABASE separately for every consuming project.
The client is lazy: importing or starting an app does not require MongoDB credentials.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pymongo import MongoClient
from pymongo.database import Database

from server_platform.core.config import get_settings


def normalize_mongodb_uri(uri: str) -> str:
    """Validate the URI scheme, remove empty options, and ensure retryWrites."""
    parts = urlsplit(uri.strip())
    if parts.scheme not in {"mongodb", "mongodb+srv"}:
        raise ValueError("MONGODB_URI must start with mongodb:// or mongodb+srv://")
    if not parts.netloc:
        raise ValueError("MONGODB_URI must include a MongoDB host")
    pairs = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key.strip()]
    options = {key.lower(): index for index, (key, _) in enumerate(pairs)}
    retry_index = options.get("retrywrites")
    if retry_index is None:
        pairs.append(("retryWrites", "true"))
    else:
        key, value = pairs[retry_index]
        if not value.strip():
            pairs[retry_index] = (key, "true")
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(pairs), parts.fragment))


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    settings = get_settings()
    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is not configured")
    return MongoClient(
        normalize_mongodb_uri(settings.mongodb_uri),
        appname=settings.app_name,
        serverSelectionTimeoutMS=settings.mongodb_server_selection_timeout_ms,
        connectTimeoutMS=settings.mongodb_connect_timeout_ms,
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
    """Close the cached client and clear it even if close raises."""
    if not get_client.cache_info().currsize:
        return
    client = get_client()
    try:
        client.close()
    finally:
        get_client.cache_clear()
