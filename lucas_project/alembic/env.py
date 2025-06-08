from __future__ import annotations

from logging.config import fileConfig

from alembic import context

from lucas_project.core.config import get_settings
from lucas_project.core.models import Base
from lucas_project.core.db import get_engine

config = context.config
fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    url = f"sqlite:///{get_settings().database_url}"
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

