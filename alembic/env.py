import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config.settings import settings
from app.database.base import Base
from app.models import ticket  # noqa: F401 to register models

# this is the Alembic Config object, which provides access to the values within the .ini file.
config = context.config
fileConfig(config.config_file_name)

def _resolve_sync_database_url(database_url: str) -> str:
    if "+aiosqlite" in database_url:
        return database_url.replace("+aiosqlite", "")
    if "+asyncpg" in database_url:
        return database_url.replace("+asyncpg", "")
    return database_url

# Set the SQLAlchemy URL from environment or config.
config.set_main_option("sqlalchemy.url", _resolve_sync_database_url(settings.database_url))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
