"""Automated backordering module."""

from __future__ import annotations

from lucas_project.core import get_db, get_logger, register_job

logger = get_logger(__name__)


@register_job(trigger="cron", hour=0)
async def run() -> None:
    """Place backorders for monitored domains."""
    async with get_db() as db:
        async with db.execute(
            "SELECT id FROM domains WHERE status = 'monitoring'"
        ) as cursor:
            domains = await cursor.fetchall()
        for row in domains:
            await db.execute(
                "INSERT INTO backorders (domain_id, provider) VALUES (?, ?)",
                (row["id"], "NoWinNoFee"),
            )
            await db.execute(
                "UPDATE domains SET status = 'backordered' WHERE id = ?",
                (row["id"],),
            )
        await db.commit()
        logger.info("Backordered %d domains", len(domains))
