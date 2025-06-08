"""Domain generator module."""

from __future__ import annotations

from typing import Iterable

from lucas_project.core import get_db, get_logger, register_job
from datetime import datetime, UTC

logger = get_logger(__name__)


def generate_domains(trends: Iterable[str]) -> list[str]:
    """Generate candidate domain names from trending phrases."""

    return [f"{trend.replace(' ', '')}.com" for trend in trends]


@register_job(trigger="interval", minutes=60)
async def run() -> None:
    """Generate domains using discovered trends."""

    async with get_db() as db:
        async with db.execute("SELECT id, phrase FROM trend_seeds") as cursor:
            seeds = await cursor.fetchall()
        for seed in seeds:
            domains = generate_domains([seed["phrase"]])
            for domain in domains:
                await db.execute(
                    "INSERT OR IGNORE INTO domains (domain, trend_seed_id, status, created_at) VALUES (?, ?, ?, ?)",
                    (domain, seed["id"], "new", datetime.now(UTC)),
                )
        await db.commit()
        logger.info("Generated domains for %d seeds", len(seeds))

