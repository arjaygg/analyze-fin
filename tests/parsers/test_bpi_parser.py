"""
TDD Tests: BPIParser Implementation

Story 1.3 AC: BPI statement parsing with password handling.
RED phase - these tests will fail until bpi.py is implemented.

BPI statement format:
- Date format: "MM/DD/YYYY" (e.g., "11/15/2024")
- Password format: SURNAME + last 4 phone digits (e.g., "GARCIA1234")
- Password-protected PDFs
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestBPIParserStructure:
    """Test BPIParser class structure."""

    def test_bpi_parser_exists(self):
        """BPIParser can be imported."""
        from analyze_fin.parsers.bpi import BPIParser

        assert BPIParser is not None

    def test_bpi_parser_inherits_from_base(self):
        """BPIParser inherits from BaseBankParser."""
        from analyze_fin.parsers.base import BaseBankParser
        from analyze_fin.parsers.bpi import BPIParser

        assert issubclass(BPIParser, BaseBankParser)

    def test_bpi_parser_can_instantiate(self):
        """BPIParser can be instantiated."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()
        assert parser is not None


class TestBPIDateParsing:
    """Test BPI date format parsing."""

    def test_parse_bpi_date_format(self):
        """Parse BPI date format: 'MM/DD/YYYY'."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        result = parser._parse_date("11/15/2024")
        assert result == datetime(2024, 11, 15)

    def test_parse_bpi_date_various_dates(self):
        """Parse dates for various formats."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        test_cases = [
            ("01/01/2024", datetime(2024, 1, 1)),
            ("02/28/2024", datetime(2024, 2, 28)),
            ("12/31/2024", datetime(2024, 12, 31)),
        ]

        for date_str, expected in test_cases:
            result = parser._parse_date(date_str)
            assert result == expected, f"Failed for {date_str}"

    def test_parse_invalid_date_raises_error(self):
        """Invalid date format raises ValueError."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        with pytest.raises(ValueError):
            parser._parse_date("invalid date")


class TestBPIAmountParsing:
    """Test BPI amount format parsing."""

    def test_parse_amount_positive(self):
        """Parse positive amount."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        result = parser._parse_amount("1,234.56")
        assert result == Decimal("1234.56")

    def test_parse_amount_negative_parentheses(self):
        """Parse negative amount in parentheses."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        result = parser._parse_amount("(1,234.56)")
        assert result == Decimal("-1234.56")

    def test_parse_credit_debit_columns(self):
        """Handle separate debit/credit columns like BPI statements."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        # BPI often has separate columns for debits and credits
        debit = parser._parse_amount("500.00")
        credit = parser._parse_amount("1,000.00")

        assert debit == Decimal("500.00")
        assert credit == Decimal("1000.00")


class TestBPIPasswordHandling:
    """Test password-protected PDF handling."""

    def test_parse_with_password_parameter(self):
        """parse() accepts password parameter."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        # Verify method signature accepts password
        import inspect
        sig = inspect.signature(parser.parse)
        assert "password" in sig.parameters

    def test_password_protected_pdf_without_password_raises_error(self):
        """Parsing password-protected PDF without password raises error."""
        from analyze_fin.exceptions import ParseError
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        # Mock pdfplumber to simulate password-protected PDF
        with patch("pdfplumber.open") as mock_open:
            mock_open.side_effect = Exception("PDF is encrypted")

            with pytest.raises(ParseError, match="password"):
                parser.parse(Path("protected.pdf"))

    def test_password_protected_pdf_with_correct_password_succeeds(self):
        """Parsing with correct password succeeds."""
        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Bank of the Philippine Islands Statement"
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["11/15/2024", "ATM WITHDRAWAL", "500.00", "", "9,500.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("protected.pdf"), password="GARCIA1234")

        assert isinstance(result, ParseResult)
        assert result.bank_type == "bpi"
        assert len(result.transactions) >= 1


class TestBPIRowExtraction:
    """Test extraction of individual transaction rows."""

    def test_extract_transaction_from_row(self):
        """Extract transaction from a BPI table row."""
        from analyze_fin.parsers.base import RawTransaction
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        # BPI format: [Date, Description, Debit, Credit, Balance]
        row = ["11/15/2024", "ATM WITHDRAWAL - SM NORTH", "500.00", "", "9,500.00"]

        tx = parser._extract_transaction_from_row(row)

        assert isinstance(tx, RawTransaction)
        assert tx.date == datetime(2024, 11, 15)
        assert tx.description == "ATM WITHDRAWAL - SM NORTH"
        assert tx.amount == Decimal("-500.00")  # Debit is negative

    def test_extract_credit_transaction(self):
        """Credit transactions have positive amounts."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        # Salary deposit (credit)
        row = ["11/15/2024", "SALARY CREDIT - COMPANY INC", "", "50,000.00", "59,500.00"]

        tx = parser._extract_transaction_from_row(row)

        assert tx.amount == Decimal("50000.00")  # Credit is positive


class TestBPIParseMethod:
    """Test the main parse method."""

    def test_parse_returns_parse_result(self):
        """parse() returns ParseResult object."""
        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Bank of the Philippine Islands"
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["11/15/2024", "ATM WITHDRAWAL", "500.00", "", "9500.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        assert isinstance(result, ParseResult)
        assert result.bank_type == "bpi"

    def test_parse_sets_quality_score(self):
        """parse() calculates and sets quality score."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Bank of the Philippine Islands"
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["11/15/2024", "ATM", "500.00", "", "9500.00"],
                ["11/16/2024", "DEPOSIT", "", "1000.00", "10500.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        assert 0.0 <= result.quality_score <= 1.0


class TestBPIAccountInfoExtraction:
    """Test BPI account identifier extraction (Story 5.1)."""

    def test_extract_account_number_masked(self):
        """Extract and mask account number from BPI statement header."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        Bank of the Philippine Islands
        SAVINGS ACCOUNT
        Account Number: 1234-5678-9012
        Account Name: JUAN DELA CRUZ
        Statement Period: November 01, 2024 - November 30, 2024
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["11/15/2024", "ATM WITHDRAWAL", "500.00", "", "9500.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        # Account number should be masked to show only last 4 digits
        assert result.account_number == "****9012"

    def test_extract_account_holder_name(self):
        """Extract account holder name from BPI statement."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        Bank of the Philippine Islands
        Account Number: 1234-5678-9012
        Account Name: MARIA SANTOS
        Statement Period: November 01, 2024 - November 30, 2024
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["11/15/2024", "ATM WITHDRAWAL", "500.00", "", "9500.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        assert result.account_holder == "MARIA SANTOS"

    def test_extract_statement_period_dates(self):
        """Extract statement period start and end dates."""
        from datetime import date

        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        Bank of the Philippine Islands
        Account Number: 1234-5678-9012
        Account Name: JUAN DELA CRUZ
        Statement Period: November 01, 2024 - November 30, 2024
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["11/15/2024", "ATM WITHDRAWAL", "500.00", "", "9500.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        assert result.period_start == date(2024, 11, 1)
        assert result.period_end == date(2024, 11, 30)

    def test_account_info_missing_returns_none(self):
        """Missing account info returns None (backwards compatible)."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        Bank of the Philippine Islands
        Some other content without account info
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["11/15/2024", "ATM WITHDRAWAL", "500.00", "", "9500.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        # Missing account info should be None, not fail
        assert result.account_number is None
        assert result.account_holder is None
        assert result.period_start is None
        assert result.period_end is None

    def test_extract_account_info_method_exists(self):
        """BPIParser has _extract_account_info method."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()
        assert hasattr(parser, "_extract_account_info")
        assert callable(parser._extract_account_info)

    def test_account_number_various_formats(self):
        """Handle various account number formats."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        # Test with different formats
        test_cases = [
            ("Account Number: 1234-5678-9012", "****9012"),
            ("Account No: 123456789012", "****9012"),
            ("Acct No.: 1234 5678 9012", "****9012"),
        ]

        for header_text, expected in test_cases:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = f"BPI Statement\n{header_text}\n"
            mock_page.extract_tables.return_value = [
                [
                    ["Date", "Description", "Debit", "Credit", "Balance"],
                    ["11/15/2024", "TEST", "100.00", "", "1000.00"],
                ]
            ]

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
            mock_pdf.__exit__ = MagicMock(return_value=False)

            with patch("pdfplumber.open", return_value=mock_pdf):
                result = parser.parse(Path("test.pdf"))

            assert result.account_number == expected, f"Failed for: {header_text}"


class TestBPISecurityRequirements:
    """Test that password is handled securely."""

    def test_password_not_stored_in_result(self):
        """Password is not stored in ParseResult."""
        from analyze_fin.parsers.bpi import BPIParser

        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Bank of the Philippine Islands"
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["11/15/2024", "ATM", "500.00", "", "9500.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"), password="SECRET123")

        # Verify password is not stored anywhere in result
        assert not hasattr(result, "password")

        # Check result doesn't contain password in any string fields
        result_str = str(result)
        assert "SECRET123" not in result_str
