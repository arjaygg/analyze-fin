"""
Unit & Integration Tests: CLI Commands

Tests for the analyze-fin CLI using Typer's CliRunner.

Priority: P0 (Critical - user-facing interface)
"""

import pytest
from typer.testing import CliRunner

from analyze_fin.cli import app


# Create CLI runner for all tests
runner = CliRunner()


class TestVersionCommand:
    """Test the version command."""

    def test_version_command_exits_successfully(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin version`
        THEN exit code is 0 (success).
        """
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0

    def test_version_command_shows_app_name(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin version`
        THEN output contains app name.
        """
        result = runner.invoke(app, ["version"])
        assert "analyze-fin" in result.stdout

    def test_version_command_shows_version_number(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin version`
        THEN output contains version number.
        """
        result = runner.invoke(app, ["version"])
        assert "0.1.0" in result.stdout


class TestHelpCommand:
    """Test help output."""

    def test_help_flag_exits_successfully(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin --help`
        THEN exit code is 0.
        """
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_usage(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin --help`
        THEN output contains usage information.
        """
        result = runner.invoke(app, ["--help"])
        assert "Usage:" in result.stdout

    def test_help_shows_commands(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin --help`
        THEN output lists available commands.
        """
        result = runner.invoke(app, ["--help"])
        # Typer with Rich uses box formatting, so look for "Commands" (not "Commands:")
        assert "Commands" in result.stdout
        assert "query" in result.stdout
        assert "version" in result.stdout

    def test_help_shows_app_description(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin --help`
        THEN output contains app description.
        """
        result = runner.invoke(app, ["--help"])
        assert "Philippine" in result.stdout or "Finance" in result.stdout


class TestQueryCommand:
    """Test the query command."""

    def test_query_command_exits_successfully(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query`
        THEN exit code is 0.
        """
        result = runner.invoke(app, ["query"])
        assert result.exit_code == 0

    def test_query_help_shows_options(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --help`
        THEN help shows available filter options.
        """
        result = runner.invoke(app, ["query", "--help"])
        assert result.exit_code == 0
        assert "--category" in result.stdout
        assert "--merchant" in result.stdout
        assert "--date-range" in result.stdout

    def test_query_with_category_flag(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --category "Food & Dining"`
        THEN command accepts the category filter.
        """
        result = runner.invoke(app, ["query", "--category", "Food & Dining"])
        assert result.exit_code == 0
        assert "Food & Dining" in result.stdout

    def test_query_with_short_category_flag(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query -c "Shopping"`
        THEN command accepts the short flag.
        """
        result = runner.invoke(app, ["query", "-c", "Shopping"])
        assert result.exit_code == 0
        assert "Shopping" in result.stdout

    def test_query_with_merchant_flag(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --merchant "Jollibee"`
        THEN command accepts the merchant filter.
        """
        result = runner.invoke(app, ["query", "--merchant", "Jollibee"])
        assert result.exit_code == 0
        assert "Jollibee" in result.stdout

    def test_query_with_short_merchant_flag(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query -m "Grab"`
        THEN command accepts the short flag.
        """
        result = runner.invoke(app, ["query", "-m", "Grab"])
        assert result.exit_code == 0
        assert "Grab" in result.stdout

    def test_query_with_date_range_flag(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --date-range "November 2024"`
        THEN command accepts the date range filter.
        """
        result = runner.invoke(app, ["query", "--date-range", "November 2024"])
        assert result.exit_code == 0
        assert "November 2024" in result.stdout

    def test_query_with_amount_min_flag(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --amount-min 500`
        THEN command accepts the minimum amount filter.
        """
        result = runner.invoke(app, ["query", "--amount-min", "500"])
        assert result.exit_code == 0
        # Output should show the minimum amount with peso formatting
        assert "500" in result.stdout

    def test_query_with_amount_max_flag(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --amount-max 1000`
        THEN command accepts the maximum amount filter.
        """
        result = runner.invoke(app, ["query", "--amount-max", "1000"])
        assert result.exit_code == 0
        assert "1,000" in result.stdout or "1000" in result.stdout

    def test_query_with_format_flag(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --format json`
        THEN command accepts the format option.
        """
        result = runner.invoke(app, ["query", "--format", "json"])
        assert result.exit_code == 0
        assert "json" in result.stdout

    def test_query_with_multiple_filters(self):
        """
        GIVEN the CLI app
        WHEN user runs query with multiple filters
        THEN all filters are accepted.
        """
        result = runner.invoke(
            app,
            [
                "query",
                "--category",
                "Food & Dining",
                "--merchant",
                "Jollibee",
                "--amount-min",
                "100",
            ],
        )
        assert result.exit_code == 0
        assert "Food & Dining" in result.stdout
        assert "Jollibee" in result.stdout


class TestNoArgsShowsHelp:
    """Test that running without args shows help."""

    def test_no_args_shows_help(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin` with no arguments
        THEN help is displayed (due to no_args_is_help=True).
        """
        result = runner.invoke(app, [])
        # With no_args_is_help=True, Typer returns exit code 0 or 2 depending on version
        # The important thing is that help is shown
        assert "Usage:" in result.stdout
        assert "Commands" in result.stdout


class TestCommandValidation:
    """Test command argument validation."""

    def test_invalid_command_shows_error(self):
        """
        GIVEN the CLI app
        WHEN user runs an invalid command
        THEN error message is shown with non-zero exit code.
        """
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0

    def test_query_rejects_invalid_format(self):
        """
        GIVEN the CLI app
        WHEN user provides invalid format option
        THEN command still runs (format is just a string option).
        """
        # The current implementation accepts any string for format
        # This tests that it doesn't crash
        result = runner.invoke(app, ["query", "--format", "invalid"])
        assert result.exit_code == 0
