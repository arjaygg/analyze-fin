# Story 5.3: Account Context in Reports & Queries

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want reports and queries to show which account data comes from,
So that I know the source of my financial information.

## Acceptance Criteria

### AC1: Report Header Displays Account Information
**Given** I generate a spending report
**When** report is rendered (HTML or Markdown)
**Then** Report header displays account information
**And** Format: "Account: [Account Name] ([Bank Type] ****1234)"
**And** If multiple accounts, all are listed
**And** Statement period is shown in header

### AC2: SpendingReport Includes Account Names
**Given** SpendingReport dataclass
**When** report is generated
**Then** SpendingReport includes `account_names: list[str]` field
**And** Report generator reads account info via ORM relationships
**And** Templates display account list from passed data

### AC3: Query Results Show Account Source
**Given** I query spending data
**When** results are displayed
**Then** Each transaction shows account source
**And** Format includes account name/identifier
**And** Pretty output shows Account column in table

### AC4: SpendingQuery Supports Account Filter
**Given** I use the SpendingQuery class
**When** I call `filter_by_account(account_id)` or `filter_by_account_name(name)`
**Then** Query filters transactions to specified account
**And** Results only include transactions from matching account

### AC5: CLI --account Flag for Filtering
**Given** I use CLI commands (query, report, export)
**When** I provide `--account "GCash Personal"` or `--account 1` (account ID)
**Then** Results are filtered to specified account only
**And** Multiple `--account` flags combine with OR logic
**And** Invalid account shows helpful error message

**Requirements:** FR49, FR50, FR51, FR52, FR53

---

## Tasks / Subtasks

### Task 1: Update SpendingReport Dataclass (AC: 2)
- [ ] 1.1: Edit `src/analyze_fin/analysis/spending.py`
- [ ] 1.2: Add `account_names: list[str] = field(default_factory=list)` to SpendingReport
- [ ] 1.3: Update SpendingAnalyzer.analyze() to accept optional `account_ids: list[int]` parameter
- [ ] 1.4: Add helper method `_get_account_names(account_ids)` to retrieve display names
- [ ] 1.5: Write tests for new SpendingReport field

### Task 2: Add Account Filter to SpendingQuery (AC: 4)
- [ ] 2.1: Edit `src/analyze_fin/queries/spending.py`
- [ ] 2.2: Import Statement model for join capability
- [ ] 2.3: Add `filter_by_account(account_id: int)` method using join
- [ ] 2.4: Add `filter_by_account_name(name: str)` method with fuzzy matching
- [ ] 2.5: Add test for account filtering

### Task 3: Update Report Generator for Account Context (AC: 1, 2)
- [ ] 3.1: Edit `src/analyze_fin/reports/generator.py`
- [ ] 3.2: Add `account_names: list[str] = None` parameter to `generate_html()` and `generate_markdown()`
- [ ] 3.3: Pass account_names to template context
- [ ] 3.4: Update `templates/reports/dashboard.html.j2` - add account header section
- [ ] 3.5: Update `templates/reports/summary.md.j2` - add account header section
- [ ] 3.6: Write tests for account display in reports

### Task 4: Update CLI Report Command (AC: 1, 5)
- [ ] 4.1: Edit `src/analyze_fin/cli/main.py` - `report` command
- [ ] 4.2: Add `--account` option (can be name or ID, multiple allowed)
- [ ] 4.3: Resolve account names/IDs to account objects
- [ ] 4.4: Pass account filter to query and account_names to report generator
- [ ] 4.5: Display account info in summary report output
- [ ] 4.6: Handle invalid account gracefully with error message

### Task 5: Update CLI Query Command (AC: 3, 5)
- [ ] 5.1: Edit `src/analyze_fin/cli/main.py` - `query` command
- [ ] 5.2: Add `--account` option to query command
- [ ] 5.3: Add Account column to pretty table output
- [ ] 5.4: Add account_name to JSON output
- [ ] 5.5: Add account_name to CSV output header and rows
- [ ] 5.6: Write tests for account column in output

### Task 6: Update CLI Export Command (AC: 5)
- [ ] 6.1: Edit `src/analyze_fin/cli/main.py` - `export` command
- [ ] 6.2: Add `--account` option to export command
- [ ] 6.3: Update DataExporter or create account filter capability
- [ ] 6.4: Ensure exported data includes account column (verify existing)
- [ ] 6.5: Write tests for export with account filter

### Task 7: Integration Testing (AC: 1-5)
- [ ] 7.1: Test report generation with single account
- [ ] 7.2: Test report generation with multiple accounts
- [ ] 7.3: Test query with account filter
- [ ] 7.4: Test CLI --account flag across commands
- [ ] 7.5: Test backward compatibility (no account filter = all accounts)

---

## Dev Notes

### Architecture Decisions

1. **Transaction → Account Relationship**: Transactions link to Accounts via Statement (Transaction.statement.account)
2. **Filter by Account**: Requires JOIN through Statement table
3. **Display Names**: Use `get_account_display_name()` from `database/operations.py`
4. **Multiple Accounts**: Support filtering by multiple accounts with OR logic
5. **Backward Compatibility**: All existing code works unchanged when no account filter provided

### Implementation Pattern

```python
# src/analyze_fin/queries/spending.py - Account Filter
def filter_by_account(self, account_id: int) -> "SpendingQuery":
    """Filter transactions by account ID."""
    from analyze_fin.database.models import Statement

    # Join through Statement to filter by account
    self._joins.append(Statement)
    self._filters.append(Statement.account_id == account_id)
    return self

def filter_by_account_name(self, name: str) -> "SpendingQuery":
    """Filter transactions by account name (fuzzy match)."""
    from analyze_fin.database.models import Account, Statement

    self._joins.extend([Statement, Account])
    self._filters.append(Account.name.ilike(f"%{name}%"))
    return self

# src/analyze_fin/analysis/spending.py - Updated SpendingReport
@dataclass
class SpendingReport:
    total_spent: Decimal
    total_transactions: int
    average_transaction: Decimal
    by_category: dict[str, dict[str, Any]]
    by_month: dict[str, dict[str, Any]]
    top_merchants: list[dict[str, Any]]
    account_names: list[str] = field(default_factory=list)  # NEW

# CLI --account flag
@app.command()
def query(
    # ... existing params ...
    account: list[str] = typer.Option(
        None,
        "--account",
        "-a",
        help="Filter by account (name or ID, can specify multiple)"
    ),
) -> None:
```

### Existing Code to Leverage

- `src/analyze_fin/database/operations.py` - `get_account_display_name(account)`
- `src/analyze_fin/database/models.py` - Account, Statement, Transaction models
- `src/analyze_fin/queries/spending.py` - SpendingQuery (add account filter)
- `templates/reports/*.j2` - Report templates (add account section)

### Template Updates

**dashboard.html.j2** - Add after title:
```html
{% if account_names %}
<div class="account-info">
  <h3>Accounts</h3>
  <ul>
  {% for name in account_names %}
    <li>{{ name }}</li>
  {% endfor %}
  </ul>
</div>
{% endif %}
```

**summary.md.j2** - Add after title:
```markdown
{% if account_names %}
## Accounts
{% for name in account_names %}
- {{ name }}
{% endfor %}
{% endif %}
```

### Testing Standards

- Use in-memory SQLite for unit tests
- Create test fixtures with multiple accounts
- Test account filter with single and multiple accounts
- Test backward compatibility (no filter = all data)
- Test invalid account name/ID error handling

### Project Structure Notes

- Alignment: Follows existing patterns in queries/ and reports/ modules
- JOIN strategy: Match pattern used in duplicate detection (through Statement)
- CLI pattern: Follow existing `--category`, `--merchant` option patterns

### References

- [Source: epics.md#Story 5.3: Account Context in Reports & Queries]
- [Source: src/analyze_fin/database/operations.py#get_account_display_name]
- [Source: src/analyze_fin/database/models.py#Account, Statement, Transaction]
- [Source: src/analyze_fin/queries/spending.py#SpendingQuery]
- [Source: project-context.md#SQLAlchemy 2.0 Models]

---

## Dependencies

- **Story 5.1** (Parser Account Identifier Extraction) - COMPLETE
  - ParseResult includes account_number, account_holder fields
- **Story 5.2** (Database Schema & Multi-Account Support) - COMPLETE
  - Account model has account_number, account_holder columns
  - get_or_create_account() and get_account_display_name() functions exist

---

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

### Completion Notes List

### File List

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-06 | Story file created from epics.md | Create-Story Workflow |
