"""Async database helpers using :mod:`aiosqlite`."""

from __future__ import annotations

from contextlib import asynccontextmanager

import aiosqlite

from .config import get_settings


@asynccontextmanager
async def get_db() -> aiosqlite.Connection:
    """Yield an aiosqlite connection configured with row factory."""

    settings = get_settings()
    db = await aiosqlite.connect(settings.database_url)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
