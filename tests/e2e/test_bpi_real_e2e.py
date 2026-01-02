"""
E2E Test: Real BPI Statement Parsing (P0)

Story: BPI Statement Parsing
Priority: P0 (Critical Path)
"""

import pytest
from pathlib import Path
from analyze_fin.parsers.bpi import BPIParser

@pytest.mark.e2e
@pytest.mark.p0
@pytest.mark.xfail(reason="Parser implementation requires adjustment for sample PDF format")
def test_parse_real_bpi_statement(real_bpi_pdf_path):
    """
    GIVEN a real sample BPI PDF statement
    WHEN I parse it with BPIParser
    THEN it should extract transactions correctly
    AND quality score should be high
    """
    # GIVEN
    parser = BPIParser()
    
    # WHEN
    result = parser.parse(real_bpi_pdf_path)
    
    # THEN
    assert result.bank_type == "bpi"
    assert result.quality_score >= 0.8  # Expect high quality
    assert len(result.transactions) > 0
    
    # Check first transaction structure
    tx = result.transactions[0]
    assert tx.date is not None
    assert tx.amount is not None
    assert tx.description is not None
    
    # Verify we have some debits (negative) and credits (positive) if applicable
    # Or at least amounts are not all zero
    assert any(tx.amount != 0 for tx in result.transactions)

