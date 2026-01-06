# Story 5.2: Database Schema & Multi-Account Support

Status: review

---

## Story

As a user,
I want the system to support multiple accounts of the same bank type,
So that my personal and business accounts remain separate.

---

## Acceptance Criteria

### AC1: Database Schema Migration
**Given** the accounts table exists
**When** I run database migration
**Then** accounts table has new columns: `account_number` (String, nullable), `account_holder` (String, nullable)
**And** Composite unique constraint on `(bank_type, account_number)` prevents duplicates
**And** Existing data migrates gracefully (null account_number allowed)

### AC2: Multiple Accounts Same Bank
**Given** I import two GCash statements from different accounts
**When** statements have different mobile numbers
**Then** Two separate Account records are created
**And** Each account has distinct account_number
**And** Transactions link to correct account via statement relationship

### AC3: Account Reuse on Re-import
**Given** I re-import a statement from existing account
**When** bank_type and account_number match existing account
**Then** Existing Account record is reused (no duplicate created)
**And** New Statement links to existing Account
**And** Transactions are added correctly

### AC4: Legacy Data Handling
**Given** legacy data without account_number
**When** querying accounts
**Then** System handles null account_number gracefully
**And** Reports show "Unknown Account" or similar for legacy data
**And** No crashes or errors from missing data

**Requirements:** FR52, FR53

---

## Tasks / Subtasks

### Task 1: Create Alembic Migration (AC: 1)
- [x] 1.1: Generate new migration: `uv run alembic revision --autogenerate -m "add_account_identifier_fields"`
- [x] 1.2: Add `account_number` column (String, nullable)
- [x] 1.3: Add `account_holder` column (String, nullable)
- [x] 1.4: Add composite unique constraint on `(bank_type, account_number)` - allow nulls
- [x] 1.5: Test migration up and down

### Task 2: Update SQLAlchemy Models (AC: 1, 2)
- [x] 2.1: Add `account_number: Mapped[str | None]` to Account model
- [x] 2.2: Add `account_holder: Mapped[str | None]` to Account model
- [x] 2.3: Add `__table_args__` with UniqueConstraint
- [x] 2.4: Update `__repr__` to include account_number

### Task 3: Update Account Lookup Logic (AC: 2, 3)
- [x] 3.1: Create `get_or_create_account(bank_type, account_number=None)` function
- [x] 3.2: Match on `(bank_type, account_number)` pair
- [x] 3.3: Handle null account_number for legacy compatibility
- [x] 3.4: Return existing account or create new one

### Task 4: Update Import Flow (AC: 2, 3)
- [x] 4.1: Pass account_number from ParseResult to account creation
- [x] 4.2: Pass account_holder from ParseResult to account creation
- [x] 4.3: Update CLI parse command to use new flow
- [x] 4.4: Display account info in import summary

### Task 5: Handle Legacy Data (AC: 4)
- [x] 5.1: Create display helper for account name with fallback
- [x] 5.2: Format: "[Holder Name] ([Bank] ****1234)" or "[Bank] Account" if no number
- [x] 5.3: Update reports to use display helper
- [x] 5.4: Test with mixed legacy/new data

### Task 6: Write Tests (AC: 1-4)
- [x] 6.1: Test migration creates columns correctly
- [x] 6.2: Test multiple accounts same bank type
- [x] 6.3: Test account reuse on re-import
- [x] 6.4: Test legacy data handling (null account_number)
- [x] 6.5: Test unique constraint enforcement

---

## Dev Notes

### Architecture Decisions

1. **Nullable Columns**: Allow null for backwards compatibility with legacy imports
2. **Composite Key**: `(bank_type, account_number)` uniquely identifies an account
3. **Partial Unique**: SQLite supports unique constraint with nulls (each null is unique)
4. **Display Logic**: Separate model from display formatting

### Implementation Pattern

```python
# src/analyze_fin/database/models.py
class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    bank_type: Mapped[str]
    account_number: Mapped[str | None]  # NEW: e.g., "09171234567" or "****1234"
    account_holder: Mapped[str | None]  # NEW: e.g., "Juan dela Cruz"
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('bank_type', 'account_number', name='uq_bank_account'),
    )

# src/analyze_fin/database/operations.py
def get_or_create_account(
    session: Session,
    bank_type: str,
    account_number: str | None = None,
    account_holder: str | None = None,
) -> Account:
    """Get existing account or create new one."""
    query = session.query(Account).filter(Account.bank_type == bank_type)
    if account_number:
        query = query.filter(Account.account_number == account_number)
    else:
        query = query.filter(Account.account_number.is_(None))

    account = query.first()
    if account:
        # Update holder name if provided and not set
        if account_holder and not account.account_holder:
            account.account_holder = account_holder
        return account

    # Create new account
    name = f"{bank_type.upper()} Account"
    if account_holder:
        name = f"{account_holder} ({bank_type.upper()})"
    elif account_number:
        masked = f"****{account_number[-4:]}" if len(account_number) >= 4 else account_number
        name = f"{bank_type.upper()} {masked}"

    account = Account(
        name=name,
        bank_type=bank_type,
        account_number=account_number,
        account_holder=account_holder,
    )
    session.add(account)
    return account
```

### Existing Code to Leverage

- `src/analyze_fin/database/models.py` - Account model
- `src/analyze_fin/parsers/base.py` - ParseResult with account_number
- `alembic/` - Migration infrastructure

### Migration Considerations

- Run migration on existing databases with data
- Test both fresh install and upgrade paths
- Document migration steps for users

### Testing Standards

- Use in-memory SQLite for unit tests
- Test migration rollback (downgrade)
- Test unique constraint violations
- Test null handling in queries

---

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References
- Tests: tests/database/test_multi_account.py (19 tests, all passing)
- Migration: alembic/versions/96f1a1b6c577_add_account_identifier_fields.py
- Full test suite: 767 passed, 3 skipped, 54 xfailed

### Completion Notes List
- Added account_number and account_holder columns to Account model
- Created composite unique constraint on (bank_type, account_number)
- Implemented get_or_create_account() function for multi-account lookup
- Implemented get_account_display_name() for legacy data handling
- Updated CLI parse command to use new account lookup flow
- Display account info during import for visibility
- All tests pass including 19 new multi-account tests

### File List
New files:
- src/analyze_fin/database/operations.py - get_or_create_account, get_account_display_name
- alembic/versions/96f1a1b6c577_add_account_identifier_fields.py - Migration
- tests/database/test_multi_account.py - 19 tests for multi-account support

Modified files:
- src/analyze_fin/database/models.py - Added account_number, account_holder columns, UniqueConstraint
- src/analyze_fin/cli/main.py - Updated parse command to use get_or_create_account

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-04 | Story file created from epics.md | Dev Agent |

---

## Dependencies

- **Story 5.1** (Parser Account Identifier Extraction) must be complete
  - ParseResult now includes account_number, account_holder fields
  - Parsers extract this data from PDFs
