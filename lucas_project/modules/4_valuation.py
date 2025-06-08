"""Domain valuation module with caching."""

from __future__ import annotations

import asyncio
import httpx

from lucas_project.core import (
    LLMCache,
    get_db,
    get_logger,
    register_job,
    rate_limiter,
    retry,
    circuit_breaker,
    get_settings,
)

logger = get_logger(__name__)
cache = LLMCache()


@retry(3, backoff=1.0)
@circuit_breaker(5, 60)
@rate_limiter(max_calls=5, period=1.0)
async def fetch_estibot(domain: str) -> float:
    await asyncio.sleep(0)
    return 100.0


@retry(3, backoff=1.0)
@circuit_breaker(5, 60)
@rate_limiter(max_calls=5, period=1.0)
async def fetch_humbleworth(domain: str) -> float:
    settings = get_settings()
    url = "https://valuation.humbleworth.com/api/valuation"
    payload = {"domains": [domain]}
    headers = {"Content-Type": "application/json"}
    if settings.humbleworth_api_key:
        headers["Authorization"] = settings.humbleworth_api_key
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    valuations = data.get("valuations", [])
    if valuations:
        val = valuations[0]
        return float(val.get("marketplace", 0))
    return 0.0


@retry(3, backoff=1.0)
@circuit_breaker(5, 60)
@rate_limiter(max_calls=5, period=1.0)
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
        async with db.execute(
            "SELECT id, domain FROM domains WHERE status = 'available'"
        ) as cursor:
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
