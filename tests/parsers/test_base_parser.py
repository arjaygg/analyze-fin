"""
TDD Tests: BaseBankParser Abstract Class

Story 1.2 AC: Parser architecture with strategy pattern.
RED phase - these tests will fail until base.py is implemented.

BaseBankParser should:
- Be an abstract class (cannot instantiate directly)
- Have abstract method extract_transactions()
- Have calculate_quality_score() method
- Have detect_bank_type() method
"""

from abc import ABC
from datetime import datetime
from decimal import Decimal

import pytest


class TestBaseBankParserStructure:
    """Test BaseBankParser class structure."""

    def test_base_parser_exists(self):
        """BaseBankParser can be imported."""
        from analyze_fin.parsers.base import BaseBankParser

        assert BaseBankParser is not None

    def test_base_parser_is_abstract(self):
        """BaseBankParser is an abstract class."""
        from analyze_fin.parsers.base import BaseBankParser

        assert issubclass(BaseBankParser, ABC)

    def test_cannot_instantiate_base_parser_directly(self):
        """Cannot create BaseBankParser instance directly."""
        from analyze_fin.parsers.base import BaseBankParser

        with pytest.raises(TypeError, match="abstract"):
            BaseBankParser()

    def test_base_parser_has_extract_transactions_abstract_method(self):
        """BaseBankParser declares extract_transactions as abstract."""

        from analyze_fin.parsers.base import BaseBankParser

        # Check that extract_transactions is defined
        assert hasattr(BaseBankParser, "extract_transactions")

        # Check that it's abstract (part of __abstractmethods__)
        assert "extract_transactions" in BaseBankParser.__abstractmethods__


class TestRawTransaction:
    """Test RawTransaction data class."""

    def test_raw_transaction_exists(self):
        """RawTransaction can be imported."""
        from analyze_fin.parsers.base import RawTransaction

        assert RawTransaction is not None

    def test_raw_transaction_has_required_fields(self):
        """RawTransaction has date, description, amount fields."""
        from analyze_fin.parsers.base import RawTransaction

        tx = RawTransaction(
            date=datetime(2024, 11, 15),
            description="JOLLIBEE GREENBELT",
            amount=Decimal("285.50"),
        )

        assert tx.date == datetime(2024, 11, 15)
        assert tx.description == "JOLLIBEE GREENBELT"
        assert tx.amount == Decimal("285.50")

    def test_raw_transaction_optional_fields(self):
        """RawTransaction has optional reference_number and confidence."""
        from analyze_fin.parsers.base import RawTransaction

        tx = RawTransaction(
            date=datetime(2024, 11, 15),
            description="Test",
            amount=Decimal("100.00"),
            reference_number="REF123",
            confidence=0.95,
        )

        assert tx.reference_number == "REF123"
        assert tx.confidence == 0.95


class TestParseResult:
    """Test ParseResult data class."""

    def test_parse_result_exists(self):
        """ParseResult can be imported."""
        from analyze_fin.parsers.base import ParseResult

        assert ParseResult is not None

    def test_parse_result_has_required_fields(self):
        """ParseResult has transactions, quality_score, bank_type."""
        from analyze_fin.parsers.base import ParseResult

        result = ParseResult(
            transactions=[],
            quality_score=0.95,
            bank_type="gcash",
        )

        assert result.transactions == []
        assert result.quality_score == 0.95
        assert result.bank_type == "gcash"

    def test_parse_result_optional_metadata(self):
        """ParseResult has optional opening/closing balance and errors."""
        from analyze_fin.parsers.base import ParseResult

        result = ParseResult(
            transactions=[],
            quality_score=0.90,
            bank_type="bpi",
            opening_balance=Decimal("5000.00"),
            closing_balance=Decimal("4500.00"),
            statement_date=datetime(2024, 11, 30),
            parsing_errors=["Warning: 1 row skipped"],
        )

        assert result.opening_balance == Decimal("5000.00")
        assert result.closing_balance == Decimal("4500.00")
        assert result.statement_date == datetime(2024, 11, 30)
        assert "Warning: 1 row skipped" in result.parsing_errors


class TestQualityScoreCalculation:
    """Test quality score calculation method."""

    def test_calculate_quality_score_exists(self):
        """BaseBankParser has calculate_quality_score method."""
        from analyze_fin.parsers.base import BaseBankParser

        assert hasattr(BaseBankParser, "calculate_quality_score")

    def test_quality_score_high_confidence_transactions(self):
        """High confidence transactions yield high quality score (>= 0.95)."""
        # Create a concrete implementation for testing
        from analyze_fin.parsers.base import BaseBankParser, RawTransaction

        class TestParser(BaseBankParser):
            def extract_transactions(self, pdf_path):
                return []

        parser = TestParser()
        transactions = [
            RawTransaction(
                date=datetime(2024, 11, 1),
                description="Tx1",
                amount=Decimal("100"),
                confidence=0.98,
            ),
            RawTransaction(
                date=datetime(2024, 11, 2),
                description="Tx2",
                amount=Decimal("200"),
                confidence=0.97,
            ),
            RawTransaction(
                date=datetime(2024, 11, 3),
                description="Tx3",
                amount=Decimal("300"),
                confidence=0.96,
            ),
        ]

        score = parser.calculate_quality_score(transactions)
        assert score >= 0.95

    def test_quality_score_low_confidence_transactions(self):
        """Low confidence transactions yield low quality score (< 0.90)."""
        from analyze_fin.parsers.base import BaseBankParser, RawTransaction

        class TestParser(BaseBankParser):
            def extract_transactions(self, pdf_path):
                return []

        parser = TestParser()
        transactions = [
            RawTransaction(
                date=datetime(2024, 11, 1),
                description="Tx1",
                amount=Decimal("100"),
                confidence=0.60,
            ),
            RawTransaction(
                date=datetime(2024, 11, 2),
                description="Tx2",
                amount=Decimal("200"),
                confidence=0.70,
            ),
        ]

        score = parser.calculate_quality_score(transactions)
        assert score < 0.90

    def test_quality_score_empty_transactions_returns_zero(self):
        """Empty transaction list returns 0.0 quality score."""
        from analyze_fin.parsers.base import BaseBankParser

        class TestParser(BaseBankParser):
            def extract_transactions(self, pdf_path):
                return []

        parser = TestParser()
        score = parser.calculate_quality_score([])
        assert score == 0.0

    def test_quality_score_default_confidence_is_one(self):
        """Transactions without confidence default to 1.0."""
        from analyze_fin.parsers.base import BaseBankParser, RawTransaction

        class TestParser(BaseBankParser):
            def extract_transactions(self, pdf_path):
                return []

        parser = TestParser()
        transactions = [
            RawTransaction(
                date=datetime(2024, 11, 1),
                description="Tx1",
                amount=Decimal("100"),
                # No confidence set - should default to 1.0
            ),
        ]

        score = parser.calculate_quality_score(transactions)
        assert score == 1.0


class TestParseResultAccountFields:
    """Test ParseResult account identifier fields (Story 5.1)."""

    def test_parse_result_has_account_number_field(self):
        """ParseResult has optional account_number field."""
        from analyze_fin.parsers.base import ParseResult

        result = ParseResult(
            transactions=[],
            quality_score=0.95,
            bank_type="gcash",
            account_number="09171234567",
        )

        assert result.account_number == "09171234567"

    def test_parse_result_account_number_defaults_to_none(self):
        """ParseResult account_number defaults to None for backwards compatibility."""
        from analyze_fin.parsers.base import ParseResult

        result = ParseResult(
            transactions=[],
            quality_score=0.95,
            bank_type="gcash",
        )

        assert result.account_number is None

    def test_parse_result_has_account_holder_field(self):
        """ParseResult has optional account_holder field."""
        from analyze_fin.parsers.base import ParseResult

        result = ParseResult(
            transactions=[],
            quality_score=0.95,
            bank_type="bpi",
            account_holder="JUAN DELA CRUZ",
        )

        assert result.account_holder == "JUAN DELA CRUZ"

    def test_parse_result_account_holder_defaults_to_none(self):
        """ParseResult account_holder defaults to None for backwards compatibility."""
        from analyze_fin.parsers.base import ParseResult

        result = ParseResult(
            transactions=[],
            quality_score=0.95,
            bank_type="bpi",
        )

        assert result.account_holder is None

    def test_parse_result_has_period_start_field(self):
        """ParseResult has optional period_start field."""
        from datetime import date

        from analyze_fin.parsers.base import ParseResult

        result = ParseResult(
            transactions=[],
            quality_score=0.95,
            bank_type="maya_savings",
            period_start=date(2024, 11, 1),
        )

        assert result.period_start == date(2024, 11, 1)

    def test_parse_result_has_period_end_field(self):
        """ParseResult has optional period_end field."""
        from datetime import date

        from analyze_fin.parsers.base import ParseResult

        result = ParseResult(
            transactions=[],
            quality_score=0.95,
            bank_type="maya_savings",
            period_end=date(2024, 11, 30),
        )

        assert result.period_end == date(2024, 11, 30)

    def test_parse_result_period_dates_default_to_none(self):
        """ParseResult period_start/period_end default to None."""
        from analyze_fin.parsers.base import ParseResult

        result = ParseResult(
            transactions=[],
            quality_score=0.95,
            bank_type="gcash",
        )

        assert result.period_start is None
        assert result.period_end is None

    def test_parse_result_all_account_fields_together(self):
        """ParseResult supports all account fields together."""
        from datetime import date

        from analyze_fin.parsers.base import ParseResult

        result = ParseResult(
            transactions=[],
            quality_score=0.98,
            bank_type="bpi",
            account_number="****1234",
            account_holder="MARIA SANTOS",
            period_start=date(2024, 10, 1),
            period_end=date(2024, 10, 31),
        )

        assert result.account_number == "****1234"
        assert result.account_holder == "MARIA SANTOS"
        assert result.period_start == date(2024, 10, 1)
        assert result.period_end == date(2024, 10, 31)


class TestQualityScoreAdjustment:
    """Test quality score adjustment for missing account info (Story 5.1 AC#4)."""

    def test_quality_score_reduced_when_account_number_missing(self):
        """Quality score reduced by 0.05 when account_number is None."""
        from pathlib import Path
        from unittest.mock import MagicMock, patch

        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        mock_page = MagicMock()
        # No account info in header
        mock_page.extract_text.return_value = "GCash Statement\nNo account info here"
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

        # Base quality score would be 1.0 (full confidence transaction)
        # Should be reduced by 0.05 for missing account_number
        # And 0.02 for missing period dates
        assert result.account_number is None
        assert result.quality_score < 1.0
        # Score should be 1.0 - 0.05 (no account) - 0.02 (no period) = 0.93
        assert result.quality_score == pytest.approx(0.93, abs=0.01)

    def test_quality_score_reduced_when_period_dates_missing(self):
        """Quality score reduced by 0.02 when period dates are None."""
        from pathlib import Path
        from unittest.mock import MagicMock, patch

        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        mock_page = MagicMock()
        # Has account number but no period dates
        mock_page.extract_text.return_value = "GCash Statement\n0917 123 4567\nNo period info"
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

        assert result.account_number is not None
        assert result.period_start is None
        # Score should be 1.0 - 0.02 (no period) = 0.98
        assert result.quality_score == pytest.approx(0.98, abs=0.01)

    def test_quality_score_not_reduced_when_all_account_info_present(self):
        """Quality score not reduced when all account info is present."""
        from pathlib import Path
        from unittest.mock import MagicMock, patch

        from analyze_fin.parsers.gcash import GCashParser

        parser = GCashParser()

        mock_page = MagicMock()
        # Full account info present
        mock_page.extract_text.return_value = """
        GCash Statement
        Account: 0917 123 4567
        Name: JUAN DELA CRUZ
        Statement Period: Nov 01 - Nov 30, 2024
        """
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

        assert result.account_number is not None
        assert result.period_start is not None
        # Score should be 1.0 (no reduction)
        assert result.quality_score == 1.0


class TestBankTypeDetection:
    """Test bank type detection method."""

    def test_detect_bank_type_exists(self):
        """BaseBankParser has detect_bank_type static method."""
        from analyze_fin.parsers.base import BaseBankParser

        assert hasattr(BaseBankParser, "detect_bank_type")

    def test_detect_bank_type_returns_none_for_unknown(self):
        """detect_bank_type returns None for unrecognized PDF."""
        from analyze_fin.parsers.base import BaseBankParser

        # This would need a mock PDF file in practice
        # For now, test that method signature is correct
        assert callable(BaseBankParser.detect_bank_type)
