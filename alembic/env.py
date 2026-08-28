from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

import backend.orm_models
from backend.database import Base, database_url, engine


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def obtener_url_migracion() -> str:
    """Usa una URL explícita de Alembic cuando una herramienta la proporciona."""
    url_configurada = config.get_main_option("sqlalchemy.url")
    if url_configurada and url_configurada != "postgresql+psycopg://":
        return url_configurada

    return database_url.render_as_string(hide_password=False)


def run_migrations_offline() -> None:
    context.configure(
        url=obtener_url_migracion(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url_configurada = config.get_main_option("sqlalchemy.url")
    motor_migracion = (
        create_engine(url_configurada)
        if url_configurada and url_configurada != "postgresql+psycopg://"
        else engine
    )

    with motor_migracion.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
