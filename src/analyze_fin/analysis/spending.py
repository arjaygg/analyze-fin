"""
Spending analysis and reporting.

Provides:
- SpendingAnalyzer: Analyze transaction spending patterns
- SpendingReport: Results of spending analysis
- Category, monthly, and merchant breakdowns
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Sequence


@dataclass
class SpendingReport:
    """Results of spending analysis.

    Attributes:
        total_spent: Total amount spent
        total_transactions: Number of transactions
        average_transaction: Average transaction amount
        by_category: Spending breakdown by category
        by_month: Spending breakdown by month
        top_merchants: Top merchants by spend
    """

    total_spent: Decimal
    total_transactions: int
    average_transaction: Decimal
    by_category: dict[str, dict[str, Any]]
    by_month: dict[str, dict[str, Any]]
    top_merchants: list[dict[str, Any]]


class SpendingAnalyzer:
    """Analyze transaction spending patterns.

    Generates reports on spending by category, month, merchant,
    and provides trend analysis.

    Example:
        analyzer = SpendingAnalyzer()

        report = analyzer.analyze(transactions)
        print(f"Total spent: {report.total_spent}")
        print(f"Top category: {list(report.by_category.keys())[0]}")

        # Filter by date
        report = analyzer.analyze(
            transactions,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
        )

        # Compare periods
        comparison = analyzer.compare_periods(
            transactions,
            period_a_start=datetime(2024, 1, 1),
            period_a_end=datetime(2024, 1, 31),
            period_b_start=datetime(2024, 2, 1),
            period_b_end=datetime(2024, 2, 28),
        )
    """

    def analyze(
        self,
        transactions: Sequence[dict[str, Any]],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        categories: list[str] | None = None,
        top_n: int = 10,
    ) -> SpendingReport:
        """Analyze spending patterns.

        Args:
            transactions: List of transaction dictionaries
            start_date: Optional start date filter
            end_date: Optional end date filter
            categories: Optional list of categories to include
            top_n: Number of top merchants to include

        Returns:
            SpendingReport with analysis results
        """
        # Filter transactions
        filtered = self._filter_transactions(
            transactions, start_date, end_date, categories
        )

        if not filtered:
            return SpendingReport(
                total_spent=Decimal("0"),
                total_transactions=0,
                average_transaction=Decimal("0"),
                by_category={},
                by_month={},
                top_merchants=[],
            )

        # Calculate totals
        total_spent = sum(tx.get("amount", Decimal("0")) for tx in filtered)
        total_transactions = len(filtered)
        average = total_spent / total_transactions if total_transactions > 0 else Decimal("0")

        # Category breakdown
        by_category = self._analyze_by_category(filtered, total_spent)

        # Monthly breakdown
        by_month = self._analyze_by_month(filtered)

        # Top merchants
        top_merchants = self._analyze_top_merchants(filtered, top_n)

        return SpendingReport(
            total_spent=total_spent,
            total_transactions=total_transactions,
            average_transaction=average,
            by_category=by_category,
            by_month=by_month,
            top_merchants=top_merchants,
        )

    def _filter_transactions(
        self,
        transactions: Sequence[dict[str, Any]],
        start_date: datetime | None,
        end_date: datetime | None,
        categories: list[str] | None,
    ) -> list[dict[str, Any]]:
        """Filter transactions by date and category."""
        result = list(transactions)

        if start_date:
            result = [tx for tx in result if tx.get("date", datetime.min) >= start_date]

        if end_date:
            result = [tx for tx in result if tx.get("date", datetime.max) <= end_date]

        if categories:
            result = [tx for tx in result if tx.get("category") in categories]

        return result

    def _analyze_by_category(
        self,
        transactions: Sequence[dict[str, Any]],
        total_spent: Decimal,
    ) -> dict[str, dict[str, Any]]:
        """Analyze spending by category."""
        categories: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"total": Decimal("0"), "count": 0, "percentage": 0.0}
        )

        for tx in transactions:
            category = tx.get("category", "Uncategorized")
            amount = tx.get("amount", Decimal("0"))
            categories[category]["total"] += amount
            categories[category]["count"] += 1

        # Calculate percentages
        if total_spent > 0:
            for cat_data in categories.values():
                cat_data["percentage"] = float(cat_data["total"] / total_spent * 100)

        return dict(categories)

    def _analyze_by_month(
        self,
        transactions: Sequence[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Analyze spending by month."""
        months: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"total": Decimal("0"), "count": 0}
        )

        for tx in transactions:
            date = tx.get("date")
            if date:
                month_key = date.strftime("%Y-%m")
                amount = tx.get("amount", Decimal("0"))
                months[month_key]["total"] += amount
                months[month_key]["count"] += 1

        return dict(months)

    def _analyze_top_merchants(
        self,
        transactions: Sequence[dict[str, Any]],
        top_n: int,
    ) -> list[dict[str, Any]]:
        """Get top merchants by spending."""
        merchants: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"total": Decimal("0"), "count": 0}
        )

        for tx in transactions:
            merchant = tx.get("merchant_normalized") or tx.get("description", "Unknown")
            amount = tx.get("amount", Decimal("0"))
            merchants[merchant]["total"] += amount
            merchants[merchant]["count"] += 1

        # Sort by total and get top N
        sorted_merchants = sorted(
            merchants.items(),
            key=lambda x: x[1]["total"],
            reverse=True,
        )[:top_n]

        return [
            {
                "merchant": name,
                "total": data["total"],
                "count": data["count"],
            }
            for name, data in sorted_merchants
        ]

    def get_trend(
        self,
        report: SpendingReport,
    ) -> dict[str, Any]:
        """Calculate spending trend from report.

        Args:
            report: SpendingReport to analyze

        Returns:
            Dictionary with trend direction and change percentage
        """
        months = report.by_month
        if len(months) < 2:
            return {"direction": "stable", "change_percent": 0.0}

        # Sort months chronologically
        sorted_months = sorted(months.keys())
        first_month_total = float(months[sorted_months[0]]["total"])
        last_month_total = float(months[sorted_months[-1]]["total"])

        if first_month_total == 0:
            change_percent = 100.0 if last_month_total > 0 else 0.0
        else:
            change_percent = ((last_month_total - first_month_total) / first_month_total) * 100

        if change_percent > 5:
            direction = "increasing"
        elif change_percent < -5:
            direction = "decreasing"
        else:
            direction = "stable"

        return {
            "direction": direction,
            "change_percent": change_percent,
        }

    def compare_periods(
        self,
        transactions: Sequence[dict[str, Any]],
        period_a_start: datetime,
        period_a_end: datetime,
        period_b_start: datetime,
        period_b_end: datetime,
    ) -> dict[str, Any]:
        """Compare spending between two periods.

        Args:
            transactions: List of transactions
            period_a_start: Start of first period
            period_a_end: End of first period
            period_b_start: Start of second period
            period_b_end: End of second period

        Returns:
            Dictionary with comparison results
        """
        report_a = self.analyze(transactions, start_date=period_a_start, end_date=period_a_end)
        report_b = self.analyze(transactions, start_date=period_b_start, end_date=period_b_end)

        period_a_total = report_a.total_spent
        period_b_total = report_b.total_spent
        difference = period_b_total - period_a_total

        if period_a_total > 0:
            change_percent = float(difference / period_a_total * 100)
        else:
            change_percent = 100.0 if period_b_total > 0 else 0.0

        return {
            "period_a_total": period_a_total,
            "period_b_total": period_b_total,
            "difference": difference,
            "change_percent": change_percent,
            "period_a_transactions": report_a.total_transactions,
            "period_b_transactions": report_b.total_transactions,
        }
