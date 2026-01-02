# Test Suite Documentation

## Overview

This test suite ensures the quality and reliability of the `analyze-fin` application. It covers End-to-End (E2E), Integration, and Unit tests.

## Structure

```
tests/
├── e2e/                # End-to-End tests (User workflows, CLI, Real file parsing)
├── integration/        # Integration tests (Database, multiple components)
├── unit/               # Unit tests (Individual functions/classes)
├── fixtures/           # Data fixtures (PDFs, DB dumps)
├── support/            # Test support code
│   ├── factories/      # Data factories (Transactions, Accounts)
│   ├── fixtures/       # Pytest fixtures (Files, DB sessions)
│   └── helpers/        # Helper utilities (Assertions)
└── conftest.py         # Global pytest configuration
```

## Running Tests

We use `pytest` for test execution.

```bash
# Run all tests
pytest

# Run by priority
pytest -m p0  # Critical paths
pytest -m p1  # High priority
pytest -m p2  # Medium priority

# Run specific type
pytest tests/e2e
pytest -m "not slow"

# Run with coverage
pytest --cov=src/analyze_fin
```

## Priority Levels

- **[P0] Critical**: Core user paths (Parsing, Categorization, CLI basics). Run on every commit.
- **[P1] High**: Important features (Export, specific bank formats). Run on PR.
- **[P2] Medium**: Edge cases, error handling. Run nightly.
- **[P3] Low**: Niche cases. Run weekly.

## Writing Tests

### Guidelines

1. **Given-When-Then**: Structure tests clearly.
2. **Atomic**: One concept per test.
3. **Factories**: Use `tests/support/factories` for creating data.
4. **Markers**: Tag tests with `@pytest.mark.pX` and type (e.g., `@pytest.mark.e2e`).

### Example

```python
@pytest.mark.unit
@pytest.mark.p1
def test_valid_email():
    # GIVEN a valid email
    email = "user@example.com"
    
    # WHEN validated
    result = validate_email(email)
    
    # THEN it returns True
    assert result is True
```

## Infrastructure

- **Fixtures**: Defined in `tests/conftest.py` and `tests/support/fixtures/`.
- **Database**: Tests use an in-memory SQLite database or temporary file (via `temp_db_file` fixture).
- **Real Files**: `tests/support/fixtures/files.py` provides paths to sample PDFs.
