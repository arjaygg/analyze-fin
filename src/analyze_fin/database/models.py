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

from sqlalchemy import ForeignKey, Numeric, String, func
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
    """

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    bank_type: Mapped[str] = mapped_column(String(50))  # gcash, bpi, maya, maya_savings, maya_wallet
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Relationships
    statements: Mapped[list["Statement"]] = relationship(
        "Statement",
        back_populates="account",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, name='{self.name}', bank_type='{self.bank_type}')>"


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
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    statement_id: Mapped[int] = mapped_column(ForeignKey("statements.id"))
    date: Mapped[datetime] = mapped_column()
    description: Mapped[str] = mapped_column(String(500))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Up to 99,999,999.99
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Relationships
    statement: Mapped["Statement"] = relationship("Statement", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, date={self.date}, amount={self.amount})>"
