import os
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from lucas_project.core.config import get_settings
from lucas_project.core.models import Base
from lucas_project.core.db import get_engine, get_db

trend = importlib.import_module('lucas_project.modules.1_trend_discovery')
gen = importlib.import_module('lucas_project.modules.2_domain_generator')


@pytest.mark.asyncio
async def test_trend_to_domain_flow(tmp_path):
    os.environ['LUCAS_DATABASE_URL'] = str(tmp_path / 'test.db')
    get_settings.cache_clear()
    engine = get_engine()
    Base.metadata.create_all(engine)

    async def fake_fetch_trends():
        return ['example trend']

    trend.fetch_trends = fake_fetch_trends
    await trend.run()

    async with get_db() as db:
        async with db.execute('SELECT phrase FROM trend_seeds') as cur:
            seeds = await cur.fetchall()
    assert [s['phrase'] for s in seeds] == ['example trend']

    await gen.run()

    async with get_db() as db:
        async with db.execute('SELECT domain FROM domains') as cur:
            domains = await cur.fetchall()
    assert [d['domain'] for d in domains] == ['exampletrend.com']
