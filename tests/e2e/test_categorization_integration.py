"""
Integration Test: Categorization & Database (P1)

Story: Categorization Integration
Priority: P1 (High)
"""

import pytest
from datetime import datetime
from decimal import Decimal
from analyze_fin.categorization.categorizer import Categorizer
from analyze_fin.parsers.base import RawTransaction

# Mocking database models since they might not be fully implemented or available in this context
# but ideally this would use real DB models if available.
# We will use the 'in_memory_db' concept but with Python objects if DB is not ready.

@pytest.mark.integration
@pytest.mark.p1
def test_categorize_and_process_transactions():
    """
    GIVEN a list of raw transactions
    WHEN they are processed by the Categorizer
    THEN they should have categories assigned
    AND high confidence results should be accepted automatically
    """
    # GIVEN
    categorizer = Categorizer()
    transactions = [
        RawTransaction(
            date=datetime(2024, 11, 15),
            description="JOLLIBEE GREENBELT",
            amount=Decimal("-250.00")
        ),
        RawTransaction(
            date=datetime(2024, 11, 16),
            description="MERALCO BILL",
            amount=Decimal("-1500.00")
        ),
        RawTransaction(
            date=datetime(2024, 11, 17),
            description="UNKNOWN VENDOR 123",
            amount=Decimal("-50.00")
        )
    ]
    
    # WHEN
    results = categorizer.categorize_transactions(transactions)
    
    # THEN
    assert len(results) == 3
    
    # Check Jollibee (Food & Dining)
    assert results[0].category == "Food & Dining"
    assert results[0].confidence > 0.9
    assert results[0].merchant_normalized == "Jollibee"
    
    # Check Meralco (Bills)
    assert results[1].category == "Bills & Utilities"
    
    # Check Unknown
    assert results[2].category == "Uncategorized"
    assert results[2].confidence == 0.0

@pytest.mark.integration
@pytest.mark.p2
def test_categorizer_consistency():
    """
    GIVEN the same transaction description
    WHEN categorized multiple times
    THEN it should always return the same result
    """
    categorizer = Categorizer()
    description = "GRAB RIDE"
    
    result1 = categorizer.categorize(description)
    result2 = categorizer.categorize(description)
    
    assert result1.category == result2.category
    assert result1.confidence == result2.confidence

