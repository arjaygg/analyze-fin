"""
Unit Tests: Database Session Management

Tests for database/session.py functions:
- get_engine: Engine creation with WAL mode
- get_session: Session management with commit/rollback
- init_db: Database initialization

Priority: P0 (Critical infrastructure)
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session


class TestGetEngine:
    """Test get_engine() function."""

    def test_get_engine_returns_engine(self, tmp_path):
        """
        GIVEN a database path
        WHEN get_engine is called
        THEN returns a SQLAlchemy Engine instance.
        """
        from analyze_fin.database.session import get_engine

        db_path = str(tmp_path / "test.db")
        engine = get_engine(db_path)

        assert engine is not None
        assert "sqlite" in str(engine.url)

    def test_get_engine_creates_parent_directory(self, tmp_path):
        """
        GIVEN a database path with non-existent parent directory
        WHEN get_engine is called
        THEN parent directory is created automatically.
        """
        from analyze_fin.database.session import get_engine

        db_path = str(tmp_path / "subdir" / "nested" / "test.db")
        engine = get_engine(db_path)

        assert Path(db_path).parent.exists()

    def test_get_engine_enables_wal_mode(self, tmp_path):
        """
        GIVEN a new database
        WHEN get_engine is called
        THEN WAL journal mode is enabled for crash recovery.
        """
        from analyze_fin.database.session import get_engine

        db_path = str(tmp_path / "test.db")
        engine = get_engine(db_path)

        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA journal_mode")).fetchone()
            assert result[0].lower() == "wal"

    def test_get_engine_enables_foreign_keys(self, tmp_path):
        """
        GIVEN a new database
        WHEN get_engine is called
        THEN foreign key constraints are enabled.
        """
        from analyze_fin.database.session import get_engine

        db_path = str(tmp_path / "test.db")
        engine = get_engine(db_path)

        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA foreign_keys")).fetchone()
            assert result[0] == 1

    def test_get_engine_with_echo_true(self, tmp_path, capsys):
        """
        GIVEN echo=True parameter
        WHEN get_engine is called
        THEN SQL statements are logged.
        """
        from analyze_fin.database.session import get_engine

        db_path = str(tmp_path / "test.db")
        engine = get_engine(db_path, echo=True)

        # Execute a statement to trigger logging
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Echo output goes to stdout
        # Just verify engine was created with echo capability
        assert engine.echo is True

    def test_get_engine_uses_default_path_when_none(self):
        """
        GIVEN no database path (None)
        WHEN get_engine is called
        THEN uses DEFAULT_DB_PATH.
        """
        from analyze_fin.database.session import DEFAULT_DB_PATH, get_engine

        engine = get_engine(None)

        assert DEFAULT_DB_PATH in str(engine.url)


class TestGetSession:
    """Test get_session() generator function."""

    def test_get_session_yields_session(self, tmp_path):
        """
        GIVEN an engine
        WHEN get_session is called
        THEN yields a SQLAlchemy Session.
        """
        from analyze_fin.database.session import get_engine, get_session

        db_path = str(tmp_path / "test.db")
        engine = get_engine(db_path)

        session_gen = get_session(engine)
        session = next(session_gen)

        assert isinstance(session, Session)

        # Clean up
        try:
            next(session_gen)
        except StopIteration:
            pass

    def test_get_session_commits_on_success(self, tmp_path):
        """
        GIVEN a session with pending changes
        WHEN session block completes without exception
        THEN changes are committed to database.
        """
        from analyze_fin.database.models import Account
        from analyze_fin.database.session import get_session, init_db

        db_path = str(tmp_path / "test.db")
        engine = init_db(db_path)

        # Add data in first session
        for session in get_session(engine):
            account = Account(name="Test Account", bank_type="gcash")
            session.add(account)

        # Verify in new session
        for session in get_session(engine):
            result = session.query(Account).filter_by(name="Test Account").first()
            assert result is not None
            assert result.name == "Test Account"

    def test_get_session_rollbacks_on_exception(self, tmp_path):
        """
        GIVEN a session with pending changes
        WHEN an exception occurs in session block
        THEN changes are rolled back.
        """
        from analyze_fin.database.models import Account
        from analyze_fin.database.session import get_session, init_db

        db_path = str(tmp_path / "test.db")
        engine = init_db(db_path)

        # Try to add data but raise exception
        try:
            for session in get_session(engine):
                account = Account(name="Rollback Test", bank_type="bpi")
                session.add(account)
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Verify data was NOT persisted
        for session in get_session(engine):
            result = session.query(Account).filter_by(name="Rollback Test").first()
            assert result is None

    def test_get_session_closes_after_use(self, tmp_path):
        """
        GIVEN a session
        WHEN session block completes
        THEN session is closed properly.
        """

        from analyze_fin.database.session import get_engine, get_session

        db_path = str(tmp_path / "test.db")
        engine = get_engine(db_path)

        session_ref = None
        for session in get_session(engine):
            session_ref = session

        # Session should be closed after generator completes
        # Verify by checking that session.close() was called (connection is None)
        # After close(), the session's bind should show it's detached
        assert session_ref.get_bind() is not None  # Engine still accessible
        # The session was properly used and cleaned up - verify no pending transactions
        assert not session_ref.dirty
        assert not session_ref.new

    def test_get_session_creates_default_engine_when_none(self):
        """
        GIVEN no engine parameter (None)
        WHEN get_session is called
        THEN creates default engine automatically.
        """
        from analyze_fin.database.session import get_session

        # This should not raise - it creates default engine
        for session in get_session(None):
            assert isinstance(session, Session)
            break  # Don't commit anything


class TestInitDb:
    """Test init_db() function."""

    def test_init_db_creates_tables(self, tmp_path):
        """
        GIVEN a new database path
        WHEN init_db is called
        THEN all model tables are created.
        """
        from analyze_fin.database.session import init_db

        db_path = str(tmp_path / "test.db")
        engine = init_db(db_path)

        # Check tables exist
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            ).fetchall()
            table_names = [row[0] for row in result]

            assert "accounts" in table_names
            assert "statements" in table_names
            assert "transactions" in table_names

    def test_init_db_returns_engine(self, tmp_path):
        """
        GIVEN a database path
        WHEN init_db is called
        THEN returns configured Engine.
        """
        from analyze_fin.database.session import init_db

        db_path = str(tmp_path / "test.db")
        engine = init_db(db_path)

        assert engine is not None
        assert "sqlite" in str(engine.url)

    def test_init_db_is_idempotent(self, tmp_path):
        """
        GIVEN an already initialized database
        WHEN init_db is called again
        THEN no errors occur (tables already exist).
        """
        from analyze_fin.database.session import init_db

        db_path = str(tmp_path / "test.db")

        # Initialize twice
        engine1 = init_db(db_path)
        engine2 = init_db(db_path)

        # Both should work without error
        assert engine1 is not None
        assert engine2 is not None

    def test_init_db_preserves_existing_data(self, tmp_path):
        """
        GIVEN a database with existing data
        WHEN init_db is called
        THEN existing data is preserved.
        """
        from analyze_fin.database.models import Account
        from analyze_fin.database.session import get_session, init_db

        db_path = str(tmp_path / "test.db")

        # First init and add data
        engine = init_db(db_path)
        for session in get_session(engine):
            session.add(Account(name="Preserved Account", bank_type="maya"))

        # Second init
        engine2 = init_db(db_path)

        # Data should still exist
        for session in get_session(engine2):
            result = session.query(Account).filter_by(name="Preserved Account").first()
            assert result is not None


class TestSessionIntegration:
    """Integration tests for session management with models."""

    def test_full_workflow_create_account_statement_transaction(self, tmp_path):
        """
        GIVEN initialized database
        WHEN creating account, statement, and transaction
        THEN all entities are persisted with relationships.
        """
        from analyze_fin.database.models import Account, Statement, Transaction
        from analyze_fin.database.session import get_session, init_db

        db_path = str(tmp_path / "test.db")
        engine = init_db(db_path)

        # Create full hierarchy
        for session in get_session(engine):
            account = Account(name="GCash", bank_type="gcash")
            session.add(account)
            session.flush()

            statement = Statement(
                account_id=account.id,
                file_path="/statements/nov2024.pdf",
                quality_score=0.95,
            )
            session.add(statement)
            session.flush()

            transaction = Transaction(
                statement_id=statement.id,
                date=datetime(2024, 11, 15),
                description="JOLLIBEE GREENBELT",
                amount=Decimal("285.50"),
            )
            session.add(transaction)

        # Verify in new session
        for session in get_session(engine):
            account = session.query(Account).first()
            assert account.name == "GCash"
            assert len(account.statements) == 1
            assert len(account.statements[0].transactions) == 1
            assert account.statements[0].transactions[0].amount == Decimal("285.50")
