# Story 4.7: Unified Parse Workflow

Status: review

## Story

As a user importing bank statements,
I want the parse workflow to automatically categorize transactions and check for duplicates,
so that I get actionable insights immediately without running multiple commands.

## Acceptance Criteria

### AC1: Parse Skill Orchestrates Full Workflow

**Given** a user invokes the `parse-statements` skill with a PDF file
**When** the statement is successfully parsed
**Then** the skill automatically runs auto-categorization on imported transactions
**And** the skill checks for duplicate transactions (warns but doesn't auto-delete)
**And** a summary is displayed showing: transactions imported, categorized count, duplicate warnings

### AC2: Summary Output After Parse

**Given** the parse workflow completes
**When** the summary is displayed
**Then** output shows: "Imported X transactions, Y categorized (Z%), W potential duplicates found"
**And** if categorization rate < 80%, suggest running manual categorization
**And** if duplicates found, suggest running `deduplicate --review` command

### AC3: CLI Commands Remain Available

**Given** the unified workflow is implemented
**When** a power user wants granular control
**Then** `analyze-fin categorize` command still works independently
**And** `analyze-fin deduplicate` command still works independently
**And** commands can be run multiple times without side effects

### AC4: Skill Consolidation

**Given** the parse-statements skill is enhanced
**When** reviewing the .claude/skills/ directory
**Then** `categorize-transactions` skill is removed (functionality in parse)
**And** `deduplicate-transactions` skill is removed (functionality in parse)
**And** `parse-statements` skill documentation is updated to reflect full workflow

### AC5: Idempotent Categorization

**Given** transactions have already been categorized
**When** parse workflow runs auto-categorization
**Then** only uncategorized transactions are processed
**And** previously categorized transactions are not modified
**And** categorization count only reflects newly categorized

### AC6: Duplicate Warning (Non-Destructive)

**Given** the parse workflow detects potential duplicates
**When** displaying the summary
**Then** duplicates are reported but NOT automatically removed
**And** user is informed: "Run `analyze-fin deduplicate --review` to resolve"
**And** no data is deleted without explicit user action

## Tasks / Subtasks

- [x] **Task 1: Update parse CLI command** (AC: 1, 5)
  - [x] 1.1 Add `--auto-categorize` flag (default: True)
  - [x] 1.2 Add `--check-duplicates` flag (default: True)
  - [x] 1.3 Call `categorize` function after successful parse if flag enabled
  - [x] 1.4 Call `detect_duplicates` function after parse if flag enabled
  - [x] 1.5 Ensure categorization only processes uncategorized transactions

- [x] **Task 2: Create unified summary output** (AC: 2)
  - [x] 2.1 Create `ParseSummary` dataclass with: total_imported, categorized_count, uncategorized_count, duplicate_count
  - [x] 2.2 Display formatted summary after parse completes
  - [x] 2.3 Add suggestions for low categorization rate or duplicates found
  - [x] 2.4 Include quality score from parser in summary

- [x] **Task 3: Update parse-statements skill** (AC: 1, 4)
  - [x] 3.1 Update `.claude/skills/parse-statements/skill.md` documentation
  - [x] 3.2 Document that categorization and duplicate checking are now automatic
  - [x] 3.3 Document how to skip with `--no-auto-categorize` or `--no-check-duplicates`

- [x] **Task 4: Remove redundant skills** (AC: 4)
  - [x] 4.1 Delete `.claude/skills/categorize-transactions/` directory
  - [x] 4.2 Delete `.claude/skills/deduplicate-transactions/` directory
  - [x] 4.3 Verify no other skills reference these removed skills

- [x] **Task 5: Update tests** (AC: 1, 2, 3, 5, 6)
  - [x] 5.1 Add tests for parse with auto-categorize enabled
  - [x] 5.2 Add tests for parse with auto-categorize disabled
  - [x] 5.3 Add tests for duplicate warning output
  - [x] 5.4 Add tests for idempotent categorization
  - [x] 5.5 Verify existing categorize/deduplicate CLI tests still pass

- [x] **Task 6: Documentation updates** (AC: 4)
  - [x] 6.1 Update README if it references separate skills
  - [x] 6.2 Update any help text that references old workflow

## Dev Notes

### Architecture Decisions

1. **Composition over Replacement**: The parse command will CALL the existing categorize and deduplicate functions, not duplicate their logic. This maintains DRY principles.

2. **Flags for Control**: Power users can disable auto-behaviors with `--no-auto-categorize` and `--no-check-duplicates` flags.

3. **Non-Destructive Duplicates**: Duplicate detection WARNS but does not DELETE. This follows the principle of zero data loss without explicit user action.

### Implementation Pattern

```python
# In src/analyze_fin/cli.py - parse command enhancement
@app.command()
def parse(
    pdf_paths: list[Path],
    password: str | None = None,
    dry_run: bool = False,
    auto_categorize: bool = typer.Option(True, help="Auto-categorize after parse"),
    check_duplicates: bool = typer.Option(True, help="Check for duplicates after parse"),
) -> None:
    # 1. Parse PDF(s) - existing logic
    results = batch_parse(pdf_paths, password, dry_run)

    # 2. Auto-categorize if enabled
    if auto_categorize and not dry_run:
        cat_count = run_categorization(uncategorized_only=True)

    # 3. Check duplicates if enabled
    if check_duplicates and not dry_run:
        dup_count = detect_duplicates(report_only=True)

    # 4. Display unified summary
    display_parse_summary(results, cat_count, dup_count)
```

### Existing Code to Leverage

- `src/analyze_fin/categorization/` - existing auto-categorization logic
- `src/analyze_fin/deduplication/` - existing duplicate detection logic
- `src/analyze_fin/cli.py` - existing parse command to enhance

### Testing Standards

- Use `CliRunner` from Typer for CLI tests
- Mock database for fast tests
- Test flag combinations: `--auto-categorize`, `--no-auto-categorize`, etc.
- Verify summary output format with regex or structured assertions

### Project Structure Notes

- Alignment with existing CLI patterns in `src/analyze_fin/cli.py`
- Skills directory: `.claude/skills/` - will have 2 directories removed
- No new modules needed - composition of existing functionality

### References

- [Source: _bmad-output/project-context.md#CLI-Exit-Codes] - Exit code standards
- [Source: _bmad-output/architecture.md#CLI-Layer] - Typer CLI patterns
- [Source: _bmad-output/epics.md#Story-4.5] - Claude Skills integration requirements
- [Source: .claude/skills/parse-statements/skill.md] - Current skill documentation

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 669 tests pass (including 5 new unified workflow tests)
- RED-GREEN TDD cycle followed

### Completion Notes List

1. **Task 1 Complete**: Added `--auto-categorize/--no-auto-categorize` and `--check-duplicates/--no-check-duplicates` flags to parse command
2. **Task 2 Complete**: Unified summary output shows imported count, categorization rate, and duplicate warnings
3. **Task 3 Complete**: Updated `.claude/skills/parse-statements/skill.md` with unified workflow documentation
4. **Task 4 Complete**: Removed `.claude/skills/categorize-transactions/` and `.claude/skills/deduplicate-transactions/` directories
5. **Task 5 Complete**: Added 5 tests in `TestParseCommandUnifiedWorkflow` class
6. **Task 6 Complete**: Updated README.md and SKILLS_GUIDE.md to reflect 4 skills and unified workflow

### File List

**Modified:**
- `src/analyze_fin/cli.py` - Added flags and unified workflow logic to parse command
- `tests/test_cli.py` - Added TestParseCommandUnifiedWorkflow test class
- `.claude/skills/parse-statements/skill.md` - Updated documentation for unified workflow
- `README.md` - Updated skills section (4 skills instead of 6)
- `SKILLS_GUIDE.md` - Updated to reflect unified workflow

**Deleted:**
- `.claude/skills/categorize-transactions/` - Merged into parse-statements
- `.claude/skills/deduplicate-transactions/` - Merged into parse-statements
