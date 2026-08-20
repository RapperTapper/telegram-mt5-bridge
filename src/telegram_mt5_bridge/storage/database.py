from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from telegram_mt5_bridge.storage.models import Base


def create_sqlite_engine(database_path: Path) -> Engine:
    """Create a SQLite engine for the local message database."""

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    database_url = URL.create(
        "sqlite",
        database=str(database_path),
    )

    engine = create_engine(
        database_url,
    )

    @event.listens_for(engine, "connect")
    def configure_sqlite(
        dbapi_connection: object,
        _connection_record: object,
    ) -> None:
        cursor = dbapi_connection.cursor()

        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")

        cursor.close()

    return engine


def create_session_factory(
    engine: Engine,
) -> sessionmaker[Session]:
    """Create a SQLAlchemy session factory."""

    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )


def init_database(engine: Engine) -> None:
    """Create database tables that do not yet exist."""

    Base.metadata.create_all(engine)


def checkpoint_database(engine: Engine) -> None:
    """Flush SQLite WAL data into the main database file."""

    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA wal_checkpoint(TRUNCATE)")
