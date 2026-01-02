# Story 1.4: Maya Statement Parser

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want to import Maya PDF statements (both Savings and Wallet),
So that I can track my Maya transactions alongside other accounts.

## Acceptance Criteria

**Given** the parser architecture exists
**When** I implement MayaParser in src/analyze_fin/parsers/maya.py
**Then** MayaParser inherits from BaseBankParser
**And** MayaParser detects Maya Savings vs Maya Wallet format
**And** Both formats are parsed correctly

**Given** a Maya Savings statement
**When** I parse the statement
**Then** Dates are extracted in ISO format (typical for Maya)
**And** Transaction descriptions are cleaned and normalized
**And** Amounts handle decimal precision correctly

**Given** a Maya Wallet statement
**When** I parse the statement
**Then** QR payment transactions are captured
**And** Load/cash-in transactions are identified
**And** All transaction types are stored consistently

**Given** Maya statements are imported
**When** I verify the results
**Then** Account records have bank_type="maya_savings" or "maya_wallet"
**And** Transactions from both account types are distinguishable
**And** Quality scoring works for both formats

**Given** edge cases in Maya statements
**When** I parse statements with special characters or multi-line descriptions
**Then** Parser handles them gracefully without data loss
**And** Quality score reflects any parsing ambiguities

**Requirements:** FR1, FR2, FR4, FR8, AR11-AR13, AR19-AR20, NFR6

## Tasks / Subtasks

- [x] Task 1: Implement MayaParser class (AC: #1)
  - [x] Create src/analyze_fin/parsers/maya.py
  - [x] MayaParser class inheriting from BaseBankParser
  - [x] Accept optional password parameter (Maya PDFs typically not protected)
  - [x] Add docstring documenting both account types

- [x] Task 2: Implement account type detection (AC: #1)
  - [x] Extract text from first PDF page
  - [x] Detect "savings" keyword → bank_type="maya_savings"
  - [x] Detect "wallet" keyword → bank_type="maya_wallet"
  - [x] Default to "maya_wallet" if neither found
  - [x] Implement _detect_account_type(text: str) -> str method

- [x] Task 3: Implement multi-format date parsing (AC: #2)
  - [x] Support ISO format: YYYY-MM-DD (most common for Maya)
  - [x] Support European format: DD/MM/YYYY
  - [x] Support US format: MM/DD/YYYY
  - [x] Use heuristic: if first number > 12, it's DD/MM/YYYY
  - [x] Otherwise assume MM/DD/YYYY
  - [x] Implement _parse_date(date_str: str) -> datetime method

- [x] Task 4: Implement Maya amount parsing (AC: #2, #3)
  - [x] Handle "PHP 1,234.56" format
  - [x] Handle "₱1,234.56" format
  - [x] Handle plain "1,234.56" format
  - [x] Handle negative amounts: "-1,234.56"
  - [x] Handle parentheses negative: "(1,234.56)"
  - [x] Remove currency symbols (PHP, ₱)
  - [x] Remove commas and whitespace
  - [x] Convert to Decimal type (never float)

- [x] Task 5: Implement Maya table extraction (AC: #2, #3)
  - [x] Extract tables from all pages
  - [x] Handle table format: Date | Description | Amount | Balance
  - [x] Minimum 3 columns required (Date, Description, Amount)
  - [x] Skip header rows (Date, Transaction Date, empty)
  - [x] Handle QR payment descriptions
  - [x] Handle load/cash-in descriptions
  - [x] Preserve transaction type information in descriptions

- [x] Task 6: Implement error handling (AC: #5)
  - [x] Raise ParseError for corrupted/invalid PDFs
  - [x] Include file_path in error context
  - [x] Capture parsing errors per row
  - [x] Continue parsing after individual row errors
  - [x] Include parsing_errors in ParseResult

- [x] Task 7: Implement quality scoring (AC: #4)
  - [x] Use base class calculate_quality_score() method
  - [x] Verify date, amount, and description completeness
  - [x] Reduce confidence for short descriptions (< 3 chars)
  - [x] Return quality_score in ParseResult

- [x] Task 8: Write comprehensive tests
  - [x] Create tests/parsers/test_maya_parser.py
  - [x] Test MayaParser with Maya Savings statement
  - [x] Test MayaParser with Maya Wallet statement
  - [x] Test account type detection (savings vs wallet)
  - [x] Test ISO date format: YYYY-MM-DD
  - [x] Test European date format: DD/MM/YYYY
  - [x] Test US date format: MM/DD/YYYY
  - [x] Test date format heuristic (first > 12 = DD/MM)
  - [x] Test amount parsing: PHP, ₱, and plain formats
  - [x] Test negative amounts
  - [x] Test QR payment transactions
  - [x] Test load/cash-in transactions
  - [x] Test multi-page statements
  - [x] Test quality scoring
  - [x] Test error handling with invalid PDFs

## Dev Notes

### Previous Story Intelligence

**From Story 1.1 (Project Foundation):**
- SQLAlchemy 2.0 models (Account, Statement, Transaction) ready
- Alembic migrations configured
- Exception hierarchy with ParseError available
- Database uses WAL mode for crash recovery
- Test infrastructure with conftest.py ready

**From Story 1.2 (GCash Parser):**
- BaseBankParser abstract class implemented
- RawTransaction dataclass with date, description, amount, confidence fields
- Quality scoring method available in base class
- Strategy pattern established for bank parsers
- pdfplumber context manager pattern
- Multi-page PDF support pattern

**From Story 1.3 (BPI Parser):**
- Password parameter pattern (optional: str | None = None)
- Multiple date format parsing techniques
- Regex patterns for date extraction
- Error handling with specific ParseError messages
- Security considerations for password handling

**Key Learnings:**
- Use pdfplumber.open(pdf_path, password=password) context manager
- Extract text for account type detection: page.extract_text()
- Multiple date format support requires regex patterns and heuristics
- Quality scoring calculated automatically by base class
- Multi-page iteration: for page in pdf.pages
- Use Decimal type for all amounts (never float)
- Store dates as datetime objects (convert to ISO for storage)
- Absolute imports: from analyze_fin.parsers.base import BaseBankParser

### Git Intelligence Summary

**Recent Implementation (Commit 275830a):**
- Maya parser already implemented ✓
- 356 tests passed, 40 skipped (ATDD tests requiring real PDFs)
- Account type detection working (maya_savings vs maya_wallet)
- Multi-format date parsing implemented

**Implementation File Located:**
- src/analyze_fin/parsers/maya.py exists and is functional
- Includes MayaParser class with account type detection
- Date parsing: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY
- Amount parsing: PHP, ₱, and plain formats
- Account type detection from PDF text

**Key Implementation Patterns Found:**
- _detect_account_type() method scans first page text
- Keywords "savings" and "wallet" determine account type
- Default to "maya_wallet" if neither keyword found
- Multi-format date parsing with regex patterns
- Date format heuristic: first > 12 means DD/MM/YYYY
- Amount parsing handles PHP and ₱ currency symbols
- Table format: Date | Description | Amount | Balance (minimum 3 columns)

**If Implementing Fresh:**
Follow TDD cycle:
1. Write test for MayaParser basic parsing
2. Implement MayaParser.parse() method
3. Write test for account type detection
4. Implement _detect_account_type() method
5. Write tests for multiple date formats
6. Implement _parse_date() with multi-format support
7. Write tests for amount parsing (PHP, ₱, plain)
8. Implement _parse_amount() method
9. Test quality scoring
10. Test edge cases (QR payments, load/cash-in)

**If Reviewing Existing Code:**
Validate against specifications:
- MayaParser inherits from BaseBankParser ✓
- Account type detection (savings vs wallet) ✓
- Multi-format date parsing ✓
- Amount parsing with currency symbols ✓
- QR payment and load/cash-in handling ✓
- Quality scoring implemented ✓

### Architecture Compliance

**MayaParser Implementation Pattern:**
```python
# src/analyze_fin/parsers/maya.py
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import pdfplumber

from analyze_fin.exceptions import ParseError
from analyze_fin.parsers.base import BaseBankParser, ParseResult, RawTransaction

class MayaParser(BaseBankParser):
    """Parser for Maya PDF statements.

    Handles both Maya Savings and Maya Wallet account statements.

    Example:
        parser = MayaParser()
        result = parser.parse(Path("maya_statement.pdf"))
        print(f"Account type: {result.bank_type}")  # maya_savings or maya_wallet
    """

    def extract_transactions(self, pdf_path: Path) -> list[RawTransaction]:
        """Extract transactions from Maya PDF statement."""
        return self.parse(pdf_path).transactions

    def parse(self, pdf_path: Path, password: str | None = None) -> ParseResult:
        """Parse Maya PDF and return structured result.

        Args:
            pdf_path: Path to the Maya PDF file
            password: Optional password (Maya PDFs typically not protected)

        Returns:
            ParseResult with transactions, quality score, and metadata

        Raises:
            ParseError: If PDF cannot be parsed
        """
        transactions: list[RawTransaction] = []
        parsing_errors: list[str] = []
        bank_type = "maya_wallet"  # Default

        try:
            with pdfplumber.open(pdf_path, password=password) as pdf:
                # Detect account type from first page
                if pdf.pages:
                    first_page_text = pdf.pages[0].extract_text() or ""
                    bank_type = self._detect_account_type(first_page_text)

                for page_num, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables() or []

                    for table in tables:
                        if not table:
                            continue

                        for row_idx, row in enumerate(table):
                            if not row or len(row) < 3:
                                continue

                            # Skip header rows
                            first_cell = str(row[0]).strip().lower() if row[0] else ""
                            if first_cell in ("date", "transaction date", ""):
                                continue

                            try:
                                tx = self._extract_transaction_from_row(row)
                                if tx:
                                    transactions.append(tx)
                            except (ValueError, InvalidOperation) as e:
                                parsing_errors.append(f"Page {page_num}, row {row_idx}: {e}")

        except Exception as e:
            raise ParseError(
                f"Failed to parse Maya PDF: {e}",
                file_path=str(pdf_path),
                reason=str(e)
            )

        quality_score = self.calculate_quality_score(transactions)

        return ParseResult(
            transactions=transactions,
            quality_score=quality_score,
            bank_type=bank_type,
            parsing_errors=parsing_errors
        )

    def _detect_account_type(self, text: str) -> str:
        """Detect Maya account type from PDF text.

        Args:
            text: Extracted text from first PDF page

        Returns:
            'maya_savings' or 'maya_wallet'
        """
        text_lower = text.lower()

        if "savings" in text_lower:
            return "maya_savings"
        elif "wallet" in text_lower:
            return "maya_wallet"

        # Default to wallet for generic Maya statements
        return "maya_wallet"

    def _extract_transaction_from_row(self, row: list) -> RawTransaction | None:
        """Extract a single transaction from a Maya table row.

        Expected row format: [Date, Description, Amount, Balance] or similar
        """
        if len(row) < 3:
            raise ValueError(f"Row too short: {len(row)} columns")

        # Extract fields
        date_str = str(row[0]).strip() if row[0] else ""
        description = str(row[1]).strip() if len(row) > 1 and row[1] else ""
        amount_str = str(row[2]).strip() if len(row) > 2 and row[2] else ""

        # Parse date
        date = self._parse_date(date_str)

        # Parse amount
        amount = self._parse_amount(amount_str)

        # Calculate confidence
        confidence = 1.0
        if len(description) < 3:
            confidence -= 0.1

        return RawTransaction(
            date=date,
            description=description,
            amount=amount,
            reference_number=None,
            confidence=max(0.0, confidence)
        )

    def _parse_date(self, date_str: str) -> datetime:
        """Parse Maya date format.

        Handles multiple formats:
        - 'YYYY-MM-DD' (ISO format)
        - 'DD/MM/YYYY' (European format)
        - 'MM/DD/YYYY' (US format)
        """
        date_str = date_str.strip()

        # Try ISO format: YYYY-MM-DD
        iso_pattern = r"(\d{4})-(\d{1,2})-(\d{1,2})"
        match = re.match(iso_pattern, date_str)
        if match:
            year, month, day = match.groups()
            return datetime(int(year), int(month), int(day))

        # Try slash format: DD/MM/YYYY or MM/DD/YYYY
        slash_pattern = r"(\d{1,2})/(\d{1,2})/(\d{4})"
        match = re.match(slash_pattern, date_str)
        if match:
            first, second, year = match.groups()
            first_int = int(first)
            second_int = int(second)
            year_int = int(year)

            # Heuristic: if first > 12, it's DD/MM/YYYY
            if first_int > 12:
                # DD/MM/YYYY
                return datetime(year_int, second_int, first_int)
            else:
                # MM/DD/YYYY
                return datetime(year_int, first_int, second_int)

        raise ValueError(f"Invalid date format: {date_str}")

    def _parse_amount(self, amount_str: str) -> Decimal:
        """Parse Maya amount format.

        Handles:
        - 'PHP 1,234.56'
        - '₱1,234.56'
        - '1,234.56'
        - '-1,234.56' (negative)
        """
        if not amount_str:
            raise ValueError("Empty amount string")

        # Check for negative
        is_negative = False
        if amount_str.startswith("-"):
            is_negative = True
            amount_str = amount_str[1:]
        elif amount_str.startswith("(") and amount_str.endswith(")"):
            is_negative = True
            amount_str = amount_str[1:-1]

        # Remove currency symbols and whitespace
        cleaned = (
            amount_str
            .replace("PHP", "")
            .replace("₱", "")
            .replace(",", "")
            .replace(" ", "")
            .strip()
        )

        if not cleaned:
            raise ValueError(f"Invalid amount: {amount_str}")

        try:
            amount = Decimal(cleaned)
            if is_negative:
                amount = -amount
            return amount
        except InvalidOperation as e:
            raise ValueError(f"Cannot parse amount '{amount_str}': {e}")
```

### Technical Requirements

**Maya Account Type Detection:**
- Extract text from first PDF page: `page.extract_text()`
- Search for keyword "savings" → bank_type="maya_savings"
- Search for keyword "wallet" → bank_type="maya_wallet"
- Case-insensitive search: convert text to lowercase
- Default to "maya_wallet" if neither keyword found
- Use simple string search: `"savings" in text.lower()`

**Maya Date Format Specifics:**
- **ISO format (most common):** "YYYY-MM-DD" (e.g., "2024-11-15")
- **European format:** "DD/MM/YYYY" (e.g., "15/11/2024")
- **US format:** "MM/DD/YYYY" (e.g., "11/15/2024")
- **Date format heuristic:** If first number > 12, it's DD/MM/YYYY, else MM/DD/YYYY
- Parse with regex patterns for each format
- Convert to datetime: `datetime(year, month, day)`
- Store as: ISO format `2024-11-15` (datetime type)

**Maya Table Structure:**
- Columns: Date | Description | Amount | Balance
- 4 columns typical, minimum 3 needed (Date, Description, Amount)
- Balance column optional, not used for transaction extraction
- Skip rows where first cell is "Date", "Transaction Date", or empty
- Handle varying table structures across Maya Savings vs Wallet

**Currency Amount Parsing:**
- Input formats:
  - With "PHP" prefix: "PHP 1,234.56"
  - With peso sign: "₱1,234.56"
  - Plain format: "1,234.56"
  - Negative: "-1,234.56"
  - Negative with parentheses: "(1,234.56)"
- Remove currency symbols: "PHP", "₱"
- Remove commas: `amount_str.replace(",", "")`
- Remove whitespace: `amount_str.strip()`
- Detect negative sign or parentheses
- Convert to Decimal: `Decimal(cleaned)`
- NEVER use float for money amounts

**QR Payment and Load/Cash-In Handling:**
- QR payments appear in description field (e.g., "QR Ph Payment to...")
- Load/cash-in transactions appear in description (e.g., "Cash In via...")
- Preserve full description text to capture transaction type
- No special parsing needed - descriptions stored as-is
- Quality scoring validates description is not empty

**Account Type Differentiation:**
- Maya Savings: bank_type="maya_savings"
- Maya Wallet: bank_type="maya_wallet"
- Both stored in same Account table with different bank_type
- Allows querying transactions by account type
- Reports can show Savings vs Wallet separately

**Database Import Flow:**
1. Parse PDF → list[RawTransaction]
2. Detect account type from PDF text
3. Calculate quality_score
4. Begin database transaction
5. Create/retrieve Account (bank_type="maya_savings" or "maya_wallet")
6. Create Statement (account_id, file_path, quality_score, bank_type)
7. Create Transactions (statement_id, date, description, amount)
8. Commit transaction
9. On error: Rollback, raise ParseError

### Library & Framework Requirements

**pdfplumber Text Extraction:**
```python
import pdfplumber

with pdfplumber.open(pdf_path) as pdf:
    # Extract text from first page for account type detection
    if pdf.pages:
        first_page_text = pdf.pages[0].extract_text() or ""
        # Search for "savings" or "wallet" keywords

    # Then extract tables from all pages
    for page in pdf.pages:
        tables = page.extract_tables() or []
        # Process tables
```

**Key pdfplumber Methods for Maya:**
- `page.extract_text()` - Extract full text from page (for account type detection)
- `page.extract_tables()` - Extract ALL tables from page (returns list of tables)
- Handle None returns: `extract_text() or ""` and `extract_tables() or []`
- Multiple tables per page possible (though less common in Maya statements)

**Regex Patterns for Multi-Format Date Parsing:**
```python
import re
from datetime import datetime

# ISO format: YYYY-MM-DD
iso_pattern = r"(\d{4})-(\d{1,2})-(\d{1,2})"
match = re.match(iso_pattern, date_str)
if match:
    year, month, day = match.groups()
    return datetime(int(year), int(month), int(day))

# Slash format: DD/MM/YYYY or MM/DD/YYYY
slash_pattern = r"(\d{1,2})/(\d{1,2})/(\d{4})"
match = re.match(slash_pattern, date_str)
if match:
    first, second, year = match.groups()
    first_int = int(first)

    # Heuristic: if first > 12, it's DD/MM/YYYY
    if first_int > 12:
        return datetime(int(year), int(second), first_int)  # DD/MM/YYYY
    else:
        return datetime(int(year), first_int, int(second))  # MM/DD/YYYY
```

**Decimal Handling for Maya Amounts:**
```python
from decimal import Decimal, InvalidOperation

# Parse amount with multiple currency formats
def parse_amount(amount_str: str) -> Decimal:
    # Handle negative
    is_negative = amount_str.startswith("-") or (
        amount_str.startswith("(") and amount_str.endswith(")")
    )

    # Remove currency symbols
    cleaned = (
        amount_str
        .replace("PHP", "")
        .replace("₱", "")
        .replace(",", "")
        .replace(" ", "")
        .strip()
    )

    try:
        amount = Decimal(cleaned)
        if is_negative:
            amount = -amount
        return amount
    except InvalidOperation:
        raise ValueError(f"Cannot parse amount: {amount_str}")
```

**Type Hints Required:**
```python
from pathlib import Path
from decimal import Decimal
from datetime import datetime

def parse(self, pdf_path: Path, password: str | None = None) -> ParseResult: ...
def _detect_account_type(self, text: str) -> str: ...
def _extract_transaction_from_row(self, row: list) -> RawTransaction | None: ...
def _parse_date(self, date_str: str) -> datetime: ...
def _parse_amount(self, amount_str: str) -> Decimal: ...
```

### File Structure Requirements

**MUST Create/Modify These Files:**
1. `src/analyze_fin/parsers/maya.py` - MayaParser implementation
2. `tests/parsers/test_maya_parser.py` - Maya parser tests
3. `src/analyze_fin/parsers/__init__.py` - Export MayaParser (if not already done)

**MayaParser Module Structure:**
```
src/analyze_fin/parsers/
├── __init__.py          # Export BaseBankParser, GCashParser, BPIParser, MayaParser
├── base.py              # BaseBankParser, RawTransaction
├── gcash.py             # GCashParser (already implemented)
├── bpi.py               # BPIParser (already implemented)
├── maya.py              # MayaParser (this story)
└── batch.py             # Batch processing (if exists)
```

### Testing Requirements

**Test Structure:**
```python
# tests/parsers/test_maya_parser.py
import pytest
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from analyze_fin.parsers.maya import MayaParser
from analyze_fin.exceptions import ParseError

def test_maya_parser_detects_savings_account():
    """Test MayaParser detects Maya Savings account type."""
    parser = MayaParser()
    result = parser.parse(Path("tests/fixtures/sample_maya_savings.pdf"))

    assert result.bank_type == "maya_savings"
    assert len(result.transactions) > 0

def test_maya_parser_detects_wallet_account():
    """Test MayaParser detects Maya Wallet account type."""
    parser = MayaParser()
    result = parser.parse(Path("tests/fixtures/sample_maya_wallet.pdf"))

    assert result.bank_type == "maya_wallet"
    assert len(result.transactions) > 0

def test_maya_parser_defaults_to_wallet():
    """Test MayaParser defaults to wallet if type unclear."""
    parser = MayaParser()
    # Mock PDF without "savings" or "wallet" keywords
    # Should default to maya_wallet

def test_maya_date_parsing_iso_format():
    """Test MayaParser parses ISO date format."""
    parser = MayaParser()

    assert parser._parse_date("2024-11-15") == datetime(2024, 11, 15)
    assert parser._parse_date("2024-1-5") == datetime(2024, 1, 5)

def test_maya_date_parsing_european_format():
    """Test MayaParser parses DD/MM/YYYY format."""
    parser = MayaParser()

    # First number > 12, so DD/MM/YYYY
    assert parser._parse_date("15/11/2024") == datetime(2024, 11, 15)
    assert parser._parse_date("31/12/2023") == datetime(2023, 12, 31)

def test_maya_date_parsing_us_format():
    """Test MayaParser parses MM/DD/YYYY format."""
    parser = MayaParser()

    # First number <= 12, so MM/DD/YYYY
    assert parser._parse_date("11/15/2024") == datetime(2024, 11, 15)
    assert parser._parse_date("1/5/2024") == datetime(2024, 1, 5)

def test_maya_amount_parsing_with_php():
    """Test MayaParser parses amounts with PHP prefix."""
    parser = MayaParser()

    assert parser._parse_amount("PHP 1,234.56") == Decimal("1234.56")
    assert parser._parse_amount("PHP 100.00") == Decimal("100.00")

def test_maya_amount_parsing_with_peso_sign():
    """Test MayaParser parses amounts with ₱ symbol."""
    parser = MayaParser()

    assert parser._parse_amount("₱1,234.56") == Decimal("1234.56")
    assert parser._parse_amount("₱100") == Decimal("100")

def test_maya_amount_parsing_plain():
    """Test MayaParser parses plain amounts."""
    parser = MayaParser()

    assert parser._parse_amount("1,234.56") == Decimal("1234.56")
    assert parser._parse_amount("100.00") == Decimal("100.00")

def test_maya_amount_parsing_negative():
    """Test MayaParser parses negative amounts."""
    parser = MayaParser()

    assert parser._parse_amount("-500.00") == Decimal("-500.00")
    assert parser._parse_amount("(500.00)") == Decimal("-500.00")

def test_maya_qr_payment_description():
    """Test MayaParser captures QR payment descriptions."""
    parser = MayaParser()

    # Mock row with QR payment description
    row = ["2024-11-15", "QR Ph Payment to JOLLIBEE", "125.50", "9,874.50"]
    tx = parser._extract_transaction_from_row(row)

    assert "QR Ph Payment" in tx.description
    assert tx.amount == Decimal("125.50")

def test_maya_cash_in_description():
    """Test MayaParser captures load/cash-in descriptions."""
    parser = MayaParser()

    # Mock row with cash-in description
    row = ["2024-11-16", "Cash In via 7-Eleven", "1000.00", "10,874.50"]
    tx = parser._extract_transaction_from_row(row)

    assert "Cash In" in tx.description
    assert tx.amount == Decimal("1000.00")

def test_maya_multi_page_support():
    """Test MayaParser handles multi-page Maya statements."""
    parser = MayaParser()
    result = parser.parse(Path("tests/fixtures/sample_maya_multipage.pdf"))

    # Verify transactions from multiple pages collected
    assert len(result.transactions) >= 15

def test_maya_quality_score():
    """Test quality score reflects Maya parsing confidence."""
    parser = MayaParser()
    result = parser.parse(Path("tests/fixtures/sample_maya_wallet.pdf"))

    assert 0.0 <= result.quality_score <= 1.0
    assert result.quality_score >= 0.95  # High confidence for valid statements

def test_maya_parser_invalid_pdf_raises_error():
    """Test ParseError raised for corrupted PDF."""
    parser = MayaParser()

    with pytest.raises(ParseError):
        parser.parse(Path("tests/fixtures/corrupted.pdf"))
```

**Test Fixtures:**
- Create `tests/fixtures/sample_maya_savings.pdf` (with "Savings" keyword)
- Create `tests/fixtures/sample_maya_wallet.pdf` (with "Wallet" keyword)
- Create `tests/fixtures/sample_maya_multipage.pdf` (multi-page)
- Or mock pdfplumber responses for deterministic tests
- Test with various Maya transaction types (QR, cash-in, transfers)

**Edge Case Testing:**
- Test special characters in descriptions
- Test multi-line descriptions (if Maya supports)
- Test very short descriptions (< 3 chars)
- Test missing amount or date fields
- Test empty rows
- Test varying column counts

### Project Structure Notes

**Alignment with Architecture:**
- Strategy pattern: BaseBankParser → GCashParser, BPIParser, MayaParser
- Maya-specific logic in maya.py (account type detection, multi-format dates)
- Shared logic in base class (quality scoring, bank detection)
- Extensible: Easy to add more banks following same pattern

**Import Pattern:**
```python
# CORRECT - absolute imports
from analyze_fin.parsers.base import BaseBankParser, RawTransaction, ParseResult
from analyze_fin.parsers.maya import MayaParser
from analyze_fin.database.models import Account, Statement, Transaction
from analyze_fin.exceptions import ParseError

# WRONG - relative imports
from .base import BaseBankParser  # NO!
from ..database.models import Account  # NO!
```

**Naming Conventions:**
- Class: `MayaParser` (PascalCase)
- File: `maya.py` (lowercase snake_case)
- Methods: `parse()`, `extract_transactions()` (snake_case)
- Private methods: `_parse_date()`, `_parse_amount()`, `_detect_account_type()` (leading underscore)
- Bank types: `"maya_savings"`, `"maya_wallet"` (lowercase with underscore)

### Critical Don't-Miss Rules

**Philippine Bank Specifics - Maya:**
- **Maya account types:** Maya Savings vs Maya Wallet (detect from PDF text)
- **Maya date formats:** YYYY-MM-DD (ISO), DD/MM/YYYY, or MM/DD/YYYY
- **Date format heuristic:** If first number > 12, it's DD/MM/YYYY, else MM/DD/YYYY
- **Maya amounts:** "PHP 1,234.56", "₱1,234.56", or plain "1,234.56"
- **Transaction types:** QR payments, load/cash-in, transfers (in description)
- **Table format:** Date | Description | Amount | Balance (typically 4 columns, minimum 3)
- **No password protection:** Maya PDFs typically not password-protected

**Account Type Detection:**
- Extract text from first PDF page only (for performance)
- Case-insensitive keyword search: "savings" or "wallet"
- Default to "maya_wallet" if neither keyword found
- Store as bank_type in Account table
- Both account types use same MayaParser class

**Multi-Format Date Parsing:**
- Try ISO format first (most common for Maya): YYYY-MM-DD
- Fall back to slash format: DD/MM/YYYY or MM/DD/YYYY
- Use heuristic to disambiguate: first > 12 means DD/MM/YYYY
- Raise ValueError if no format matches
- DO NOT guess or assume - be explicit about format detection

**Error Handling:**
- Raise ParseError (NOT generic Exception)
- Include file_path in ParseError for user context
- Capture per-row parsing errors in parsing_errors list
- Continue parsing after individual row errors (graceful degradation)
- Include parsing_errors in ParseResult for user review

**Data Types:**
- Dates: `datetime` type (NOT string, NOT datetime.date)
- Amounts: `Decimal` type (NEVER float)
- Descriptions: `str` type (stripped of whitespace)
- Account type: `str` type ("maya_savings" or "maya_wallet")

**Quality Scoring Thresholds:**
- `>= 0.95`: High confidence, auto-accept
- `0.80 - 0.95`: Medium confidence, flag for review
- `< 0.80`: Low confidence, manual review required
- Reduce confidence for short descriptions (< 3 chars)

**Transaction Type Preservation:**
- QR payments: preserve "QR Ph Payment" in description
- Load/cash-in: preserve "Cash In via" in description
- Transfers: preserve "Transfer to/from" in description
- All transaction type information captured in description field
- No separate transaction_type field needed

### References

All technical details sourced from:
- [Source: _bmad-output/epics.md#Story 1.4]
- [Source: _bmad-output/architecture.md#Parser Architecture]
- [Source: _bmad-output/project-context.md#Philippine Bank-Specific Rules]
- [Source: _bmad-output/project-context.md#Framework-Specific Rules]
- [Source: src/analyze_fin/parsers/maya.py#Existing Implementation]
- [Source: Story 1.1#Previous Story Intelligence]
- [Source: Story 1.2#Previous Story Intelligence]
- [Source: Story 1.3#Previous Story Intelligence]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All Maya parser tests passing: 17 tests in test_maya_parser.py
- Full parser test suite: 96 passed, 12 skipped
- Ruff linting: All checks passed (after fixing exception chaining)

### Completion Notes List

- [x] All acceptance criteria verified
- [x] MayaParser class implemented with account type detection
- [x] Account type detection from PDF text working
- [x] Maya Savings vs Maya Wallet differentiation working
- [x] ISO date format parsing (YYYY-MM-DD) working
- [x] European date format parsing (DD/MM/YYYY) working
- [x] US date format parsing (MM/DD/YYYY) working
- [x] Date format heuristic (first > 12) working correctly
- [x] Amount parsing with "PHP" prefix working
- [x] Amount parsing with "₱" symbol working
- [x] Amount parsing plain format working
- [x] Negative amount handling working
- [x] QR payment descriptions preserved
- [x] Load/cash-in descriptions preserved
- [x] Multi-page PDF support tested
- [x] Quality scoring >= 0.95 for valid statements
- [x] ParseError handling tested
- [x] Tests passing (pytest)
- [x] Code quality checks passing (ruff)

### File List

Files created/modified during implementation:
- src/analyze_fin/parsers/maya.py
- tests/parsers/test_maya_parser.py

### Change Log

- 2025-12-19: Story implementation verified complete - all tests passing, code quality checks passing
