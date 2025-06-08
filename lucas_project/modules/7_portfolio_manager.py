"""Manage owned domains and export portfolio."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from lucas_project.core import get_db, get_logger, register_job

logger = get_logger(__name__)


def _export_csv(rows: list[tuple[str, float]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["domain", "estimated_value"])
        writer.writerows(rows)


@register_job(trigger="cron", day_of_week="sun", hour=0)
async def run() -> None:
    """Export portfolio of owned domains."""
    async with get_db() as db:
        async with db.execute(
            "SELECT domain, value FROM domains d JOIN valuations v ON d.id = v.domain_id WHERE d.status = 'owned'"
        ) as cursor:
            rows = await cursor.fetchall()
        today = date.today().isoformat()
        out_path = Path(f"lucas_project/data/portfolio_{today}.csv")
        _export_csv([(r["domain"], r["value"]) for r in rows], out_path)
        logger.info("Exported portfolio to %s", out_path)
