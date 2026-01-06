# Story 5.4: Account-Scoped Deduplication

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want duplicate detection to consider account context,
So that transfers between my own accounts aren't incorrectly flagged.

## Acceptance Criteria

### AC1: Default Behavior - Same Account Deduplication
**Given** duplicate detection is running
**When** comparing transactions for duplicates
**Then** Default behavior: only compare within same account
**And** Transaction from GCash is NOT compared to BPI transaction
**And** This reduces false positives from cross-account transfers

### AC2: Cross-Account Deduplication Flag
**Given** I want cross-account duplicate detection
**When** I use `--cross-account` flag
**Then** Duplicates are checked across all accounts
**And** Useful for finding true duplicates from re-imports across accounts
**And** Warning shown: "Cross-account mode may flag internal transfers"

### AC3: Internal Transfer Detection (Not Duplicates)
**Given** internal transfer between own accounts
**When** GCash shows "-₱5,000 Transfer to BPI" and BPI shows "+₱5,000 Transfer from GCash"
**Then** These are NOT flagged as duplicates (different accounts, opposite amounts)
**And** System correctly identifies as potential internal transfer (FR10)
**And** Both transactions are preserved

### AC4: Same Account Duplicate Detection Works
**Given** same account duplicate detection
**When** same statement imported twice to same account
**Then** Duplicates are detected within that account
**And** Reference number matching works
**And** Content hash matching works
**And** User can review and resolve

### AC5: Account Context in Duplicate Groups
**Given** duplicates are grouped for display
**When** showing duplicate matches to user
**Then** Each transaction shows its account source
**And** Format: "[Date] [Description] [Amount] (GCash Personal)"
**And** User understands account context before making decision

**Requirements:** FR57 (Account-scoped deduplication), FR10 (Internal transfer detection)

---

## Tasks / Subtasks

### Task 1: Add Account Context to DuplicateDetector (AC: 1, 2)
- [ ] 1.1: Edit `src/analyze_fin/dedup/detector.py`
- [ ] 1.2: Add `account_scoped: bool = True` parameter to `__init__`
- [ ] 1.3: Add `account_id` to transaction dict requirements in type hints
- [ ] 1.4: Update `find_duplicates()` to check account_id before comparing
- [ ] 1.5: If `account_scoped=True`, skip comparison when account_ids differ
- [ ] 1.6: Add `set_account_scoped(scoped: bool)` method for runtime toggle
- [ ] 1.7: Write tests for account-scoped behavior

### Task 2: Update Content Hash Index for Account Scope (AC: 1)
- [ ] 2.1: Update `_build_content_hash_index()` to include account_id in grouping
- [ ] 2.2: Change index key from `hash` to `(account_id, hash)` when account_scoped=True
- [ ] 2.3: Ensure backward compatibility when account_id is None (legacy data)
- [ ] 2.4: Write tests for index behavior with and without account scope

### Task 3: Add Internal Transfer Detection (AC: 3)
- [ ] 3.1: Create `is_potential_transfer(tx_a, tx_b) -> bool` method
- [ ] 3.2: Detect: same date, opposite amounts (one positive, one negative), different accounts
- [ ] 3.3: Detect: description contains "transfer" + bank name patterns
- [ ] 3.4: Add `match_type="internal_transfer"` to DuplicateMatch
- [ ] 3.5: Never mark internal transfers as duplicates to remove
- [ ] 3.6: Write tests for internal transfer detection

### Task 4: Update DuplicateMatch for Account Context (AC: 5)
- [ ] 4.1: Add `account_a: str | None` field to DuplicateMatch dataclass
- [ ] 4.2: Add `account_b: str | None` field to DuplicateMatch dataclass
- [ ] 4.3: Populate account names in `is_duplicate()` from transaction dict
- [ ] 4.4: Update `__repr__` to include account info
- [ ] 4.5: Write tests for account info in match objects

### Task 5: Update CLI Deduplicate Command (AC: 2, 4, 5)
- [ ] 5.1: Edit `src/analyze_fin/cli/main.py` - `deduplicate` command (line 1222)
- [ ] 5.2: Add `--cross-account` flag (default: False) after `dry_run` param
- [ ] 5.3: Show warning when --cross-account enabled
- [ ] 5.4: Update tx_dicts (lines 1269-1276) to include `account_id` and `account_name`
- [ ] 5.5: Add Account columns to duplicate table (lines 1311-1315)
- [ ] 5.6: Update help text to explain account-scoped behavior
- [ ] 5.7: Write CLI tests for --cross-account flag

### Task 6: Update Parse Command Integration (AC: 1)
- [ ] 6.1: Edit `src/analyze_fin/cli/main.py` - `parse` command's auto-dedupe (lines 687-715)
- [ ] 6.2: Update tx_dicts (lines 696-702) to include `account_id` and `account_name`
- [ ] 6.3: Ensure auto-dedupe during parse uses account_scoped=True (default)
- [ ] 6.4: Add `--cross-account` flag to parse command (optional override, match deduplicate flag name)
- [ ] 6.5: Update parse summary to show account context for duplicates found
- [ ] 6.6: Write tests for parse command dedup integration

### Task 7: Update DuplicateResolver for Account Context (AC: 4)
- [ ] 7.1: Edit `src/analyze_fin/dedup/resolver.py`
- [ ] 7.2: Add account_id to Resolution storage if useful for filtering
- [ ] 7.3: Update `filter_transactions()` to work with account-scoped data
- [ ] 7.4: Update `auto_resolve()` to SKIP matches with `match_type="internal_transfer"`
- [ ] 7.5: Ensure auto_resolve respects account scope
- [ ] 7.6: Write tests for resolver with account context

### Task 8: Integration Testing (AC: 1-5)
- [ ] 8.1: Test same-account duplicates are detected
- [ ] 8.2: Test cross-account transactions NOT flagged (default mode)
- [ ] 8.3: Test --cross-account flag enables cross-account detection
- [ ] 8.4: Test internal transfers detected but NOT marked as duplicates
- [ ] 8.5: Test backward compatibility with legacy data (no account_id)
- [ ] 8.6: Test CLI output shows account context

---

## Dev Notes

### Architecture Decisions

1. **Default Behavior**: Account-scoped (compare within same account only) - prevents false positives
2. **Opt-in Cross-Account**: `--cross-account` flag for special cases (re-import detection)
3. **Internal Transfers**: Detected but NOT treated as duplicates - opposite amounts + different accounts
4. **Account Context**: Transaction dicts must include `account_id` and optionally `account_name`
5. **Backward Compatibility**: Handle null account_id gracefully (legacy data compared to all)

### Implementation Pattern

```python
# src/analyze_fin/dedup/detector.py - Key Changes

class DuplicateDetector:
    def __init__(
        self,
        time_threshold_hours: float = 24,
        amount_threshold_percent: float = 1.0,
        account_scoped: bool = True,  # NEW: default to account-scoped
    ) -> None:
        self.time_threshold = timedelta(hours=time_threshold_hours)
        self.amount_threshold_percent = amount_threshold_percent
        self.account_scoped = account_scoped  # NEW

    def find_duplicates(
        self, transactions: Sequence[dict[str, Any]]
    ) -> list[DuplicateMatch]:
        """Find duplicate pairs, respecting account scope."""
        # ... existing code ...

        # NEW: Skip comparison if different accounts (when account_scoped=True)
        # In _compare_indices or is_duplicate methods

    def is_duplicate(
        self, tx_a: dict[str, Any], tx_b: dict[str, Any]
    ) -> DuplicateMatch | None:
        """Check if two transactions are duplicates."""
        # NEW: Account scope check
        if self.account_scoped:
            account_a = tx_a.get("account_id")
            account_b = tx_b.get("account_id")
            # Only compare if same account (or either is None for legacy)
            if account_a is not None and account_b is not None:
                if account_a != account_b:
                    return None

        # Check for internal transfer (different accounts, opposite amounts)
        if self._is_potential_transfer(tx_a, tx_b):
            # Return as internal_transfer type, NOT as duplicate to remove
            return DuplicateMatch(
                transaction_a=tx_a,
                transaction_b=tx_b,
                confidence=0.8,
                match_type="internal_transfer",
                reasons=["Potential internal transfer (opposite amounts, different accounts)"],
                account_a=tx_a.get("account_name"),
                account_b=tx_b.get("account_name"),
            )

        # ... rest of existing comparison logic ...

    def _is_potential_transfer(
        self, tx_a: dict[str, Any], tx_b: dict[str, Any]
    ) -> bool:
        """Detect internal transfers between accounts."""
        account_a = tx_a.get("account_id")
        account_b = tx_b.get("account_id")

        # Must be different accounts
        if account_a == account_b:
            return False
        if account_a is None or account_b is None:
            return False

        # Must have opposite amounts (one positive, one negative)
        amount_a = tx_a.get("amount", 0)
        amount_b = tx_b.get("amount", 0)

        # One should be negative, one positive, and roughly equal absolute value
        if (amount_a > 0 and amount_b < 0) or (amount_a < 0 and amount_b > 0):
            if abs(abs(amount_a) - abs(amount_b)) < 0.01:  # Within 1 centavo
                return True

        return False


# Updated DuplicateMatch dataclass
@dataclass
class DuplicateMatch:
    transaction_a: dict[str, Any]
    transaction_b: dict[str, Any]
    confidence: float
    match_type: str  # 'exact', 'near', 'cross_source', 'internal_transfer'
    reasons: list[str] = field(default_factory=list)
    account_a: str | None = None  # NEW: Account name for display
    account_b: str | None = None  # NEW: Account name for display


# CLI command update
@app.command()
def deduplicate(
    # ... existing params ...
    cross_account: bool = typer.Option(
        False,
        "--cross-account",
        help="Check duplicates across all accounts (default: same account only)"
    ),
) -> None:
    """Detect and resolve duplicate transactions."""
    if cross_account:
        console.print("[yellow]Warning: Cross-account mode may flag internal transfers as duplicates[/yellow]")

    detector = DuplicateDetector(account_scoped=not cross_account)
    # ... rest of command ...
```

### Transaction Dict Requirements

For account-scoped deduplication, transaction dicts must include:
```python
{
    "id": int,
    "date": datetime,
    "description": str,
    "amount": Decimal,
    "reference_number": str | None,
    # NEW fields for account scope
    "account_id": int | None,      # From Transaction.statement.account.id
    "account_name": str | None,    # For display (use get_account_display_name)
}
```

### Existing Code to Leverage

- `src/analyze_fin/dedup/detector.py` - DuplicateDetector class (modify)
- `src/analyze_fin/dedup/resolver.py` - DuplicateResolver class (minor updates)
- `src/analyze_fin/database/models.py` - Transaction → Statement → Account relationship
- `src/analyze_fin/database/operations.py` - `get_account_display_name(account)`
- `src/analyze_fin/cli/main.py` - deduplicate (line 1222) and parse (line 431) commands

### Required Imports

```python
# For eager loading account relationships in CLI commands:
from sqlalchemy.orm import joinedload

# For account display names:
from analyze_fin.database.operations import get_account_display_name
from analyze_fin.database.models import Statement, Account
```

### Query Pattern for Account-Enriched Transactions

```python
# Get transactions with account context for deduplication
from sqlalchemy.orm import joinedload

def get_transactions_with_account(session: Session) -> list[dict]:
    """Get transactions enriched with account info for deduplication."""
    txs = session.query(Transaction).options(
        joinedload(Transaction.statement).joinedload(Statement.account)
    ).filter(Transaction.is_duplicate == False).all()

    return [
        {
            "id": tx.id,
            "date": tx.date,
            "description": tx.description,
            "amount": tx.amount,
            "reference_number": tx.reference_number,
            "account_id": tx.statement.account.id,
            "account_name": get_account_display_name(tx.statement.account),
        }
        for tx in txs
    ]
```

### Testing Standards

**Test File Location:** Add new test class to `tests/dedup/test_detector.py` (existing file, 513 lines)

**New Test Class:**
```python
class TestAccountScopedDeduplication:
    """Test account-scoped duplicate detection (Story 5.4)."""
    # Add tests here following existing patterns in file
```

**Test Scenarios:**
- Use in-memory SQLite with multiple accounts
- Create test fixtures: 2 GCash accounts, 1 BPI account
- Required tests:
  1. Same account, same transaction = duplicate (detected)
  2. Different accounts, same transaction = NOT duplicate (skipped in default mode)
  3. Different accounts, opposite amounts = internal transfer (flagged but not removed)
  4. `--cross-account`: Different accounts, same transaction = duplicate (detected)
  5. Backward compatibility with null account_id (legacy data compared as same account)

### Project Structure Notes

- Alignment: Follows existing patterns in dedup/ module
- Account lookup: Use existing relationship chain (Transaction.statement.account)
- CLI pattern: Follow existing flag patterns (--batch, --yes, etc.)

### References

- [Source: epics.md#Story 5.4: Account-Scoped Deduplication]
- [Source: src/analyze_fin/dedup/detector.py#DuplicateDetector]
- [Source: src/analyze_fin/dedup/resolver.py#DuplicateResolver]
- [Source: src/analyze_fin/database/models.py#Transaction, Statement, Account]
- [Source: project-context.md#Duplicate Detection Rules]

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
