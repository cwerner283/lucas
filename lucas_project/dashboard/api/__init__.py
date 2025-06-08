"""FastAPI router setup for dashboard."""

from fastapi import APIRouter, FastAPI

from .routes import router as dashboard_router


def init_app(app: FastAPI) -> None:
    """Include dashboard routes in ``app``."""
    api_router = APIRouter(prefix="/api")
    api_router.include_router(dashboard_router)
    app.include_router(api_router)
