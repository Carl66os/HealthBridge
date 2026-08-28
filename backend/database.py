from collections.abc import Generator
from os import getenv

from sqlalchemy import URL, create_engine, make_url
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def obtener_database_url() -> str | URL:
    """Devuelve la URL temporal indicada o construye la conexión PostgreSQL normal."""
    if url_temporal := getenv("DATABASE_URL"):
        return url_temporal

    from backend.config import settings

    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


def crear_engine(database_url: str | URL) -> Engine:
    """Crea un engine compatible con PostgreSQL y SQLite local."""
    opciones: dict[str, object] = {"pool_pre_ping": True}
    if make_url(database_url).get_backend_name() == "sqlite":
        opciones["connect_args"] = {"check_same_thread": False}

    return create_engine(database_url, **opciones)


database_url = obtener_database_url()
engine = crear_engine(database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
