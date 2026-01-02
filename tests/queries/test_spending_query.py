"""
Unit Tests: SpendingQuery - Transaction Query Engine

Tests for the SpendingQuery class which provides filtering and querying
of transactions by category, merchant, date range, and amount.

Test Levels:
- Unit: SpendingQuery class methods
- Integration: Database interaction with SQLAlchemy

Priority Classification:
- [P0] Critical paths - query execution, filtering
- [P1] High priority - edge cases, method chaining
- [P2] Medium priority - helper functions, formatting
"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from analyze_fin.database.models import Account, Base, Statement, Transaction
from analyze_fin.queries.spending import SpendingQuery, format_currency, format_date_localized

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def test_engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_engine):
    """Provide database session with automatic cleanup."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture
def sample_account(db_session) -> Account:
    """Create a sample account for transactions."""
    account = Account(
        name="Test GCash Account",
        bank_type="gcash",
    )
    db_session.add(account)
    db_session.commit()
    return account


@pytest.fixture
def sample_statement(db_session, sample_account) -> Statement:
    """Create a sample statement for transactions."""
    statement = Statement(
        account_id=sample_account.id,
        file_path="/path/to/statement.pdf",
        quality_score=0.95,
    )
    db_session.add(statement)
    db_session.commit()
    return statement


@pytest.fixture
def sample_transactions(db_session, sample_statement) -> list[Transaction]:
    """
    Create diverse sample transactions for testing.

    Transactions span:
    - Multiple dates (Nov 1-15, 2024)
    - Multiple amounts (₱50 to ₱5000)
    - Various descriptions
    """
    transactions = []
    base_date = datetime(2024, 11, 1)

    # Create 10 transactions with varying amounts and dates
    for i in range(10):
        tx = Transaction(
            statement_id=sample_statement.id,
            date=base_date + timedelta(days=i),
            description=f"MERCHANT {i} - TEST TRANSACTION",
            amount=Decimal(f"{100 + i * 50}.00"),  # 100, 150, 200, ..., 550
        )
        transactions.append(tx)
        db_session.add(tx)

    # Add high-value transaction
    high_value_tx = Transaction(
        statement_id=sample_statement.id,
        date=datetime(2024, 11, 15),
        description="HIGH VALUE PURCHASE",
        amount=Decimal("5000.00"),
    )
    transactions.append(high_value_tx)
    db_session.add(high_value_tx)

    # Add low-value transaction
    low_value_tx = Transaction(
        statement_id=sample_statement.id,
        date=datetime(2024, 11, 16),
        description="SMALL PURCHASE",
        amount=Decimal("50.00"),
    )
    transactions.append(low_value_tx)
    db_session.add(low_value_tx)

    db_session.commit()
    return transactions


# ============================================================================
# Test: SpendingQuery Initialization
# ============================================================================


class TestSpendingQueryInit:
    """Test SpendingQuery initialization."""

    def test_p0_query_can_be_instantiated(self, db_session):
        """
        [P0] GIVEN a valid database session
        WHEN SpendingQuery is instantiated
        THEN query object is created successfully
        """
        # GIVEN: Valid session
        session = db_session

        # WHEN: Instantiate query
        query = SpendingQuery(session)

        # THEN: Query object exists
        assert query is not None
        assert isinstance(query, SpendingQuery)

    def test_p1_query_stores_session_reference(self, db_session):
        """
        [P1] GIVEN a database session
        WHEN SpendingQuery is instantiated
        THEN session is stored for later use
        """
        # GIVEN: Session
        session = db_session

        # WHEN: Create query
        query = SpendingQuery(session)

        # THEN: Session is accessible
        assert query._session is session

    def test_p1_query_initializes_empty_filters(self, db_session):
        """
        [P1] GIVEN a new SpendingQuery
        WHEN instantiated
        THEN filters list is empty
        """
        # GIVEN/WHEN: New query
        query = SpendingQuery(db_session)

        # THEN: No filters applied
        assert query._filters == []


# ============================================================================
# Test: filter_by_date_range
# ============================================================================


class TestFilterByDateRange:
    """Test date range filtering."""

    def test_p0_filter_by_start_date(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions spanning multiple dates
        WHEN filtering with start_date
        THEN only transactions on or after start_date are returned
        """
        # GIVEN: Transactions from Nov 1-16
        query = SpendingQuery(db_session)

        # WHEN: Filter from Nov 10 onwards
        start_date = datetime(2024, 11, 10)
        results = query.filter_by_date_range(start_date=start_date).execute()

        # THEN: Only transactions from Nov 10+ returned
        assert len(results) > 0
        for tx in results:
            assert tx.date >= start_date

    def test_p0_filter_by_end_date(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions spanning multiple dates
        WHEN filtering with end_date
        THEN only transactions on or before end_date are returned
        """
        # GIVEN: Transactions from Nov 1-16
        query = SpendingQuery(db_session)

        # WHEN: Filter up to Nov 5
        end_date = datetime(2024, 11, 5)
        results = query.filter_by_date_range(end_date=end_date).execute()

        # THEN: Only transactions up to Nov 5 returned
        assert len(results) > 0
        for tx in results:
            assert tx.date <= end_date

    def test_p0_filter_by_date_range_inclusive(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions
        WHEN filtering with both start and end date
        THEN range is inclusive on both ends
        """
        # GIVEN: Transactions
        query = SpendingQuery(db_session)

        # WHEN: Filter Nov 3 to Nov 7 (inclusive)
        start_date = datetime(2024, 11, 3)
        end_date = datetime(2024, 11, 7)
        results = query.filter_by_date_range(
            start_date=start_date,
            end_date=end_date
        ).execute()

        # THEN: 5 days of transactions (Nov 3, 4, 5, 6, 7)
        assert len(results) == 5
        for tx in results:
            assert start_date <= tx.date <= end_date

    def test_p1_filter_returns_self_for_chaining(self, db_session):
        """
        [P1] GIVEN a SpendingQuery
        WHEN filter_by_date_range is called
        THEN returns self for method chaining
        """
        # GIVEN: Query
        query = SpendingQuery(db_session)

        # WHEN: Apply filter
        result = query.filter_by_date_range(start_date=datetime(2024, 1, 1))

        # THEN: Returns same query object
        assert result is query

    def test_p2_filter_with_none_values_is_noop(self, db_session, sample_transactions):
        """
        [P2] GIVEN transactions
        WHEN filter called with None for both dates
        THEN all transactions returned (no filtering)
        """
        # GIVEN: 12 transactions total
        query = SpendingQuery(db_session)

        # WHEN: Filter with no dates (both None)
        results = query.filter_by_date_range(
            start_date=None,
            end_date=None
        ).execute()

        # THEN: All transactions returned
        assert len(results) == 12


# ============================================================================
# Test: filter_by_amount
# ============================================================================


class TestFilterByAmount:
    """Test amount range filtering."""

    def test_p0_filter_by_min_amount(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions with various amounts
        WHEN filtering with min_amount
        THEN only transactions >= min_amount returned
        """
        # GIVEN: Transactions with amounts ₱50 to ₱5000
        query = SpendingQuery(db_session)

        # WHEN: Filter min ₱400
        min_amount = Decimal("400.00")
        results = query.filter_by_amount(min_amount=min_amount).execute()

        # THEN: Only high-value transactions
        assert len(results) > 0
        for tx in results:
            assert tx.amount >= min_amount

    def test_p0_filter_by_max_amount(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions with various amounts
        WHEN filtering with max_amount
        THEN only transactions <= max_amount returned
        """
        # GIVEN: Transactions with amounts ₱50 to ₱5000
        query = SpendingQuery(db_session)

        # WHEN: Filter max ₱200
        max_amount = Decimal("200.00")
        results = query.filter_by_amount(max_amount=max_amount).execute()

        # THEN: Only low-value transactions
        assert len(results) > 0
        for tx in results:
            assert tx.amount <= max_amount

    def test_p0_filter_by_amount_range(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions with various amounts
        WHEN filtering with both min and max amount
        THEN only transactions within range returned
        """
        # GIVEN: Transactions
        query = SpendingQuery(db_session)

        # WHEN: Filter ₱150 to ₱300
        min_amount = Decimal("150.00")
        max_amount = Decimal("300.00")
        results = query.filter_by_amount(
            min_amount=min_amount,
            max_amount=max_amount
        ).execute()

        # THEN: Transactions in range
        assert len(results) > 0
        for tx in results:
            assert min_amount <= tx.amount <= max_amount

    def test_p1_filter_amount_returns_self_for_chaining(self, db_session):
        """
        [P1] GIVEN a SpendingQuery
        WHEN filter_by_amount is called
        THEN returns self for method chaining
        """
        # GIVEN: Query
        query = SpendingQuery(db_session)

        # WHEN: Apply filter
        result = query.filter_by_amount(min_amount=Decimal("100.00"))

        # THEN: Returns same query object
        assert result is query

    def test_p2_filter_amount_with_none_is_noop(self, db_session, sample_transactions):
        """
        [P2] GIVEN transactions
        WHEN filter called with None for both amounts
        THEN all transactions returned
        """
        # GIVEN: 12 transactions
        query = SpendingQuery(db_session)

        # WHEN: Filter with no amounts
        results = query.filter_by_amount(
            min_amount=None,
            max_amount=None
        ).execute()

        # THEN: All transactions returned
        assert len(results) == 12


# ============================================================================
# Test: Method Chaining (Combined Filters)
# ============================================================================


class TestMethodChaining:
    """Test combining multiple filters with AND logic."""

    def test_p0_chain_date_and_amount_filters(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions
        WHEN chaining date and amount filters
        THEN both filters applied with AND logic
        """
        # GIVEN: Transactions Nov 1-16, amounts ₱50-5000
        query = SpendingQuery(db_session)

        # WHEN: Chain filters: Nov 1-5 AND amount >= ₱200
        results = (
            query
            .filter_by_date_range(
                start_date=datetime(2024, 11, 1),
                end_date=datetime(2024, 11, 5)
            )
            .filter_by_amount(min_amount=Decimal("200.00"))
            .execute()
        )

        # THEN: Only transactions matching BOTH criteria
        for tx in results:
            assert datetime(2024, 11, 1) <= tx.date <= datetime(2024, 11, 5)
            assert tx.amount >= Decimal("200.00")

    def test_p1_empty_result_when_filters_exclude_all(self, db_session, sample_transactions):
        """
        [P1] GIVEN transactions
        WHEN filters exclude all transactions
        THEN empty list returned
        """
        # GIVEN: Transactions
        query = SpendingQuery(db_session)

        # WHEN: Impossible filter combination
        results = (
            query
            .filter_by_date_range(end_date=datetime(2024, 1, 1))  # Before all transactions
            .filter_by_amount(min_amount=Decimal("10000.00"))  # Above all amounts
            .execute()
        )

        # THEN: Empty result
        assert results == []


# ============================================================================
# Test: execute()
# ============================================================================


class TestExecute:
    """Test query execution."""

    def test_p0_execute_returns_list_of_transactions(self, db_session, sample_transactions):
        """
        [P0] GIVEN a query with no filters
        WHEN execute() is called
        THEN returns list of Transaction objects
        """
        # GIVEN: Query
        query = SpendingQuery(db_session)

        # WHEN: Execute
        results = query.execute()

        # THEN: List of Transaction objects
        assert isinstance(results, list)
        assert len(results) == 12  # All sample transactions
        assert all(isinstance(tx, Transaction) for tx in results)

    def test_p1_execute_returns_sorted_by_date_desc(self, db_session, sample_transactions):
        """
        [P1] GIVEN transactions with different dates
        WHEN execute() is called
        THEN results sorted by date descending (most recent first)
        """
        # GIVEN: Transactions spanning dates
        query = SpendingQuery(db_session)

        # WHEN: Execute
        results = query.execute()

        # THEN: Sorted by date descending
        dates = [tx.date for tx in results]
        assert dates == sorted(dates, reverse=True)

    def test_p2_execute_on_empty_database_returns_empty_list(self, db_session):
        """
        [P2] GIVEN empty database
        WHEN execute() is called
        THEN returns empty list
        """
        # GIVEN: Empty database (no sample_transactions fixture)
        query = SpendingQuery(db_session)

        # WHEN: Execute
        results = query.execute()

        # THEN: Empty list
        assert results == []


# ============================================================================
# Test: count()
# ============================================================================


class TestCount:
    """Test transaction counting."""

    def test_p0_count_returns_total_transactions(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions in database
        WHEN count() is called without filters
        THEN returns total count
        """
        # GIVEN: 12 transactions
        query = SpendingQuery(db_session)

        # WHEN: Count
        count = query.count()

        # THEN: Total count
        assert count == 12

    def test_p0_count_respects_filters(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions
        WHEN count() is called with filters
        THEN returns count matching filters
        """
        # GIVEN: Transactions
        query = SpendingQuery(db_session)

        # WHEN: Count with date filter
        count = (
            query
            .filter_by_date_range(
                start_date=datetime(2024, 11, 1),
                end_date=datetime(2024, 11, 5)
            )
            .count()
        )

        # THEN: Only 5 transactions in range
        assert count == 5

    def test_p2_count_returns_zero_for_empty_result(self, db_session):
        """
        [P2] GIVEN empty database
        WHEN count() is called
        THEN returns 0
        """
        # GIVEN: Empty database
        query = SpendingQuery(db_session)

        # WHEN: Count
        count = query.count()

        # THEN: Zero
        assert count == 0


# ============================================================================
# Test: total_amount()
# ============================================================================


class TestTotalAmount:
    """Test total amount calculation."""

    def test_p0_total_amount_sums_all_transactions(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions in database
        WHEN total_amount() is called without filters
        THEN returns sum of all amounts
        """
        # GIVEN: Transactions with known amounts
        # Amounts: 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 5000, 50
        # Sum = 8300.00
        query = SpendingQuery(db_session)

        # WHEN: Total
        total = query.total_amount()

        # THEN: Sum of all amounts
        expected = Decimal("8300.00")
        assert total == expected

    def test_p0_total_amount_respects_filters(self, db_session, sample_transactions):
        """
        [P0] GIVEN transactions
        WHEN total_amount() called with filters
        THEN returns sum of matching transactions only
        """
        # GIVEN: Transactions
        query = SpendingQuery(db_session)

        # WHEN: Total with amount filter (only >= ₱400)
        total = query.filter_by_amount(min_amount=Decimal("400.00")).total_amount()

        # THEN: Sum of 400 + 450 + 500 + 550 + 5000 = 6900
        expected = Decimal("6900.00")
        assert total == expected

    def test_p2_total_amount_returns_zero_for_empty_result(self, db_session):
        """
        [P2] GIVEN empty database
        WHEN total_amount() is called
        THEN returns Decimal(0)
        """
        # GIVEN: Empty database
        query = SpendingQuery(db_session)

        # WHEN: Total
        total = query.total_amount()

        # THEN: Zero as Decimal
        assert total == Decimal("0")
        assert isinstance(total, Decimal)


# ============================================================================
# Test: filter_by_category
# ============================================================================


class TestFilterByCategory:
    """Test category filtering."""

    def test_p0_filter_by_category_returns_matching_transactions(
        self, db_session, sample_statement
    ):
        """
        [P0] GIVEN transactions with different categories
        WHEN filter_by_category() is called
        THEN only transactions with matching category returned
        """
        # GIVEN: Transactions with categories
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

        # WHEN: Filter by Food & Dining
        results = query.filter_by_category("Food & Dining").execute()

        # THEN: Only food transactions returned
        assert len(results) == 2
        for tx in results:
            assert tx.category == "Food & Dining"

    def test_p1_filter_by_category_returns_self_for_chaining(self, db_session):
        """
        [P1] GIVEN SpendingQuery
        WHEN filter_by_category() is called
        THEN returns self for method chaining
        """
        # GIVEN: Query
        query = SpendingQuery(db_session)

        # WHEN: Filter by category
        result = query.filter_by_category("Food & Dining")

        # THEN: Returns self for chaining
        assert result is query

    def test_p1_filter_by_category_no_matches_returns_empty(
        self, db_session, sample_transactions
    ):
        """
        [P1] GIVEN transactions without matching category
        WHEN filter_by_category() is called
        THEN returns empty list
        """
        # GIVEN: Transactions without categories set
        query = SpendingQuery(db_session)

        # WHEN: Filter by non-existent category
        results = query.filter_by_category("Non-Existent Category").execute()

        # THEN: Empty result
        assert results == []


# ============================================================================
# Test: filter_by_merchant
# ============================================================================


class TestFilterByMerchant:
    """Test merchant filtering."""

    def test_p0_filter_by_merchant_returns_matching_transactions(
        self, db_session, sample_statement
    ):
        """
        [P0] GIVEN transactions with normalized merchants
        WHEN filter_by_merchant() is called
        THEN only transactions matching merchant returned
        """
        # GIVEN: Transactions with normalized merchants
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

        # WHEN: Filter by Jollibee
        results = query.filter_by_merchant("Jollibee").execute()

        # THEN: Only Jollibee transactions returned
        assert len(results) == 2
        for tx in results:
            assert "Jollibee" in tx.merchant_normalized

    def test_p1_filter_by_merchant_case_insensitive(
        self, db_session, sample_statement
    ):
        """
        [P1] GIVEN transactions with normalized merchants
        WHEN filter_by_merchant() is called with different case
        THEN matching is case-insensitive
        """
        # GIVEN: Transaction with merchant
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

        # WHEN: Filter with lowercase
        results = query.filter_by_merchant("jollibee").execute()

        # THEN: Match found
        assert len(results) == 1

    def test_p1_filter_by_merchant_partial_match(
        self, db_session, sample_statement
    ):
        """
        [P1] GIVEN transactions with normalized merchants
        WHEN filter_by_merchant() is called with partial name
        THEN partial matching works (ILIKE)
        """
        # GIVEN: Transaction with merchant
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

        # WHEN: Filter with partial name
        results = query.filter_by_merchant("Jollibee").execute()

        # THEN: Partial match found
        assert len(results) == 1

    def test_p1_filter_by_merchant_returns_self_for_chaining(self, db_session):
        """
        [P1] GIVEN SpendingQuery
        WHEN filter_by_merchant() is called
        THEN returns self for method chaining
        """
        # GIVEN: Query
        query = SpendingQuery(db_session)

        # WHEN: Filter by merchant
        result = query.filter_by_merchant("Jollibee")

        # THEN: Returns self for chaining
        assert result is query

    def test_p1_filter_by_merchant_no_matches_returns_empty(
        self, db_session, sample_transactions
    ):
        """
        [P1] GIVEN transactions without matching merchant
        WHEN filter_by_merchant() is called
        THEN returns empty list
        """
        # GIVEN: Transactions without merchant_normalized set
        query = SpendingQuery(db_session)

        # WHEN: Filter by non-existent merchant
        results = query.filter_by_merchant("Non-Existent Merchant").execute()

        # THEN: Empty result
        assert results == []


# ============================================================================
# Test: Helper Functions
# ============================================================================


class TestFormatCurrency:
    """Test Philippine peso currency formatting."""

    def test_p2_format_currency_basic(self):
        """
        [P2] GIVEN a decimal amount
        WHEN format_currency() is called
        THEN returns ₱{amount:,.2f} format
        """
        # GIVEN: Amount
        amount = Decimal("1234.56")

        # WHEN: Format
        formatted = format_currency(amount)

        # THEN: Philippine peso format
        assert formatted == "₱1,234.56"

    def test_p2_format_currency_with_thousands(self):
        """
        [P2] GIVEN a large amount
        WHEN format_currency() is called
        THEN includes thousands separator
        """
        # GIVEN: Large amount
        amount = Decimal("1234567.89")

        # WHEN: Format
        formatted = format_currency(amount)

        # THEN: Thousands separators
        assert formatted == "₱1,234,567.89"

    def test_p2_format_currency_small_amount(self):
        """
        [P2] GIVEN a small amount
        WHEN format_currency() is called
        THEN formats with 2 decimal places
        """
        # GIVEN: Small amount
        amount = Decimal("5.00")

        # WHEN: Format
        formatted = format_currency(amount)

        # THEN: Two decimal places
        assert formatted == "₱5.00"

    def test_p2_format_currency_zero(self):
        """
        [P2] GIVEN zero amount
        WHEN format_currency() is called
        THEN returns ₱0.00
        """
        # GIVEN: Zero
        amount = Decimal("0")

        # WHEN: Format
        formatted = format_currency(amount)

        # THEN: Zero formatted
        assert formatted == "₱0.00"


class TestFormatDateLocalized:
    """Test localized date formatting."""

    def test_p2_format_date_localized_basic(self):
        """
        [P2] GIVEN a datetime
        WHEN format_date_localized() is called
        THEN returns "Mon DD, YYYY" format
        """
        # GIVEN: Date
        date = datetime(2024, 11, 15)

        # WHEN: Format
        formatted = format_date_localized(date)

        # THEN: Localized format
        assert formatted == "Nov 15, 2024"

    def test_p2_format_date_localized_january(self):
        """
        [P2] GIVEN a January date
        WHEN format_date_localized() is called
        THEN returns correct month abbreviation
        """
        # GIVEN: January date
        date = datetime(2024, 1, 1)

        # WHEN: Format
        formatted = format_date_localized(date)

        # THEN: Jan format
        assert formatted == "Jan 01, 2024"

    def test_p2_format_date_localized_december(self):
        """
        [P2] GIVEN a December date
        WHEN format_date_localized() is called
        THEN returns correct month abbreviation
        """
        # GIVEN: December date
        date = datetime(2024, 12, 25)

        # WHEN: Format
        formatted = format_date_localized(date)

        # THEN: Dec format
        assert formatted == "Dec 25, 2024"
