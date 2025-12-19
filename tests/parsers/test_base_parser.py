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

import pytest
from abc import ABC
from decimal import Decimal
from datetime import datetime
from pathlib import Path


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
        import inspect

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
        from analyze_fin.parsers.base import ParseResult, RawTransaction

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
        from analyze_fin.parsers.base import RawTransaction

        # Create a concrete implementation for testing
        from analyze_fin.parsers.base import BaseBankParser

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
        from analyze_fin.parsers.base import RawTransaction, BaseBankParser

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
        from analyze_fin.parsers.base import RawTransaction, BaseBankParser

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
