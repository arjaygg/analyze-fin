"""
TDD Tests: Database Models (SQLAlchemy 2.0)

Story 1.1 AC: Database models with proper schema and relationships.
RED phase - these tests will fail until models are implemented.

Tables:
- accounts (id, name, bank_type, created_at)
- statements (id, account_id FK, file_path, imported_at, quality_score)
- transactions (id, statement_id FK, date, description, amount, created_at)
"""

import pytest
from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session


class TestAccountModel:
    """Test Account model structure and behavior."""

    def test_account_model_exists(self):
        """Account model can be imported."""
        from analyze_fin.database.models import Account

        assert Account is not None

    def test_account_has_required_columns(self):
        """Account has id, name, bank_type, created_at columns."""
        from analyze_fin.database.models import Account

        mapper = inspect(Account)
        column_names = [c.key for c in mapper.columns]

        assert "id" in column_names
        assert "name" in column_names
        assert "bank_type" in column_names
        assert "created_at" in column_names

    def test_account_id_is_primary_key(self):
        """Account.id is the primary key."""
        from analyze_fin.database.models import Account

        mapper = inspect(Account)
        pk_columns = [c.key for c in mapper.primary_key]
        assert pk_columns == ["id"]

    def test_account_tablename(self):
        """Account uses 'accounts' table name (plural, snake_case)."""
        from analyze_fin.database.models import Account

        assert Account.__tablename__ == "accounts"

    def test_create_account_instance(self, db_session):
        """Can create and persist an Account."""
        from analyze_fin.database.models import Account

        account = Account(name="GCash Main", bank_type="gcash")
        db_session.add(account)
        db_session.commit()

        assert account.id is not None
        assert account.name == "GCash Main"
        assert account.bank_type == "gcash"
        assert account.created_at is not None


class TestStatementModel:
    """Test Statement model structure and behavior."""

    def test_statement_model_exists(self):
        """Statement model can be imported."""
        from analyze_fin.database.models import Statement

        assert Statement is not None

    def test_statement_has_required_columns(self):
        """Statement has id, account_id, file_path, imported_at, quality_score."""
        from analyze_fin.database.models import Statement

        mapper = inspect(Statement)
        column_names = [c.key for c in mapper.columns]

        assert "id" in column_names
        assert "account_id" in column_names
        assert "file_path" in column_names
        assert "imported_at" in column_names
        assert "quality_score" in column_names

    def test_statement_tablename(self):
        """Statement uses 'statements' table name."""
        from analyze_fin.database.models import Statement

        assert Statement.__tablename__ == "statements"

    def test_statement_has_account_foreign_key(self):
        """Statement.account_id is a foreign key to accounts."""
        from analyze_fin.database.models import Statement

        mapper = inspect(Statement)
        fks = list(mapper.columns["account_id"].foreign_keys)
        assert len(fks) == 1
        assert fks[0].target_fullname == "accounts.id"

    def test_create_statement_with_account(self, db_session):
        """Can create Statement linked to Account."""
        from analyze_fin.database.models import Account, Statement

        account = Account(name="BPI Savings", bank_type="bpi")
        db_session.add(account)
        db_session.commit()

        statement = Statement(
            account_id=account.id,
            file_path="/path/to/statement.pdf",
            quality_score=0.95,
        )
        db_session.add(statement)
        db_session.commit()

        assert statement.id is not None
        assert statement.account_id == account.id
        assert float(statement.quality_score) == 0.95


class TestTransactionModel:
    """Test Transaction model structure and behavior."""

    def test_transaction_model_exists(self):
        """Transaction model can be imported."""
        from analyze_fin.database.models import Transaction

        assert Transaction is not None

    def test_transaction_has_required_columns(self):
        """Transaction has id, statement_id, date, description, amount, created_at."""
        from analyze_fin.database.models import Transaction

        mapper = inspect(Transaction)
        column_names = [c.key for c in mapper.columns]

        assert "id" in column_names
        assert "statement_id" in column_names
        assert "date" in column_names
        assert "description" in column_names
        assert "amount" in column_names
        assert "created_at" in column_names

    def test_transaction_tablename(self):
        """Transaction uses 'transactions' table name."""
        from analyze_fin.database.models import Transaction

        assert Transaction.__tablename__ == "transactions"

    def test_transaction_has_statement_foreign_key(self):
        """Transaction.statement_id is a foreign key to statements."""
        from analyze_fin.database.models import Transaction

        mapper = inspect(Transaction)
        fks = list(mapper.columns["statement_id"].foreign_keys)
        assert len(fks) == 1
        assert fks[0].target_fullname == "statements.id"

    def test_transaction_amount_is_decimal(self, db_session):
        """Transaction.amount is stored as Decimal for precision."""
        from analyze_fin.database.models import Account, Statement, Transaction

        account = Account(name="Maya Wallet", bank_type="maya")
        db_session.add(account)
        db_session.commit()

        statement = Statement(
            account_id=account.id,
            file_path="/path/to/maya.pdf",
            quality_score=0.90,
        )
        db_session.add(statement)
        db_session.commit()

        transaction = Transaction(
            statement_id=statement.id,
            date=datetime(2024, 11, 15),
            description="JOLLIBEE GREENBELT",
            amount=Decimal("285.50"),
        )
        db_session.add(transaction)
        db_session.commit()

        # Reload from DB and verify Decimal precision
        db_session.refresh(transaction)
        assert transaction.amount == Decimal("285.50")
        assert isinstance(transaction.amount, Decimal)


class TestDatabaseRelationships:
    """Test relationships between models."""

    def test_account_has_statements_relationship(self, db_session):
        """Account.statements returns related statements."""
        from analyze_fin.database.models import Account, Statement

        account = Account(name="Test Account", bank_type="gcash")
        db_session.add(account)
        db_session.commit()

        stmt1 = Statement(account_id=account.id, file_path="/jan.pdf", quality_score=0.95)
        stmt2 = Statement(account_id=account.id, file_path="/feb.pdf", quality_score=0.92)
        db_session.add_all([stmt1, stmt2])
        db_session.commit()

        db_session.refresh(account)
        assert len(account.statements) == 2

    def test_statement_has_transactions_relationship(self, db_session):
        """Statement.transactions returns related transactions."""
        from analyze_fin.database.models import Account, Statement, Transaction

        account = Account(name="Test Account", bank_type="bpi")
        db_session.add(account)
        db_session.commit()

        statement = Statement(account_id=account.id, file_path="/test.pdf", quality_score=0.90)
        db_session.add(statement)
        db_session.commit()

        tx1 = Transaction(
            statement_id=statement.id,
            date=datetime(2024, 11, 1),
            description="Tx 1",
            amount=Decimal("100.00"),
        )
        tx2 = Transaction(
            statement_id=statement.id,
            date=datetime(2024, 11, 2),
            description="Tx 2",
            amount=Decimal("200.00"),
        )
        db_session.add_all([tx1, tx2])
        db_session.commit()

        db_session.refresh(statement)
        assert len(statement.transactions) == 2

    def test_statement_account_backref(self, db_session):
        """Statement.account returns the related Account."""
        from analyze_fin.database.models import Account, Statement

        account = Account(name="Backref Test", bank_type="gcash")
        db_session.add(account)
        db_session.commit()

        statement = Statement(account_id=account.id, file_path="/test.pdf", quality_score=0.95)
        db_session.add(statement)
        db_session.commit()

        db_session.refresh(statement)
        assert statement.account.name == "Backref Test"

    def test_transaction_statement_backref(self, db_session):
        """Transaction.statement returns the related Statement."""
        from analyze_fin.database.models import Account, Statement, Transaction

        account = Account(name="Test", bank_type="maya")
        db_session.add(account)
        db_session.commit()

        statement = Statement(account_id=account.id, file_path="/test.pdf", quality_score=0.90)
        db_session.add(statement)
        db_session.commit()

        transaction = Transaction(
            statement_id=statement.id,
            date=datetime(2024, 11, 15),
            description="Test",
            amount=Decimal("50.00"),
        )
        db_session.add(transaction)
        db_session.commit()

        db_session.refresh(transaction)
        assert transaction.statement.file_path == "/test.pdf"


class TestForeignKeyConstraints:
    """Test that foreign key constraints are enforced."""

    def test_cannot_create_statement_without_valid_account(self, db_session):
        """Statement requires valid account_id."""
        from sqlalchemy.exc import IntegrityError
        from analyze_fin.database.models import Statement

        statement = Statement(
            account_id=99999,  # Non-existent account
            file_path="/test.pdf",
            quality_score=0.90,
        )
        db_session.add(statement)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_cannot_create_transaction_without_valid_statement(self, db_session):
        """Transaction requires valid statement_id."""
        from sqlalchemy.exc import IntegrityError
        from analyze_fin.database.models import Transaction

        transaction = Transaction(
            statement_id=99999,  # Non-existent statement
            date=datetime(2024, 11, 15),
            description="Test",
            amount=Decimal("100.00"),
        )
        db_session.add(transaction)

        with pytest.raises(IntegrityError):
            db_session.commit()


class TestBaseModel:
    """Test the declarative base configuration."""

    def test_base_model_exists(self):
        """Base declarative class exists."""
        from analyze_fin.database.models import Base

        assert Base is not None

    def test_all_models_share_base(self):
        """All models inherit from the same Base."""
        from analyze_fin.database.models import Account, Base, Statement, Transaction

        assert issubclass(Account, Base)
        assert issubclass(Statement, Base)
        assert issubclass(Transaction, Base)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database session for testing."""
    from analyze_fin.database.models import Base

    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        # Enable foreign key support for SQLite
        connect_args={"check_same_thread": False},
    )

    # Enable foreign keys for SQLite
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        session.rollback()
