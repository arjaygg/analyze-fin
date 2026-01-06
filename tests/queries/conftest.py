from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from analyze_fin.database.models import Account, Base, Statement, Transaction


@pytest.fixture
def test_engine():
    """Create in-memory SQLite engine for query tests."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_engine):
    """Provide database session with automatic cleanup (queries test suite local DB)."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_account(db_session) -> Account:
    """Create a sample account for transactions."""
    account = Account(name="Test GCash Account", bank_type="gcash")
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
    - Multiple dates (Nov 1-16, 2024)
    - Multiple amounts (₱50 to ₱5000)
    - Various descriptions
    """
    transactions: list[Transaction] = []
    base_date = datetime(2024, 11, 1)

    for i in range(10):
        tx = Transaction(
            statement_id=sample_statement.id,
            date=base_date + timedelta(days=i),
            description=f"MERCHANT {i} - TEST TRANSACTION",
            amount=Decimal(f"{100 + i * 50}.00"),
        )
        transactions.append(tx)
        db_session.add(tx)

    high_value_tx = Transaction(
        statement_id=sample_statement.id,
        date=datetime(2024, 11, 15),
        description="HIGH VALUE PURCHASE",
        amount=Decimal("5000.00"),
    )
    transactions.append(high_value_tx)
    db_session.add(high_value_tx)

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


