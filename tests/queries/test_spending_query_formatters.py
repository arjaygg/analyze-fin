"""
Unit Tests: SpendingQuery helper formatting functions.
"""

from datetime import datetime
from decimal import Decimal

from analyze_fin.queries.spending import format_currency, format_date_localized


class TestFormatCurrency:
    """Test Philippine peso currency formatting."""

    def test_p2_format_currency_basic(self):
        amount = Decimal("1234.56")
        formatted = format_currency(amount)
        assert formatted == "₱1,234.56"

    def test_p2_format_currency_with_thousands(self):
        amount = Decimal("1234567.89")
        formatted = format_currency(amount)
        assert formatted == "₱1,234,567.89"

    def test_p2_format_currency_small_amount(self):
        amount = Decimal("5.00")
        formatted = format_currency(amount)
        assert formatted == "₱5.00"

    def test_p2_format_currency_zero(self):
        amount = Decimal("0")
        formatted = format_currency(amount)
        assert formatted == "₱0.00"


class TestFormatDateLocalized:
    """Test localized date formatting."""

    def test_p2_format_date_localized_basic(self):
        date = datetime(2024, 11, 15)
        formatted = format_date_localized(date)
        assert formatted == "Nov 15, 2024"

    def test_p2_format_date_localized_january(self):
        date = datetime(2024, 1, 1)
        formatted = format_date_localized(date)
        assert formatted == "Jan 01, 2024"

    def test_p2_format_date_localized_december(self):
        date = datetime(2024, 12, 25)
        formatted = format_date_localized(date)
        assert formatted == "Dec 25, 2024"


