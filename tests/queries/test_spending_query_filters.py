"""
Unit/Integration Tests: SpendingQuery - filter methods.
"""

from datetime import datetime
from decimal import Decimal

from analyze_fin.database.models import Transaction
from analyze_fin.queries.spending import SpendingQuery


class TestFilterByDateRange:
    """Test date range filtering."""

    def test_p0_filter_by_start_date(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        start_date = datetime(2024, 11, 10)
        results = query.filter_by_date_range(start_date=start_date).execute()

        assert len(results) > 0
        for tx in results:
            assert tx.date >= start_date

    def test_p0_filter_by_end_date(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        end_date = datetime(2024, 11, 5)
        results = query.filter_by_date_range(end_date=end_date).execute()

        assert len(results) > 0
        for tx in results:
            assert tx.date <= end_date

    def test_p0_filter_by_date_range_inclusive(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        start_date = datetime(2024, 11, 3)
        end_date = datetime(2024, 11, 7)
        results = query.filter_by_date_range(start_date=start_date, end_date=end_date).execute()

        assert len(results) == 5
        for tx in results:
            assert start_date <= tx.date <= end_date

    def test_p1_filter_returns_self_for_chaining(self, db_session):
        query = SpendingQuery(db_session)
        result = query.filter_by_date_range(start_date=datetime(2024, 1, 1))
        assert result is query

    def test_p2_filter_with_none_values_is_noop(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        results = query.filter_by_date_range(start_date=None, end_date=None).execute()
        assert len(results) == 12


class TestFilterByAmount:
    """Test amount range filtering."""

    def test_p0_filter_by_min_amount(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        min_amount = Decimal("400.00")
        results = query.filter_by_amount(min_amount=min_amount).execute()

        assert len(results) > 0
        for tx in results:
            assert tx.amount >= min_amount

    def test_p0_filter_by_max_amount(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        max_amount = Decimal("200.00")
        results = query.filter_by_amount(max_amount=max_amount).execute()

        assert len(results) > 0
        for tx in results:
            assert tx.amount <= max_amount

    def test_p0_filter_by_amount_range(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        min_amount = Decimal("150.00")
        max_amount = Decimal("300.00")
        results = query.filter_by_amount(min_amount=min_amount, max_amount=max_amount).execute()

        assert len(results) > 0
        for tx in results:
            assert min_amount <= tx.amount <= max_amount

    def test_p1_filter_amount_returns_self_for_chaining(self, db_session):
        query = SpendingQuery(db_session)
        result = query.filter_by_amount(min_amount=Decimal("100.00"))
        assert result is query

    def test_p2_filter_amount_with_none_is_noop(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        results = query.filter_by_amount(min_amount=None, max_amount=None).execute()
        assert len(results) == 12


class TestMethodChaining:
    """Test combining multiple filters with AND logic."""

    def test_p0_chain_date_and_amount_filters(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        results = (
            query.filter_by_date_range(
                start_date=datetime(2024, 11, 1),
                end_date=datetime(2024, 11, 5),
            )
            .filter_by_amount(min_amount=Decimal("200.00"))
            .execute()
        )

        for tx in results:
            assert datetime(2024, 11, 1) <= tx.date <= datetime(2024, 11, 5)
            assert tx.amount >= Decimal("200.00")

    def test_p1_empty_result_when_filters_exclude_all(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        results = (
            query.filter_by_date_range(end_date=datetime(2024, 1, 1))
            .filter_by_amount(min_amount=Decimal("10000.00"))
            .execute()
        )
        assert results == []


class TestFilterByCategory:
    """Test category filtering."""

    def test_p0_filter_by_category_returns_matching_transactions(self, db_session, sample_statement):
        tx_food = Transaction(
            statement_id=sample_statement.id,
            date=datetime(2024, 11, 1),
            description="JOLLIBEE",
            amount=Decimal("200.00"),
            category="Food & Dining",
        )
        tx_transport = Transaction(
            statement_id=sample_statement.id,
            date=datetime(2024, 11, 2),
            description="GRAB RIDE",
            amount=Decimal("150.00"),
            category="Transportation",
        )
        tx_food2 = Transaction(
            statement_id=sample_statement.id,
            date=datetime(2024, 11, 3),
            description="MCDO",
            amount=Decimal("180.00"),
            category="Food & Dining",
        )
        db_session.add_all([tx_food, tx_transport, tx_food2])
        db_session.commit()

        query = SpendingQuery(db_session)
        results = query.filter_by_category("Food & Dining").execute()

        assert len(results) == 2
        for tx in results:
            assert tx.category == "Food & Dining"

    def test_p1_filter_by_category_returns_self_for_chaining(self, db_session):
        query = SpendingQuery(db_session)
        result = query.filter_by_category("Food & Dining")
        assert result is query

    def test_p1_filter_by_category_no_matches_returns_empty(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        results = query.filter_by_category("Non-Existent Category").execute()
        assert results == []


class TestFilterByMerchant:
    """Test merchant filtering."""

    def test_p0_filter_by_merchant_returns_matching_transactions(self, db_session, sample_statement):
        tx_jb1 = Transaction(
            statement_id=sample_statement.id,
            date=datetime(2024, 11, 1),
            description="JOLLIBEE GREENBELT",
            amount=Decimal("200.00"),
            merchant_normalized="Jollibee",
        )
        tx_grab = Transaction(
            statement_id=sample_statement.id,
            date=datetime(2024, 11, 2),
            description="GRAB RIDE MAKATI",
            amount=Decimal("150.00"),
            merchant_normalized="Grab",
        )
        tx_jb2 = Transaction(
            statement_id=sample_statement.id,
            date=datetime(2024, 11, 3),
            description="JOLLIBEE AYALA",
            amount=Decimal("180.00"),
            merchant_normalized="Jollibee",
        )
        db_session.add_all([tx_jb1, tx_grab, tx_jb2])
        db_session.commit()

        query = SpendingQuery(db_session)
        results = query.filter_by_merchant("Jollibee").execute()

        assert len(results) == 2
        for tx in results:
            assert "Jollibee" in tx.merchant_normalized

    def test_p1_filter_by_merchant_case_insensitive(self, db_session, sample_statement):
        tx = Transaction(
            statement_id=sample_statement.id,
            date=datetime(2024, 11, 1),
            description="JOLLIBEE",
            amount=Decimal("200.00"),
            merchant_normalized="Jollibee",
        )
        db_session.add(tx)
        db_session.commit()

        query = SpendingQuery(db_session)
        results = query.filter_by_merchant("jollibee").execute()
        assert len(results) == 1

    def test_p1_filter_by_merchant_partial_match(self, db_session, sample_statement):
        tx = Transaction(
            statement_id=sample_statement.id,
            date=datetime(2024, 11, 1),
            description="JOLLIBEE GREENBELT",
            amount=Decimal("200.00"),
            merchant_normalized="Jollibee Foods Corporation",
        )
        db_session.add(tx)
        db_session.commit()

        query = SpendingQuery(db_session)
        results = query.filter_by_merchant("Jollibee").execute()
        assert len(results) == 1

    def test_p1_filter_by_merchant_returns_self_for_chaining(self, db_session):
        query = SpendingQuery(db_session)
        result = query.filter_by_merchant("Jollibee")
        assert result is query

    def test_p1_filter_by_merchant_no_matches_returns_empty(self, db_session, sample_transactions):
        query = SpendingQuery(db_session)
        results = query.filter_by_merchant("Non-Existent Merchant").execute()
        assert results == []


