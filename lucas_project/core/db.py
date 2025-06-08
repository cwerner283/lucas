"""Async database helpers using :mod:`aiosqlite`."""

from __future__ import annotations

from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

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


def get_engine() -> Engine:
    """Return a synchronous SQLAlchemy engine for migrations."""

    settings = get_settings()
    return create_engine(f"sqlite:///{settings.database_url}")
