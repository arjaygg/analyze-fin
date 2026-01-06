"""Test assertion helpers for transaction validation."""

from decimal import Decimal
from typing import Any


def assert_model_matches(model_instance: Any, expected_data: dict[str, Any]) -> None:
    """
    Assert that a SQLAlchemy model instance matches expected data.

    Args:
        model_instance: The model object to check
        expected_data: Dictionary of expected field values
    """
    for key, value in expected_data.items():
        assert hasattr(model_instance, key), f"Model {model_instance} missing attribute {key}"
        actual_value = getattr(model_instance, key)

        # Handle Decimal comparison
        if isinstance(actual_value, Decimal) and not isinstance(value, Decimal):
             if isinstance(value, (str, int, float)):
                 value = Decimal(str(value))

        assert actual_value == value, f"Field {key}: expected {value}, got {actual_value}"


def assert_valid_iso_date(date_str: str) -> None:
    """Assert that a string is a valid ISO date (YYYY-MM-DD)."""
    from datetime import datetime
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise AssertionError(f"String '{date_str}' is not a valid ISO date (YYYY-MM-DD)") from e


def assert_valid_currency(amount_str: str) -> None:
    """Assert that a string is a valid currency amount."""
    try:
        float(amount_str)
    except ValueError as e:
        raise AssertionError(f"String '{amount_str}' is not a valid currency amount") from e


def assert_transaction_valid(transaction: Any) -> None:
    """Assert that a transaction has all required fields.

    Supports both dict and object with attributes.
    """
    required_fields = ["date", "description", "amount"]
    for field in required_fields:
        if isinstance(transaction, dict):
            assert field in transaction, f"Transaction missing required field: {field}"
            assert transaction[field] is not None, f"Transaction field {field} is None"
        else:
            assert hasattr(transaction, field), f"Transaction missing required field: {field}"
            assert getattr(transaction, field) is not None, f"Transaction field {field} is None"


def assert_transactions_equal(tx_a: Any, tx_b: Any) -> None:
    """Assert that two transactions have equal core fields."""
    fields = ["date", "description", "amount"]
    for field in fields:
        val_a = getattr(tx_a, field, None)
        val_b = getattr(tx_b, field, None)
        assert val_a == val_b, f"Transactions differ on {field}: {val_a} != {val_b}"


def assert_currency_equal(
    actual: Decimal | float | str,
    expected: Decimal | float | str,
    precision: int = 2
) -> None:
    """Assert two currency amounts are equal to given precision."""
    actual_dec = Decimal(str(actual)) if not isinstance(actual, Decimal) else actual
    expected_dec = Decimal(str(expected)) if not isinstance(expected, Decimal) else expected
    assert round(actual_dec, precision) == round(expected_dec, precision), \
        f"Currency mismatch: {actual_dec} != {expected_dec}"


def assert_quality_score_valid(score: float) -> None:
    """Assert quality score is within valid range [0.0, 1.0]."""
    assert 0.0 <= score <= 1.0, f"Quality score {score} not in range [0.0, 1.0]"


def assert_no_duplicates(transactions: list[Any], key_func: Any = None) -> None:
    """Assert no duplicate transactions in list.

    Args:
        transactions: List of transactions
        key_func: Optional function to extract comparison key
    """
    if key_func is None:
        def key_func(tx):
            return (tx.date, tx.description, str(tx.amount))

    seen = set()
    for tx in transactions:
        key = key_func(tx)
        assert key not in seen, f"Duplicate transaction found: {key}"
        seen.add(key)


def assert_categorized(transaction: Any) -> None:
    """Assert that a transaction has been categorized."""
    category = getattr(transaction, "category", None)
    assert category is not None, "Transaction is not categorized"
    assert category != "Uncategorized", "Transaction is still Uncategorized"
