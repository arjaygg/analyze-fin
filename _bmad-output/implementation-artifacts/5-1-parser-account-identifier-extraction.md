# Story 5.1: Parser Account Identifier Extraction

Status: completed

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want the system to extract unique account identifiers from my bank statements,
So that transactions from different accounts are properly distinguished.

## Acceptance Criteria

**Given** a GCash statement PDF
**When** the parser extracts transaction data
**Then** Mobile number (account identifier) is extracted and stored
**And** Account holder name is extracted when available
**And** Statement period (start/end dates) is extracted from statement header
**And** ParseResult includes account_number, account_holder, period_start, period_end fields

**Given** a BPI statement PDF
**When** the parser extracts transaction data
**Then** Account number (masked, e.g., "****1234") is extracted from header section
**And** Account holder name is extracted
**And** Statement period (start/end dates) is extracted
**And** Account type (savings/checking) is detected if present

**Given** a Maya statement PDF
**When** the parser extracts transaction data
**Then** Account number/ID is extracted from statement header
**And** Account holder name is extracted
**And** Statement period is extracted
**And** Account type (savings/wallet) is correctly identified

**Given** account identifier cannot be extracted from PDF
**When** PDF format doesn't contain expected account info
**Then** System logs warning but continues parsing transactions
**And** account_number field defaults to None (backwards compatible)
**And** Quality score is reduced by 0.05 to indicate incomplete extraction
**And** Parsing does not fail - transactions are still extracted

**Given** ParseResult dataclass
**When** I review the updated structure
**Then** ParseResult has new optional fields: account_number: str | None
**And** ParseResult has new optional field: account_holder: str | None
**And** ParseResult has new optional field: period_start: date | None
**And** ParseResult has new optional field: period_end: date | None
**And** All new fields default to None for backwards compatibility

**Requirements:** FR49, FR50, FR51

## Tasks / Subtasks

- [x] Task 1: Update ParseResult dataclass (AC: #5)
  - [x] Edit src/analyze_fin/parsers/base.py
  - [x] Add account_number: str | None = None to ParseResult
  - [x] Add account_holder: str | None = None to ParseResult
  - [x] Add period_start: date | None = None to ParseResult
  - [x] Add period_end: date | None = None to ParseResult
  - [x] Ensure all existing code continues to work (backwards compatible)
  - [x] Write unit test for new ParseResult fields

- [x] Task 2: Enhance GCash Parser to extract account info (AC: #1)
  - [x] Edit src/analyze_fin/parsers/gcash.py
  - [x] Add _extract_account_info(pdf) method
  - [x] Extract mobile number from statement header (typically "09XX XXX XXXX")
  - [x] Extract account holder name if present
  - [x] Extract statement period dates from header
  - [x] Populate ParseResult with extracted account info
  - [x] Handle missing info gracefully (return None, log warning)
  - [x] Write tests with sample GCash PDF

- [x] Task 3: Enhance BPI Parser to extract account info (AC: #2)
  - [x] Edit src/analyze_fin/parsers/bpi.py
  - [x] Add _extract_account_info(pdf) method
  - [x] Extract account number from header (mask to show only last 4 digits)
  - [x] Extract account holder name
  - [x] Extract statement period dates
  - [x] Detect account type if present (savings/checking)
  - [x] Populate ParseResult with extracted account info
  - [x] Handle missing info gracefully
  - [x] Write tests with sample BPI PDF

- [x] Task 4: Enhance Maya Parser to extract account info (AC: #3)
  - [x] Edit src/analyze_fin/parsers/maya.py
  - [x] Add _extract_account_info(pdf) method
  - [x] Extract account number/ID from statement header
  - [x] Extract account holder name
  - [x] Extract statement period dates
  - [x] Ensure account type (savings/wallet) is correctly populated
  - [x] Populate ParseResult with extracted account info
  - [x] Handle missing info gracefully
  - [x] Write tests with sample Maya PDF

- [x] Task 5: Implement quality score adjustment (AC: #4)
  - [x] Edit quality scoring in base.py or each parser
  - [x] If account_number is None after extraction, reduce score by 0.05
  - [x] If period_start/period_end is None, reduce score by 0.02
  - [x] Log warning when account info cannot be extracted
  - [x] Ensure parsing continues even if account info missing
  - [x] Write tests verifying quality score adjustment

- [x] Task 6: Integration testing
  - [x] Test parsing real GCash statement - verify account info extracted
  - [x] Test parsing real BPI statement - verify account info extracted
  - [x] Test parsing real Maya statement - verify account info extracted
  - [x] Test backwards compatibility with existing code
  - [x] Test that missing account info doesn't break parsing
  - [x] Verify quality score reflects extraction completeness

## Dev Notes

### PDF Header Locations (Based on Existing Parser Code)

**GCash:** Account info typically on first page header
- Mobile number format: "09XX XXX XXXX"
- Statement period: "Statement Period: MMM DD - MMM DD, YYYY"

**BPI:** Account info in statement header block
- Account number typically near account holder name
- Format: "Account Number: XXXX-XXXX-1234"
- Mask to "****1234" before storing

**Maya:** Account info varies by statement type
- Savings: Account number in header
- Wallet: May use different identifier
- Period usually in header or footer

### Backwards Compatibility

All new fields are optional with None defaults. Existing tests should pass without modification. CLI and other code using ParseResult will continue to work - they simply won't use the new fields until Story 5.2 (database schema) and Story 5.3 (downstream skills) are implemented.

### Dependencies

- None - this is the first story in Epic 5
- Stories 5.2-5.5 depend on this story completing first

## Test Files

Create test files in tests/parsers/:
- test_gcash_account_extraction.py
- test_bpi_account_extraction.py
- test_maya_account_extraction.py

Or add to existing parser test files with new test cases.

## Implementation Notes (Completed 2026-01-04)

### Files Modified
- `src/analyze_fin/parsers/base.py` - Added account_number, account_holder, period_start, period_end fields to ParseResult
- `src/analyze_fin/parsers/gcash.py` - Added _extract_account_info() method and quality score adjustment
- `src/analyze_fin/parsers/bpi.py` - Added _extract_account_info() method with account masking (****XXXX) and quality score adjustment
- `src/analyze_fin/parsers/maya.py` - Added _extract_account_info() method and quality score adjustment

### Test Files Added/Modified
- `tests/parsers/test_base_parser.py` - Added TestParseResultAccountFields (8 tests) and TestQualityScoreAdjustment (3 tests)
- `tests/parsers/test_gcash_parser.py` - Added TestGCashAccountInfoExtraction (6 tests)
- `tests/parsers/test_bpi_parser.py` - Added TestBPIAccountInfoExtraction (6 tests)
- `tests/parsers/test_maya_parser.py` - Added TestMayaAccountInfoExtraction (6 tests)
- `tests/e2e/test_account_info_extraction.py` - NEW file with 12 integration tests

### Key Implementation Details
1. **Regex Patterns**: Each parser uses bank-specific regex patterns to extract account info from PDF headers
2. **Quality Score Adjustment**: -0.05 for missing account_number, -0.02 for missing period_start/period_end
3. **BPI Account Masking**: Full account numbers are masked to show only last 4 digits for security
4. **Backwards Compatibility**: All new fields default to None, existing code continues to work unchanged

### Test Coverage
- 672 tests passing (12 new integration tests)
- All acceptance criteria verified through automated tests
