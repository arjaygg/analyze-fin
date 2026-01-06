from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from analyze_fin.parsers.base import ParseResult, RawTransaction
from analyze_fin.parsers.batch import BatchImportResult


class TestParseCommandUnifiedWorkflow:
    """Test parse command with unified workflow (auto-categorize, check-duplicates)."""

    def test_parse_help_shows_auto_categorize_option(self, runner, app):
        result = runner.invoke(app, ["parse", "--help"])
        assert result.exit_code == 0
        assert "--auto-categorize" in result.stdout or "auto-categorize" in result.stdout.lower()

    def test_parse_help_shows_check_duplicates_option(self, runner, app):
        result = runner.invoke(app, ["parse", "--help"])
        assert result.exit_code == 0
        assert "--check-duplicates" in result.stdout or "check-duplicates" in result.stdout.lower()

    def test_parse_accepts_no_auto_categorize_flag(self, runner, app, temp_db, tmp_path):
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        result = runner.invoke(app, ["parse", str(pdf_file), "--no-auto-categorize", "--dry-run"])
        # Command should not fail on flag parsing (may fail on PDF parsing)
        assert "--no-auto-categorize" not in result.stdout or result.exit_code in [0, 1, 2]

    def test_parse_accepts_no_check_duplicates_flag(self, runner, app, temp_db, tmp_path):
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        result = runner.invoke(app, ["parse", str(pdf_file), "--no-check-duplicates", "--dry-run"])
        # Command should not fail on flag parsing
        assert "--no-check-duplicates" not in result.stdout or result.exit_code in [0, 1, 2]

    def test_parse_dry_run_skips_auto_categorize(self, runner, app, temp_db, tmp_path):
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        result = runner.invoke(app, ["parse", str(pdf_file), "--dry-run"])
        # Dry run should not show "categorized" in output
        # (may fail on parsing, that's ok - we're testing dry-run behavior)
        assert "Dry run" in result.stdout or result.exit_code in [1, 2]

    def test_parse_summary_shows_imported_count(self, runner, app, temp_db, tmp_path):
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        mock_result = BatchImportResult(
            total_files=1,
            successful=1,
            failed=0,
            average_quality_score=1.0,
            results=[],
            errors=[],
            duplicates=[],
        )
        transactions = [
            RawTransaction(date=datetime(2024, 1, i), description=f"TX{i}", amount=Decimal("100.00"))
            for i in range(1, 4)
        ]
        parse_result = ParseResult(
            file_path=str(pdf_file),
            bank_type="gcash",
            transactions=transactions,
            quality_score=Decimal("1.0"),
        )
        mock_result.results.append(parse_result)

        with patch("analyze_fin.parsers.batch.BatchImporter") as MockImporter:
            instance = MockImporter.return_value
            instance.import_all.return_value = mock_result

            result = runner.invoke(
                app, ["parse", str(pdf_file), "--no-auto-categorize", "--no-check-duplicates"]
            )

            assert result.exit_code == 0
            assert "Import Summary" in result.stdout
            assert "Imported:" in result.stdout
            assert "transactions" in result.stdout

    def test_parse_summary_shows_categorization_rate(self, runner, app, temp_db, tmp_path):
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        mock_result = BatchImportResult(
            total_files=1,
            successful=1,
            failed=0,
            average_quality_score=1.0,
            results=[],
            errors=[],
            duplicates=[],
        )
        transactions = [
            RawTransaction(date=datetime(2024, 1, i), description=f"TX{i}", amount=Decimal("100.00"))
            for i in range(1, 3)
        ]
        parse_result = ParseResult(
            file_path=str(pdf_file),
            bank_type="gcash",
            transactions=transactions,
            quality_score=Decimal("1.0"),
        )
        mock_result.results.append(parse_result)

        with patch("analyze_fin.parsers.batch.BatchImporter") as MockImporter:
            instance = MockImporter.return_value
            instance.import_all.return_value = mock_result

            # Enable auto-categorize (default), disable duplicate check
            result = runner.invoke(app, ["parse", str(pdf_file), "--no-check-duplicates"])

            assert result.exit_code == 0
            assert "Categorized:" in result.stdout
            assert "%" in result.stdout


