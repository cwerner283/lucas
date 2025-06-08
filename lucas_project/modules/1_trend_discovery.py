"""Trend discovery module."""

from __future__ import annotations

import asyncio

from lucas_project.core import get_logger, register_job

logger = get_logger(__name__)


async def fetch_trends() -> list[str]:
    """Return a list of trending search phrases."""

    await asyncio.sleep(0)  # simulate I/O
    return ["ai", "chatgpt", "quantum computing"]


@register_job(trigger="interval", minutes=60)
async def run() -> None:
    """Periodic task that fetches and logs trending phrases."""

    trends = await fetch_trends()
    logger.info("Discovered trends: %s", trends)
