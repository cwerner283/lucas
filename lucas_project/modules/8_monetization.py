"""Push domains to marketplaces for sale."""

from __future__ import annotations

from pathlib import Path

from lucas_project.core import get_db, get_logger, register_job

logger = get_logger(__name__)


def _sedo_csv_row(domain: str, price: float) -> str:
    return f"{domain},{price},USD"


@register_job(trigger="cron", day_of_week="mon", hour=1)
async def run() -> None:
    """Upload domains to marketplaces and update listings."""
    async with get_db() as db:
        async with db.execute(
            "SELECT d.id, d.domain, v.value FROM domains d JOIN valuations v ON d.id = v.domain_id WHERE d.status = 'backordered'"
        ) as cursor:
            rows = await cursor.fetchall()
        sedo_rows = []
        for row in rows:
            sedo_rows.append(_sedo_csv_row(row["domain"], row["value"]))
            await db.execute(
                "INSERT INTO listings (domain_id, marketplace, url, status) VALUES (?, ?, ?, ?)",
                (row["id"], "Sedo", None, "listed"),
            )
        if sedo_rows:
            csv_path = Path("lucas_project/data/sedo_upload.csv")
            csv_path.write_text("\n".join(sedo_rows), encoding="utf-8")
        await db.commit()
        logger.info("Listed %d domains", len(rows))
