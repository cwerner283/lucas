"""Async database helpers using :mod:`aiosqlite`."""

from __future__ import annotations

from contextlib import asynccontextmanager
import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

import aiosqlite

from .config import get_settings


@asynccontextmanager
async def get_db() -> aiosqlite.Connection:
    """Yield an aiosqlite connection configured with row factory."""

    settings = get_settings()
    db = await aiosqlite.connect(
        settings.database_url,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


def get_engine() -> Engine:
    """Return a synchronous SQLAlchemy engine for migrations."""

    settings = get_settings()
    return create_engine(f"sqlite:///{settings.database_url}")
