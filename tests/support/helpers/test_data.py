"""
Test data generators for creating realistic sample data.

Provides utilities to generate transactions, statements, and other
test data that closely mimics real-world data.
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

# Philippine merchants for realistic test data
# Categories aligned with analyze_fin.categorization.taxonomy
PHILIPPINE_MERCHANTS = [
    ("Jollibee", "Food & Dining"),
    ("7-Eleven", "Food & Dining"),  # Convenience stores categorized as Food
    ("SM Supermarket", "Groceries"),
    ("Mercury Drug", "Health & Wellness"),
    ("Grab", "Transportation"),
    ("McDonald's", "Food & Dining"),
    ("Ministop", "Food & Dining"),  # Convenience stores categorized as Food
    ("Puregold", "Groceries"),
    ("Shopee", "Shopping"),
    ("Lazada", "Shopping"),
    ("Starbucks", "Food & Dining"),
    ("National Bookstore", "Shopping"),
]

# Create lookup dict for merchant -> category
MERCHANT_TO_CATEGORY = {name: cat for name, cat in PHILIPPINE_MERCHANTS}


def generate_transaction(
    date: datetime = None,
    merchant: str = None,
    category: str = None,
    amount: Decimal = None,
    **overrides
) -> dict[str, Any]:
    """
    Generate a realistic transaction.

    Args:
        date: Transaction date (default: random recent date)
        merchant: Merchant name (default: random Philippine merchant)
        category: Category (default: auto-assigned from merchant)
        amount: Transaction amount (default: random amount)
        **overrides: Additional fields to override

    Returns:
        Transaction dictionary
    """
    if date is None:
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        date = datetime.now() - timedelta(days=days_ago)

    if merchant is None:
        # Pick a random merchant
        merchant_name, merchant_category = random.choice(PHILIPPINE_MERCHANTS)
        merchant = merchant_name
        if category is None:
            category = merchant_category
    elif category is None:
        # Merchant provided - look up category or default to Uncategorized
        category = MERCHANT_TO_CATEGORY.get(merchant, "Uncategorized")

    if amount is None:
        # Random amount between 50 and 2000
        amount = Decimal(str(round(random.uniform(50, 2000), 2)))

    transaction = {
        "date": date,
        "description": merchant.upper(),
        "amount": amount,
        "category": category,
        "merchant_normalized": merchant,
    }

    transaction.update(overrides)
    return transaction


def generate_transactions(count: int, **kwargs) -> list[dict[str, Any]]:
    """
    Generate multiple transactions.

    Args:
        count: Number of transactions to generate
        **kwargs: Arguments passed to generate_transaction

    Returns:
        List of transaction dictionaries
    """
    return [generate_transaction(**kwargs) for _ in range(count)]


def generate_monthly_transactions(
    year: int,
    month: int,
    count: int = 20
) -> list[dict[str, Any]]:
    """
    Generate transactions for a specific month.

    Args:
        year: Year
        month: Month (1-12)
        count: Number of transactions

    Returns:
        List of transactions spread across the month
    """
    transactions = []
    start_date = datetime(year, month, 1)

    # Determine number of days in month
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    days_in_month = (end_date - start_date).days + 1

    for _ in range(count):
        # Random day in the month
        day_offset = random.randint(0, days_in_month - 1)
        txn_date = start_date + timedelta(days=day_offset)

        transactions.append(generate_transaction(date=txn_date))

    # Sort by date
    transactions.sort(key=lambda t: t["date"])
    return transactions


def generate_statement_data(
    bank_type: str = "gcash",
    year: int = None,
    month: int = None,
    transaction_count: int = 20
) -> dict[str, Any]:
    """
    Generate complete statement data with transactions.

    Args:
        bank_type: Type of bank (gcash, bpi, maya)
        year: Statement year (default: current year)
        month: Statement month (default: last month)
        transaction_count: Number of transactions

    Returns:
        Statement dictionary with metadata and transactions
    """
    if year is None or month is None:
        now = datetime.now()
        if month is None:
            # Last month
            last_month = now.replace(day=1) - timedelta(days=1)
            month = last_month.month
            year = last_month.year if year is None else year

    transactions = generate_monthly_transactions(year, month, transaction_count)

    # Calculate balances
    opening_balance = Decimal("5000.00")
    total_spent = sum(txn["amount"] for txn in transactions)
    closing_balance = opening_balance - total_spent

    return {
        "account_name": f"{bank_type.upper()} Main Account",
        "bank_type": bank_type,
        "statement_date": datetime(year, month, 1),
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "transactions": transactions,
        "quality_score": 0.95,
    }


def generate_duplicate_transaction(original: dict[str, Any]) -> dict[str, Any]:
    """
    Create a duplicate of a transaction (for testing deduplication).

    Args:
        original: Original transaction

    Returns:
        Duplicate transaction with same key fields
    """
    return {
        "date": original["date"],
        "description": original["description"],
        "amount": original["amount"],
        "category": original.get("category"),
        "merchant_normalized": original.get("merchant_normalized"),
    }


def generate_near_duplicate_transaction(
    original: dict[str, Any],
    time_delta_seconds: int = 60
) -> dict[str, Any]:
    """
    Create a near-duplicate transaction (slightly different timestamp).

    Useful for testing fuzzy duplicate detection.

    Args:
        original: Original transaction
        time_delta_seconds: Seconds to shift the date

    Returns:
        Near-duplicate transaction
    """
    return {
        "date": original["date"] + timedelta(seconds=time_delta_seconds),
        "description": original["description"],
        "amount": original["amount"],
        "category": original.get("category"),
        "merchant_normalized": original.get("merchant_normalized"),
    }
