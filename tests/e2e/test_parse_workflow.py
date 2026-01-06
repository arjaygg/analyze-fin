"""
E2E Acceptance Tests: Parse Workflow

Tests the 'analyze-fin parse' command flow.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from analyze_fin.cli import app
from analyze_fin.database.models import Account, Statement, Transaction
from analyze_fin.parsers.base import ParseResult, RawTransaction
from analyze_fin.parsers.batch import BatchImportResult


@pytest.mark.e2e
@pytest.mark.cli
def test_parse_command_saves_to_db(cli_runner, temp_db_file, monkeypatch, tmp_path):
    """
    GIVEN a PDF file and a mocked parser
    WHEN I run `analyze-fin parse statement.pdf`
    THEN the transactions are saved to the database
    """
    import analyze_fin.database.session
    from analyze_fin.config import ConfigManager

    # Reset config state to ensure clean test
    ConfigManager.reset_instance()
    monkeypatch.setattr(analyze_fin.database.session, "_config", None)

    # Mock database path via environment variable (config system uses this)
    monkeypatch.setenv("ANALYZE_FIN_DATABASE_PATH", str(temp_db_file))
    # Also patch legacy path for backwards compatibility
    monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(temp_db_file))

    # Create a temporary PDF file (CLI checks if file exists)
    temp_pdf = tmp_path / "statement.pdf"
    temp_pdf.write_bytes(b"%PDF-1.4 fake pdf content")

    # Mock BatchImporter
    mock_result = BatchImportResult(
        total_files=1,
        successful=1,
        failed=0,
        average_quality_score=1.0,
        results=[],
        errors=[],
        duplicates=[]
    )

    tx_data = RawTransaction(
        date=datetime(2024, 1, 15),
        description="TEST TRANSACTION",
        amount=Decimal("500.00"),
        reference_number="REF123"
    )

    parse_result = ParseResult(
        file_path=str(temp_pdf),
        bank_type="gcash",
        transactions=[tx_data],
        quality_score=Decimal("1.0")
    )

    mock_result.results.append(parse_result)

    with patch("analyze_fin.parsers.batch.BatchImporter") as MockImporter:
        instance = MockImporter.return_value
        instance.import_all.return_value = mock_result

        # Run command
        result = cli_runner.invoke(app, ["parse", str(temp_pdf)])

        # Assert CLI success
        assert result.exit_code == 0
        assert "Parsing complete" in result.stdout
        assert "Saved 1 transactions" in result.stdout

        # Assert DB content
        from sqlalchemy import create_engine, select
        from sqlalchemy.orm import Session

        engine = create_engine(f"sqlite:///{temp_db_file}")
        with Session(engine) as session:
            # Check Account
            account = session.scalar(select(Account).where(Account.bank_type == "gcash"))
            assert account is not None
            assert account.name == "GCASH Account"

            # Check Statement
            stmt = session.scalar(select(Statement).where(Statement.account_id == account.id))
            assert stmt is not None
            assert stmt.file_path.endswith("statement.pdf")

            # Check Transaction
            tx = session.scalar(select(Transaction).where(Transaction.statement_id == stmt.id))
            assert tx is not None
            assert tx.description == "TEST TRANSACTION"
            assert tx.amount == Decimal("500.00")

@pytest.mark.e2e
@pytest.mark.cli
def test_parse_command_dry_run(cli_runner, temp_db_file, monkeypatch, tmp_path):
    """
    GIVEN a PDF file and a mocked parser
    WHEN I run `analyze-fin parse statement.pdf --dry-run`
    THEN the transactions are NOT saved to the database
    """
    import analyze_fin.database.session
    from analyze_fin.config import ConfigManager

    # Reset config state to ensure clean test
    ConfigManager.reset_instance()
    monkeypatch.setattr(analyze_fin.database.session, "_config", None)

    # Mock database path via environment variable (config system uses this)
    monkeypatch.setenv("ANALYZE_FIN_DATABASE_PATH", str(temp_db_file))
    # Also patch legacy path for backwards compatibility
    monkeypatch.setattr(analyze_fin.database.session, "DEFAULT_DB_PATH", str(temp_db_file))

    # Create a temporary PDF file (CLI checks if file exists)
    temp_pdf = tmp_path / "statement.pdf"
    temp_pdf.write_bytes(b"%PDF-1.4 fake pdf content")

    mock_result = BatchImportResult(
        total_files=1,
        successful=1,
        failed=0,
        average_quality_score=1.0,
        results=[],
        errors=[],
        duplicates=[]
    )
    parse_result = ParseResult(
        file_path=str(temp_pdf),
        bank_type="gcash",
        transactions=[RawTransaction(date=datetime.now(), description="T", amount=Decimal("1"))],
        quality_score=Decimal("1.0")
    )
    mock_result.results.append(parse_result)


    with patch("analyze_fin.parsers.batch.BatchImporter") as MockImporter:
        instance = MockImporter.return_value
        instance.import_all.return_value = mock_result

        result = cli_runner.invoke(app, ["parse", str(temp_pdf), "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run" in result.stdout
        assert "Saved" not in result.stdout

        # Verify empty DB (except maybe account created? No, nothing should be saved)
        from sqlalchemy import create_engine, select
        from sqlalchemy.orm import Session
        engine = create_engine(f"sqlite:///{temp_db_file}")
        with Session(engine) as session:
            tx = session.scalar(select(Transaction))
            assert tx is None

