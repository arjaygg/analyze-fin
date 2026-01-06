from __future__ import annotations

from decimal import Decimal

import pytest


@pytest.fixture
def sample_by_category() -> dict[str, dict]:
    """Sample category spending data matching SpendingReport.by_category format."""
    return {
        "Food & Dining": {"total": Decimal("15000.00"), "count": 40, "percentage": 30.0},
        "Transportation": {"total": Decimal("8000.00"), "count": 25, "percentage": 16.0},
        "Shopping": {"total": Decimal("12000.00"), "count": 20, "percentage": 24.0},
        "Utilities": {"total": Decimal("5000.00"), "count": 10, "percentage": 10.0},
        "Entertainment": {"total": Decimal("10000.00"), "count": 15, "percentage": 20.0},
    }


@pytest.fixture
def empty_by_category() -> dict[str, dict]:
    """Empty category data."""
    return {}


@pytest.fixture
def single_category() -> dict[str, dict]:
    """Single category data (100% case)."""
    return {
        "Food & Dining": {"total": Decimal("50000.00"), "count": 100, "percentage": 100.0},
    }


@pytest.fixture
def sample_by_month() -> dict[str, dict]:
    """Sample monthly spending data matching SpendingReport.by_month format."""
    return {
        "2024-09": {"total": Decimal("18000.00"), "count": 35},
        "2024-10": {"total": Decimal("20000.00"), "count": 45},
        "2024-11": {"total": Decimal("30000.00"), "count": 55},
        "2024-12": {"total": Decimal("25000.00"), "count": 50},
    }


@pytest.fixture
def empty_by_month() -> dict[str, dict]:
    """Empty monthly data."""
    return {}


@pytest.fixture
def single_month() -> dict[str, dict]:
    """Single month data point."""
    return {
        "2024-11": {"total": Decimal("50000.00"), "count": 100},
    }


@pytest.fixture
def sample_comparison_data() -> dict:
    """Sample comparison data matching SpendingAnalyzer.compare_periods format."""
    return {
        "period_a_total": Decimal("25000.00"),
        "period_b_total": Decimal("30000.00"),
        "difference": Decimal("5000.00"),
        "change_percent": 20.0,
        "period_a_transactions": 50,
        "period_b_transactions": 60,
    }


@pytest.fixture
def comparison_decrease() -> dict:
    """Comparison data showing spending decrease."""
    return {
        "period_a_total": Decimal("40000.00"),
        "period_b_total": Decimal("30000.00"),
        "difference": Decimal("-10000.00"),
        "change_percent": -25.0,
        "period_a_transactions": 80,
        "period_b_transactions": 60,
    }


@pytest.fixture
def empty_comparison() -> dict:
    """Empty/zero comparison data."""
    return {
        "period_a_total": Decimal("0"),
        "period_b_total": Decimal("0"),
        "difference": Decimal("0"),
        "change_percent": 0.0,
        "period_a_transactions": 0,
        "period_b_transactions": 0,
    }


@pytest.fixture
def sample_top_merchants() -> list[dict]:
    """Sample top merchants data matching SpendingReport.top_merchants format."""
    return [
        {"merchant": "Jollibee", "total": Decimal("5000.00"), "count": 15},
        {"merchant": "Grab", "total": Decimal("4000.00"), "count": 20},
        {"merchant": "7-Eleven", "total": Decimal("3500.00"), "count": 25},
        {"merchant": "SM Supermarket", "total": Decimal("3000.00"), "count": 8},
        {"merchant": "Shopee", "total": Decimal("2500.00"), "count": 10},
    ]


@pytest.fixture
def empty_merchants() -> list[dict]:
    """Empty merchants list."""
    return []


@pytest.fixture
def many_merchants() -> list[dict]:
    """More than 10 merchants for limit testing."""
    return [
        {"merchant": f"Merchant {i}", "total": Decimal(str(1000 * (15 - i))), "count": i + 5}
        for i in range(15)
    ]


@pytest.fixture
def sample_spending_report():
    """Complete SpendingReport fixture for integration testing."""
    from analyze_fin.analysis.spending import SpendingReport

    return SpendingReport(
        total_spent=Decimal("50000.00"),
        total_transactions=100,
        average_transaction=Decimal("500.00"),
        by_category={
            "Food & Dining": {"total": Decimal("15000.00"), "count": 40, "percentage": 30.0},
            "Transportation": {"total": Decimal("8000.00"), "count": 25, "percentage": 16.0},
            "Shopping": {"total": Decimal("12000.00"), "count": 20, "percentage": 24.0},
            "Utilities": {"total": Decimal("5000.00"), "count": 10, "percentage": 10.0},
            "Entertainment": {"total": Decimal("10000.00"), "count": 15, "percentage": 20.0},
        },
        by_month={
            "2024-09": {"total": Decimal("18000.00"), "count": 35},
            "2024-10": {"total": Decimal("20000.00"), "count": 45},
            "2024-11": {"total": Decimal("30000.00"), "count": 55},
            "2024-12": {"total": Decimal("25000.00"), "count": 50},
        },
        top_merchants=[
            {"merchant": "Jollibee", "total": Decimal("5000.00"), "count": 15},
            {"merchant": "Grab", "total": Decimal("4000.00"), "count": 20},
            {"merchant": "7-Eleven", "total": Decimal("3500.00"), "count": 25},
            {"merchant": "SM Supermarket", "total": Decimal("3000.00"), "count": 8},
            {"merchant": "Shopee", "total": Decimal("2500.00"), "count": 10},
        ],
    )


