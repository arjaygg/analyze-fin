# Test Suite Documentation

## Overview

This test suite provides comprehensive testing infrastructure for **analyze-fin**, a Python CLI tool for Philippine financial statement parsing and analysis.

**Test Framework:** pytest
**Test Organization:** Domain-driven (parsers, database, categorization, etc.)
**Test Types:** Unit, Integration, End-to-End

---

## Quick Start

### Prerequisites

```bash
# Ensure project is initialized
cd /Users/agallentes/git/analyze-fin

# Install dependencies (when pyproject.toml exists)
uv sync  # or pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_example.py

# Run tests matching a pattern
pytest -k "transaction"

# Run tests with specific marker
pytest -m unit
pytest -m integration
pytest -m slow
```

### Common Test Commands

```bash
# Fast unit tests only (no I/O)
pytest -m unit

# Integration tests (database, files)
pytest -m integration

# Run until first failure
pytest -x

# Show local variables on failure
pytest -l

# Run tests in parallel (when pytest-xdist installed)
pytest -n auto

# Generate coverage report
pytest --cov=src/analyze_fin --cov-report=html
```

---

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                      # Shared fixtures
├── pytest.ini                       # pytest configuration
├── .env.test                        # Test environment variables
│
├── test_example.py                  # Example test patterns
├── test_cli.py                      # CLI command tests
│
├── parsers/                         # Statement parser tests
│   ├── test_example_parser.py
│   ├── test_gcash_parser.py         # (to be implemented)
│   ├── test_bpi_parser.py
│   └── test_maya_parser.py
│
├── database/                        # Database/model tests
│   ├── test_example_models.py
│   └── test_models.py               # (to be implemented)
│
├── categorization/                  # Categorization logic tests
│   ├── test_example_categorizer.py
│   └── test_categorizer.py          # (to be implemented)
│
├── deduplication/                   # Deduplication logic tests
├── queries/                         # Query logic tests
├── reports/                         # Report generation tests
├── export/                          # Export functionality tests
│
├── fixtures/                        # Test data
│   └── sample_statements/           # Sample PDF files
│
└── support/                         # Test utilities
    └── helpers/
        ├── assertions.py            # Custom assertions
        └── test_data.py             # Data generators
```

### Test Markers

Tests are organized using pytest markers:

| Marker | Purpose | When to Use |
|--------|---------|-------------|
| `@pytest.mark.unit` | Unit tests | Fast, isolated, no I/O |
| `@pytest.mark.integration` | Integration tests | Database, file operations |
| `@pytest.mark.slow` | Slow tests | PDF parsing, large datasets |
| `@pytest.mark.parser` | Parser tests | Statement parsing logic |
| `@pytest.mark.database` | Database tests | SQLAlchemy operations |
| `@pytest.mark.categorization` | Categorization tests | Merchant categorization |
| `@pytest.mark.cli` | CLI tests | Typer command invocation |
| `@pytest.mark.smoke` | Smoke tests | Critical path verification |

**Example:**

```python
@pytest.mark.unit
@pytest.mark.parser
def test_parse_transaction_row():
    """Fast unit test for parser logic."""
    pass
```

---

## Writing Tests

### Test Structure

Follow this pattern for all tests:

```python
"""
Module docstring explaining what is being tested.
"""

import pytest
from tests.support.helpers import assert_transaction_valid, generate_transaction


@pytest.mark.unit
def test_descriptive_name(fixture_name):
    """
    Test docstring explaining:
    - What is being tested
    - What behavior is expected
    - Any important context
    """
    # Arrange: Set up test data
    transaction = generate_transaction(amount=Decimal("100.00"))

    # Act: Perform the operation
    result = process_transaction(transaction)

    # Assert: Verify the result
    assert_transaction_valid(result)
    assert result.amount == Decimal("100.00")
```

### Naming Conventions

- **Test files:** `test_*.py` (e.g., `test_gcash_parser.py`)
- **Test functions:** `test_*` (e.g., `test_parse_statement`)
- **Test classes:** `Test*` (e.g., `class TestTransactionOperations:`)
- **Fixtures:** Descriptive names (e.g., `sample_transaction_data`, `temp_db_file`)

**Good names:**
- `test_parse_gcash_statement_returns_transactions`
- `test_categorize_known_merchant_assigns_correct_category`
- `test_duplicate_detection_identifies_exact_matches`

**Avoid:**
- `test_1`, `test_function`, `test_it_works`

### Using Fixtures

Fixtures provide reusable test setup:

```python
def test_with_database(db_session, sample_transaction_data):
    """Use fixtures from conftest.py."""
    transaction = Transaction(**sample_transaction_data)
    db_session.add(transaction)
    db_session.commit()

    assert transaction.id is not None
```

**Available fixtures** (see `conftest.py`):
- `in_memory_db` - In-memory SQLite database
- `temp_db_file` - Temporary database file
- `sample_transaction_data` - Single transaction sample
- `sample_transactions` - List of transactions
- `sample_merchant_mapping` - Merchant mapping dictionary
- `temp_dir` - Temporary directory for file tests
- `cli_runner` - Typer CLI test runner
- `test_data_factory` - Factory for generating test data

### Custom Assertions

Use domain-specific assertions from `tests/support/helpers/assertions.py`:

```python
from tests.support.helpers import (
    assert_transaction_valid,
    assert_currency_equal,
    assert_no_duplicates,
)

def test_transaction_creation():
    transaction = create_transaction()

    # Better than: assert "date" in transaction and "amount" in transaction
    assert_transaction_valid(transaction)

    # Better than: assert abs(actual - expected) < 0.01
    assert_currency_equal(actual, expected)

    # Better than: assert len(txns) == len(set(...))
    assert_no_duplicates(transactions)
```

### Test Data Generators

Use data generators from `tests/support/helpers/test_data.py`:

```python
from tests.support.helpers import (
    generate_transaction,
    generate_transactions,
    generate_statement_data,
)

def test_with_generated_data():
    # Generate single transaction
    transaction = generate_transaction(
        merchant="Jollibee",
        amount=Decimal("285.50")
    )

    # Generate multiple transactions
    transactions = generate_transactions(count=10)

    # Generate complete statement with transactions
    statement = generate_statement_data(
        bank_type="gcash",
        year=2024,
        month=11,
        transaction_count=20
    )
```

### Parametrized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("amount,expected_valid", [
    (Decimal("100.00"), True),
    (Decimal("0.01"), True),
    (Decimal("0.00"), False),
    (Decimal("-50.00"), False),
])
def test_amount_validation(amount, expected_valid):
    result = validate_amount(amount)
    assert result == expected_valid
```

---

## Best Practices

### 1. Test Isolation

Each test should be independent and not rely on other tests:

```python
# ✅ Good: Each test is independent
def test_create_transaction(db_session):
    transaction = create_transaction(db_session, sample_data)
    assert transaction.id is not None

def test_update_transaction(db_session):
    transaction = create_transaction(db_session, sample_data)
    update_transaction(db_session, transaction.id, new_data)
    # ...

# ❌ Bad: Tests depend on each other
def test_create_transaction(db_session):
    self.transaction_id = create_transaction(db_session, sample_data).id

def test_update_transaction(db_session):
    update_transaction(db_session, self.transaction_id, new_data)
```

### 2. Arrange-Act-Assert Pattern

Structure tests clearly:

```python
def test_categorize_transaction():
    # Arrange: Set up test data
    categorizer = MerchantCategorizer(merchant_mapping)
    transaction = {"description": "JOLLIBEE"}

    # Act: Perform the operation
    result = categorizer.categorize(transaction)

    # Assert: Verify the result
    assert result.category == "Food & Dining"
```

### 3. Test One Thing

Each test should verify one behavior:

```python
# ✅ Good: Single responsibility
def test_parse_extracts_transactions():
    result = parser.parse(pdf_path)
    assert len(result.transactions) > 0

def test_parse_calculates_quality_score():
    result = parser.parse(pdf_path)
    assert result.quality_score > 0.90

# ❌ Bad: Testing multiple things
def test_parse():
    result = parser.parse(pdf_path)
    assert len(result.transactions) > 0
    assert result.quality_score > 0.90
    assert result.opening_balance is not None
    assert result.closing_balance is not None
```

### 4. Use Descriptive Assertions

Make failures easy to debug:

```python
# ✅ Good: Clear error messages
assert transaction["amount"] == expected, \
    f"Expected amount {expected}, got {transaction['amount']}"

# ❌ Bad: No context on failure
assert transaction["amount"] == expected
```

### 5. Test Error Cases

Don't just test happy paths:

```python
def test_parse_handles_missing_file():
    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent.pdf")

def test_parse_handles_password_protected():
    with pytest.raises(PasswordRequiredError):
        parser.parse(protected_pdf)
```

---

## Environment Configuration

Tests use `.env.test` for environment variables:

```bash
# Automatic test environment setup
# See .env.test for configuration

# Override specific variables
export TEST_DB_PATH=/tmp/test.db
pytest
```

---

## Coverage

### Generate Coverage Reports

```bash
# Terminal coverage report
pytest --cov=src/analyze_fin

# HTML coverage report
pytest --cov=src/analyze_fin --cov-report=html
open htmlcov/index.html

# Coverage with missing lines
pytest --cov=src/analyze_fin --cov-report=term-missing
```

### Coverage Targets

- **Unit tests:** 90%+ coverage
- **Integration tests:** Cover critical paths
- **Overall project:** 80%+ coverage

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync

      - name: Run tests
        run: pytest -v --cov=src/analyze_fin

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### Common Issues

**Issue:** Tests can't find modules
**Solution:** Ensure you're running tests from project root:
```bash
cd /Users/agallentes/git/analyze-fin
pytest
```

**Issue:** Fixture not found
**Solution:** Check fixture is defined in `conftest.py` or imported correctly

**Issue:** Tests are slow
**Solution:** Run only unit tests: `pytest -m unit`

**Issue:** Database errors
**Solution:** Use `temp_db_file` fixture or `in_memory_db` for isolation

---

## Next Steps

1. **Implement code** - Follow architecture in `_bmad-output/architecture.md`
2. **Replace example tests** - Update `test_example_*.py` files with real tests
3. **Add sample PDFs** - Place test statements in `tests/fixtures/sample_statements/`
4. **Run tests continuously** - Use `pytest --watch` (requires pytest-watch)
5. **Maintain coverage** - Run coverage checks regularly

---

## Resources

- **pytest documentation:** https://docs.pytest.org/
- **Python testing best practices:** https://docs.python-guide.org/writing/tests/
- **Project architecture:** `_bmad-output/architecture.md`
- **Example tests:** `tests/test_example.py`

---

## Questions?

For test framework questions, refer to:
1. Example tests in `tests/test_example*.py`
2. Fixture definitions in `tests/conftest.py`
3. Custom helpers in `tests/support/helpers/`
4. pytest documentation

**Test framework is ready!** Write tests as you implement features. 🧪
