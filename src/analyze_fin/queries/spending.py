"""
Spending query engine for transaction analysis.

Provides:
- SpendingQuery: Query and filter transactions by category, merchant, date, amount
- Support for multiple filters with AND logic
- Query result formatting
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from analyze_fin.database.models import Transaction


class SpendingQuery:
    """Query and filter transactions for spending analysis.

    Supports filtering by:
    - Category
    - Merchant (merchant_normalized field, case-insensitive)
    - Date range (inclusive)
    - Amount range (min/max)

    Filters combine with AND logic.
    Results sorted by date descending (most recent first).

    Example:
        query = SpendingQuery(db_session)
        results = query.filter_by_category("Food & Dining") \\
                       .filter_by_date_range(start_date, end_date) \\
                       .execute()
    """

    def __init__(self, session: Session) -> None:
        """Initialize query with database session.

        Args:
            session: SQLAlchemy session
        """
        self._session = session
        self._filters: list[Any] = []
        self._order_by = Transaction.date.desc()

    def filter_by_category(self, category: str) -> "SpendingQuery":
        """Filter transactions by category.

        Args:
            category: Category name (e.g., "Food & Dining")

        Returns:
            Self for method chaining
        """
        self._filters.append(Transaction.category == category)
        return self

    def filter_by_merchant(self, merchant: str) -> "SpendingQuery":
        """Filter transactions by merchant.

        Uses merchant_normalized field for consistent matching.
        Case-insensitive matching.

        Args:
            merchant: Merchant name (e.g., "Jollibee")

        Returns:
            Self for method chaining
        """
        self._filters.append(Transaction.merchant_normalized.ilike(f"%{merchant}%"))
        return self

    def filter_by_date_range(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> "SpendingQuery":
        """Filter transactions by date range (inclusive).

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            Self for method chaining
        """
        if start_date:
            self._filters.append(Transaction.date >= start_date)
        if end_date:
            self._filters.append(Transaction.date <= end_date)
        return self

    def filter_by_amount(
        self,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None
    ) -> "SpendingQuery":
        """Filter transactions by amount range (inclusive).

        Args:
            min_amount: Minimum amount (inclusive)
            max_amount: Maximum amount (inclusive)

        Returns:
            Self for method chaining
        """
        if min_amount is not None:
            self._filters.append(Transaction.amount >= min_amount)
        if max_amount is not None:
            self._filters.append(Transaction.amount <= max_amount)
        return self

    def execute(self) -> list[Transaction]:
        """Execute query and return results.

        Returns:
            List of Transaction objects matching all filters
        """
        stmt = select(Transaction)

        if self._filters:
            stmt = stmt.where(and_(*self._filters))

        stmt = stmt.order_by(self._order_by)

        result = self._session.execute(stmt)
        return list(result.scalars().all())

    def count(self) -> int:
        """Count transactions matching filters without fetching all rows.

        Returns:
            Number of transactions matching filters
        """
        from sqlalchemy import func

        stmt = select(func.count(Transaction.id))

        if self._filters:
            stmt = stmt.where(and_(*self._filters))

        result = self._session.execute(stmt)
        return result.scalar() or 0

    def total_amount(self) -> Decimal:
        """Calculate total amount of transactions matching filters.

        Returns:
            Sum of transaction amounts
        """
        from sqlalchemy import func

        stmt = select(func.sum(Transaction.amount))

        if self._filters:
            stmt = stmt.where(and_(*self._filters))

        result = self._session.execute(stmt)
        total = result.scalar()
        return total if total is not None else Decimal("0")


def format_currency(amount: Decimal) -> str:
    """Format amount as Philippine peso currency.

    Args:
        amount: Decimal amount

    Returns:
        Formatted string: ₱12,345.67
    """
    return f"₱{amount:,.2f}"


def format_date_localized(date: datetime) -> str:
    """Format date in localized format.

    Args:
        date: datetime object

    Returns:
        Formatted string: Nov 15, 2024
    """
    return date.strftime("%b %d, %Y")
