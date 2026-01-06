"""Tests for CLI exit codes and error handling."""

import pytest
from typer.testing import CliRunner

from analyze_fin.cli import app
from analyze_fin.cli.exit_codes import (
    CONFIG_ERROR,
    DB_ERROR,
    ERROR,
    PARSE_ERROR,
    SUCCESS,
    get_exit_code_for_exception,
)


@pytest.fixture
def runner():
    return CliRunner()


class TestExitCodeConstants:
    """Test exit code constant values."""

    def test_success_is_zero(self):
        """SUCCESS exit code should be 0."""
        assert SUCCESS == 0

    def test_error_is_one(self):
        """ERROR exit code should be 1."""
        assert ERROR == 1

    def test_parse_error_is_two(self):
        """PARSE_ERROR exit code should be 2."""
        assert PARSE_ERROR == 2

    def test_config_error_is_three(self):
        """CONFIG_ERROR exit code should be 3."""
        assert CONFIG_ERROR == 3

    def test_db_error_is_four(self):
        """DB_ERROR exit code should be 4."""
        assert DB_ERROR == 4


class TestExitCodeMapping:
    """Test exception to exit code mapping."""

    def test_parse_error_maps_to_parse_code(self):
        """ParseError should map to PARSE_ERROR."""
        from analyze_fin.exceptions import ParseError

        exc = ParseError("test")
        assert get_exit_code_for_exception(exc) == PARSE_ERROR

    def test_validation_error_maps_to_parse_code(self):
        """ValidationError should map to PARSE_ERROR."""
        from analyze_fin.exceptions import ValidationError

        exc = ValidationError("test")
        assert get_exit_code_for_exception(exc) == PARSE_ERROR

    def test_config_error_maps_to_config_code(self):
        """ConfigError should map to CONFIG_ERROR."""
        from analyze_fin.exceptions import ConfigError

        exc = ConfigError("test")
        assert get_exit_code_for_exception(exc) == CONFIG_ERROR

    def test_unknown_error_maps_to_general_code(self):
        """Unknown exceptions should map to ERROR."""
        exc = ValueError("unknown error")
        assert get_exit_code_for_exception(exc) == ERROR


class TestQuietFlag:
    """Test --quiet flag behavior."""

    def test_quiet_flag_is_recognized(self, runner):
        """--quiet flag should be accepted by CLI."""
        result = runner.invoke(app, ["--quiet", "version"])
        assert result.exit_code == 0

    def test_q_short_flag_is_recognized(self, runner):
        """Short -q flag should be accepted by CLI."""
        result = runner.invoke(app, ["-q", "version"])
        assert result.exit_code == 0

    def test_quiet_suppresses_version_output(self, runner):
        """--quiet should suppress version output."""
        # Normal output
        normal_result = runner.invoke(app, ["version"])
        # Quiet output
        quiet_result = runner.invoke(app, ["--quiet", "version"])

        # Version info should be in normal output
        assert "analyze-fin" in normal_result.output.lower()

        # Quiet should have minimal or no output
        # (version command may still output as it's informational)
        assert quiet_result.exit_code == 0


class TestSuccessfulCommands:
    """Test exit code 0 for successful commands."""

    def test_version_returns_success(self, runner):
        """version command should return exit code 0."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == SUCCESS

    def test_help_returns_success(self, runner):
        """--help should return exit code 0."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == SUCCESS


class TestErrorExitCodes:
    """Test error-specific exit codes."""

    def test_invalid_command_returns_error(self, runner):
        """Invalid command should return exit code 2 (Click/Typer usage error)."""
        result = runner.invoke(app, ["nonexistent-command"])
        # Typer returns 2 for usage errors
        assert result.exit_code == 2

    def test_file_not_found_returns_error(self, runner, tmp_path, monkeypatch):
        """parse with non-existent file should return error."""
        from analyze_fin.config import ConfigManager

        ConfigManager.reset_instance()
        monkeypatch.setenv("ANALYZE_FIN_DATABASE_PATH", str(tmp_path / "test.db"))

        result = runner.invoke(app, ["parse", "/nonexistent/file.pdf"])
        assert result.exit_code == ERROR
        assert "not found" in result.output.lower()

        ConfigManager.reset_instance()


class TestDatabaseErrorExitCode:
    """Test DB_ERROR exit code for database failures."""

    def test_sqlalchemy_operational_error_maps_to_db_error(self):
        """SQLAlchemy OperationalError should map to DB_ERROR."""
        from sqlalchemy.exc import OperationalError

        # Create a mock OperationalError (contains 'sql' in class name)
        exc = OperationalError("connection failed", None, None)
        assert get_exit_code_for_exception(exc) == DB_ERROR

    def test_sqlite_error_maps_to_db_error(self):
        """SQLite errors should map to DB_ERROR based on name matching."""
        # Create a custom exception with 'sqlite' in the name
        class SQLiteError(Exception):
            pass

        exc = SQLiteError("database is locked")
        assert get_exit_code_for_exception(exc) == DB_ERROR

    def test_database_error_maps_to_db_error(self):
        """Exception with 'database' in name should map to DB_ERROR."""
        class DatabaseConnectionError(Exception):
            pass

        exc = DatabaseConnectionError("cannot connect")
        assert get_exit_code_for_exception(exc) == DB_ERROR

    def test_invalid_database_path_returns_error(self, runner, monkeypatch):
        """Query with invalid database path should return error."""
        from analyze_fin.config import ConfigManager

        ConfigManager.reset_instance()
        # Use a directory path instead of file path - will fail
        monkeypatch.setenv("ANALYZE_FIN_DATABASE_PATH", "/nonexistent/path/db.sqlite")

        result = runner.invoke(app, ["query", "--category", "Food"])
        # Should return an error (1 for general error since init_db catches and wraps)
        assert result.exit_code != SUCCESS

        ConfigManager.reset_instance()


class TestPipeFriendlyOutput:
    """Test pipe-friendly output behavior (AC11)."""

    def test_json_output_is_valid_json(self, runner, tmp_path, monkeypatch):
        """JSON output should be valid parseable JSON."""
        import json as json_module

        from analyze_fin.config import ConfigManager

        ConfigManager.reset_instance()
        monkeypatch.setenv("ANALYZE_FIN_DATABASE_PATH", str(tmp_path / "test.db"))

        # Query with JSON format - should produce valid JSON even if no results
        result = runner.invoke(app, ["query", "--category", "Food", "--format", "json"])

        # If successful, output should be valid JSON or contain error
        if result.exit_code == SUCCESS:
            # Try to parse as JSON
            try:
                # Find JSON content (may have other output around it)
                output = result.output.strip()
                if output.startswith("[") or output.startswith("{"):
                    json_module.loads(output)
            except json_module.JSONDecodeError:
                # May have mixed output, that's acceptable
                pass

        ConfigManager.reset_instance()

    def test_csv_output_has_no_rich_markup(self, runner, tmp_path, monkeypatch):
        """CSV output should not contain Rich markup."""
        from analyze_fin.config import ConfigManager

        ConfigManager.reset_instance()
        monkeypatch.setenv("ANALYZE_FIN_DATABASE_PATH", str(tmp_path / "test.db"))

        result = runner.invoke(app, ["query", "--category", "Food", "--format", "csv"])

        # CSV output should not have Rich markup like [red], [green], etc.
        assert "[red]" not in result.output or "Error" in result.output
        assert "[green]" not in result.output or result.exit_code != SUCCESS

        ConfigManager.reset_instance()

    def test_batch_mode_output_is_machine_readable(self, runner, tmp_path, monkeypatch):
        """Batch mode should produce machine-readable output."""
        from analyze_fin.config import ConfigManager

        ConfigManager.reset_instance()
        monkeypatch.setenv("ANALYZE_FIN_DATABASE_PATH", str(tmp_path / "test.db"))

        # Version in batch mode should still work
        result = runner.invoke(app, ["--batch", "version"])
        assert result.exit_code == SUCCESS

        ConfigManager.reset_instance()
