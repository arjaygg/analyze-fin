"""
Database session and engine configuration for analyze-fin.

Provides:
- get_engine: Create SQLAlchemy engine with WAL mode enabled
- get_session: Create database session with automatic cleanup
- init_db: Initialize database schema

SQLite Configuration:
- WAL mode enabled for crash recovery and concurrent reads
- Foreign key constraints enforced
"""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from analyze_fin.database.models import Base

# Default database path
DEFAULT_DB_PATH = "data/analyze-fin.db"


def get_engine(db_path: str | None = None, echo: bool = False) -> Engine:
    """Create SQLAlchemy engine with WAL mode enabled.

    Args:
        db_path: Path to SQLite database file. Defaults to DEFAULT_DB_PATH.
        echo: If True, log all SQL statements.

    Returns:
        Configured SQLAlchemy Engine with WAL mode and foreign keys enabled.
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH

    # Ensure parent directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # Create engine with SQLite-specific settings
    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=echo,
        connect_args={"check_same_thread": False},
    )

    # Configure SQLite pragmas on every connection
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set SQLite pragmas for performance and data integrity."""
        cursor = dbapi_connection.cursor()
        # Enable WAL mode for crash recovery and concurrent reads
        cursor.execute("PRAGMA journal_mode=WAL")
        # Enable foreign key constraint enforcement
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def get_session(engine: Engine | None = None) -> Generator[Session, None, None]:
    """Create database session with automatic cleanup.

    Args:
        engine: SQLAlchemy engine. If None, creates default engine.

    Yields:
        Database session that commits on success, rollbacks on exception.
    """
    if engine is None:
        engine = get_engine()

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(db_path: str | None = None, echo: bool = False) -> Engine:
    """Initialize database with schema.

    Creates all tables defined in models if they don't exist.

    Args:
        db_path: Path to SQLite database file.
        echo: If True, log all SQL statements.

    Returns:
        Configured SQLAlchemy Engine.
    """
    engine = get_engine(db_path, echo)
    Base.metadata.create_all(engine)
    return engine
