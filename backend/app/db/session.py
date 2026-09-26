"""SQLAlchemy engine/session with SQLite WAL + FK enforcement."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core import config


class Base(DeclarativeBase):
    pass


def _sqlite_url(url: str) -> bool:
    return url.startswith("sqlite")


connect_args = {"check_same_thread": False} if _sqlite_url(config.DATABASE_URL) else {}
engine = create_engine(config.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)


@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_connection, _connection_record):  # pragma: no cover - driver hook
    if _sqlite_url(config.DATABASE_URL):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
