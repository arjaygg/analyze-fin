"""
SQLAlchemy 2.0 Database Models for analyze-fin.

Tables:
- accounts: Bank accounts (GCash, BPI, Maya)
- statements: Imported PDF statements
- transactions: Individual transactions

All models use SQLAlchemy 2.0 Mapped[] type annotations.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    pass


class Base(DeclarativeBase):
    """Declarative base class for all models."""

    pass


class Account(Base):
    """Bank account model.

    Represents a user's bank account (GCash, BPI, Maya, etc.).
    Each account can have multiple statements imported.

    Multi-account support (Story 5.2):
    - account_number: Bank account number or mobile number for identification
    - account_holder: Account holder name
    - Composite unique constraint on (bank_type, account_number)
    """

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    bank_type: Mapped[str] = mapped_column(String(50))  # gcash, bpi, maya, maya_savings, maya_wallet
    account_number: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., "09171234567" or "****1234"
    account_holder: Mapped[str | None] = mapped_column(String(200), nullable=True)  # e.g., "Juan dela Cruz"
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Composite unique constraint: (bank_type, account_number)
    # SQLite allows multiple NULL values in unique constraints
    __table_args__ = (
        UniqueConstraint("bank_type", "account_number", name="uq_bank_account"),
    )

    # Relationships
    statements: Mapped[list["Statement"]] = relationship(
        "Statement",
        back_populates="account",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        acct_num = f", account_number='{self.account_number}'" if self.account_number else ""
        return f"<Account(id={self.id}, name='{self.name}', bank_type='{self.bank_type}'{acct_num})>"


class Statement(Base):
    """Bank statement model.

    Represents an imported PDF bank statement.
    Each statement belongs to one account and contains multiple transactions.
    """

    __tablename__ = "statements"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    file_path: Mapped[str] = mapped_column(String(500))
    imported_at: Mapped[datetime] = mapped_column(default=func.now())
    quality_score: Mapped[float] = mapped_column(Numeric(3, 2))  # 0.00 to 1.00

    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="statements")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="statement",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Statement(id={self.id}, file_path='{self.file_path}', quality={self.quality_score})>"


class Transaction(Base):
    """Transaction model.

    Represents a single financial transaction from a bank statement.
    Amount is stored as Decimal for currency precision.

    Categorization fields are populated after parsing:
    - category: Assigned category (e.g., "Food & Dining")
    - merchant_normalized: Properly-cased merchant name (e.g., "Jollibee")
    - confidence: Extraction/categorization confidence (0.0 to 1.0)

    Deduplication fields:
    - reference_number: Bank-provided reference (if available)
    - is_duplicate: True if marked as duplicate of another transaction
    - duplicate_of_id: ID of the original transaction (if duplicate)
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    statement_id: Mapped[int] = mapped_column(ForeignKey("statements.id"))
    date: Mapped[datetime] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(String(500))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Up to 99,999,999.99
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Categorization fields
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    merchant_normalized: Mapped[str | None] = mapped_column(String(200), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00

    # Deduplication fields
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    duplicate_of_id: Mapped[int | None] = mapped_column(
        ForeignKey("transactions.id"), nullable=True
    )

    # Relationships
    statement: Mapped["Statement"] = relationship("Statement", back_populates="transactions")
    duplicate_of: Mapped["Transaction | None"] = relationship(
        "Transaction", remote_side=[id], foreign_keys=[duplicate_of_id]
    )

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_transactions_date_category", "date", "category"),
        Index("ix_transactions_statement_date", "statement_id", "date"),
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, date={self.date}, amount={self.amount}, category='{self.category}')>"
