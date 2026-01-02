"""
Test helper utilities.

Import common helpers for easy access:
    from tests.support.helpers import assert_transaction_valid, generate_transaction
"""

from .assertions import (
    assert_categorized,
    assert_currency_equal,
    assert_no_duplicates,
    assert_quality_score_valid,
    assert_transaction_valid,
    assert_transactions_equal,
)
from .test_data import (
    generate_duplicate_transaction,
    generate_monthly_transactions,
    generate_near_duplicate_transaction,
    generate_statement_data,
    generate_transaction,
    generate_transactions,
)

__all__ = [
    # Assertions
    "assert_transaction_valid",
    "assert_transactions_equal",
    "assert_currency_equal",
    "assert_quality_score_valid",
    "assert_no_duplicates",
    "assert_categorized",
    # Data generators
    "generate_transaction",
    "generate_transactions",
    "generate_monthly_transactions",
    "generate_statement_data",
    "generate_duplicate_transaction",
    "generate_near_duplicate_transaction",
]
