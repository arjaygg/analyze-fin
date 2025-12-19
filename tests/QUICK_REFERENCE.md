# pytest Quick Reference Card

## Running Tests

```bash
# All tests
pytest

# Verbose output
pytest -v

# Specific file
pytest tests/test_cli.py

# Specific test
pytest tests/test_cli.py::test_version_command

# By marker
pytest -m unit           # Fast unit tests only
pytest -m integration    # Integration tests
pytest -m "not slow"     # Exclude slow tests

# Pattern matching
pytest -k "transaction"  # Tests with "transaction" in name

# Stop at first failure
pytest -x

# Show local variables on failure
pytest -l

# Parallel execution (if pytest-xdist installed)
pytest -n auto
```

## Coverage

```bash
# Run with coverage
pytest --cov=src/analyze_fin

# HTML report
pytest --cov=src/analyze_fin --cov-report=html
open htmlcov/index.html

# Show missing lines
pytest --cov=src/analyze_fin --cov-report=term-missing
```

## Writing Tests

```python
import pytest
from tests.support.helpers import generate_transaction

@pytest.mark.unit
def test_something(sample_transaction_data):
    """Test docstring."""
    # Arrange
    transaction = sample_transaction_data

    # Act
    result = process(transaction)

    # Assert
    assert result.is_valid()
```

## Common Fixtures

```python
def test_example(
    db_session,                    # Database session
    sample_transaction_data,       # Single transaction
    sample_transactions,           # List of transactions
    sample_merchant_mapping,       # Merchant mapping dict
    temp_dir,                      # Temporary directory
    temp_db_file,                  # Temporary database file
    cli_runner,                    # Typer CLI runner
    test_data_factory,             # Data factory
):
    pass
```

## Custom Helpers

```python
from tests.support.helpers import (
    # Assertions
    assert_transaction_valid,
    assert_currency_equal,
    assert_no_duplicates,

    # Data generators
    generate_transaction,
    generate_transactions,
    generate_statement_data,
)
```

## Markers

```python
@pytest.mark.unit           # Fast, isolated tests
@pytest.mark.integration    # Database, file I/O
@pytest.mark.slow          # Slow tests (PDF parsing)
@pytest.mark.parser        # Parser-specific
@pytest.mark.database      # Database-specific
@pytest.mark.cli           # CLI command tests
@pytest.mark.smoke         # Smoke tests
```

## Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (100, True),
    (0, False),
    (-50, False),
])
def test_validation(input, expected):
    assert validate(input) == expected
```

## Exception Testing

```python
def test_raises_exception():
    with pytest.raises(ValueError, match="Invalid"):
        do_something_invalid()
```

## Skip Tests

```python
@pytest.mark.skip(reason="Not implemented")
def test_future_feature():
    pass

@pytest.mark.skipif(condition, reason="...")
def test_conditional():
    pass
```

## Debugging

```bash
# Drop into debugger on failure
pytest --pdb

# Capture disabled (see print output)
pytest -s

# Very verbose
pytest -vv
```
