# Story 4.1: Data Export (CSV & JSON)

Status: done

---

## Story

As a user,
I want to export my transaction data to CSV and JSON formats,
So that I can analyze data in Excel, Python, or other tools.

---

## Acceptance Criteria

**Given** transactions exist in the database
**When** I implement the export module
**Then** `src/analyze_fin/export/exporter.py` contains `DataExporter` class
**And** `DataExporter` supports: CSV, JSON output formats
**And** `DataExporter` accepts filter parameters: date_range, category, merchant

**Given** I want to export all transactions to CSV
**When** I run export command with `--format csv`
**Then** CSV file is created with headers: date, merchant, category, amount, description, account
**And** Dates are in ISO format: 2024-11-15
**And** Amounts are formatted as: 12345.67 (no currency symbol in CSV)
**And** All transactions are included

**Given** I want to export all transactions to JSON
**When** I run export command with `--format json`
**Then** JSON file is created as array of transaction objects
**And** Each object has keys: transaction_id, date, merchant_normalized, category, amount, description, account, created_at
**And** JSON keys use snake_case (AR21)
**And** Amounts are strings for precision: "12345.67"
**And** Dates are ISO strings: "2024-11-15"

**Given** I want filtered exports
**When** I export with date_range="November 2024" AND category="Food & Dining"
**Then** Only matching transactions are exported
**And** Export filename indicates filters: "export_food_nov2024.csv"
**And** Filter summary is included as comment/metadata

**Given** I want to export query results
**When** I run a query and choose to export results
**Then** Current query filters are applied to export
**And** User can choose format: CSV or JSON
**And** Export preserves query context

**Given** CSV export is complete
**When** I open the file in Excel
**Then** Data loads correctly with proper column types
**And** Currency amounts display correctly
**And** Dates are recognized as dates
**And** UTF-8 encoding preserves Philippine characters (₱, Ñ, etc.)

**Given** JSON export is complete
**When** I load the file in Python/JavaScript
**Then** JSON parses correctly
**And** Data structure is consistent and predictable
**And** Amounts can be converted to Decimal without precision loss

**Given** large dataset export
**When** I export 3,000+ transactions
**Then** Export completes successfully without memory issues
**And** File is created incrementally (streaming)
**And** Progress is shown for large exports

**Given** export with no matching data
**When** Filters result in zero transactions
**Then** Empty file is created with headers only (CSV) or empty array (JSON)
**And** User is informed: "No transactions match filters. Empty export created."

**Requirements:** FR35, FR36, FR37, FR38, AR21, NFR22

---

## Tasks / Subtasks

### Task 1: Refactor existing CLI export to DataExporter class (AC: 1, 2, 3)
- [x] 1.1: Create `src/analyze_fin/export/exporter.py` with `DataExporter` class
  - Extract export logic from `cli.py:export()` function (lines 634-760)
  - Design class with methods: `export_csv()`, `export_json()`, `apply_filters()`
  - Accept session and filter params in constructor
- [x] 1.2: Implement `DataExporter.export_csv()` method
  - Use `csv.DictWriter` with UTF-8 encoding
  - Headers: date, merchant, category, amount, description, account
  - Dates in ISO format (YYYY-MM-DD)
  - Amounts as plain decimal numbers (no ₱ symbol)
  - Handle empty result set gracefully (headers only)
- [x] 1.3: Implement `DataExporter.export_json()` method
  - Return list of dict objects with snake_case keys
  - Keys: transaction_id, date, merchant_normalized, category, amount, description, account, created_at
  - Amounts as strings for precision: "12345.67"
  - Dates as ISO strings
  - Use `json.dumps()` with `indent=2` for pretty output
- [x] 1.4: Refactor CLI `export()` command to use `DataExporter`
  - Instantiate `DataExporter` with session and filters
  - Call appropriate method based on `--format` flag
  - Keep CLI thin, move all logic to `DataExporter`

### Task 2: Add filter parameter support (AC: 4, 5)
- [x] 2.1: Add filter methods to `DataExporter`
  - `filter_by_category(category: str)`
  - `filter_by_date_range(start_date, end_date)`
  - `filter_by_merchant(merchant: str)`
  - Chain filters (builder pattern or method chaining)
- [x] 2.2: Generate filter-aware filenames
  - Pattern: `export_{category}_{date_range}.{ext}`
  - Example: `export_food_nov2024.csv`
  - Sanitize filename (remove special chars)
- [x] 2.3: Add filter metadata to exports
  - CSV: Add comment header lines (# Filter: category="Food & Dining")
  - JSON: Add metadata object at top level with filters applied
  - Include timestamp of export

### Task 3: Implement streaming for large datasets (AC: 8)
- [x] 3.1: Convert `export_csv()` to use streaming
  - Use generator pattern to yield rows
  - Write incrementally with `csv.writer()`
  - Avoid loading all transactions into memory
- [x] 3.2: Add progress indicators for large exports
  - Show progress bar using Rich library (already in project)
  - Update every 100 transactions
  - Estimate completion time
- [x] 3.3: Test with 3,000+ transaction dataset
  - Verify memory usage stays constant
  - Confirm streaming works correctly
  - Benchmark performance

### Task 4: UTF-8 encoding and special character handling (AC: 6)
- [x] 4.1: Ensure UTF-8 encoding for CSV exports
  - Explicitly set `encoding='utf-8'` in file open
  - Test with Philippine characters: ₱, Ñ, ñ
  - Verify Excel compatibility (BOM handling)
- [x] 4.2: Test special characters in all fields
  - Merchant names with accents
  - Descriptions with emojis/unicode
  - Proper escaping of quotes and commas in CSV

### Task 5: Testing and edge cases (AC: 9, all)
- [x] 5.1: Write unit tests for `DataExporter` class
  - Test CSV export with sample transactions
  - Test JSON export with sample transactions
  - Test filter combinations
  - Test empty result sets
- [x] 5.2: Write integration tests with CLI
  - Test `analyze-fin export --format csv`
  - Test `analyze-fin export --format json --output file.json`
  - Test filtered exports with category/date filters
- [x] 5.3: Test edge cases
  - Export with zero transactions
  - Export with duplicate transactions (should export all)
  - Export with null/missing fields
  - Export with very long descriptions (>1000 chars)

---

## Dev Notes

### Current State Analysis

**✅ Already Implemented (in cli.py:634-760):**
- CLI `export()` command with basic CSV/JSON support
- Filter by category and date_range parameters
- Helper functions `_export_csv()` and `_export_json()` (inline in CLI)
- Output to file or stdout
- Integration with SpendingQuery for filtering

**❌ Missing (This Story's Scope):**
- Proper `DataExporter` class in separate module
- Merchant filtering (only category and date implemented)
- Filter metadata in exported files
- Streaming for large datasets
- Progress indicators
- Comprehensive test coverage
- Filename generation from filters

### Critical Implementation Notes

1. **REFACTORING NOT REWRITING**: Extract existing logic from cli.py, don't start from scratch
2. **Maintain CLI Interface**: The `export()` CLI command should continue to work exactly as it does now, just use `DataExporter` internally
3. **Transaction Model Fields**: Ensure all AC-required fields exist in Transaction model:
   - ✅ id, date, description, amount (confirmed in models.py)
   - ✅ category, merchant_normalized (added in recent commits - see git log)
   - ✅ created_at (standard timestamp field)
   - ❓ account field - verify existence or derive from statement.account relationship

### Architecture Compliance

**Project Context Rules (project-context.md):**
- ✅ Python 3.11+ with type hints on all public methods
- ✅ Modern type syntax: `list[dict]`, `str | None`
- ✅ Absolute imports: `from analyze_fin.export.exporter import DataExporter`
- ✅ JSON keys must be snake_case (AR21)
- ✅ Currency as Decimal internally, string in JSON exports
- ✅ Dates as ISO format for storage and export

**SQLAlchemy 2.0 Patterns:**
- Use `Session` context manager: `with Session(engine) as session:`
- Query via SpendingQuery class (already exists)
- Type-safe `Mapped[]` annotations

**Testing Standards:**
- Test file: `tests/export/test_exporter.py`
- Fixtures in `tests/conftest.py` for db_session, sample_transactions
- BDD-style test naming: `test_exports_csv_with_all_transactions`

**Error Handling:**
- Raise `ValidationError` for invalid format parameter
- Raise `IOError` for file write failures
- CLI layer catches and formats user-friendly messages
- Use `--verbose` flag to show full tracebacks

### File Structure Requirements

```
src/analyze_fin/export/
├── __init__.py          # Already exists (empty)
├── exporter.py          # NEW - DataExporter class
└── formatters.py        # OPTIONAL - CSV/JSON formatting helpers

tests/export/
├── __init__.py
├── test_exporter.py     # NEW - DataExporter tests
└── test_cli_export.py   # NEW - CLI integration tests
```

### Library & Framework Requirements

**Standard Library:**
- `csv`: Use `csv.DictWriter` for CSV exports with UTF-8 encoding
- `json`: Use `json.dumps()` with `indent=2` for pretty JSON
- `pathlib.Path`: For file path handling

**Project Dependencies (already available):**
- `rich`: For progress bars and console output
- `typer`: CLI framework (used in cli.py)
- `sqlalchemy`: Database access via Session

**NOT NEEDED:**
- pandas: Overkill for simple exports, adds heavy dependency
- openpyxl: Not in scope (Excel format not required)

### Previous Story Intelligence

**Recent Commits Show:**
1. **e14de66**: Added CLI tests (403→431 tests) with BDD patterns
   - Follow same test structure for export tests
   - Use `typer.testing.CliRunner` for CLI integration tests
2. **5f9a2ea**: Added category, merchant_normalized, confidence fields to Transaction model
   - These fields are now available for export
3. **275830a**: Core implementation with TDD approach
   - Continue test-first development

**Story 3.6 (Natural Language Query):**
- Implemented CLI commands with Rich formatting
- Used SpendingQuery for database access
- Follow same patterns for export command integration

### Latest Technical Specifics

**Python csv module (Python 3.11+):**
- Use `csv.DictWriter` for structured CSV output
- UTF-8 encoding: `open(file, 'w', encoding='utf-8', newline='')`
- Excel compatibility: May need BOM for UTF-8 (`utf-8-sig` encoding)

**JSON Best Practices:**
- Use `json.dumps(obj, indent=2, ensure_ascii=False)` for readable output
- `ensure_ascii=False` preserves Unicode characters (₱, Ñ)
- For large datasets, consider `json.dump()` with streaming

**SQLAlchemy Query Performance:**
- Use `session.execute()` with yield_per() for streaming large result sets
- Avoid loading all objects into memory at once
- Consider `session.scalars()` for single-column queries

### Implementation Strategy

**Phase 1: Create DataExporter class (Task 1)**
1. Extract current CSV/JSON logic from cli.py
2. Create class with constructor accepting session and filters
3. Implement `export_csv()` and `export_json()` methods
4. Refactor CLI to use new class

**Phase 2: Enhance filtering (Task 2)**
1. Add merchant filter support
2. Generate filter-aware filenames
3. Add filter metadata to exports

**Phase 3: Streaming & performance (Task 3)**
1. Implement generator-based streaming
2. Add progress indicators
3. Test with large datasets

**Phase 4: Testing & polish (Tasks 4-5)**
1. UTF-8 encoding tests
2. Unit tests for DataExporter
3. CLI integration tests
4. Edge case coverage

### Testing Requirements

**Unit Tests (tests/export/test_exporter.py):**
```python
def test_export_csv_with_all_fields(db_session, sample_transactions):
    """Given transactions exist, CSV export includes all required fields."""
    exporter = DataExporter(db_session)
    result = exporter.export_csv()

    # Verify CSV headers
    assert "date,merchant,category,amount,description,account" in result

    # Verify data format
    # Verify ISO dates
    # Verify decimal amounts (no currency symbol)
```

**CLI Integration Tests (tests/export/test_cli_export.py):**
```python
def test_cli_export_csv_creates_file(cli_runner, tmp_path):
    """Given export command, CSV file is created with correct content."""
    output_file = tmp_path / "transactions.csv"
    result = cli_runner.invoke(app, ["export", "--format", "csv", "--output", str(output_file)])

    assert result.exit_code == 0
    assert output_file.exists()
    # Verify file contents
```

### Project Context Reference

**Critical Rules from project-context.md:**
- ✅ Type hints required on all public functions
- ✅ Absolute imports only (no relative imports)
- ✅ JSON keys always snake_case
- ✅ Currency as Decimal type, display formatted
- ✅ Dates in ISO format for storage/export
- ✅ Tests in separate `tests/` folder (not co-located)
- ✅ Use `uv` for dependencies (not pip)
- ✅ Use ruff for linting and formatting

**Architecture Patterns to Follow:**
- src layout: `src/analyze_fin/export/exporter.py`
- SQLAlchemy 2.0 with `Mapped[]` annotations
- Typer CLI with type-hint based help
- pytest for testing with fixtures in conftest.py

---

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

No debug issues encountered during implementation.

### Implementation Notes

**Approach:**
- Followed red-green-refactor TDD cycle
- Wrote comprehensive failing tests first
- Implemented minimal code to pass tests
- Refactored for streaming and metadata support

**Key Technical Decisions:**
1. JSON export returns array directly (not wrapped in object) per AC specification
2. Filter metadata is opt-in via `include_metadata=True` parameter
3. Streaming uses SQLAlchemy's `yield_per()` for memory efficiency
4. Progress callback accepts `(current, total)` signature for flexible integration

### Completion Notes List

- [x] DataExporter class created in `src/analyze_fin/export/exporter.py`
- [x] CSV export with all required fields and UTF-8 encoding
- [x] JSON export with snake_case keys and string amounts
- [x] Filter support for category, date_range, and merchant
- [x] Filter-aware filename generation (e.g., `export_food_dining_nov2024.csv`)
- [x] Streaming implementation for large datasets
- [x] Progress callback support for exports
- [x] Comprehensive test coverage (30 unit tests)
- [x] CLI refactored to use DataExporter with --merchant flag added
- [x] Edge cases handled (empty results, special characters, UTF-8)

### File List

**Created:**
- `src/analyze_fin/export/exporter.py` - DataExporter class (420 lines)

**Modified:**
- `src/analyze_fin/cli.py` - Refactored export() command to use DataExporter, added --merchant flag
- `src/analyze_fin/export/__init__.py` - Export DataExporter class
- `tests/export/test_exporter.py` - Comprehensive unit tests (30 tests)
- `tests/test_cli.py` - Updated test_export_json_format to match new array format

**Test Results:**
- 631 tests passing (30 new export tests added)
- No regressions introduced

### Review Follow-ups (AI) - Code Review 2026-01-04

- [x] [AI-Review][LOW] Sync story status to "done" in sprint-status.yaml - all tasks complete, tests passing [sprint-status.yaml:75] ✅ Done
- [ ] [AI-Review][LOW] Update test count in File List - actual count is 32 tests, not 30 [4-1-data-export-csv-json.md:396]

### Change Log

- 2026-01-02: Story 4.1 implemented - DataExporter class with CSV/JSON export, filtering, streaming, and progress support
- 2026-01-04: Senior Developer Review (AI) - Story APPROVED, 2 LOW priority action items added for status sync

---

_Story created: 2026-01-02_
_Story completed: 2026-01-02_
