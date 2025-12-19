"""
Custom assertion helpers for test suite.

Provides domain-specific assertions that make tests more readable
and provide better error messages.
"""

from decimal import Decimal
from typing import Any, Dict, List


def assert_transaction_valid(transaction: Dict[str, Any]) -> None:
    """
    Assert that a transaction has all required fields and valid values.

    Args:
        transaction: Transaction dictionary to validate

    Raises:
        AssertionError: If transaction is invalid
    """
    required_fields = ["date", "description", "amount"]

    for field in required_fields:
        assert field in transaction, f"Transaction missing required field: {field}"

    assert isinstance(transaction["amount"], Decimal), \
        f"Amount must be Decimal, got {type(transaction['amount'])}"

    assert transaction["amount"] != 0, "Transaction amount cannot be zero"


def assert_transactions_equal(actual: Dict, expected: Dict, ignore_fields: List[str] = None) -> None:
    """
    Assert two transactions are equal, optionally ignoring certain fields.

    Args:
        actual: Actual transaction
        expected: Expected transaction
        ignore_fields: List of field names to ignore in comparison
    """
    ignore_fields = ignore_fields or ["id", "created_at", "updated_at"]

    actual_filtered = {k: v for k, v in actual.items() if k not in ignore_fields}
    expected_filtered = {k: v for k, v in expected.items() if k not in ignore_fields}

    assert actual_filtered == expected_filtered, \
        f"Transactions don't match.\nActual: {actual_filtered}\nExpected: {expected_filtered}"


def assert_currency_equal(actual: Decimal, expected: Decimal, tolerance: Decimal = Decimal("0.01")) -> None:
    """
    Assert two currency values are equal within tolerance.

    Args:
        actual: Actual amount
        expected: Expected amount
        tolerance: Maximum allowed difference (default: 0.01 or 1 centavo)
    """
    diff = abs(actual - expected)
    assert diff <= tolerance, \
        f"Currency amounts differ by {diff} (tolerance: {tolerance}). Actual: {actual}, Expected: {expected}"


def assert_quality_score_valid(score: float) -> None:
    """
    Assert quality score is valid (between 0 and 1).

    Args:
        score: Quality score to validate
    """
    assert 0.0 <= score <= 1.0, f"Quality score must be between 0 and 1, got {score}"


def assert_no_duplicates(transactions: List[Dict], key_fields: List[str] = None) -> None:
    """
    Assert there are no duplicate transactions based on key fields.

    Args:
        transactions: List of transactions
        key_fields: Fields to check for duplicates (default: date, amount, description)
    """
    key_fields = key_fields or ["date", "amount", "description"]

    seen = set()
    duplicates = []

    for txn in transactions:
        key = tuple(txn.get(field) for field in key_fields)
        if key in seen:
            duplicates.append(txn)
        seen.add(key)

    assert not duplicates, f"Found {len(duplicates)} duplicate transactions: {duplicates}"


def assert_categorized(transaction: Dict) -> None:
    """
    Assert transaction has been categorized.

    Args:
        transaction: Transaction to check
    """
    assert "category" in transaction, "Transaction missing category field"
    assert transaction["category"] is not None, "Transaction category is None"
    assert transaction["category"] != "", "Transaction category is empty"
    assert transaction["category"] != "Uncategorized", \
        "Transaction should be categorized but is marked as Uncategorized"
