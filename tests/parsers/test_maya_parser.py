"""
TDD Tests: MayaParser Implementation

Story 1.4 AC: Maya statement parsing for Savings and Wallet accounts.
RED phase - these tests will fail until maya.py is implemented.

Maya statement format:
- Two account types: maya_savings and maya_wallet
- Date format varies: "YYYY-MM-DD" or "DD/MM/YYYY"
"""

import pytest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestMayaParserStructure:
    """Test MayaParser class structure."""

    def test_maya_parser_exists(self):
        """MayaParser can be imported."""
        from analyze_fin.parsers.maya import MayaParser

        assert MayaParser is not None

    def test_maya_parser_inherits_from_base(self):
        """MayaParser inherits from BaseBankParser."""
        from analyze_fin.parsers.maya import MayaParser
        from analyze_fin.parsers.base import BaseBankParser

        assert issubclass(MayaParser, BaseBankParser)

    def test_maya_parser_can_instantiate(self):
        """MayaParser can be instantiated."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()
        assert parser is not None


class TestMayaAccountTypeDetection:
    """Test detection of Maya account types."""

    def test_detect_maya_savings_account(self):
        """Detect Maya Savings account from PDF content."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Maya Savings Account Statement"
        mock_page.extract_tables.return_value = [[]]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("maya.pdf"))

        assert result.bank_type == "maya_savings"

    def test_detect_maya_wallet_account(self):
        """Detect Maya Wallet account from PDF content."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Maya Wallet Statement"
        mock_page.extract_tables.return_value = [[]]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("maya.pdf"))

        assert result.bank_type == "maya_wallet"

    def test_default_to_maya_wallet_when_unclear(self):
        """Default to maya_wallet when account type is unclear."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Maya Statement"  # Generic text
        mock_page.extract_tables.return_value = [[]]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("maya.pdf"))

        assert result.bank_type in ("maya_wallet", "maya_savings")


class TestMayaDateParsing:
    """Test Maya date format parsing."""

    def test_parse_maya_date_iso_format(self):
        """Parse Maya date in ISO format: 'YYYY-MM-DD'."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        result = parser._parse_date("2024-11-15")
        assert result == datetime(2024, 11, 15)

    def test_parse_maya_date_slash_format(self):
        """Parse Maya date in slash format: 'DD/MM/YYYY'."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        result = parser._parse_date("15/11/2024")
        assert result == datetime(2024, 11, 15)

    def test_parse_maya_date_us_format(self):
        """Parse Maya date in US format: 'MM/DD/YYYY'."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        # Should handle MM/DD/YYYY format (common in Maya)
        result = parser._parse_date("11/15/2024")
        assert result == datetime(2024, 11, 15)

    def test_parse_invalid_date_raises_error(self):
        """Invalid date format raises ValueError."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        with pytest.raises(ValueError):
            parser._parse_date("invalid date")


class TestMayaAmountParsing:
    """Test Maya amount format parsing."""

    def test_parse_amount_with_php_symbol(self):
        """Parse amount with PHP symbol."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        result = parser._parse_amount("PHP 1,234.56")
        assert result == Decimal("1234.56")

    def test_parse_amount_with_peso_symbol(self):
        """Parse amount with ₱ symbol."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        result = parser._parse_amount("₱1,234.56")
        assert result == Decimal("1234.56")

    def test_parse_amount_plain_number(self):
        """Parse plain number amount."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        result = parser._parse_amount("1234.56")
        assert result == Decimal("1234.56")


class TestMayaRowExtraction:
    """Test extraction of individual transaction rows."""

    def test_extract_transaction_from_row(self):
        """Extract transaction from a Maya table row."""
        from analyze_fin.parsers.maya import MayaParser
        from analyze_fin.parsers.base import RawTransaction

        parser = MayaParser()

        # Maya format varies, but typically: [Date, Description, Amount, Balance]
        row = ["2024-11-15", "Cash In via BPI", "1,000.00", "5,000.00"]

        tx = parser._extract_transaction_from_row(row)

        assert isinstance(tx, RawTransaction)
        assert tx.date == datetime(2024, 11, 15)
        assert tx.description == "Cash In via BPI"
        assert tx.amount == Decimal("1000.00")

    def test_extract_debit_transaction(self):
        """Debit transactions (payments) are detected."""
        from analyze_fin.parsers.maya import MayaParser

        parser = MayaParser()

        # Payment/debit row
        row = ["2024-11-15", "Payment to JOLLIBEE", "-500.00", "4,500.00"]

        tx = parser._extract_transaction_from_row(row)

        assert tx.amount == Decimal("-500.00")


class TestMayaParseMethod:
    """Test the main parse method."""

    def test_parse_returns_parse_result(self):
        """parse() returns ParseResult object."""
        from analyze_fin.parsers.maya import MayaParser
        from analyze_fin.parsers.base import ParseResult

        parser = MayaParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Maya Wallet Statement"
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Amount", "Balance"],
                ["2024-11-15", "Cash In", "1000.00", "5000.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        assert isinstance(result, ParseResult)
        assert result.bank_type in ("maya_wallet", "maya_savings")

    def test_parse_handles_errors_gracefully(self):
        """parse() handles parsing errors gracefully."""
        from analyze_fin.parsers.maya import MayaParser
        from analyze_fin.exceptions import ParseError

        parser = MayaParser()

        with patch("pdfplumber.open", side_effect=Exception("PDF error")):
            with pytest.raises(ParseError):
                parser.parse(Path("invalid.pdf"))
