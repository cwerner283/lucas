"""Dashboard API routes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}


@router.get("/kpis")
async def kpis() -> dict[str, int]:
    """Return placeholder KPIs."""
    return {"domains": 0, "revenue": 0}


@router.get("/finance")
async def finance() -> dict[str, float]:
    """Return finance metrics."""
    return {"profit": 0.0}


@router.get("/domains")
async def domains() -> list[str]:
    """Return managed domains."""
    return []
