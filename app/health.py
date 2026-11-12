"""Standard liveness and readiness endpoints."""
import logging

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.database.mongo import ping_database

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", tags=["health"])
def readyz() -> dict[str, str]:
    if get_settings().mongodb_uri:
        try:
            ping_database()
        except Exception as exc:
            logger.warning("Readiness check failed for configured database: %s", type(exc).__name__)
            raise HTTPException(status_code=503, detail="Service not ready") from exc
    return {"status": "ready"}
