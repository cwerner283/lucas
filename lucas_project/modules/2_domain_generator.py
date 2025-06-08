"""Domain generator module."""

from __future__ import annotations

import asyncio
from typing import Iterable

from lucas_project.core import get_logger, register_job

logger = get_logger(__name__)


def generate_domains(trends: Iterable[str]) -> list[str]:
    """Generate candidate domain names from trending phrases."""

    return [f"{trend.replace(' ', '')}.com" for trend in trends]


@register_job(trigger="interval", minutes=60)
async def run() -> None:
    """Generate domains using discovered trends."""

    await asyncio.sleep(0)
    trends = ["example"]
    domains = generate_domains(trends)
    logger.info("Generated domains: %s", domains)

