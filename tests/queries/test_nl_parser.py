"""
Unit Tests: Natural Language Query Parser

Tests for the NLQueryParser class which parses natural language queries
into SpendingQuery filter parameters.

Test Levels:
- Unit: NLQueryParser.parse() and helper methods
"""

from datetime import datetime
from decimal import Decimal

import pytest

from analyze_fin.queries.nl_parser import NLQueryParser, ParsedQuery, parse_natural_language_query


@pytest.fixture
def parser():
    """Create parser instance for tests."""
    return NLQueryParser()


# ============================================================================
# Test: Category Extraction
# ============================================================================


class TestCategoryExtraction:
    """Test category extraction from queries."""

    def test_extracts_food_category(self, parser):
        """
        GIVEN a query about food
        WHEN parsing
        THEN Food & Dining category is extracted
        """
        result = parser.parse("How much did I spend on food?")
        assert result.category == "Food & Dining"

    def test_extracts_dining_category(self, parser):
        """
        GIVEN a query about dining
        WHEN parsing
        THEN Food & Dining category is extracted
        """
        result = parser.parse("Show my dining expenses")
        assert result.category == "Food & Dining"

    def test_extracts_transport_category(self, parser):
        """
        GIVEN a query about transportation
        WHEN parsing
        THEN Transportation category is extracted
        """
        result = parser.parse("Total transport costs")
        assert result.category == "Transportation"

    def test_extracts_groceries_category(self, parser):
        """
        GIVEN a query about groceries
        WHEN parsing
        THEN Groceries category is extracted
        """
        result = parser.parse("How much on groceries?")
        assert result.category == "Groceries"

    def test_extracts_bills_category(self, parser):
        """
        GIVEN a query about bills
        WHEN parsing
        THEN Bills & Utilities category is extracted
        """
        result = parser.parse("Show my bills")
        assert result.category == "Bills & Utilities"

    def test_no_category_returns_none(self, parser):
        """
        GIVEN a query without category keywords
        WHEN parsing
        THEN category is None
        """
        result = parser.parse("Show all transactions")
        assert result.category is None


# ============================================================================
# Test: Merchant Extraction
# ============================================================================


class TestMerchantExtraction:
    """Test merchant extraction from queries."""

    def test_extracts_merchant_from_pattern(self, parser):
        """
        GIVEN a query with "from Merchant" pattern
        WHEN parsing
        THEN merchant name is extracted
        """
        result = parser.parse("What did I buy from Jollibee?")
        assert result.merchant == "Jollibee"

    def test_extracts_merchant_at_pattern(self, parser):
        """
        GIVEN a query with "at Merchant" pattern
        WHEN parsing
        THEN merchant name is extracted
        """
        result = parser.parse("Transactions at McDonald's")
        assert result.merchant == "McDonald's"

    def test_extracts_multi_word_merchant(self, parser):
        """
        GIVEN a query with multi-word merchant
        WHEN parsing
        THEN full merchant name is extracted
        """
        result = parser.parse("from Greenwich Pizza")
        assert result.merchant == "Greenwich Pizza"

    def test_no_merchant_returns_none(self, parser):
        """
        GIVEN a query without merchant pattern
        WHEN parsing
        THEN merchant is None
        """
        result = parser.parse("Show all my transactions")
        assert result.merchant is None


# ============================================================================
# Test: Date Range Extraction
# ============================================================================


class TestDateRangeExtraction:
    """Test date range extraction from queries."""

    def test_extracts_month_name(self, parser):
        """
        GIVEN a query with month name
        WHEN parsing
        THEN correct date range is extracted
        """
        result = parser.parse("spending in November 2024")
        assert result.start_date == datetime(2024, 11, 1)
        assert result.end_date == datetime(2024, 11, 30)

    def test_extracts_abbreviated_month(self, parser):
        """
        GIVEN a query with abbreviated month
        WHEN parsing
        THEN correct date range is extracted
        """
        result = parser.parse("transactions in nov 2024")
        assert result.start_date == datetime(2024, 11, 1)
        assert result.end_date == datetime(2024, 11, 30)

    def test_extracts_last_month(self, parser):
        """
        GIVEN a query with "last month"
        WHEN parsing
        THEN previous month date range is extracted
        """
        result = parser.parse("spending last month")
        assert result.start_date is not None
        assert result.end_date is not None
        # Start date should be first of last month
        assert result.start_date.day == 1

    def test_extracts_this_month(self, parser):
        """
        GIVEN a query with "this month"
        WHEN parsing
        THEN current month date range is extracted
        """
        result = parser.parse("spending this month")
        now = datetime.now()
        assert result.start_date.month == now.month
        assert result.start_date.year == now.year
        assert result.start_date.day == 1

    def test_extracts_today(self, parser):
        """
        GIVEN a query with "today"
        WHEN parsing
        THEN today's date is extracted
        """
        result = parser.parse("transactions today")
        now = datetime.now()
        assert result.start_date.year == now.year
        assert result.start_date.month == now.month
        assert result.start_date.day == now.day

    def test_no_date_returns_none(self, parser):
        """
        GIVEN a query without date references
        WHEN parsing
        THEN start_date and end_date are None
        """
        result = parser.parse("Show all food expenses")
        assert result.start_date is None
        assert result.end_date is None


# ============================================================================
# Test: Amount Extraction
# ============================================================================


class TestAmountExtraction:
    """Test amount filter extraction from queries."""

    def test_extracts_over_amount(self, parser):
        """
        GIVEN a query with "over X" pattern
        WHEN parsing
        THEN min_amount is extracted
        """
        result = parser.parse("transactions over 1000")
        assert result.min_amount == Decimal("1000")

    def test_extracts_above_amount(self, parser):
        """
        GIVEN a query with "above X" pattern
        WHEN parsing
        THEN min_amount is extracted
        """
        result = parser.parse("spending above 500")
        assert result.min_amount == Decimal("500")

    def test_extracts_under_amount(self, parser):
        """
        GIVEN a query with "under X" pattern
        WHEN parsing
        THEN max_amount is extracted
        """
        result = parser.parse("transactions under 200")
        assert result.max_amount == Decimal("200")

    def test_extracts_less_than_amount(self, parser):
        """
        GIVEN a query with "less than X" pattern
        WHEN parsing
        THEN max_amount is extracted
        """
        result = parser.parse("items less than 100")
        assert result.max_amount == Decimal("100")

    def test_extracts_between_amounts(self, parser):
        """
        GIVEN a query with "between X and Y" pattern
        WHEN parsing
        THEN both min and max amounts are extracted
        """
        result = parser.parse("transactions between 500 and 2000")
        assert result.min_amount == Decimal("500")
        assert result.max_amount == Decimal("2000")

    def test_extracts_amount_with_peso_sign(self, parser):
        """
        GIVEN a query with peso sign
        WHEN parsing
        THEN amount is extracted correctly
        """
        result = parser.parse("transactions over ₱1000")
        assert result.min_amount == Decimal("1000")

    def test_extracts_amount_with_comma(self, parser):
        """
        GIVEN a query with comma-formatted amount
        WHEN parsing
        THEN amount is extracted correctly
        """
        result = parser.parse("transactions over 10,000")
        assert result.min_amount == Decimal("10000")

    def test_no_amount_returns_none(self, parser):
        """
        GIVEN a query without amount patterns
        WHEN parsing
        THEN min_amount and max_amount are None
        """
        result = parser.parse("Show food transactions")
        assert result.min_amount is None
        assert result.max_amount is None


# ============================================================================
# Test: Intent Detection
# ============================================================================


class TestIntentDetection:
    """Test query intent detection."""

    def test_detects_total_intent(self, parser):
        """
        GIVEN a query asking for total
        WHEN parsing
        THEN intent is 'total'
        """
        result = parser.parse("How much did I spend on food?")
        assert result.intent == "total"

    def test_detects_count_intent(self, parser):
        """
        GIVEN a query asking for count
        WHEN parsing
        THEN intent is 'count'
        """
        result = parser.parse("How many transactions from Jollibee?")
        assert result.intent == "count"

    def test_detects_average_intent(self, parser):
        """
        GIVEN a query asking for average
        WHEN parsing
        THEN intent is 'average'
        """
        result = parser.parse("Average food expense")
        assert result.intent == "average"

    def test_default_list_intent(self, parser):
        """
        GIVEN a query without specific intent
        WHEN parsing
        THEN intent defaults to 'list'
        """
        result = parser.parse("Show me transactions")
        assert result.intent == "list"


# ============================================================================
# Test: Combined Queries
# ============================================================================


class TestCombinedQueries:
    """Test parsing complex queries with multiple filters."""

    def test_category_and_date(self, parser):
        """
        GIVEN a query with category and date
        WHEN parsing
        THEN both are extracted
        """
        result = parser.parse("Food expenses in November 2024")
        assert result.category == "Food & Dining"
        assert result.start_date == datetime(2024, 11, 1)

    def test_merchant_and_amount(self, parser):
        """
        GIVEN a query with merchant and amount
        WHEN parsing
        THEN both are extracted
        """
        result = parser.parse("Purchases from Jollibee over 200")
        assert result.merchant == "Jollibee"
        assert result.min_amount == Decimal("200")

    def test_full_complex_query(self, parser):
        """
        GIVEN a complex query with multiple filters
        WHEN parsing
        THEN all filters are extracted
        """
        result = parser.parse("How much did I spend on food from Jollibee in November 2024 over 100?")
        assert result.intent == "total"
        assert result.category == "Food & Dining"
        assert result.merchant == "Jollibee"
        assert result.start_date == datetime(2024, 11, 1)
        assert result.min_amount == Decimal("100")


# ============================================================================
# Test: Convenience Function
# ============================================================================


class TestConvenienceFunction:
    """Test the parse_natural_language_query function."""

    def test_convenience_function_works(self):
        """
        GIVEN a query string
        WHEN using convenience function
        THEN ParsedQuery is returned
        """
        result = parse_natural_language_query("Food expenses last month")
        assert isinstance(result, ParsedQuery)
        assert result.category == "Food & Dining"

    def test_original_query_preserved(self):
        """
        GIVEN a query string
        WHEN parsing
        THEN original query is preserved
        """
        query = "How much on food?"
        result = parse_natural_language_query(query)
        assert result.original_query == query

