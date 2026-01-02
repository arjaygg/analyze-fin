"""
Example test file demonstrating pytest patterns and best practices.

This file shows the recommended structure and patterns for writing tests
in the analyze-fin project. Use this as a template for actual tests.
"""

from datetime import datetime
from decimal import Decimal

import pytest

from tests.support.helpers import (
    assert_transaction_valid,
    generate_transaction,
)

# ============================================================================
# Unit Tests (fast, isolated)
# ============================================================================

@pytest.mark.unit
def test_sample_fixture_usage(sample_transaction_data):
    """
    Example: Using fixtures from conftest.py.

    Fixtures provide reusable test data and setup.
    """
    assert sample_transaction_data["description"] == "JOLLIBEE GREENBELT 3"
    assert sample_transaction_data["amount"] == Decimal("285.50")


@pytest.mark.unit
def test_custom_assertion_helpers():
    """
    Example: Using custom assertion helpers.

    Custom assertions provide better error messages and domain-specific validation.
    """
    transaction = {
        "date": datetime(2024, 11, 15),
        "description": "Test Merchant",
        "amount": Decimal("100.50"),
    }

    # This will validate all required fields and types
    assert_transaction_valid(transaction)


@pytest.mark.unit
def test_data_generator_usage():
    """
    Example: Using test data generators.

    Generators create realistic test data with minimal code.
    """
    transaction = generate_transaction(
        merchant="7-Eleven",
        amount=Decimal("50.00")
    )

    assert transaction["merchant_normalized"] == "7-Eleven"
    assert transaction["category"] == "Food & Dining"  # Convenience stores categorized as Food
    assert transaction["amount"] == Decimal("50.00")


# ============================================================================
# Integration Tests (database, file I/O)
# ============================================================================

@pytest.mark.integration
def test_database_integration_example(temp_db_file):
    """
    Example: Integration test using temporary database.

    Integration tests verify components work together correctly.
    """
    # When actual database code exists, you would:
    # 1. Create database connection
    # 2. Perform operations
    # 3. Verify results
    # 4. Database automatically cleaned up after test

    assert temp_db_file.exists()
    # db = create_connection(temp_db_file)
    # transaction = create_transaction(db, sample_data)
    # assert transaction.id is not None


@pytest.mark.integration
def test_file_operations_example(temp_dir):
    """
    Example: Testing file operations with isolated filesystem.

    Use temp_dir fixture for file operations to avoid polluting the project.
    """
    test_file = temp_dir / "test_output.json"
    test_file.write_text('{"key": "value"}')

    assert test_file.exists()
    assert '"key"' in test_file.read_text()


# ============================================================================
# Parametrized Tests (test multiple scenarios)
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("amount,expected_type", [
    (Decimal("100.00"), Decimal),
    (Decimal("0.01"), Decimal),
    (Decimal("9999.99"), Decimal),
])
def test_parametrized_example(amount, expected_type):
    """
    Example: Parametrized test - runs once per parameter set.

    Useful for testing multiple input scenarios with same logic.
    """
    assert isinstance(amount, expected_type)


@pytest.mark.unit
@pytest.mark.parametrize("merchant,expected_category", [
    ("Jollibee", "Food & Dining"),
    ("7-Eleven", "Food & Dining"),  # Convenience stores categorized as Food
    ("Grab", "Transportation"),
])
def test_categorization_example(merchant, expected_category):
    """
    Example: Testing categorization logic with multiple merchants.
    """
    transaction = generate_transaction(merchant=merchant)
    assert transaction["category"] == expected_category


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.unit
def test_exception_handling_example():
    """
    Example: Testing that exceptions are raised correctly.

    Use pytest.raises to verify exception behavior.
    """
    # When actual code exists:
    # with pytest.raises(ValidationError, match="Invalid transaction"):
    #     validate_transaction({"invalid": "data"})
    pass


# ============================================================================
# Test Organization Tips
# ============================================================================

class TestTransactionOperations:
    """
    Example: Grouping related tests in a class.

    Classes help organize tests without sharing state.
    Don't use __init__ or self state - use fixtures instead.
    """

    @pytest.mark.unit
    def test_create_operation(self):
        """Test transaction creation."""
        pass

    @pytest.mark.unit
    def test_update_operation(self):
        """Test transaction update."""
        pass

    @pytest.mark.unit
    def test_delete_operation(self):
        """Test transaction deletion."""
        pass


# ============================================================================
# Skipping and Conditional Tests
# ============================================================================

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """
    Example: Skip test for unimplemented features.

    Use @pytest.mark.skip to mark tests that aren't ready.
    """
    pass


@pytest.mark.skipif(
    condition=True,  # Replace with actual condition
    reason="Skipped on certain conditions"
)
def test_conditional_skip():
    """
    Example: Conditionally skip tests.

    Use @pytest.mark.skipif for platform or dependency-specific tests.
    """
    pass
