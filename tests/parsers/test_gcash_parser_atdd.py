"""
ATDD Acceptance Tests: GCash PDF Parser

Feature: Parse GCash bank statements from PDF files
Story: FR1-7 - Statement Parsing (GCash Support)

These tests are INTENTIONALLY FAILING (RED phase) to guide implementation.
They define the expected behavior before any code is written.

Acceptance Criteria:
- AC1: Extract transactions from valid GCash PDF with >95% accuracy
- AC2: Handle password-protected PDFs (password: surname + last 4 digits)
- AC3: Calculate quality score based on extraction confidence
- AC4: Detect GCash bank type automatically
- AC5: Handle corrupted or invalid PDFs gracefully
- AC6: Support batch parsing of multiple statement files
- AC7: Extract opening/closing balances and statement metadata

Test Status: 🔴 RED (Failing - awaiting implementation)
"""

import pytest
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# These imports will fail until implementation exists
# from src.analyze_fin.parsers.gcash import GCashParser
# from src.analyze_fin.parsers.base import ParseError, PasswordRequiredError
# from src.analyze_fin.parsers.detector import BankTypeDetector

from tests.support.helpers import (
    assert_transaction_valid,
    assert_quality_score_valid,
)


# ============================================================================
# AC1: Extract transactions from valid GCash PDF with >95% accuracy
# ============================================================================

@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.integration
@pytest.mark.slow
def test_parse_valid_gcash_statement_extracts_all_transactions(sample_pdf_path):
    """
    GIVEN a valid GCash PDF statement with 28 transactions
    WHEN the parser processes the file
    THEN all 28 transactions are extracted with >95% quality score

    Implementation Tasks:
    - [ ] Create GCashParser class in src/analyze_fin/parsers/gcash.py
    - [ ] Implement parse() method
    - [ ] Add pdfplumber-based table extraction
    - [ ] Return ParseResult with transactions list
    - [ ] Run: pytest tests/parsers/test_gcash_parser_atdd.py::test_parse_valid_gcash_statement_extracts_all_transactions
    """
    pytest.skip("Implementation pending - awaiting GCashParser class")

    # Expected implementation:
    # parser = GCashParser()
    # result = parser.parse(sample_pdf_path)
    #
    # assert result.quality_score >= 0.95, f"Quality score {result.quality_score} below 95%"
    # assert len(result.transactions) == 28
    # assert result.bank_type == "gcash"


@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.unit
def test_extracted_transaction_has_required_fields():
    """
    GIVEN a single transaction row from GCash PDF
    WHEN the parser extracts the transaction
    THEN the transaction has all required fields: date, description, amount

    Implementation Tasks:
    - [ ] Implement extract_transaction() method in GCashParser
    - [ ] Parse date field (format: "Nov 15, 2024")
    - [ ] Parse description field (merchant name)
    - [ ] Parse amount field (format: "₱1,234.56" or "1234.56")
    - [ ] Return Transaction model with all fields
    """
    pytest.skip("Implementation pending - awaiting GCashParser.extract_transaction()")

    # Expected implementation:
    # parser = GCashParser()
    # row = ["Nov 15, 2024", "JOLLIBEE GREENBELT 3", "₱285.50"]
    #
    # transaction = parser.extract_transaction(row)
    #
    # assert_transaction_valid(transaction)
    # assert transaction.date == datetime(2024, 11, 15)
    # assert transaction.description == "JOLLIBEE GREENBELT 3"
    # assert transaction.amount == Decimal("285.50")


@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.integration
def test_parse_extracts_statement_metadata():
    """
    GIVEN a GCash PDF statement
    WHEN the parser processes the file
    THEN statement metadata is extracted: opening balance, closing balance, statement date

    Implementation Tasks:
    - [ ] Extract opening balance from PDF header/footer
    - [ ] Extract closing balance from PDF header/footer
    - [ ] Extract statement period (month/year)
    - [ ] Add metadata to ParseResult
    """
    pytest.skip("Implementation pending - awaiting metadata extraction")

    # Expected implementation:
    # parser = GCashParser()
    # result = parser.parse(sample_pdf_path)
    #
    # assert result.opening_balance > 0
    # assert result.closing_balance >= 0
    # assert result.statement_date.month == 11
    # assert result.statement_date.year == 2024


# ============================================================================
# AC2: Handle password-protected PDFs
# ============================================================================

@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.integration
def test_parse_password_protected_pdf_raises_error_without_password():
    """
    GIVEN a password-protected GCash PDF
    WHEN the parser attempts to open without password
    THEN a PasswordRequiredError is raised with helpful message

    Implementation Tasks:
    - [ ] Detect password-protected PDFs in parse() method
    - [ ] Define PasswordRequiredError in src/analyze_fin/exceptions.py
    - [ ] Raise error with message: "PDF is password protected. Provide password."
    """
    pytest.skip("Implementation pending - awaiting password detection")

    # Expected implementation:
    # parser = GCashParser()
    # protected_pdf = Path("tests/fixtures/sample_statements/gcash_protected.pdf")
    #
    # with pytest.raises(PasswordRequiredError, match="password protected"):
    #     parser.parse(protected_pdf)


@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.integration
def test_parse_password_protected_pdf_succeeds_with_correct_password():
    """
    GIVEN a password-protected GCash PDF
    WHEN the parser is provided the correct password
    THEN transactions are extracted successfully

    Implementation Tasks:
    - [ ] Add password parameter to parse() method
    - [ ] Pass password to pdfplumber.open()
    - [ ] Successfully extract transactions from protected PDF
    """
    pytest.skip("Implementation pending - awaiting password parameter")

    # Expected implementation:
    # parser = GCashParser()
    # protected_pdf = Path("tests/fixtures/sample_statements/gcash_protected.pdf")
    # password = "DELA CRUZ1234"  # Surname + last 4 phone digits
    #
    # result = parser.parse(protected_pdf, password=password)
    #
    # assert len(result.transactions) > 0
    # assert result.quality_score >= 0.90


# ============================================================================
# AC3: Calculate quality score based on extraction confidence
# ============================================================================

@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.unit
def test_quality_score_calculation_based_on_extraction_confidence():
    """
    GIVEN a list of extracted transactions with varying confidence levels
    WHEN quality score is calculated
    THEN score reflects average confidence: (high confidence → score > 0.95)

    Implementation Tasks:
    - [ ] Add confidence field to each extracted transaction
    - [ ] Implement calculate_quality_score() method
    - [ ] Calculate average confidence across all transactions
    - [ ] Return score between 0.0 and 1.0
    """
    pytest.skip("Implementation pending - awaiting quality score calculation")

    # Expected implementation:
    # parser = GCashParser()
    #
    # # Simulate transactions with confidence scores
    # transactions_high_conf = [
    #     {"confidence": 0.98},
    #     {"confidence": 0.97},
    #     {"confidence": 0.96}
    # ]
    #
    # quality_score = parser.calculate_quality_score(transactions_high_conf)
    #
    # assert_quality_score_valid(quality_score)
    # assert quality_score >= 0.96


@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.unit
def test_quality_score_below_threshold_for_poor_extraction():
    """
    GIVEN transactions with low extraction confidence
    WHEN quality score is calculated
    THEN score is below 0.90 (warning threshold)

    Implementation Tasks:
    - [ ] Quality score accurately reflects poor extractions
    - [ ] Log warning when quality score < 0.90
    """
    pytest.skip("Implementation pending - awaiting quality score thresholds")

    # Expected implementation:
    # parser = GCashParser()
    #
    # transactions_low_conf = [
    #     {"confidence": 0.60},
    #     {"confidence": 0.70},
    #     {"confidence": 0.65}
    # ]
    #
    # quality_score = parser.calculate_quality_score(transactions_low_conf)
    #
    # assert quality_score < 0.90


# ============================================================================
# AC4: Detect GCash bank type automatically
# ============================================================================

@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.unit
def test_detect_gcash_bank_type_from_pdf_content():
    """
    GIVEN a GCash PDF statement
    WHEN bank type detection is performed
    THEN "gcash" is correctly identified

    Implementation Tasks:
    - [ ] Create BankTypeDetector in src/analyze_fin/parsers/detector.py
    - [ ] Implement detect() method
    - [ ] Search PDF text for "GCash" keyword
    - [ ] Return "gcash" when detected
    """
    pytest.skip("Implementation pending - awaiting BankTypeDetector")

    # Expected implementation:
    # detector = BankTypeDetector()
    # pdf_path = Path("tests/fixtures/sample_statements/sample_gcash.pdf")
    #
    # bank_type = detector.detect(pdf_path)
    #
    # assert bank_type == "gcash"


# ============================================================================
# AC5: Handle corrupted or invalid PDFs gracefully
# ============================================================================

@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.integration
def test_parse_corrupted_pdf_raises_parse_error():
    """
    GIVEN a corrupted PDF file
    WHEN the parser attempts to process it
    THEN a ParseError is raised with clear error message

    Implementation Tasks:
    - [ ] Define ParseError in src/analyze_fin/exceptions.py
    - [ ] Wrap pdfplumber operations in try-except
    - [ ] Raise ParseError with message: "Failed to parse PDF: {reason}"
    """
    pytest.skip("Implementation pending - awaiting error handling")

    # Expected implementation:
    # parser = GCashParser()
    # corrupted_pdf = Path("tests/fixtures/sample_statements/corrupted.pdf")
    #
    # with pytest.raises(ParseError, match="Failed to parse"):
    #     parser.parse(corrupted_pdf)


@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.integration
def test_parse_non_gcash_pdf_raises_parse_error():
    """
    GIVEN a PDF that is not a GCash statement
    WHEN GCashParser attempts to parse it
    THEN a ParseError is raised indicating wrong bank type

    Implementation Tasks:
    - [ ] Validate PDF is GCash statement before parsing
    - [ ] Raise ParseError if bank type detection fails
    - [ ] Suggest using correct parser
    """
    pytest.skip("Implementation pending - awaiting bank type validation")

    # Expected implementation:
    # parser = GCashParser()
    # bpi_pdf = Path("tests/fixtures/sample_statements/sample_bpi.pdf")
    #
    # with pytest.raises(ParseError, match="not a GCash statement"):
    #     parser.parse(bpi_pdf)


# ============================================================================
# AC6: Support batch parsing of multiple statement files
# ============================================================================

@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.integration
@pytest.mark.slow
def test_parse_batch_processes_multiple_statements(temp_dir):
    """
    GIVEN multiple GCash PDF files in a directory
    WHEN batch parse is invoked
    THEN all files are processed and results aggregated

    Implementation Tasks:
    - [ ] Implement parse_batch() method in GCashParser
    - [ ] Accept list of PDF paths or directory path
    - [ ] Parse each file independently
    - [ ] Return list of ParseResults
    - [ ] Handle individual file failures gracefully (don't stop entire batch)
    """
    pytest.skip("Implementation pending - awaiting batch parsing")

    # Expected implementation:
    # parser = GCashParser()
    # pdf_files = [
    #     temp_dir / "jan_2024.pdf",
    #     temp_dir / "feb_2024.pdf",
    #     temp_dir / "mar_2024.pdf"
    # ]
    #
    # results = parser.parse_batch(pdf_files)
    #
    # assert len(results) == 3
    # assert all(r.quality_score > 0.90 for r in results)
    # assert sum(len(r.transactions) for r in results) > 50  # Total transactions


# ============================================================================
# AC7: Extract opening/closing balances and statement metadata
# ============================================================================

@pytest.mark.atdd
@pytest.mark.parser
@pytest.mark.integration
def test_balances_match_transaction_totals():
    """
    GIVEN a GCash PDF with opening balance, closing balance, and transactions
    WHEN parsed
    THEN calculated balance (opening + sum(transactions)) matches closing balance

    Implementation Tasks:
    - [ ] Extract opening balance from PDF
    - [ ] Extract closing balance from PDF
    - [ ] Calculate expected closing = opening + sum(all transactions)
    - [ ] Validate balance reconciliation
    - [ ] Add validation_errors to ParseResult if mismatch
    """
    pytest.skip("Implementation pending - awaiting balance validation")

    # Expected implementation:
    # parser = GCashParser()
    # result = parser.parse(sample_pdf_path)
    #
    # calculated_closing = result.opening_balance + sum(t.amount for t in result.transactions)
    #
    # # Allow small rounding difference (1 centavo)
    # assert abs(calculated_closing - result.closing_balance) <= Decimal("0.01")


# ============================================================================
# IMPLEMENTATION CHECKLIST
# ============================================================================

"""
## Red-Green-Refactor Implementation Guide

### RED Phase (Complete) ✅
- ✅ All tests written and failing
- ✅ Acceptance criteria mapped to tests
- ✅ Expected behavior defined

### GREEN Phase (DEV Team - Start Here) 🟢

#### Step 1: Create Base Structure
- [ ] Create src/analyze_fin/parsers/ directory
- [ ] Create src/analyze_fin/parsers/__init__.py
- [ ] Create src/analyze_fin/parsers/base.py (BaseBankParser abstract class)
- [ ] Create src/analyze_fin/exceptions.py (ParseError, PasswordRequiredError)

#### Step 2: Implement GCashParser (Minimal)
- [ ] Create src/analyze_fin/parsers/gcash.py
- [ ] Implement GCashParser class inheriting from BaseBankParser
- [ ] Implement parse() method (minimal working version)
- [ ] Run test: test_parse_valid_gcash_statement_extracts_all_transactions
- [ ] ✅ Make test pass (green)

#### Step 3: Add Transaction Extraction
- [ ] Implement extract_transaction() method
- [ ] Parse date, description, amount fields
- [ ] Run test: test_extracted_transaction_has_required_fields
- [ ] ✅ Make test pass

#### Step 4: Add Metadata Extraction
- [ ] Extract opening/closing balances
- [ ] Extract statement date
- [ ] Run test: test_parse_extracts_statement_metadata
- [ ] ✅ Make test pass

#### Step 5: Add Password Support
- [ ] Detect password-protected PDFs
- [ ] Add password parameter to parse()
- [ ] Run tests: test_parse_password_protected_*
- [ ] ✅ Make tests pass

#### Step 6: Add Quality Score Calculation
- [ ] Implement confidence scoring per transaction
- [ ] Implement calculate_quality_score() method
- [ ] Run tests: test_quality_score_*
- [ ] ✅ Make tests pass

#### Step 7: Add Bank Type Detection
- [ ] Create src/analyze_fin/parsers/detector.py
- [ ] Implement BankTypeDetector class
- [ ] Run test: test_detect_gcash_bank_type_from_pdf_content
- [ ] ✅ Make test pass

#### Step 8: Add Error Handling
- [ ] Wrap PDF operations in try-except
- [ ] Validate bank type before parsing
- [ ] Run tests: test_parse_corrupted_pdf_*, test_parse_non_gcash_pdf_*
- [ ] ✅ Make tests pass

#### Step 9: Add Batch Parsing
- [ ] Implement parse_batch() method
- [ ] Handle multiple files
- [ ] Run test: test_parse_batch_processes_multiple_statements
- [ ] ✅ Make test pass

#### Step 10: Add Balance Validation
- [ ] Implement balance reconciliation logic
- [ ] Add validation warnings to ParseResult
- [ ] Run test: test_balances_match_transaction_totals
- [ ] ✅ Make test pass

### REFACTOR Phase (After All Tests Pass) ♻️
- [ ] Extract duplicate code
- [ ] Optimize PDF parsing performance
- [ ] Add type hints
- [ ] Add docstrings
- [ ] Run full test suite to ensure refactoring doesn't break tests

## Running Tests

```bash
# Run all GCash parser ATDD tests
pytest tests/parsers/test_gcash_parser_atdd.py -v

# Run specific test
pytest tests/parsers/test_gcash_parser_atdd.py::test_parse_valid_gcash_statement_extracts_all_transactions -v

# Run with markers
pytest -m "atdd and parser" -v

# Skip slow tests during development
pytest tests/parsers/test_gcash_parser_atdd.py -m "not slow" -v
```

## Expected Timeline

- Step 1-2: ~2 hours (base structure + minimal parser)
- Steps 3-5: ~3 hours (transaction extraction, metadata, passwords)
- Steps 6-8: ~2 hours (quality score, detection, error handling)
- Steps 9-10: ~2 hours (batch parsing, validation)
- Refactor: ~1 hour

**Total: ~10 hours of focused development**

## Success Criteria

When all tests pass (green):
- ✅ Can parse valid GCash PDFs with >95% accuracy
- ✅ Handles password-protected PDFs
- ✅ Calculates quality scores
- ✅ Detects bank type automatically
- ✅ Handles errors gracefully
- ✅ Supports batch parsing
- ✅ Validates balances
"""
