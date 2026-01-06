# Test Suite (pytest)

## Overview

This repository uses **pytest**. Tests are organized by feature area (CLI, parsers, queries, reports, etc.) and tagged with markers for selective runs.

## Structure (high level)

- **`tests/analysis/`**: analysis logic
- **`tests/categorization/`**: categorizer + learning/normalization
- **`tests/cli/`**: Typer CLI tests (split into focused modules)
- **`tests/database/`**: SQLAlchemy models/session
- **`tests/dedup/`**: dedup detector/resolver
- **`tests/e2e/`**: workflow-level tests
- **`tests/export/`**: exporting logic
- **`tests/parsers/`**: PDF parser tests
- **`tests/queries/`**: query engine + NL parsing
- **`tests/reports/`**: report + chart generation
- **`tests/fixtures/`**: sample PDFs + fixture docs
- **`tests/support/`**: shared factories/helpers/fixtures

## Running tests

We recommend running via `uv` for consistent environments:

```bash
# Full suite (includes ATDD + slow tests)
uv run pytest

# Recommended dev default: exclude ATDD + slow
uv run pytest -m "not atdd and not slow"

# Exclude ATDD only (keeps slow tests)
uv run pytest -m "not atdd"

# ATDD/RED suite only (often xfail(strict) until implemented)
uv run pytest -m atdd

# Slow tests only / exclude slow tests
uv run pytest -m slow
uv run pytest -m "not slow"
```

## Markers / selection

Registered markers live in `pytest.ini`. Common ones:

- **`atdd`**: acceptance tests (typically `xfail(strict=True)` until implemented)
- **`unit`**, **`integration`**
- **`slow`**, **`performance`**
- **`e2e`**
- **`parser`**, **`database`**, **`categorization`**, **`cli`**, **`smoke`**
- **`p0/p1/p2/p3`**: priority bands (optional selection)

Examples:

```bash
uv run pytest -m "p0 and not atdd"
uv run pytest -m "e2e and not atdd"
uv run pytest -m "cli and not slow"
```

## Reproducibility (determinism knobs)

Some test data uses deterministic helpers in `tests/support/helpers/determinism.py`.

- **`TEST_SEED`**: seeds Python `random` (default `0`)
- **`TEST_NOW`**: fixed clock (ISO format, default `2024-11-15T10:00:00`)

Example:

```bash
TEST_SEED=123 TEST_NOW=2024-01-01T00:00:00 uv run pytest -m "not atdd"
```

## Opt-in tests (real PDFs)

Some E2E tests parse real/sample PDF files and are **skipped by default** to keep CI and local runs deterministic.

Run them explicitly with either:

```bash
uv run pytest -m "real_pdf and e2e"
uv run pytest --run-real-pdf -m "e2e and slow"
RUN_REAL_PDF_E2E=1 uv run pytest -m "real_pdf"
```

## Notes

- **DB isolation**: most tests use an in-memory SQLite DB session fixture (`tests/conftest.py`).
- **CLI isolation**: CLI tests use a temp DB fixture (`tests/cli/conftest.py::temp_db`) so they never touch your local/dev DB.
