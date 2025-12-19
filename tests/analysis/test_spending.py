"""
TDD Tests: Spending Analysis

Story 4.1 AC: Analyze spending patterns and generate reports.
RED phase - these tests will fail until spending.py is implemented.
"""

import pytest
from datetime import datetime
from decimal import Decimal


class TestSpendingAnalyzerStructure:
    """Test SpendingAnalyzer class structure."""

    def test_analyzer_exists(self):
        """SpendingAnalyzer can be imported."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        assert SpendingAnalyzer is not None

    def test_analyzer_can_instantiate(self):
        """SpendingAnalyzer can be instantiated."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        assert analyzer is not None

    def test_analyzer_has_analyze_method(self):
        """SpendingAnalyzer has analyze method."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        assert callable(analyzer.analyze)


class TestSpendingReport:
    """Test SpendingReport data class."""

    def test_spending_report_exists(self):
        """SpendingReport can be imported."""
        from analyze_fin.analysis.spending import SpendingReport

        assert SpendingReport is not None

    def test_spending_report_has_required_fields(self):
        """SpendingReport has all required fields."""
        from analyze_fin.analysis.spending import SpendingReport

        report = SpendingReport(
            total_spent=Decimal("1000.00"),
            total_transactions=10,
            average_transaction=Decimal("100.00"),
            by_category={},
            by_month={},
            top_merchants=[],
        )

        assert report.total_spent == Decimal("1000.00")
        assert report.total_transactions == 10
        assert report.average_transaction == Decimal("100.00")


class TestBasicAnalysis:
    """Test basic spending analysis."""

    def test_analyze_returns_report(self):
        """analyze() returns SpendingReport."""
        from analyze_fin.analysis.spending import SpendingAnalyzer, SpendingReport

        analyzer = SpendingAnalyzer()
        transactions = [
            {
                "date": datetime(2024, 1, 15),
                "amount": Decimal("100.00"),
                "category": "Food & Dining",
                "description": "JOLLIBEE",
            },
        ]

        report = analyzer.analyze(transactions)

        assert isinstance(report, SpendingReport)

    def test_analyze_calculates_total_spent(self):
        """analyze() calculates total spent."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food"},
            {"date": datetime(2024, 1, 2), "amount": Decimal("200.00"), "category": "Food"},
            {"date": datetime(2024, 1, 3), "amount": Decimal("50.00"), "category": "Food"},
        ]

        report = analyzer.analyze(transactions)

        assert report.total_spent == Decimal("350.00")

    def test_analyze_counts_transactions(self):
        """analyze() counts total transactions."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food"},
            {"date": datetime(2024, 1, 2), "amount": Decimal("200.00"), "category": "Food"},
        ]

        report = analyzer.analyze(transactions)

        assert report.total_transactions == 2

    def test_analyze_calculates_average(self):
        """analyze() calculates average transaction amount."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food"},
            {"date": datetime(2024, 1, 2), "amount": Decimal("200.00"), "category": "Food"},
            {"date": datetime(2024, 1, 3), "amount": Decimal("300.00"), "category": "Food"},
        ]

        report = analyzer.analyze(transactions)

        assert report.average_transaction == Decimal("200.00")

    def test_analyze_empty_transactions(self):
        """analyze() handles empty transactions."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        report = analyzer.analyze([])

        assert report.total_spent == Decimal("0")
        assert report.total_transactions == 0


class TestCategoryBreakdown:
    """Test spending breakdown by category."""

    def test_by_category_groups_spending(self):
        """by_category groups spending by category."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food & Dining"},
            {"date": datetime(2024, 1, 2), "amount": Decimal("200.00"), "category": "Shopping"},
            {"date": datetime(2024, 1, 3), "amount": Decimal("50.00"), "category": "Food & Dining"},
        ]

        report = analyzer.analyze(transactions)

        assert "Food & Dining" in report.by_category
        assert "Shopping" in report.by_category
        assert report.by_category["Food & Dining"]["total"] == Decimal("150.00")
        assert report.by_category["Shopping"]["total"] == Decimal("200.00")

    def test_by_category_includes_count(self):
        """by_category includes transaction count per category."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food & Dining"},
            {"date": datetime(2024, 1, 2), "amount": Decimal("50.00"), "category": "Food & Dining"},
            {"date": datetime(2024, 1, 3), "amount": Decimal("200.00"), "category": "Shopping"},
        ]

        report = analyzer.analyze(transactions)

        assert report.by_category["Food & Dining"]["count"] == 2
        assert report.by_category["Shopping"]["count"] == 1

    def test_by_category_calculates_percentage(self):
        """by_category calculates percentage of total."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food & Dining"},
            {"date": datetime(2024, 1, 2), "amount": Decimal("100.00"), "category": "Shopping"},
        ]

        report = analyzer.analyze(transactions)

        assert report.by_category["Food & Dining"]["percentage"] == 50.0
        assert report.by_category["Shopping"]["percentage"] == 50.0


class TestMonthlyBreakdown:
    """Test spending breakdown by month."""

    def test_by_month_groups_spending(self):
        """by_month groups spending by month."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 15), "amount": Decimal("100.00"), "category": "Food"},
            {"date": datetime(2024, 1, 20), "amount": Decimal("50.00"), "category": "Food"},
            {"date": datetime(2024, 2, 10), "amount": Decimal("200.00"), "category": "Food"},
        ]

        report = analyzer.analyze(transactions)

        assert "2024-01" in report.by_month
        assert "2024-02" in report.by_month
        assert report.by_month["2024-01"]["total"] == Decimal("150.00")
        assert report.by_month["2024-02"]["total"] == Decimal("200.00")

    def test_by_month_includes_count(self):
        """by_month includes transaction count per month."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food"},
            {"date": datetime(2024, 1, 15), "amount": Decimal("50.00"), "category": "Food"},
            {"date": datetime(2024, 2, 1), "amount": Decimal("200.00"), "category": "Food"},
        ]

        report = analyzer.analyze(transactions)

        assert report.by_month["2024-01"]["count"] == 2
        assert report.by_month["2024-02"]["count"] == 1


class TestTopMerchants:
    """Test top merchants analysis."""

    def test_top_merchants_lists_highest_spend(self):
        """top_merchants lists merchants by total spend."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "merchant_normalized": "Jollibee", "category": "Food"},
            {"date": datetime(2024, 1, 2), "amount": Decimal("200.00"), "merchant_normalized": "McDonald's", "category": "Food"},
            {"date": datetime(2024, 1, 3), "amount": Decimal("150.00"), "merchant_normalized": "Jollibee", "category": "Food"},
        ]

        report = analyzer.analyze(transactions)

        # Jollibee total: 250, McDonald's total: 200
        assert len(report.top_merchants) >= 2
        assert report.top_merchants[0]["merchant"] == "Jollibee"
        assert report.top_merchants[0]["total"] == Decimal("250.00")

    def test_top_merchants_limits_to_n(self):
        """top_merchants limits to top N merchants."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "merchant_normalized": f"Merchant{i}", "category": "Food"}
            for i in range(20)
        ]

        report = analyzer.analyze(transactions, top_n=5)

        assert len(report.top_merchants) == 5


class TestDateFiltering:
    """Test date range filtering."""

    def test_analyze_with_date_range(self):
        """analyze() filters by date range."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food"},
            {"date": datetime(2024, 2, 1), "amount": Decimal("200.00"), "category": "Food"},
            {"date": datetime(2024, 3, 1), "amount": Decimal("300.00"), "category": "Food"},
        ]

        report = analyzer.analyze(
            transactions,
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 2, 15),
        )

        # Only February transaction is in range
        assert report.total_spent == Decimal("200.00")
        assert report.total_transactions == 1


class TestCategoryFiltering:
    """Test category filtering."""

    def test_analyze_with_category_filter(self):
        """analyze() filters by category."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food & Dining"},
            {"date": datetime(2024, 1, 2), "amount": Decimal("200.00"), "category": "Shopping"},
            {"date": datetime(2024, 1, 3), "amount": Decimal("50.00"), "category": "Food & Dining"},
        ]

        report = analyzer.analyze(transactions, categories=["Food & Dining"])

        assert report.total_spent == Decimal("150.00")
        assert report.total_transactions == 2


class TestTrends:
    """Test spending trend analysis."""

    def test_monthly_trend(self):
        """Calculate month-over-month trend."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food"},
            {"date": datetime(2024, 2, 1), "amount": Decimal("150.00"), "category": "Food"},
            {"date": datetime(2024, 3, 1), "amount": Decimal("200.00"), "category": "Food"},
        ]

        report = analyzer.analyze(transactions)

        # Check trend data exists
        assert "2024-01" in report.by_month
        assert "2024-02" in report.by_month
        assert "2024-03" in report.by_month

    def test_get_trend_direction(self):
        """Determine if spending is increasing or decreasing."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            {"date": datetime(2024, 1, 1), "amount": Decimal("100.00"), "category": "Food"},
            {"date": datetime(2024, 2, 1), "amount": Decimal("200.00"), "category": "Food"},
            {"date": datetime(2024, 3, 1), "amount": Decimal("300.00"), "category": "Food"},
        ]

        report = analyzer.analyze(transactions)
        trend = analyzer.get_trend(report)

        assert trend["direction"] == "increasing"
        assert trend["change_percent"] > 0


class TestComparisonAnalysis:
    """Test period comparison analysis."""

    def test_compare_periods(self):
        """Compare spending between two periods."""
        from analyze_fin.analysis.spending import SpendingAnalyzer

        analyzer = SpendingAnalyzer()
        transactions = [
            # January
            {"date": datetime(2024, 1, 10), "amount": Decimal("100.00"), "category": "Food"},
            {"date": datetime(2024, 1, 20), "amount": Decimal("50.00"), "category": "Food"},
            # February
            {"date": datetime(2024, 2, 10), "amount": Decimal("200.00"), "category": "Food"},
        ]

        comparison = analyzer.compare_periods(
            transactions,
            period_a_start=datetime(2024, 1, 1),
            period_a_end=datetime(2024, 1, 31),
            period_b_start=datetime(2024, 2, 1),
            period_b_end=datetime(2024, 2, 28),
        )

        assert comparison["period_a_total"] == Decimal("150.00")
        assert comparison["period_b_total"] == Decimal("200.00")
        assert comparison["difference"] == Decimal("50.00")
        assert comparison["change_percent"] > 0  # Increased
