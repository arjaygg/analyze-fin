"""
Unit tests for DataExporter class.

Tests cover:
- CSV export with all required fields
- JSON export with snake_case keys
- Filter support (category, date_range, merchant)
- Empty result handling
- UTF-8 encoding for Philippine characters
"""

import csv
import io
import json
from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from analyze_fin.database.models import Account, Base, Statement, Transaction


@pytest.fixture
def test_engine():
    """Create in-memory SQLite engine for tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Provide database session with test data."""
    with Session(test_engine) as session:
        # Create test account
        account = Account(
            name="Test GCash",
            bank_type="gcash",
        )
        session.add(account)
        session.flush()

        # Create test statement
        statement = Statement(
            account_id=account.id,
            file_path="/test/statement.pdf",
            quality_score=0.95,
        )
        session.add(statement)
        session.flush()

        # Create test transactions
        transactions = [
            Transaction(
                statement_id=statement.id,
                date=datetime(2024, 11, 15),
                description="JOLLIBEE GREENBELT 3",
                amount=Decimal("285.50"),
                category="Food & Dining",
                merchant_normalized="Jollibee",
            ),
            Transaction(
                statement_id=statement.id,
                date=datetime(2024, 11, 16),
                description="GRAB RIDE - BGC TO MAKATI",
                amount=Decimal("150.00"),
                category="Transportation",
                merchant_normalized="Grab",
            ),
            Transaction(
                statement_id=statement.id,
                date=datetime(2024, 11, 17),
                description="7-ELEVEN AYALA AVE",
                amount=Decimal("75.25"),
                category="Shopping",
                merchant_normalized="7-Eleven",
            ),
            Transaction(
                statement_id=statement.id,
                date=datetime(2024, 11, 18),
                description="PEÑAFLORIDA CAFÉ",
                amount=Decimal("350.00"),
                category="Food & Dining",
                merchant_normalized="Peñaflorida Café",
            ),
        ]
        session.add_all(transactions)
        session.commit()
        yield session


class TestDataExporterCSV:
    """Tests for CSV export functionality."""

    def test_export_csv_includes_required_headers(self, test_session):
        """Given transactions exist, CSV export includes all required headers."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        result = exporter.export_csv()

        # Parse CSV to verify headers
        reader = csv.DictReader(io.StringIO(result))
        headers = reader.fieldnames

        required_headers = ["date", "merchant", "category", "amount", "description", "account"]
        for header in required_headers:
            assert header in headers, f"Missing required header: {header}"

    def test_export_csv_dates_in_iso_format(self, test_session):
        """Given transactions exist, dates are in ISO format YYYY-MM-DD."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        result = exporter.export_csv()

        reader = csv.DictReader(io.StringIO(result))
        for row in reader:
            # Verify date format matches YYYY-MM-DD pattern
            date_str = row["date"]
            assert len(date_str) == 10, f"Date should be 10 chars: {date_str}"
            assert date_str[4] == "-" and date_str[7] == "-", f"Invalid ISO format: {date_str}"
            # Verify it parses correctly
            datetime.strptime(date_str, "%Y-%m-%d")

    def test_export_csv_amounts_no_currency_symbol(self, test_session):
        """Given transactions exist, amounts have no currency symbol."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        result = exporter.export_csv()

        reader = csv.DictReader(io.StringIO(result))
        for row in reader:
            amount = row["amount"]
            assert "₱" not in amount, f"Currency symbol found in amount: {amount}"
            assert "$" not in amount, f"Dollar sign found in amount: {amount}"
            # Verify it's a valid decimal number
            Decimal(amount)

    def test_export_csv_includes_all_transactions(self, test_session):
        """Given 4 transactions exist, CSV export includes all 4."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        result = exporter.export_csv()

        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 4, f"Expected 4 rows, got {len(rows)}"


class TestDataExporterJSON:
    """Tests for JSON export functionality."""

    def test_export_json_is_valid_json(self, test_session):
        """Given transactions exist, JSON export is valid JSON."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        result = exporter.export_json()

        # Should not raise exception
        data = json.loads(result)
        assert isinstance(data, list), "JSON should be array of transactions"

    def test_export_json_has_required_keys(self, test_session):
        """Given transactions exist, JSON objects have all required keys."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        result = exporter.export_json()
        data = json.loads(result)

        required_keys = [
            "transaction_id",
            "date",
            "merchant_normalized",
            "category",
            "amount",
            "description",
            "account",
            "created_at",
        ]

        for tx in data:
            for key in required_keys:
                assert key in tx, f"Missing required key: {key}"

    def test_export_json_uses_snake_case_keys(self, test_session):
        """Given transactions exist, JSON keys use snake_case (AR21)."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        result = exporter.export_json()
        data = json.loads(result)

        for tx in data:
            for key in tx.keys():
                # Snake case keys should not have uppercase letters or camelCase
                assert key == key.lower(), f"Key not lowercase: {key}"
                assert "-" not in key, f"Key has hyphen: {key}"

    def test_export_json_amounts_are_strings(self, test_session):
        """Given transactions exist, amounts are strings for precision."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        result = exporter.export_json()
        data = json.loads(result)

        for tx in data:
            assert isinstance(tx["amount"], str), f"Amount should be string: {tx['amount']}"
            # Should be valid decimal string
            Decimal(tx["amount"])

    def test_export_json_dates_are_iso_strings(self, test_session):
        """Given transactions exist, dates are ISO format strings."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        result = exporter.export_json()
        data = json.loads(result)

        for tx in data:
            assert isinstance(tx["date"], str), f"Date should be string: {tx['date']}"
            # Verify parseable as ISO date
            datetime.strptime(tx["date"], "%Y-%m-%d")


class TestDataExporterFilters:
    """Tests for filter functionality."""

    def test_filter_by_category(self, test_session):
        """Given category filter, only matching transactions exported."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("Food & Dining")
        result = exporter.export_csv()

        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)

        # Should have 2 Food & Dining transactions
        assert len(rows) == 2
        for row in rows:
            assert row["category"] == "Food & Dining"

    def test_filter_by_date_range(self, test_session):
        """Given date range filter, only transactions in range exported."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_date_range(
            start_date=datetime(2024, 11, 16),
            end_date=datetime(2024, 11, 17)
        )
        result = exporter.export_csv()

        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)

        # Should have 2 transactions (Nov 16 and Nov 17)
        assert len(rows) == 2

    def test_filter_by_merchant(self, test_session):
        """Given merchant filter, only matching transactions exported."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_merchant("Jollibee")
        result = exporter.export_csv()

        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["merchant"] == "Jollibee"

    def test_multiple_filters_combined(self, test_session):
        """Given multiple filters, they combine with AND logic."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("Food & Dining")
        exporter.filter_by_date_range(
            start_date=datetime(2024, 11, 18),
            end_date=datetime(2024, 11, 18)
        )
        result = exporter.export_csv()

        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)

        # Should have 1 transaction: Peñaflorida Café on Nov 18
        assert len(rows) == 1
        assert rows[0]["category"] == "Food & Dining"


class TestDataExporterEmptyResults:
    """Tests for empty result handling."""

    def test_export_csv_empty_has_headers_only(self, test_session):
        """Given no matching transactions, CSV has headers only."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("NonexistentCategory")
        result = exporter.export_csv()

        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)

        # Headers should exist, no data rows
        assert reader.fieldnames is not None
        assert len(rows) == 0

    def test_export_json_empty_is_empty_array(self, test_session):
        """Given no matching transactions, JSON is empty array."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("NonexistentCategory")
        result = exporter.export_json()

        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 0


class TestDataExporterUTF8:
    """Tests for UTF-8 encoding and special characters."""

    def test_export_csv_preserves_philippine_characters(self, test_session):
        """Given Philippine characters, CSV preserves them correctly."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_merchant("Peñaflorida")
        result = exporter.export_csv()

        # Verify ñ is preserved
        assert "Peñaflorida" in result

    def test_export_json_preserves_unicode(self, test_session):
        """Given Unicode characters, JSON preserves them correctly."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        result = exporter.export_json()

        # Verify ñ is preserved (not escaped)
        data = json.loads(result)
        cafe_tx = [tx for tx in data if "Peñaflorida" in (tx.get("merchant_normalized") or "")]
        assert len(cafe_tx) == 1


class TestDataExporterFilename:
    """Tests for filter-aware filename generation."""

    def test_generate_filename_no_filters(self, test_session):
        """Given no filters, filename is just 'export.csv'."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        filename = exporter.generate_filename("csv")

        assert filename == "export.csv"

    def test_generate_filename_with_category(self, test_session):
        """Given category filter, filename includes sanitized category."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("Food & Dining")
        filename = exporter.generate_filename("csv")

        assert filename == "export_food_dining.csv"

    def test_generate_filename_with_date_range_same_month(self, test_session):
        """Given date range in same month, filename shows single month."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_date_range(
            start_date=datetime(2024, 11, 1),
            end_date=datetime(2024, 11, 30)
        )
        filename = exporter.generate_filename("csv")

        assert filename == "export_nov2024.csv"

    def test_generate_filename_with_category_and_date(self, test_session):
        """Given category and date filters, filename includes both."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("Food & Dining")
        exporter.filter_by_date_range(
            start_date=datetime(2024, 11, 1),
            end_date=datetime(2024, 11, 30)
        )
        filename = exporter.generate_filename("csv")

        assert filename == "export_food_dining_nov2024.csv"

    def test_generate_filename_json_extension(self, test_session):
        """Given json extension request, filename has .json."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("Shopping")
        filename = exporter.generate_filename("json")

        assert filename == "export_shopping.json"


class TestDataExporterMetadata:
    """Tests for filter metadata in exports."""

    def test_csv_with_metadata_includes_comments(self, test_session):
        """Given include_metadata=True, CSV has filter comments."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("Food & Dining")
        result = exporter.export_csv(include_metadata=True)

        assert '# Filter: category="Food & Dining"' in result
        assert "# Export generated:" in result

    def test_json_with_metadata_has_wrapper_object(self, test_session):
        """Given include_metadata=True, JSON has metadata wrapper."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("Food & Dining")
        result = exporter.export_json(include_metadata=True)

        data = json.loads(result)
        assert "metadata" in data
        assert "transactions" in data
        assert "count" in data
        assert data["metadata"]["filters"]["category"] == "Food & Dining"

    def test_get_filter_metadata(self, test_session):
        """Given filters applied, metadata reflects them."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("Transportation")
        exporter.filter_by_merchant("Grab")

        metadata = exporter.get_filter_metadata()

        assert metadata["filters"]["category"] == "Transportation"
        assert metadata["filters"]["merchant"] == "Grab"
        assert "exported_at" in metadata


class TestDataExporterStreaming:
    """Tests for streaming export functionality."""

    def test_count_returns_correct_number(self, test_session):
        """Given transactions, count returns correct number."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        count = exporter.count()

        assert count == 4

    def test_count_with_filter(self, test_session):
        """Given filter, count returns filtered count."""
        from analyze_fin.export.exporter import DataExporter

        exporter = DataExporter(test_session)
        exporter.filter_by_category("Food & Dining")
        count = exporter.count()

        assert count == 2

    def test_streaming_csv_produces_same_output(self, test_session):
        """Given streaming=True, CSV output matches non-streaming."""
        from analyze_fin.export.exporter import DataExporter

        exporter1 = DataExporter(test_session)
        normal_output = exporter1.export_csv(streaming=False)

        exporter2 = DataExporter(test_session)
        streaming_output = exporter2.export_csv(streaming=True)

        assert normal_output == streaming_output

    def test_streaming_json_produces_same_output(self, test_session):
        """Given streaming=True, JSON output matches non-streaming."""
        from analyze_fin.export.exporter import DataExporter

        exporter1 = DataExporter(test_session)
        normal_output = exporter1.export_json(streaming=False)

        exporter2 = DataExporter(test_session)
        streaming_output = exporter2.export_json(streaming=True)

        assert normal_output == streaming_output

    def test_progress_callback_called(self, test_session):
        """Given progress_callback, it gets called during streaming."""
        from analyze_fin.export.exporter import DataExporter

        progress_calls = []

        def track_progress(current, total):
            progress_calls.append((current, total))

        exporter = DataExporter(test_session)
        exporter.export_csv(streaming=True, progress_callback=track_progress)

        # With 4 transactions, should call with (4, 4) at minimum
        assert len(progress_calls) > 0
        assert progress_calls[-1] == (4, 4)
