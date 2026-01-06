"""
Unit/Integration Tests: SpendingQuery - execute/count/total aggregations.
"""

from datetime import datetime
from decimal import Decimal

from analyze_fin.database.models import Transaction
from analyze_fin.queries.spending import SpendingQuery


class TestExecute:
    """Test query execution."""

    def test_p0_execute_returns_list_of_transactions(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        results = query.execute()

        assert isinstance(results, list)
        assert len(results) == 12
        assert all(isinstance(tx, Transaction) for tx in results)

    def test_p1_execute_returns_sorted_by_date_desc(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        results = query.execute()

        dates = [tx.date for tx in results]
        assert dates == sorted(dates, reverse=True)

    def test_p2_execute_on_empty_database_returns_empty_list(self, db_session):
        query = SpendingQuery(db_session)
        results = query.execute()
        assert results == []


class TestCount:
    """Test transaction counting."""

    def test_p0_count_returns_total_transactions(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        count = query.count()
        assert count == 12

    def test_p0_count_respects_filters(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        count = (
            query.filter_by_date_range(
                start_date=datetime(2024, 11, 1),
                end_date=datetime(2024, 11, 5),
            )
            .count()
        )
        assert count == 5

    def test_p2_count_returns_zero_for_empty_result(self, db_session):
        query = SpendingQuery(db_session)
        count = query.count()
        assert count == 0


class TestTotalAmount:
    """Test total amount calculation."""

    def test_p0_total_amount_sums_all_transactions(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        total = query.total_amount()

        expected = Decimal("8300.00")
        assert total == expected

    def test_p0_total_amount_respects_filters(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        total = query.filter_by_amount(min_amount=Decimal("400.00")).total_amount()

        expected = Decimal("6900.00")
        assert total == expected

    def test_p2_total_amount_returns_zero_for_empty_result(self, db_session):
        query = SpendingQuery(db_session)
        total = query.total_amount()

        assert total == Decimal("0")
        assert isinstance(total, Decimal)


