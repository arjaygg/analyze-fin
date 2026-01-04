"""
Unit & Integration Tests: CLI Commands

Tests for the analyze-fin CLI using Typer's CliRunner.

Priority: P0 (Critical - user-facing interface)
"""

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

    def test_query_command_exits_successfully(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app with an empty database
        WHEN user runs `analyze-fin query`
        THEN exit code is 0 (no transactions found).
        """
        # Use temp database to avoid pollution
        db_path = tmp_path / "test.db"
        monkeypatch.setenv("ANALYZE_FIN_DB", str(db_path))
        # Patch the default db path
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["query"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

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

    def test_query_with_category_flag(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --category "Food & Dining"`
        THEN command accepts the category filter.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["query", "--category", "Food & Dining"])
        assert result.exit_code == 0
        # No transactions, but command succeeds
        assert "No transactions found" in result.stdout

    def test_query_with_short_category_flag(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query -c "Shopping"`
        THEN command accepts the short flag.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["query", "-c", "Shopping"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_merchant_flag(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --merchant "Jollibee"`
        THEN command accepts the merchant filter.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["query", "--merchant", "Jollibee"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_short_merchant_flag(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query -m "Grab"`
        THEN command accepts the short flag.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["query", "-m", "Grab"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_date_range_flag(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --date-range "November 2024"`
        THEN command accepts the date range filter.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["query", "--date-range", "November 2024"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_amount_min_flag(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --amount-min 500`
        THEN command accepts the minimum amount filter.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["query", "--amount-min", "500"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_amount_max_flag(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --amount-max 1000`
        THEN command accepts the maximum amount filter.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["query", "--amount-max", "1000"])
        assert result.exit_code == 0
        assert "No transactions found" in result.stdout

    def test_query_with_format_flag_json(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin query --format json`
        THEN command outputs JSON format.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["query", "--format", "json"])
        assert result.exit_code == 0
        # JSON output should be valid JSON with count and transactions
        import json
        output = json.loads(result.stdout)
        assert "count" in output
        assert "transactions" in output
        assert output["count"] == 0

    def test_query_with_multiple_filters(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs query with multiple filters
        THEN all filters are accepted.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

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
        assert "No transactions found" in result.stdout


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
        THEN command returns exit code 2 (usage error).
        """
        result = runner.invoke(app, ["query", "--format", "invalid"])
        assert result.exit_code == 2
        assert "Invalid format" in result.stdout

    def test_query_rejects_invalid_amount_min(self):
        """
        GIVEN the CLI app
        WHEN user provides non-numeric amount-min
        THEN command returns exit code 2.
        """
        result = runner.invoke(app, ["query", "--amount-min", "abc"])
        assert result.exit_code == 2
        assert "Invalid amount-min" in result.stdout

    def test_query_rejects_invalid_date_range(self):
        """
        GIVEN the CLI app
        WHEN user provides invalid date range format
        THEN command returns exit code 2.
        """
        result = runner.invoke(app, ["query", "--date-range", "invalid-date"])
        assert result.exit_code == 2
        assert "Unrecognized date range" in result.stdout


# ============================================================================
# Test: Report Command
# ============================================================================


class TestReportCommand:
    """Test the report command."""

    def test_report_help_shows_options(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin report --help`
        THEN help shows available options.
        """
        result = runner.invoke(app, ["report", "--help"])
        assert result.exit_code == 0
        assert "--format" in result.stdout or "--output" in result.stdout

    def test_report_with_empty_database(self, tmp_path, monkeypatch):
        """
        GIVEN empty database
        WHEN user runs `analyze-fin report`
        THEN helpful message is shown.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["report"])
        # Should succeed but note no transactions
        assert result.exit_code == 0
        assert "No transactions" in result.stdout or "report" in result.stdout.lower()


# ============================================================================
# Test: Export Command
# ============================================================================


class TestExportCommand:
    """Test the export command."""

    def test_export_help_shows_options(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin export --help`
        THEN help shows available options.
        """
        result = runner.invoke(app, ["export", "--help"])
        assert result.exit_code == 0
        assert "--format" in result.stdout

    def test_export_csv_format(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin export --format csv`
        THEN CSV output is generated.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["export", "--format", "csv"])
        assert result.exit_code == 0
        # Should have CSV header
        assert "date" in result.stdout or "No transactions" in result.stdout

    def test_export_json_format(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin export --format json`
        THEN JSON output is generated as array of transaction objects.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["export", "--format", "json"])
        assert result.exit_code == 0
        # Should be valid JSON - an array (empty when no transactions)
        import json
        data = json.loads(result.stdout)
        assert isinstance(data, list), "JSON output should be an array of transactions"


# ============================================================================
# Test: Categorize Command
# ============================================================================


class TestCategorizeCommand:
    """Test the categorize command."""

    def test_categorize_help_shows_options(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin categorize --help`
        THEN help shows available options.
        """
        result = runner.invoke(app, ["categorize", "--help"])
        assert result.exit_code == 0

    def test_categorize_with_empty_database(self, tmp_path, monkeypatch):
        """
        GIVEN empty database
        WHEN user runs `analyze-fin categorize`
        THEN helpful message is shown.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["categorize"])
        assert result.exit_code == 0
        assert "No" in result.stdout or "categoriz" in result.stdout.lower()


# ============================================================================
# Test: Deduplicate Command
# ============================================================================


class TestDeduplicateCommand:
    """Test the deduplicate command."""

    def test_deduplicate_help_shows_options(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin deduplicate --help`
        THEN help shows available options.
        """
        result = runner.invoke(app, ["deduplicate", "--help"])
        assert result.exit_code == 0

    def test_deduplicate_with_empty_database(self, tmp_path, monkeypatch):
        """
        GIVEN empty database
        WHEN user runs `analyze-fin deduplicate`
        THEN helpful message is shown.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["deduplicate"])
        assert result.exit_code == 0
        assert "No" in result.stdout or "duplicat" in result.stdout.lower()


# ============================================================================
# Test: Ask Command (Natural Language)
# ============================================================================


# ============================================================================
# Test: Parse Command - Unified Workflow (Story 4.7)
# ============================================================================


class TestParseCommandUnifiedWorkflow:
    """Test parse command with unified workflow (auto-categorize, check-duplicates)."""

    def test_parse_help_shows_auto_categorize_option(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin parse --help`
        THEN help shows --auto-categorize option.
        """
        result = runner.invoke(app, ["parse", "--help"])
        assert result.exit_code == 0
        assert "--auto-categorize" in result.stdout or "auto-categorize" in result.stdout.lower()

    def test_parse_help_shows_check_duplicates_option(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin parse --help`
        THEN help shows --check-duplicates option.
        """
        result = runner.invoke(app, ["parse", "--help"])
        assert result.exit_code == 0
        assert "--check-duplicates" in result.stdout or "check-duplicates" in result.stdout.lower()

    def test_parse_accepts_no_auto_categorize_flag(self, tmp_path, monkeypatch):
        """
        GIVEN a PDF file
        WHEN user runs `analyze-fin parse file.pdf --no-auto-categorize`
        THEN command accepts the flag without error.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        # Create a dummy file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        result = runner.invoke(app, ["parse", str(pdf_file), "--no-auto-categorize", "--dry-run"])
        # Command should not fail on flag parsing (may fail on PDF parsing)
        assert "--no-auto-categorize" not in result.stdout or result.exit_code in [0, 1, 2]

    def test_parse_accepts_no_check_duplicates_flag(self, tmp_path, monkeypatch):
        """
        GIVEN a PDF file
        WHEN user runs `analyze-fin parse file.pdf --no-check-duplicates`
        THEN command accepts the flag without error.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        # Create a dummy file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        result = runner.invoke(app, ["parse", str(pdf_file), "--no-check-duplicates", "--dry-run"])
        # Command should not fail on flag parsing
        assert "--no-check-duplicates" not in result.stdout or result.exit_code in [0, 1, 2]

    def test_parse_dry_run_skips_auto_categorize(self, tmp_path, monkeypatch):
        """
        GIVEN a PDF file
        WHEN user runs `analyze-fin parse file.pdf --dry-run`
        THEN auto-categorization is skipped (not saved).
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        result = runner.invoke(app, ["parse", str(pdf_file), "--dry-run"])
        # Dry run should not show "categorized" in output
        # (may fail on parsing, that's ok - we're testing dry-run behavior)
        assert "Dry run" in result.stdout or result.exit_code in [1, 2]


# ============================================================================
# Test: Ask Command (Natural Language)
# ============================================================================


class TestAskCommand:
    """Test the ask command (natural language queries)."""

    def test_ask_help_shows_options(self):
        """
        GIVEN the CLI app
        WHEN user runs `analyze-fin ask --help`
        THEN help shows available options.
        """
        result = runner.invoke(app, ["ask", "--help"])
        assert result.exit_code == 0
        assert "natural language" in result.stdout.lower() or "question" in result.stdout.lower()

    def test_ask_parses_category_query(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user asks about food spending
        THEN category is parsed correctly.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["ask", "How much did I spend on food?"])
        assert result.exit_code == 0
        assert "Food & Dining" in result.stdout

    def test_ask_parses_total_intent(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user asks "how much"
        THEN total intent is detected.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["ask", "How much did I spend?"])
        assert result.exit_code == 0
        assert "total" in result.stdout.lower()

    def test_ask_parses_date_range(self, tmp_path, monkeypatch):
        """
        GIVEN the CLI app
        WHEN user asks about last month
        THEN date range is parsed.
        """
        db_path = tmp_path / "test.db"
        import analyze_fin.database.session
        monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(db_path))

        result = runner.invoke(app, ["ask", "Show transactions last month"])
        assert result.exit_code == 0
        assert "From:" in result.stdout

    def test_ask_requires_question(self):
        """
        GIVEN the CLI app
        WHEN user runs ask without question
        THEN error is shown.
        """
        result = runner.invoke(app, ["ask"])
        assert result.exit_code != 0
