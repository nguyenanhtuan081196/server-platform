"""Example consuming-project entry point."""
from fastapi import APIRouter

from app.main import create_app

api = APIRouter(prefix="/api")


@api.get("/example")
def example():
    return {"project": "replace-me", "status": "ok"}


app = create_app(routers=[api], title="New Project API")
