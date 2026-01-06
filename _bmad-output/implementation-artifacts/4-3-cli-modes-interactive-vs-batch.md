# Story 4.3: CLI Modes (Interactive vs Batch)

Status: review

---

## Story

As a user,
I want to run commands in interactive or batch mode,
So that I can choose between guided prompts or automated scripting.

---

## Acceptance Criteria

### AC1: Mode Infrastructure
**Given** the CLI framework exists
**When** I implement mode handling
**Then** `src/analyze_fin/cli.py` uses Typer for command definition
**And** All commands support `--batch` and `--yes` flags
**And** Interactive mode is default

### AC2: Interactive Mode (Default)
**Given** I run in interactive mode (default)
**When** I import a BPI statement
**Then** System prompts for password: "Enter BPI statement password:"
**And** System asks about unknown merchants: "Category for 'UNKNOWN MERCHANT'?"
**And** User input is required for decisions

### AC3: Batch Mode
**Given** I run in batch mode
**When** I use `--batch` flag
**Then** No prompts are shown
**And** Default values are used for all decisions
**And** Unknown merchants are categorized as "Uncategorized"
**And** Processing continues without user interaction

### AC4: Auto-Confirm Flag
**Given** I want to auto-confirm prompts
**When** I use `--yes` or `-y` flag
**Then** All yes/no prompts are automatically confirmed
**And** Useful for: re-import confirmations, overwrite warnings
**And** Still prompts for required input (like passwords in interactive)

### AC5: Batch Mode Automation
**Given** batch mode for automation
**When** I script: `analyze-fin parse *.pdf --batch --auto-categorize`
**Then** All PDFs are processed automatically
**And** Script can run unattended (e.g., cron job)
**And** Exit code indicates success/failure for scripting

### AC6: Interactive Duplicate Handling
**Given** interactive mode with duplicate detection
**When** Duplicate is found
**Then** User is prompted: "Duplicate found. [K]eep both, Keep [F]irst, Keep [S]econd?"
**And** User input is awaited
**And** Decision is applied immediately

### AC7: Batch Duplicate Handling
**Given** batch mode with duplicate detection
**When** Duplicate is found
**Then** Default action is taken: Keep first (skip duplicate)
**And** Summary reports duplicates skipped
**And** No user interaction required

### AC8: Output Verbosity
**Given** mode affects output verbosity
**When** I compare interactive vs batch output
**Then** Interactive: Detailed progress, friendly messages, colors
**And** Batch: Minimal output, machine-readable format available
**And** Both: Same functionality, different UX

**Requirements:** FR44, FR45

---

## Tasks / Subtasks

### Task 1: Add Global Mode Flags (AC: 1)
- [x] 1.1: Add `--batch` flag to Typer app callback
- [x] 1.2: Add `--yes/-y` flag to Typer app callback
- [x] 1.3: Store mode state in module-level state (via prompts.py)
- [x] 1.4: Create `is_batch_mode()` and `is_auto_confirm()` helpers

### Task 2: Create Prompt Utilities (AC: 2, 3, 4)
- [x] 2.1: Create `src/analyze_fin/cli/prompts.py` module
- [x] 2.2: Implement `prompt_for_input(message, default=None)` - respects batch mode
- [x] 2.3: Implement `prompt_yes_no(message, default=True)` - respects --yes flag
- [x] 2.4: Implement `prompt_choice(message, choices)` - respects batch mode

### Task 3: Update Parse Command (AC: 2, 3, 5)
- [x] 3.1: Add password prompting in interactive mode
- [x] 3.2: Skip password prompt in batch mode (use env var or config)
- [x] 3.3: Add ANALYZE_FIN_BPI_PASSWORD env var support for batch
- [x] 3.4: Ensure exit codes work for scripting

### Task 4: Update Categorize Command (AC: 2, 3)
- [x] 4.1: Batch mode defaults to "Uncategorized" (no prompts)
- [x] 4.2: Default to "Uncategorized" in batch mode
- [x] 4.3: Add summary of uncategorized count in batch mode

### Task 5: Update Deduplicate Command (AC: 6, 7)
- [x] 5.1: Interactive mode shows table of duplicates
- [x] 5.2: Implement batch mode default (keep first, remove duplicate)
- [x] 5.3: Add summary of skipped duplicates in batch mode

### Task 6: Adjust Output Verbosity (AC: 8)
- [x] 6.1: Reduce output in batch mode (no colors, minimal messages)
- [x] 6.2: Keep progress indicators in interactive mode
- [x] 6.3: Ensure errors always print regardless of mode

### Task 7: Write Tests (AC: 1-8)
- [x] 7.1: Test batch mode suppresses prompts
- [x] 7.2: Test --yes auto-confirms
- [x] 7.3: Test interactive mode prompts (with mocked input)
- [x] 7.4: Test exit codes in batch mode
- [x] 7.5: Test duplicate handling in both modes

---

## Dev Notes

### Architecture Decisions

1. **Typer Context**: Use Typer's context object to pass mode state to subcommands
2. **Prompt Abstraction**: All prompts go through utility functions that check mode
3. **Environment Variables**: Batch mode can get sensitive input from env vars
4. **Exit Code Consistency**: Same exit codes in both modes

### Implementation Pattern

```python
# src/analyze_fin/cli/prompts.py
import typer
from rich.prompt import Prompt, Confirm

def get_mode_state(ctx: typer.Context) -> dict:
    return ctx.obj or {"batch": False, "yes": False}

def prompt_for_input(ctx: typer.Context, message: str, default: str | None = None) -> str:
    state = get_mode_state(ctx)
    if state["batch"]:
        if default is not None:
            return default
        raise typer.BadParameter(f"Required input in batch mode: {message}")
    return Prompt.ask(message, default=default)

def prompt_yes_no(ctx: typer.Context, message: str, default: bool = True) -> bool:
    state = get_mode_state(ctx)
    if state["yes"] or state["batch"]:
        return default
    return Confirm.ask(message, default=default)
```

### Existing Code to Leverage

- `src/analyze_fin/cli.py` - Commands to update
- Rich library for interactive prompts
- Typer's context passing mechanism

### Testing Standards

- Mock `sys.stdin` for testing interactive prompts
- Use `CliRunner` with `input` parameter for simulated input
- Test both modes for each command

---

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References
- All 709 tests pass (58 CLI tests, 651 other tests)
- Ruff check passes on src/analyze_fin/cli/

### Completion Notes List
- Implemented `--batch` and `--yes/-y` global flags in CLI callback
- Created `src/analyze_fin/cli/prompts.py` module with mode-aware prompt utilities
- Refactored `src/analyze_fin/cli.py` to `src/analyze_fin/cli/main.py` (package structure)
- Updated parse command: password via env var in batch mode, reduced verbosity
- Updated categorize command: batch mode outputs machine-readable summary
- Updated deduplicate command: batch mode auto-removes duplicates (keeps first)
- Added comprehensive tests in `tests/cli/test_modes.py` (14 tests)

### File List
- src/analyze_fin/cli/__init__.py (new)
- src/analyze_fin/cli/main.py (moved from cli.py, updated)
- src/analyze_fin/cli/prompts.py (new)
- tests/cli/test_modes.py (new)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-04 | Story file created from epics.md | Dev Agent |
| 2026-01-05 | Implementation complete: global mode flags, prompts module, command updates | Claude Opus 4.5 |
