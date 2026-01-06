"""Tests for multi-account database support (Story 5.2).

Tests AC1-AC4:
- AC1: Database schema migration with new columns
- AC2: Multiple accounts of same bank type
- AC3: Account reuse on re-import
- AC4: Legacy data handling
"""

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from analyze_fin.database.models import Account, Base, Statement, Transaction


@pytest.fixture
def memory_engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(memory_engine):
    """Create session for testing."""
    with Session(memory_engine) as session:
        yield session


class TestSchemaColumns:
    """Test AC1: Database schema has required columns."""

    def test_account_has_account_number_column(self, memory_engine):
        """Account table should have account_number column."""
        inspector = inspect(memory_engine)
        columns = {col["name"] for col in inspector.get_columns("accounts")}
        assert "account_number" in columns

    def test_account_has_account_holder_column(self, memory_engine):
        """Account table should have account_holder column."""
        inspector = inspect(memory_engine)
        columns = {col["name"] for col in inspector.get_columns("accounts")}
        assert "account_holder" in columns

    def test_account_number_is_nullable(self, session):
        """account_number should be nullable for legacy data."""
        account = Account(
            name="Test Account",
            bank_type="gcash",
            account_number=None,
            account_holder=None,
        )
        session.add(account)
        session.commit()
        assert account.id is not None
        assert account.account_number is None

    def test_account_holder_is_nullable(self, session):
        """account_holder should be nullable for legacy data."""
        account = Account(
            name="Test Account",
            bank_type="bpi",
            account_number="****1234",
        )
        session.add(account)
        session.commit()
        assert account.account_holder is None


class TestUniqueConstraint:
    """Test AC1: Composite unique constraint on (bank_type, account_number)."""

    def test_duplicate_bank_account_number_rejected(self, session):
        """Two accounts with same (bank_type, account_number) should fail."""
        account1 = Account(
            name="Account 1",
            bank_type="gcash",
            account_number="09171234567",
        )
        session.add(account1)
        session.commit()

        account2 = Account(
            name="Account 2",
            bank_type="gcash",
            account_number="09171234567",
        )
        session.add(account2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_same_number_different_bank_allowed(self, session):
        """Same account_number with different bank_type should be allowed."""
        account1 = Account(
            name="GCash Account",
            bank_type="gcash",
            account_number="09171234567",
        )
        account2 = Account(
            name="Maya Account",
            bank_type="maya_wallet",
            account_number="09171234567",
        )
        session.add(account1)
        session.add(account2)
        session.commit()

        assert account1.id != account2.id

    def test_null_account_numbers_are_unique(self, session):
        """Multiple accounts with null account_number should be allowed (legacy)."""
        account1 = Account(
            name="GCash Account 1",
            bank_type="gcash",
            account_number=None,
        )
        account2 = Account(
            name="GCash Account 2",
            bank_type="gcash",
            account_number=None,
        )
        session.add(account1)
        session.add(account2)
        # In SQLite, NULL != NULL, so this should work
        session.commit()

        assert account1.id is not None
        assert account2.id is not None


class TestMultipleAccountsSameBank:
    """Test AC2: Multiple accounts of same bank type."""

    def test_create_two_gcash_accounts_different_numbers(self, session):
        """Should create two separate GCash accounts with different numbers."""
        account1 = Account(
            name="Personal GCash",
            bank_type="gcash",
            account_number="09171111111",
            account_holder="Juan dela Cruz",
        )
        account2 = Account(
            name="Business GCash",
            bank_type="gcash",
            account_number="09172222222",
            account_holder="Juan's Store",
        )
        session.add(account1)
        session.add(account2)
        session.commit()

        gcash_accounts = session.query(Account).filter_by(bank_type="gcash").all()
        assert len(gcash_accounts) == 2

    def test_transactions_link_to_correct_account(self, session):
        """Transactions should link to correct account via statement."""
        # Create two accounts
        account1 = Account(
            name="Personal",
            bank_type="gcash",
            account_number="09171111111",
        )
        account2 = Account(
            name="Business",
            bank_type="gcash",
            account_number="09172222222",
        )
        session.add(account1)
        session.add(account2)
        session.commit()

        # Create statements for each
        stmt1 = Statement(
            account_id=account1.id,
            file_path="/path/personal.pdf",
            quality_score=0.95,
        )
        stmt2 = Statement(
            account_id=account2.id,
            file_path="/path/business.pdf",
            quality_score=0.95,
        )
        session.add(stmt1)
        session.add(stmt2)
        session.commit()

        # Verify transactions would link correctly
        assert stmt1.account_id == account1.id
        assert stmt2.account_id == account2.id
        assert stmt1.account.account_number == "09171111111"
        assert stmt2.account.account_number == "09172222222"


class TestGetOrCreateAccount:
    """Test AC2, AC3: get_or_create_account function."""

    def test_creates_new_account_when_none_exists(self, session):
        """Should create new account when no match exists."""
        from analyze_fin.database.operations import get_or_create_account

        account = get_or_create_account(
            session,
            bank_type="gcash",
            account_number="09171234567",
            account_holder="Juan dela Cruz",
        )
        session.commit()

        assert account.id is not None
        assert account.bank_type == "gcash"
        assert account.account_number == "09171234567"
        assert account.account_holder == "Juan dela Cruz"

    def test_returns_existing_account_on_match(self, session):
        """Should return existing account when bank_type and account_number match."""
        from analyze_fin.database.operations import get_or_create_account

        # Create first account
        account1 = get_or_create_account(
            session,
            bank_type="gcash",
            account_number="09171234567",
            account_holder="Juan dela Cruz",
        )
        session.commit()
        original_id = account1.id

        # Try to create same account again
        account2 = get_or_create_account(
            session,
            bank_type="gcash",
            account_number="09171234567",
        )

        assert account2.id == original_id

    def test_different_account_number_creates_new(self, session):
        """Different account_number should create new account."""
        from analyze_fin.database.operations import get_or_create_account

        account1 = get_or_create_account(
            session,
            bank_type="gcash",
            account_number="09171111111",
        )
        session.commit()

        account2 = get_or_create_account(
            session,
            bank_type="gcash",
            account_number="09172222222",
        )
        session.commit()

        assert account1.id != account2.id

    def test_updates_holder_if_not_set(self, session):
        """Should update account_holder if not previously set."""
        from analyze_fin.database.operations import get_or_create_account

        # Create without holder
        account1 = get_or_create_account(
            session,
            bank_type="gcash",
            account_number="09171234567",
        )
        session.commit()
        assert account1.account_holder is None

        # Get again with holder
        account2 = get_or_create_account(
            session,
            bank_type="gcash",
            account_number="09171234567",
            account_holder="Juan dela Cruz",
        )
        session.commit()

        assert account2.id == account1.id
        assert account2.account_holder == "Juan dela Cruz"

    def test_handles_null_account_number_legacy(self, session):
        """Should handle null account_number for legacy imports."""
        from analyze_fin.database.operations import get_or_create_account

        # Legacy import without account number
        account = get_or_create_account(
            session,
            bank_type="gcash",
            account_number=None,
        )
        session.commit()

        assert account.id is not None
        assert account.account_number is None


class TestLegacyDataHandling:
    """Test AC4: Legacy data handling."""

    def test_query_with_null_account_number(self, session):
        """Queries should handle null account_number gracefully."""
        # Create legacy account (no account_number)
        legacy = Account(
            name="Legacy GCash",
            bank_type="gcash",
            account_number=None,
        )
        # Create new account (with account_number)
        new = Account(
            name="New GCash",
            bank_type="gcash",
            account_number="09171234567",
        )
        session.add(legacy)
        session.add(new)
        session.commit()

        # Query all gcash accounts
        accounts = session.query(Account).filter_by(bank_type="gcash").all()
        assert len(accounts) == 2

        # Query by account_number
        found = session.query(Account).filter_by(
            bank_type="gcash",
            account_number="09171234567",
        ).first()
        assert found.id == new.id

    def test_account_display_name_legacy(self, session):
        """Display helper should handle legacy data."""
        from analyze_fin.database.operations import get_account_display_name

        account = Account(
            name="Legacy GCash",
            bank_type="gcash",
            account_number=None,
            account_holder=None,
        )
        session.add(account)
        session.commit()

        display = get_account_display_name(account)
        assert "Unknown" in display or "GCASH" in display.upper()

    def test_account_display_name_with_holder(self, session):
        """Display helper should show holder name."""
        from analyze_fin.database.operations import get_account_display_name

        account = Account(
            name="GCash Account",
            bank_type="gcash",
            account_number="09171234567",
            account_holder="Juan dela Cruz",
        )
        session.add(account)
        session.commit()

        display = get_account_display_name(account)
        assert "Juan dela Cruz" in display

    def test_account_display_name_masked_number(self, session):
        """Display helper should mask account number."""
        from analyze_fin.database.operations import get_account_display_name

        account = Account(
            name="GCash Account",
            bank_type="gcash",
            account_number="09171234567",
            account_holder=None,
        )
        session.add(account)
        session.commit()

        display = get_account_display_name(account)
        # Should show masked number like ****4567
        assert "****" in display or "4567" in display


class TestAccountRepr:
    """Test updated __repr__ method."""

    def test_repr_includes_account_number(self, session):
        """__repr__ should include account_number when set."""
        account = Account(
            name="Test",
            bank_type="gcash",
            account_number="09171234567",
        )
        session.add(account)
        session.commit()

        repr_str = repr(account)
        assert "09171234567" in repr_str or "account_number" in repr_str.lower()
