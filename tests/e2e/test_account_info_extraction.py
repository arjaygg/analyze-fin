"""
E2E Tests: Account Info Extraction (Story 5.1)

Verifies that parsers correctly extract account identifiers from statements
and that quality scores reflect extraction completeness.

Story: 5.1 Parser Account Identifier Extraction
"""

from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from analyze_fin.parsers.base import ParseResult, RawTransaction
from analyze_fin.parsers.bpi import BPIParser
from analyze_fin.parsers.gcash import GCashParser
from analyze_fin.parsers.maya import MayaParser


@pytest.fixture(autouse=True)
def mock_pdf_exists():
    """Mock Path.exists() to return True for PDF files in tests."""
    original_exists = Path.exists

    def mocked_exists(self):
        if str(self).endswith('.pdf'):
            return True
        return original_exists(self)

    with patch.object(Path, 'exists', mocked_exists):
        yield


class TestGCashAccountInfoIntegration:
    """Integration tests for GCash account info extraction."""

    @pytest.mark.integration
    def test_gcash_full_account_info_extraction(self):
        """
        GIVEN a GCash statement with complete account info
        WHEN I parse the PDF
        THEN all account fields are extracted
        AND quality score is not reduced
        """
        # GIVEN - Mock PDF with complete account info
        parser = GCashParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        GCash Statement
        Account: 0917 123 4567
        Name: JUAN DELA CRUZ
        Statement Period: Nov 01 - Nov 30, 2024

        Transaction History
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 15, 2024", "JOLLIBEE GREENBELT", "REF123", "285.50", "", "4714.50"],
                ["Nov 16, 2024", "CASH IN", "REF124", "", "1000.00", "5714.50"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        # WHEN
        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("gcash_statement.pdf"))

        # THEN
        assert result.bank_type == "gcash"
        assert result.account_number == "09171234567"
        assert result.account_holder == "JUAN DELA CRUZ"
        assert result.period_start == date(2024, 11, 1)
        assert result.period_end == date(2024, 11, 30)
        assert result.quality_score == 1.0  # No reduction
        assert len(result.transactions) == 2

    @pytest.mark.integration
    def test_gcash_partial_account_info_quality_adjustment(self):
        """
        GIVEN a GCash statement with missing account number
        WHEN I parse the PDF
        THEN quality score is reduced by 0.05
        AND parsing still succeeds
        """
        # GIVEN - Mock PDF without account number
        parser = GCashParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        GCash Statement
        Statement Period: Nov 01 - Nov 30, 2024

        Transaction History
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 15, 2024", "JOLLIBEE GREENBELT", "REF123", "285.50", "", "4714.50"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        # WHEN
        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("gcash_statement.pdf"))

        # THEN
        assert result.account_number is None
        assert result.period_start == date(2024, 11, 1)
        assert result.quality_score == pytest.approx(0.95, abs=0.01)  # -0.05 for missing account
        assert len(result.transactions) == 1  # Parsing still works


class TestBPIAccountInfoIntegration:
    """Integration tests for BPI account info extraction."""

    @pytest.mark.integration
    def test_bpi_full_account_info_with_masking(self):
        """
        GIVEN a BPI statement with account number
        WHEN I parse the PDF
        THEN account number is masked to show only last 4 digits
        AND all other account fields are extracted
        """
        # GIVEN - Mock PDF with BPI account info
        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        BPI STATEMENT OF ACCOUNT
        Account Number: 1234-5678-9012
        Account Name: MARIA SANTOS
        Statement Period: October 01, 2024 - October 31, 2024
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["10/15/2024", "ATM WITHDRAWAL", "5000.00", "", "10000.00"],
                ["10/20/2024", "SALARY DEPOSIT", "", "25000.00", "35000.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        # WHEN
        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("bpi_statement.pdf"))

        # THEN
        assert result.bank_type == "bpi"
        assert result.account_number == "****9012"  # Masked
        assert result.account_holder == "MARIA SANTOS"
        assert result.period_start == date(2024, 10, 1)
        assert result.period_end == date(2024, 10, 31)
        assert result.quality_score == 1.0
        assert len(result.transactions) == 2

    @pytest.mark.integration
    def test_bpi_missing_all_account_info_quality_reduction(self):
        """
        GIVEN a BPI statement without any account info
        WHEN I parse the PDF
        THEN quality score is reduced by 0.07 total
        AND parsing completes without errors
        """
        # GIVEN - Mock PDF without account info
        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        BPI STATEMENT
        Transaction Details Below
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["10/15/2024", "ATM WITHDRAWAL", "5000.00", "", "10000.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        # WHEN
        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("bpi_statement.pdf"))

        # THEN
        assert result.account_number is None
        assert result.account_holder is None
        assert result.period_start is None
        assert result.period_end is None
        # -0.05 for missing account, -0.02 for missing period = 0.93
        assert result.quality_score == pytest.approx(0.93, abs=0.01)
        assert len(result.transactions) == 1


class TestMayaAccountInfoIntegration:
    """Integration tests for Maya account info extraction."""

    @pytest.mark.integration
    def test_maya_savings_account_info_extraction(self):
        """
        GIVEN a Maya savings statement with account info
        WHEN I parse the PDF
        THEN account type is detected as maya_savings
        AND all account fields are extracted
        """
        # GIVEN - Mock PDF with Maya savings info
        parser = MayaParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        MAYA SAVINGS ACCOUNT STATEMENT
        Account Number: 1234567890
        Account Holder: PEDRO REYES
        Statement Period: November 01, 2024 - November 30, 2024
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Amount", "Balance"],
                ["2024-11-15", "INTEREST CREDIT", "50.00", "10050.00"],
                ["2024-11-20", "TRANSFER OUT", "-1000.00", "9050.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        # WHEN
        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("maya_statement.pdf"))

        # THEN
        assert result.bank_type == "maya_savings"
        assert result.account_number == "1234567890"
        assert result.account_holder == "PEDRO REYES"
        assert result.period_start == date(2024, 11, 1)
        assert result.period_end == date(2024, 11, 30)
        assert result.quality_score == 1.0
        assert len(result.transactions) == 2

    @pytest.mark.integration
    def test_maya_wallet_account_type_detection(self):
        """
        GIVEN a Maya wallet statement
        WHEN I parse the PDF
        THEN account type is detected as maya_wallet
        """
        # GIVEN - Mock PDF with Maya wallet header
        parser = MayaParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        MAYA WALLET STATEMENT
        Account ID: 9876543210
        Account Holder: ANA GARCIA
        Statement Period: December 01, 2024 - December 31, 2024
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Amount", "Balance"],
                ["2024-12-10", "QR PAYMENT", "-150.00", "850.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        # WHEN
        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("maya_wallet.pdf"))

        # THEN
        assert result.bank_type == "maya_wallet"
        assert result.account_number == "9876543210"


class TestBackwardsCompatibility:
    """Tests to ensure backwards compatibility with existing code."""

    @pytest.mark.integration
    def test_parse_result_without_account_fields_still_works(self):
        """
        GIVEN existing code that doesn't use account fields
        WHEN ParseResult is created without account fields
        THEN all defaults are None and existing code still works
        """
        # GIVEN/WHEN - Create ParseResult like old code would
        result = ParseResult(
            transactions=[],
            quality_score=0.95,
            bank_type="gcash",
        )

        # THEN - All account fields default to None
        assert result.account_number is None
        assert result.account_holder is None
        assert result.period_start is None
        assert result.period_end is None

        # Old code accessing existing fields still works
        assert result.transactions == []
        assert result.quality_score == 0.95
        assert result.bank_type == "gcash"

    @pytest.mark.integration
    def test_existing_parser_tests_still_pass(self):
        """
        GIVEN parsers with new account info extraction
        WHEN parsing PDFs that worked before
        THEN transactions are still extracted correctly
        """
        # This test validates that the core parsing logic is unchanged
        parser = GCashParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "GCash Statement"
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 15, 2024", "GRAB RIDE", "REF001", "150.00", "", "850.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        # Core functionality unchanged
        assert len(result.transactions) == 1
        tx = result.transactions[0]
        assert tx.description == "GRAB RIDE"
        assert tx.amount == Decimal("-150.00")


class TestQualityScoreEdgeCases:
    """Tests for quality score edge cases."""

    @pytest.mark.integration
    def test_quality_score_floor_at_zero(self):
        """
        GIVEN a parser with very low base quality score
        WHEN account info is missing
        THEN quality score doesn't go below 0
        """
        parser = GCashParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "GCash"  # No account info
        # Very low confidence transactions
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 15, 2024", "X", "", "0.01", "", "0.01"],  # Short description = low confidence
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        # Quality score should not go below 0
        assert result.quality_score >= 0.0

    @pytest.mark.integration
    def test_quality_score_with_only_period_missing(self):
        """
        GIVEN a statement with account number but no period
        WHEN parsed
        THEN only 0.02 is deducted from quality score
        """
        parser = BPIParser()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        BPI STATEMENT
        Account Number: 1234567890123
        Account Name: TEST USER
        """
        mock_page.extract_tables.return_value = [
            [
                ["Date", "Description", "Debit", "Credit", "Balance"],
                ["10/15/2024", "PAYMENT", "100.00", "", "900.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        assert result.account_number is not None
        assert result.period_start is None
        # -0.02 for missing period only
        assert result.quality_score == pytest.approx(0.98, abs=0.01)


class TestMultiPageStatements:
    """Tests for statements spanning multiple pages."""

    @pytest.mark.integration
    def test_account_info_extracted_from_first_page_only(self):
        """
        GIVEN a multi-page statement
        WHEN parsed
        THEN account info is extracted from first page
        AND transactions are extracted from all pages
        """
        parser = GCashParser()

        # First page with account info
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = """
        GCash Statement
        0917 999 8888
        Statement Period: Nov 01 - Nov 30, 2024
        """
        mock_page1.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 01, 2024", "TX1", "R1", "100.00", "", "900.00"],
            ]
        ]

        # Second page without account info (continuation)
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Transaction History Continued"
        mock_page2.extract_tables.return_value = [
            [
                ["Date", "Description", "Ref#", "Debit", "Credit", "Balance"],
                ["Nov 15, 2024", "TX2", "R2", "200.00", "", "700.00"],
            ]
        ]

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("multi_page.pdf"))

        # Account info from first page
        assert result.account_number == "09179998888"
        assert result.period_start == date(2024, 11, 1)

        # Transactions from all pages
        assert len(result.transactions) == 2


@pytest.mark.integration
def test_all_parsers_return_parse_result_with_account_fields():
    """
    GIVEN all three parser types
    WHEN parsing any statement
    THEN ParseResult always includes account fields (may be None)
    """
    parsers = [
        (GCashParser(), "GCash"),
        (BPIParser(), "BPI"),
        (MayaParser(), "Maya"),
    ]

    for parser, name in parsers:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = f"{name} Statement"
        mock_page.extract_tables.return_value = []

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = parser.parse(Path("test.pdf"))

        # All parsers return ParseResult with account fields accessible
        assert hasattr(result, "account_number")
        assert hasattr(result, "account_holder")
        assert hasattr(result, "period_start")
        assert hasattr(result, "period_end")
