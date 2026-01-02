

# PDF Fixtures Guide for ATDD Tests

**Purpose:** Enable the 40 skipped @atdd tests that require actual PDF bank statement files.

**Status:** Currently 40 @atdd tests are skipped because they need real PDF fixtures.

---

## Overview

The following test files contain skipped @atdd tests waiting for PDF fixtures:

- `tests/parsers/test_gcash_parser_atdd.py` - 14 tests (GCash statement parsing)
- `tests/categorization/test_categorization_atdd.py` - 12 tests (Auto-categorization with real statements)
- Additional @atdd tests in other modules - 14 tests

---

## Required PDF Fixtures

### 1. GCash Statement PDF

**File:** `tests/fixtures/sample_statements/sample_gcash.pdf`

**Requirements:**
- Multi-page statement with 28+ transactions
- Date format: "MMM DD, YYYY" (e.g., "Nov 15, 2024")
- Amount format: "₱1,234.56" with peso symbol
- Transaction table with columns: Date, Description, Amount
- Opening and closing balances
- Account holder information

**How to Obtain:**
```bash
# Option 1: Anonymize a real GCash statement
# - Download your actual GCash statement PDF
# - Use PDF editing tool to anonymize:
#   * Account number → "1234-5678-9012"
#   * Account holder name → "JUAN DELA CRUZ"
#   * Transaction descriptions → Keep merchant names, remove personal info
# - Save as: tests/fixtures/sample_statements/sample_gcash.pdf

# Option 2: Create a synthetic PDF (requires manual PDF creation)
# Use tools like LaTeX, Python reportlab, or Word + Print to PDF
# See templates/gcash_statement_template.md for structure
```

**Test Coverage:**
- Extract all 28 transactions with >95% accuracy
- Parse dates correctly
- Parse amounts as Decimal (not float)
- Handle multi-page statements
- Calculate quality score
- Detect bank type automatically

---

### 2. BPI Statement PDF (Password-Protected)

**File:** `tests/fixtures/sample_statements/sample_bpi_protected.pdf`

**Requirements:**
- Password-protected PDF
- Password format: SURNAME + last 4 digits (e.g., "GARCIA1234")
- Date format: "MM/DD/YYYY"
- Debit and credit columns (signed amounts)
- Account debits and credits correctly signed

**How to Obtain:**
```bash
# Option 1: Anonymize a real BPI statement
# - Download BPI statement (usually password-protected)
# - Note the password pattern
# - Anonymize sensitive info
# - Save with known password: tests/fixtures/sample_statements/sample_bpi_protected.pdf
# - Document password in: tests/fixtures/sample_statements/README.md

# Option 2: Create and password-protect a PDF
# Use PDF tools to add password protection:
pdftk sample_bpi.pdf output sample_bpi_protected.pdf owner_pw GARCIA1234 user_pw GARCIA1234
```

**Test Password:** `TESTUSER1234` (documented for test use)

**Test Coverage:**
- Decrypt with correct password
- Extract transactions from password-protected PDF
- Handle incorrect password gracefully
- Parse MM/DD/YYYY date format
- Handle positive and negative amounts (debits/credits)

---

### 3. Maya Wallet Statement PDF

**File:** `tests/fixtures/sample_statements/sample_maya_wallet.pdf`

**Requirements:**
- Maya Wallet format (different from Maya Savings)
- QR payment transactions
- Load/cash-in transactions
- Date format: ISO (YYYY-MM-DD) or similar
- Various transaction types

**How to Obtain:**
```bash
# Option 1: Anonymize real Maya statement
# - Download from Maya app
# - Anonymize account numbers and personal info
# - Keep merchant names and transaction types
# - Save as: tests/fixtures/sample_statements/sample_maya_wallet.pdf

# Option 2: Mock Maya statement
# Create PDF matching Maya's format
```

**Test Coverage:**
- Detect Maya Wallet vs Maya Savings format
- Parse QR payment transactions
- Parse load/cash-in transactions
- Extract transaction descriptions

---

### 4. Maya Savings Statement PDF

**File:** `tests/fixtures/sample_statements/sample_maya_savings.pdf`

**Requirements:**
- Maya Savings account format
- Standard banking transactions
- Interest credits
- Different format from Maya Wallet

**Test Coverage:**
- Distinguish between Maya product types (Wallet vs Savings)
- Parse savings account transactions
- Handle interest transactions

---

## Directory Structure

```
tests/fixtures/sample_statements/
├── README.md                      # Password documentation & fixture inventory
├── sample_gcash.pdf               # GCash statement (28 transactions)
├── sample_bpi_protected.pdf       # BPI statement (password: TESTUSER1234)
├── sample_maya_wallet.pdf         # Maya Wallet statement
├── sample_maya_savings.pdf        # Maya Savings statement
├── sample_gcash_corrupted.pdf     # Intentionally corrupted for error testing
└── sample_mixed/                  # Folder with multiple statements for batch testing
    ├── gcash_nov2024.pdf
    ├── bpi_nov2024.pdf
    └── maya_nov2024.pdf
```

---

## Creating Synthetic PDF Fixtures (Recommended Approach)

Since real bank statements contain sensitive information, **create synthetic PDFs** for testing:

### Using Python reportlab

```python
# scripts/create_test_fixtures.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from decimal import Decimal
from datetime import datetime, timedelta

def create_gcash_pdf(output_path):
    """Create a synthetic GCash statement PDF."""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Header
    c.drawString(200, height - 50, "GCash Statement")
    c.drawString(50, height - 80, "Account: 1234-5678-9012")
    c.drawString(50, height - 100, "Period: November 1-30, 2024")

    # Transactions table
    y = height - 150
    c.drawString(50, y, "Date")
    c.drawString(150, y, "Description")
    c.drawString(400, y, "Amount")

    y -= 30
    transactions = [
        ("Nov 15, 2024", "JOLLIBEE GREENBELT 3", "₱285.50"),
        ("Nov 16, 2024", "7-ELEVEN BGC", "₱120.00"),
        ("Nov 17, 2024", "GRAB TRANSPORT", "₱180.00"),
        # ... add 25 more transactions
    ]

    for date, desc, amount in transactions:
        c.drawString(50, y, date)
        c.drawString(150, y, desc)
        c.drawString(400, y, amount)
        y -= 20

    c.save()

# Create fixtures
create_gcash_pdf("tests/fixtures/sample_statements/sample_gcash.pdf")
```

Run the script:
```bash
python scripts/create_test_fixtures.py
```

---

## Enabling Skipped Tests

Once PDF fixtures are in place:

### 1. Update conftest.py fixture

```python
# tests/conftest.py

@pytest.fixture
def sample_pdf_path() -> Path:
    """Return path to sample PDF statement."""
    pdf_path = Path("tests/fixtures/sample_statements/sample_gcash.pdf")
    if not pdf_path.exists():
        pytest.skip("Sample PDF not available - see tests/fixtures/PDF_FIXTURES_GUIDE.md")
    return pdf_path


@pytest.fixture
def sample_bpi_pdf_path() -> Path:
    """Return path to password-protected BPI PDF."""
    pdf_path = Path("tests/fixtures/sample_statements/sample_bpi_protected.pdf")
    if not pdf_path.exists():
        pytest.skip("BPI PDF fixture not available")
    return pdf_path


@pytest.fixture
def bpi_test_password() -> str:
    """Return test password for BPI PDF."""
    return "TESTUSER1234"
```

### 2. Remove pytest.skip() from tests

In `tests/parsers/test_gcash_parser_atdd.py`:

```python
# Before:
@pytest.mark.atdd
def test_parse_valid_gcash_statement(sample_pdf_path):
    pytest.skip("Implementation pending - awaiting GCashParser class")
    # ...

# After (once PDF fixture + implementation ready):
@pytest.mark.atdd
def test_parse_valid_gcash_statement(sample_pdf_path):
    parser = GCashParser()
    result = parser.parse(sample_pdf_path)

    assert result.quality_score >= 0.95
    assert len(result.transactions) == 28
```

### 3. Run ATDD tests

```bash
# Run all ATDD tests (will skip if fixtures missing)
pytest -m atdd

# Run specific ATDD test file
pytest tests/parsers/test_gcash_parser_atdd.py -v

# Run with verbose output to see skip reasons
pytest -m atdd -v

# Run only non-skipped ATDD tests
pytest -m atdd --co  # Show collection
```

---

## Test Data Requirements

### Transactions for Categorization Testing

The sample statements should include transactions from these Philippine merchants:

**Food & Dining:**
- Jollibee, McDonald's, KFC, Mang Inasal
- Starbucks, Coffee Project, Café Adriatico
- Foodpanda, Grab Food

**Shopping:**
- SM Supermalls, Lazada, Shopee
- 7-Eleven, Ministop, Alfamart

**Transportation:**
- Grab Transport, Angkas
- MRT/LRT load

**Utilities:**
- Meralco, Manila Water, Maynilad

**Telecommunications:**
- Globe, Smart, PLDT

**Healthcare:**
- Mercury Drug, Watsons
- Medical City, St. Luke's

This ensures auto-categorization tests can validate the Philippine merchant database.

---

## Security & Privacy Guidelines

**CRITICAL:** Never commit real bank statements to version control.

### Anonymization Checklist

When creating fixtures from real statements:

- [ ] Remove real account numbers → use "1234-5678-9012"
- [ ] Remove real names → use "JUAN DELA CRUZ"
- [ ] Remove real addresses
- [ ] Remove real phone numbers
- [ ] Remove real email addresses
- [ ] Keep merchant names (public information)
- [ ] Keep transaction amounts (or normalize all to round numbers)
- [ ] Keep date structure (but can shift to different month/year)

### .gitignore Entry

Ensure sensitive PDFs are never committed:

```gitignore
# .gitignore
tests/fixtures/sample_statements/*_real.pdf
tests/fixtures/sample_statements/*_actual.pdf
tests/fixtures/sample_statements/personal/
```

---

## Alternative: Use Mocked PDF Content

If creating PDF files is too complex, use mocked `pdfplumber` responses:

```python
# tests/parsers/test_gcash_parser_atdd.py

from unittest.mock import Mock, patch

@pytest.mark.atdd
def test_parse_valid_gcash_statement_with_mock():
    """Test with mocked PDF content instead of real file."""

    # Mock pdfplumber response
    mock_pages = [
        Mock(extract_tables=Mock(return_value=[
            [
                ["Date", "Description", "Amount"],
                ["Nov 15, 2024", "JOLLIBEE GREENBELT 3", "₱285.50"],
                ["Nov 16, 2024", "7-ELEVEN BGC", "₱120.00"],
                # ... 26 more rows
            ]
        ]))
    ]

    with patch('pdfplumber.open') as mock_pdf:
        mock_pdf.return_value.__enter__.return_value.pages = mock_pages

        parser = GCashParser()
        result = parser.parse(Path("fake.pdf"))

        assert result.quality_score >= 0.95
        assert len(result.transactions) == 28
```

This approach:
- ✅ No real PDF files needed
- ✅ Faster test execution
- ✅ No privacy concerns
- ❌ Doesn't test actual PDF parsing (pdfplumber integration)

---

## Running Tests in CI/CD

For GitHub Actions or other CI:

### Option 1: Skip ATDD tests in CI

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: pytest -m "not atdd"  # Skip ATDD tests requiring PDFs
```

### Option 2: Store encrypted PDF fixtures

```bash
# Encrypt fixtures for CI
tar -czf fixtures.tar.gz tests/fixtures/sample_statements/
gpg --symmetric --cipher-algo AES256 fixtures.tar.gz

# In CI, decrypt before tests
echo "$FIXTURES_PASSWORD" | gpg --passphrase-fd 0 fixtures.tar.gz.gpg
tar -xzf fixtures.tar.gz
pytest -m atdd
```

### Option 3: Generate synthetic PDFs in CI

```yaml
# .github/workflows/test.yml
- name: Generate test fixtures
  run: python scripts/create_test_fixtures.py

- name: Run ATDD tests
  run: pytest -m atdd
```

---

## Summary

**To enable the 40 skipped @atdd tests:**

1. Create synthetic PDF fixtures using `reportlab` or similar
2. Place PDFs in `tests/fixtures/sample_statements/`
3. Update fixtures to not skip when files exist
4. Remove `pytest.skip()` calls from test functions
5. Run tests: `pytest -m atdd`

**Quick Start Script:**

```bash
# Install PDF creation library
pip install reportlab

# Create test fixtures
python scripts/create_test_fixtures.py

# Verify fixtures created
ls -lh tests/fixtures/sample_statements/

# Run ATDD tests
pytest -m atdd -v
```

**Expected Outcome:**

- 40 previously skipped tests now run
- Tests validate PDF parsing with real file I/O
- Tests guide implementation of GCash, BPI, Maya parsers
- TDD RED-GREEN-REFACTOR cycle is complete

---

## Next Steps

1. Create `scripts/create_test_fixtures.py` (PDF generation script)
2. Run script to generate synthetic PDFs
3. Verify PDFs can be opened and read
4. Enable ATDD tests by removing skips
5. Run tests to verify RED phase (all failing)
6. Implement parsers to make tests pass (GREEN phase)
7. Refactor with confidence (tests provide safety net)

---

**Questions?**

See main test documentation: `tests/README.md`
See quick reference: `tests/QUICK_REFERENCE.md`

