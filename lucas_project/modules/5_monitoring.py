"""Monitor expiring domains and enforce free-tier limits."""

from __future__ import annotations

from lucas_project.core import (
    get_db,
    get_logger,
    register_job,
    rate_limiter,
    retry,
    circuit_breaker,
)

logger = get_logger(__name__)

UPTIME_ROBOT_CAP = 50
FREE_DOMAIN_ALERTS_CAP = 20


async def _count_monitors(db, service: str) -> int:
    async with db.execute(
        "SELECT COUNT(*) FROM monitors WHERE service = ?",
        (service,),
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else 0


async def _drop_lowest_value(db, service: str) -> None:
    query = (
        "SELECT m.id FROM monitors m "
        "JOIN valuations v ON m.domain_id = v.domain_id "
        "WHERE m.service = ? ORDER BY v.value ASC LIMIT 1"
    )
    async with db.execute(query, (service,)) as cursor:
        row = await cursor.fetchone()
    if row:
        await db.execute("DELETE FROM monitors WHERE id = ?", (row[0],))


@retry(3, backoff=1.0)
@circuit_breaker(5, 60)
@rate_limiter(max_calls=5, period=1.0)
async def _add_monitor(db, domain_id: int, service: str) -> None:
    cap = UPTIME_ROBOT_CAP if service == "UptimeRobot" else FREE_DOMAIN_ALERTS_CAP
    if await _count_monitors(db, service) >= cap:
        await _drop_lowest_value(db, service)
    await db.execute(
        "INSERT INTO monitors (domain_id, service, monitor_ref) VALUES (?, ?, ?)",
        (domain_id, service, f"{service}-{domain_id}"),
    )


@register_job(trigger="interval", minutes=1440)
async def run() -> None:
    """Add monitors for valuated domains within free-tier caps."""
    async with get_db() as db:
        async with db.execute(
            "SELECT id FROM domains WHERE status = 'valuated'"
        ) as cursor:
            domains = await cursor.fetchall()
        for row in domains:
            await _add_monitor(db, row["id"], "UptimeRobot")
            await _add_monitor(db, row["id"], "FreeDomainAlerts")
            await db.execute(
                "UPDATE domains SET status = 'monitoring' WHERE id = ?",
                (row["id"],),
            )
        await db.commit()
        logger.info("Monitoring %d domains", len(domains))
