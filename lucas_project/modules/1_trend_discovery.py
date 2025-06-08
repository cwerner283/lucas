"""Trend discovery module."""

from __future__ import annotations

import httpx

from lucas_project.core import (
    get_db,
    get_logger,
    get_settings,
    rate_limiter,
    register_job,
    retry,
    circuit_breaker,
)

logger = get_logger(__name__)


@retry(3, backoff=1.0)
@circuit_breaker(5, 60)
@rate_limiter(max_calls=5, period=60.0)
async def fetch_trends() -> list[str]:
    """Fetch trending repository names from GitHub."""

    settings = get_settings()
    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"
    url = (
        "https://api.github.com/search/repositories?q=stars:%3E50000&sort=stars&"
        "order=desc&per_page=5"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    return [item["name"] for item in data.get("items", [])]


@register_job(trigger="interval", minutes=60)
async def run() -> None:
    """Periodic task that fetches and stores trending phrases."""

    trends = await fetch_trends()
    async with get_db() as db:
        for phrase in trends:
            await db.execute(
                "INSERT OR IGNORE INTO trend_seeds (phrase) VALUES (?)",
                (phrase,),
            )
        await db.commit()
    logger.info("Discovered trends: %s", trends)
