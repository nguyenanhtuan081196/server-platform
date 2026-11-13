"""FastAPI application factory used by consuming projects."""
from collections.abc import Sequence
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from server_platform.core.config import get_settings
from server_platform.core.logging import configure_logging
from server_platform.database.mongo import close_client
from server_platform.health import router as health_router
from server_platform.middleware import install_middleware


def create_app(
    *,
    routers: Sequence[APIRouter] = (),
    title: str | None = None,
    version: str = "1.0.0",
) -> FastAPI:
    configure_logging()
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        close_client()

    application = FastAPI(
        title=title or settings.app_name,
        version=version,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )
    install_middleware(application)
    application.include_router(health_router)
    for router in routers:
        application.include_router(router)
    return application


app = create_app()
