"""
Shared pytest fixtures for analyze-fin test suite.

This module provides reusable fixtures for:
- Database setup/teardown
- Sample data creation
- File handling
- CLI testing
"""

import tempfile
from collections.abc import Generator
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from analyze_fin.database.models import Base
from tests.support.fixtures import files as _files  # noqa: F401
from tests.support.helpers.determinism import get_test_now, seed_python_random

# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_db_path() -> Path:
    """Return path to test database file."""
    return Path("tests/fixtures/test_analyze_fin.db")


@pytest.fixture
def in_memory_db():
    """
    Provide an in-memory SQLite database for fast unit tests.

    Usage:
        def test_something(in_memory_db):
            # Use in_memory_db connection
            pass
    """
    # Note: Actual SQLAlchemy setup will be added when models are implemented
    # For now, this is a placeholder structure
    return "sqlite:///:memory:"


@pytest.fixture
def temp_db_file() -> Generator[Path, None, None]:
    """
    Create a temporary database file for integration tests.

    Automatically cleaned up after test completion.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def db_session(in_memory_db):
    """
    Provide a database session with automatic rollback.

    Each test gets a fresh session that rolls back changes.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):  # noqa: ARG001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        session.rollback()


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_transaction_data():
    """Provide sample transaction data for testing."""
    return {
        "date": datetime(2024, 11, 15, 14, 30),
        "description": "JOLLIBEE GREENBELT 3",
        "amount": Decimal("285.50"),
        "category": "Food & Dining",
        "merchant_normalized": "Jollibee",
    }


@pytest.fixture
def sample_transactions():
    """Provide a list of sample transactions."""
    base_date = datetime(2024, 11, 1)
    return [
        {
            "date": base_date + timedelta(days=i),
            "description": f"Merchant {i}",
            "amount": Decimal(f"{100 + i * 10}.50"),
            "category": "Shopping" if i % 2 == 0 else "Food & Dining",
        }
        for i in range(10)
    ]


@pytest.fixture
def sample_statement_data():
    """Provide sample statement metadata."""
    return {
        "account_name": "GCash Main Account",
        "bank_type": "gcash",
        "statement_date": datetime(2024, 11, 30),
        "opening_balance": Decimal("5000.00"),
        "closing_balance": Decimal("4500.00"),
    }


@pytest.fixture
def sample_merchant_mapping():
    """Provide sample merchant mapping data."""
    return {
        "JOLLIBEE": {
            "normalized": "Jollibee",
            "category": "Food & Dining",
        },
        "7-ELEVEN": {
            "normalized": "7-Eleven",
            "category": "Convenience Store",
        },
        "GRAB": {
            "normalized": "Grab",
            "category": "Transportation",
        },
    }


# ============================================================================
# File Fixtures
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pdf_path() -> Path:
    """Return path to sample PDF statement (if exists)."""
    pdf_path = Path("tests/fixtures/sample_statements/sample_gcash.pdf")
    if not pdf_path.exists():
        pytest.skip("Sample PDF not available")
    return pdf_path


@pytest.fixture
def test_config_file(temp_dir) -> Path:
    """Create a temporary test configuration file."""
    config_path = temp_dir / "config.yaml"
    config_content = """
database_path: tests/fixtures/test_analyze_fin.db
merchant_mapping_path: tests/fixtures/test_merchant_mapping.json
default_category: Uncategorized
"""
    config_path.write_text(config_content)
    return config_path


# ============================================================================
# CLI Fixtures
# ============================================================================

@pytest.fixture
def cli_runner():
    """
    Provide Typer CLI test runner.

    Usage:
        def test_cli_command(cli_runner):
            result = cli_runner.invoke(app, ["command", "--flag"])
            assert result.exit_code == 0
    """
    from typer.testing import CliRunner

    return CliRunner()


@pytest.fixture
def mock_cli_args():
    """Provide mock CLI arguments for testing."""
    return {
        "format": "json",
        "verbose": False,
        "config": None,
    }


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def _seed_test_random() -> int:
    """
    Seed Python's random module once per test session for reproducibility.

    Override with TEST_SEED=<int>.
    """
    return seed_python_random()


@pytest.fixture(autouse=True)
def test_env_setup(monkeypatch):
    """
    Automatically set test environment variables for all tests.

    Uses monkeypatch to safely modify environment without affecting other tests.
    """
    test_env = {
        "TEST_MODE": "true",
        "DATABASE_URL": "sqlite:///:memory:",
        "LOG_LEVEL": "DEBUG",
    }

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def isolated_filesystem(temp_dir, monkeypatch):
    """
    Provide an isolated filesystem for tests.

    Changes working directory to temp dir and restores after test.
    """
    original_cwd = Path.cwd()
    monkeypatch.chdir(temp_dir)
    yield temp_dir
    monkeypatch.chdir(original_cwd)


# ============================================================================
# Test Helpers (Non-fixture utilities)
# ============================================================================

class TestDataFactory:
    """Factory for generating test data with sensible defaults."""

    @staticmethod
    def create_transaction(**overrides):
        """Create a transaction with defaults and overrides."""
        defaults = {
            "date": get_test_now(),
            "description": "Test Transaction",
            "amount": Decimal("100.00"),
            "category": None,
        }
        return {**defaults, **overrides}

    @staticmethod
    def create_statement(**overrides):
        """Create a statement with defaults and overrides."""
        defaults = {
            "account_name": "Test Account",
            "bank_type": "gcash",
            "statement_date": get_test_now(),
            "opening_balance": Decimal("1000.00"),
            "closing_balance": Decimal("900.00"),
        }
        return {**defaults, **overrides}


@pytest.fixture
def test_data_factory():
    """Provide TestDataFactory instance."""
    return TestDataFactory()
