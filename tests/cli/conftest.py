import pytest
from typer.testing import CliRunner

import analyze_fin.database.session as db_session_mod
from analyze_fin.cli import app as cli_app
from analyze_fin.config import ConfigManager


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def app():
    return cli_app


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    """Isolated empty DB for CLI tests to avoid polluting local/dev data."""
    db_path = tmp_path / "test.db"

    # Reset config singleton to ensure clean state
    ConfigManager.reset_instance()

    # Set environment variable for database path (used by config system)
    monkeypatch.setenv("ANALYZE_FIN_DATABASE_PATH", str(db_path))

    # Also patch DEFAULT_DB_PATH for legacy code paths
    monkeypatch.setattr(db_session_mod, "DEFAULT_DB_PATH", str(db_path))

    # Reset global config reference in session module
    monkeypatch.setattr(db_session_mod, "_config", None)

    yield db_path

    # Cleanup: reset singleton after test
    ConfigManager.reset_instance()


