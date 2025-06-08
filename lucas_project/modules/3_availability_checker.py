"""Check domain availability respecting rate limits."""

from __future__ import annotations

import asyncio

from lucas_project.core import get_db, get_logger, rate_limiter, register_job

logger = get_logger(__name__)


@rate_limiter(max_calls=5, period=1.0)
async def check_domain_availability(domain: str) -> bool:
    """Simulate a WHOIS call returning availability."""
    await asyncio.sleep(0)
    return True


@register_job(trigger="interval", minutes=60)
async def run() -> None:
    """Check new domains for availability and record results."""
    async with get_db() as db:
        async with db.execute("SELECT id, domain FROM domains WHERE status = 'new'") as cursor:
            rows = await cursor.fetchall()
        for row in rows:
            available = await check_domain_availability(row["domain"])
            await db.execute(
                "INSERT INTO availability_checks (domain_id, available) VALUES (?, ?)",
                (row["id"], available),
            )
            status = "available" if available else "taken"
            await db.execute(
                "UPDATE domains SET status = ? WHERE id = ?",
                (status, row["id"]),
            )
        await db.commit()
        logger.info("Checked availability for %d domains", len(rows))
