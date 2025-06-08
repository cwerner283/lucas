"""Domain valuation module with caching."""

from __future__ import annotations

import asyncio

from lucas_project.core import LLMCache, get_db, get_logger, register_job

logger = get_logger(__name__)
cache = LLMCache()


async def fetch_estibot(domain: str) -> float:
    await asyncio.sleep(0)
    return 100.0


async def fetch_humbleworth(domain: str) -> float:
    await asyncio.sleep(0)
    return 80.0


async def fetch_godaddy(domain: str) -> float:
    await asyncio.sleep(0)
    return 60.0


SERVICE_FUNCS = {
    "EstiBot": fetch_estibot,
    "HumbleWorth": fetch_humbleworth,
    "GoDaddy": fetch_godaddy,
}


@register_job(trigger="interval", minutes=120)
async def run() -> None:
    """Value available domains using external services."""
    async with get_db() as db:
        async with db.execute("SELECT id, domain FROM domains WHERE status = 'available'") as cursor:
            rows = await cursor.fetchall()
        for row in rows:
            for service, func in SERVICE_FUNCS.items():
                key = f"valuation:{service}:{row['domain']}"
                value = cache.lookup(key)
                if value is None:
                    value = await func(row["domain"])
                    cache.store(key, value)
                await db.execute(
                    "INSERT INTO valuations (domain_id, service, value) VALUES (?, ?, ?)",
                    (row["id"], service, value),
                )
            await db.execute(
                "UPDATE domains SET status = 'valuated' WHERE id = ?",
                (row["id"],),
            )
        await db.commit()
        logger.info("Valuated %d domains", len(rows))
