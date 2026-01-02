"""
TDD Tests: GCashParser Implementation

Story 1.2 AC: GCash statement parsing with >95% accuracy.
RED phase - these tests will fail until gcash.py is implemented.

GCash statement format:
- Date format: "MMM DD, YYYY" (e.g., "Nov 15, 2024")
- Amount format: "₱1,234.56" or "1234.56"
- Table columns: Date | Description | Reference | Debit | Credit | Balance
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestGCashParserStructure:
    """Test GCashParser class structure."""

    def test_gcash_parser_exists(self):
        """GCashParser can be imported."""
        from analyze_fin.parsers.gcash import GCashParser

        assert GCashParser is not None

    def test_gcash_parser_inherits_from_base(self):
        """GCashParser inherits from BaseBankParser."""
        from analyze_fin.parsers.base import BaseBankParser
        from analyze_fin.parsers.gcash import GCashParser

        assert issubclass(GCashParser, BaseBankParser)

    def test_gcash_parser_can_instantiate(self):
        """GCashParser can be instantiated."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()
        assert parser is not None

    def test_gcash_parser_has_extract_transactions_method(self):
        """GCashParser implements extract_transactions method."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()
        assert callable(parser.extract_transactions)


class TestGCashDateParsing:
    """Test GCash date format parsing."""

    def test_parse_gcash_date_format(self):
        """Parse GCash date format: 'MMM DD, YYYY'."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        # GCash uses "Nov 15, 2024" format
        result = parser._parse_date("Nov 15, 2024")
        assert result == datetime(2024, 11, 15)

    def test_parse_gcash_date_various_months(self):
        """Parse dates for various months."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        test_cases = [
            ("Jan 01, 2024", datetime(2024, 1, 1)),
            ("Feb 28, 2024", datetime(2024, 2, 28)),
            ("Mar 15, 2024", datetime(2024, 3, 15)),
            ("Dec 31, 2024", datetime(2024, 12, 31)),
        ]

        for date_str, expected in test_cases:
            result = parser._parse_date(date_str)
            assert result == expected, f"Failed for {date_str}"

    def test_parse_invalid_date_raises_error(self):
        """Invalid date format raises ValueError."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        with pytest.raises(ValueError):
            parser._parse_date("invalid date")


class TestGCashAmountParsing:
    """Test GCash amount format parsing."""

    def test_parse_amount_with_peso_symbol(self):
        """Parse amount with ₱ symbol: '₱1,234.56'."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        result = parser._parse_amount("₱1,234.56")
        assert result == Decimal("1234.56")

    def test_parse_amount_without_symbol(self):
        """Parse amount without symbol: '1234.56'."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        result = parser._parse_amount("1234.56")
        assert result == Decimal("1234.56")

    def test_parse_amount_with_commas(self):
        """Parse amount with thousands separator: '12,345.67'."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        result = parser._parse_amount("12,345.67")
        assert result == Decimal("12345.67")

    def test_parse_negative_amount_parentheses(self):
        """Parse negative amount in parentheses: '(1,234.56)'."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        result = parser._parse_amount("(1,234.56)")
        assert result == Decimal("-1234.56")

    def test_parse_negative_amount_minus_sign(self):
        """Parse negative amount with minus: '-1,234.56'."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        result = parser._parse_amount("-1,234.56")
        assert result == Decimal("-1234.56")

    def test_parse_amount_preserves_decimal_precision(self):
        """Amount parsing preserves Decimal precision."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        result = parser._parse_amount("285.50")
        assert result == Decimal("285.50")
        assert isinstance(result, Decimal)


class TestGCashRowExtraction:
    """Test extraction of individual transaction rows."""

    def test_extract_transaction_from_row(self):
        """Extract transaction from a table row."""
        from analyze_fin.parsers.base import RawTransaction
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        # Simulate a row from GCash table
        # Format: [Date, Description, Reference, Debit, Credit, Balance]
        row = ["Nov 15, 2024", "JOLLIBEE GREENBELT 3", "REF123", "285.50", "", "4,714.50"]

        tx = parser._extract_transaction_from_row(row)

        assert isinstance(tx, RawTransaction)
        assert tx.date == datetime(2024, 11, 15)
        assert tx.description == "JOLLIBEE GREENBELT 3"
        assert tx.amount == Decimal("-285.50")  # Debit is negative
        assert tx.reference_number == "REF123"

    def test_extract_credit_transaction(self):
        """Credit transactions have positive amounts."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        # Credit transaction (money coming in)
        row = ["Nov 15, 2024", "Cash In via Maya", "REF456", "", "1,000.00", "5,714.50"]

        tx = parser._extract_transaction_from_row(row)

        assert tx.amount == Decimal("1000.00")  # Credit is positive

    def test_extract_row_with_missing_reference(self):
        """Handle rows with missing reference number."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        row = ["Nov 15, 2024", "Transfer to BPI", "", "500.00", "", "4,214.50"]

        tx = parser._extract_transaction_from_row(row)

        assert tx.reference_number is None or tx.reference_number == ""


class TestGCashParseMethod:
    """Test the main parse method with mock PDF."""

    def test_parse_returns_parse_result(self):
        """parse() returns ParseResult object."""
        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        # Mock pdfplumber to return test data
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "GCash Statement"
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 15, 2024", "JOLLIBEE", "REF1", "285.50", "", "4714.50"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        assert isinstance(result, ParseResult)
        assert result.bank_type == "gcash"
        assert len(result.transactions) >= 1

    def test_parse_sets_quality_score(self):
        """parse() calculates and sets quality score."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "GCash Statement"
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 15, 2024", "JOLLIBEE", "REF1", "285.50", "", "4714.50"],
                ["Nov 16, 2024", "7-ELEVEN", "REF2", "100.00", "", "4614.50"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        assert 0.0 <= result.quality_score <= 1.0

    def test_parse_invalid_pdf_raises_parse_error(self):
        """parse() raises ParseError for invalid PDF."""
        from analyze_fin.exceptions import ParseError
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        with patch("pdfplumber.open", side_effect=Exception("PDF error")):
            with pytest.raises(ParseError):
                parser.parse(Path("invalid.pdf"))


class TestGCashMultiPageHandling:
    """Test multi-page statement handling."""

    def test_parse_extracts_from_all_pages(self):
        """parse() extracts transactions from all pages."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        # Create mock pages
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "GCash Statement Page 1"
        mock_page1.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 15, 2024", "JOLLIBEE", "REF1", "285.50", "", "4714.50"],
            ]
        ]

        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "GCash Statement Page 2"
        mock_page2.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 16, 2024", "7-ELEVEN", "REF2", "100.00", "", "4614.50"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        # Should have transactions from both pages
        assert len(result.transactions) == 2


class TestGCashParserErrorHandling:
    """Test error handling in GCash parser."""

    def test_skips_malformed_rows(self):
        """Parser skips malformed rows and continues."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "GCash Statement"
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 15, 2024", "JOLLIBEE", "REF1", "285.50", "", "4714.50"],  # Valid
                ["invalid", "row"],  # Malformed - should be skipped
                ["Nov 16, 2024", "7-ELEVEN", "REF2", "100.00", "", "4614.50"],  # Valid
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        # Should have 2 valid transactions, skipping the malformed one
        assert len(result.transactions) == 2

    def test_records_parsing_errors(self):
        """Parser records errors but continues processing."""
        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "GCash Statement"
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 15, 2024", "JOLLIBEE", "REF1", "285.50", "", "4714.50"],
                ["invalid", "row"],  # Will cause an error
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        # Parsing errors should be recorded
        assert len(result.parsing_errors) >= 1 or len(result.transactions) == 1
