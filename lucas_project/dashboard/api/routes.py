"""Dashboard API routes."""

from __future__ import annotations

from fastapi import APIRouter

from lucas_project.core import get_db

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}


@router.get("/kpis")
async def kpis() -> dict[str, int]:
    """Return simple KPIs from the database."""
    async with get_db() as db:
        async with db.execute("SELECT COUNT(*) FROM domains") as cursor:
            row = await cursor.fetchone()
            domains = row[0] if row else 0
    return {"domains": domains, "revenue": 0}


@router.get("/finance")
async def finance() -> dict[str, float]:
    """Return finance metrics."""
    async with get_db() as db:
        async with db.execute(
            "SELECT SUM(value) FROM valuations"
        ) as cursor:
            row = await cursor.fetchone()
            value = row[0] if row and row[0] is not None else 0.0
    return {"profit": float(value)}


@router.get("/domains")
async def domains() -> list[str]:
    """Return managed domains."""
    async with get_db() as db:
        async with db.execute("SELECT domain FROM domains") as cursor:
            rows = await cursor.fetchall()
    return [r["domain"] for r in rows]
