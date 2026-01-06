# Story 5.5: Skill Updates for Account Context

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want all Claude Skills to understand and display account context,
So that my conversational experience includes accurate source attribution.

## Acceptance Criteria

### AC1: parse-statements Skill Reports Account Info
**Given** a statement is successfully parsed
**When** the parse-statements skill reports results
**Then** Skill reports: "Imported to account: [Name] ([Bank] ****1234)"
**And** If new account created, reports: "New account detected and created"
**And** Account info is part of success message
**And** Skill documentation explains account handling

### AC2: generate-report Skill Shows Account Context
**Given** I use the generate-report skill
**When** generating a report
**Then** Skill mentions which account(s) are included
**And** If single account: "Generating report for GCash Personal"
**And** If multiple: "Generating report for 3 accounts"
**And** Skill documentation shows --account filter examples
**And** Response format includes account header info

### AC3: query-spending Skill Supports Account Filtering
**Given** I use the query-spending skill
**When** answering spending questions
**Then** Results include account attribution for each transaction
**And** User can ask: "How much from my BPI account?"
**And** Clarification asked if ambiguous: "Which account? GCash Personal or GCash Business?"
**And** Skill documentation shows account filter examples
**And** Response format includes Account column

### AC4: export-data Skill Supports Account Context
**Given** I use the export-data skill
**When** exporting data
**Then** Export includes account column (verify existing implementation)
**And** User can filter export by account via --account flag
**And** Exported filename can optionally include account name
**And** Skill documentation shows account filter examples

### AC5: All Skills Handle Legacy Data Gracefully
**Given** database contains legacy data without account_number
**When** any skill displays or filters account information
**Then** Shows "Unknown Account" or "[Bank] Account" for legacy data
**And** No crashes or errors from missing account_number
**And** Skills explain this gracefully to user

### AC6: Natural Language Account References Work
**Given** I ask account-specific questions
**When** I say "spending from GCash" or "BPI transactions"
**Then** Skills extract account filter from natural language
**And** Common patterns work: "from [account]", "in [bank]", "[account] spending"
**And** Ambiguous references prompt for clarification

**Requirements:** FR54, FR55, FR56, FR58

---

## Tasks / Subtasks

### Task 1: Update parse-statements SKILL.md (AC: 1, 5)
- [ ] 1.1: Edit `.claude/skills/parse-statements/SKILL.md`
- [ ] 1.2: Add "Account Attribution" section after "Basic Workflow"
- [ ] 1.3: Document that CLI now reports: "Imported to account: [Display Name]"
- [ ] 1.4: Add example response showing account info in summary
- [ ] 1.5: Document "New account detected and created" message for first-time imports
- [ ] 1.6: Add "Handling Multiple Accounts" section explaining multi-account scenarios
- [ ] 1.7: Document legacy data handling ("Unknown Account" display)

### Task 2: Update generate-report SKILL.md (AC: 2, 5)
- [ ] 2.1: Edit `.claude/skills/generate-report/SKILL.md`
- [ ] 2.2: Add `--account` filter to all command examples
- [ ] 2.3: Document account filtering syntax: `--account "GCash Personal"` or `--account 1`
- [ ] 2.4: Add example response showing account header in report
- [ ] 2.5: Update "Customization Options" to include account filtering
- [ ] 2.6: Add "Account-Specific Reports" section showing single vs multi-account reports
- [ ] 2.7: Document that report header displays: "Account: [Name] ([Bank] ****1234)"
- [ ] 2.8: Add example: "Generating report for GCash Personal (Oct-Nov 2024)"
- [ ] 2.9: Document legacy data handling

### Task 3: Update query-spending SKILL.md (AC: 3, 5, 6)
- [ ] 3.1: Edit `.claude/skills/query-spending/SKILL.md`
- [ ] 3.2: Add `--account` flag to all command examples
- [ ] 3.3: Add "Account Column" to output format examples (pretty, JSON, CSV)
- [ ] 3.4: Document account filtering syntax in "Available Query Filters" section
- [ ] 3.5: Add "Query by Account" pattern to "Common Query Patterns" section
- [ ] 3.6: Add natural language patterns: "from GCash", "in BPI", "[account] spending"
- [ ] 3.7: Update example responses to include account attribution per transaction
- [ ] 3.8: Add clarification example: "Which account? GCash Personal or GCash Business?"
- [ ] 3.9: Add section "Combining Account with Other Filters"
- [ ] 3.10: Document legacy data handling in "Handling Edge Cases"

### Task 4: Update export-data SKILL.md (AC: 4, 5)
- [ ] 4.1: Edit `.claude/skills/export-data/SKILL.md`
- [ ] 4.2: Add `--account` filter to command examples
- [ ] 4.3: Verify `account` column is already documented in CSV format (line 117)
- [ ] 4.4: Add account filtering examples to "Filter Options" section
- [ ] 4.5: Document multiple `--account` flags can be combined (OR logic)
- [ ] 4.6: Update "Common Export Scenarios" with account-specific exports
- [ ] 4.7: Add example: Export single account for tax records
- [ ] 4.8: Document export filename suggestion: `gcash_personal_2024_11.csv`
- [ ] 4.9: Document legacy data handling

### Task 5: Add Account Context Response Patterns (AC: 1-6)
- [ ] 5.1: Create consistent response patterns across all skills
- [ ] 5.2: Document standard account display format: "[Name] ([Bank] ****1234)"
- [ ] 5.3: Document standard clarification prompt for ambiguous accounts
- [ ] 5.4: Document standard "no data for account" message
- [ ] 5.5: Document standard multi-account summary format

### Task 6: Test Skill Updates Manually (AC: 1-6)
- [ ] 6.1: Test parse-statements skill with account info in output
- [ ] 6.2: Test generate-report skill with --account flag
- [ ] 6.3: Test query-spending skill with --account flag
- [ ] 6.4: Test export-data skill with --account flag
- [ ] 6.5: Verify natural language account extraction works
- [ ] 6.6: Test with legacy data (no account_number)

---

## Dev Notes

### Architecture Decisions

1. **Skill Files Only**: This story ONLY updates skill documentation (.md files), no code changes
2. **Depends on Story 5.3**: The CLI --account flag must be implemented first
3. **Consistent Patterns**: All skills use same account display and clarification patterns
4. **Natural Language**: Leverage NLQueryParser patterns for account extraction
5. **Backward Compatibility**: Document graceful handling of legacy data

### Key Implementation Insight

**This story is documentation-only** after Story 5.3 implements the actual CLI changes. The skills are markdown files that guide Claude Code on how to use the CLI commands. Once `--account` flag exists in CLI, we update the skill docs to teach Claude how to use it.

### Current Skill File Structure

```
.claude/skills/
├── parse-statements/
│   └── SKILL.md       # ~254 lines - update for AC1
├── generate-report/
│   └── SKILL.md       # ~369 lines - update for AC2
├── query-spending/
│   └── SKILL.md       # ~231 lines - update for AC3
└── export-data/
    └── SKILL.md       # ~442 lines - update for AC4
```

### Account Display Format Standard

Use `get_account_display_name()` format from Story 5.2:
```
[Account Holder] ([Bank Type] ****1234)
  e.g., "Juan dela Cruz (GCash ****5678)"

# Or if no holder name:
[Bank Type] ****1234
  e.g., "GCash ****5678"

# Or if legacy (no account_number):
[Bank Type] Account
  e.g., "GCash Account"
```

### Response Pattern Updates

**parse-statements success message:**
```
Great! I've parsed your November GCash statement.

📊 Import Summary:
- Account: Juan dela Cruz (GCash ****5678)
- Imported: 28 transactions
- Quality: High Confidence (95%)
- Categorized: 24 (86%)
- No duplicates found

Your transactions are ready! What would you like to know about your spending?
```

**generate-report with account:**
```
✅ Report generated for Juan dela Cruz (GCash ****5678)!

📊 November 2024 Spending Dashboard:
- Total: ₱42,350.75
- Transactions: 110
[...]
```

**query-spending with account column:**
```
You spent ₱8,456.78 on Food & Dining across 42 transactions.

| Date | Merchant | Amount | Account |
|------|----------|--------|---------|
| Nov 20 | Jollibee | ₱285.00 | GCash ****5678 |
| Nov 19 | Grab Food | ₱450.00 | BPI ****1234 |
[...]
```

**export-data account filtering:**
```bash
# Export single account
uv run analyze-fin export --format csv --account "GCash Personal" --output ~/exports/gcash_nov.csv

# Export multiple accounts
uv run analyze-fin export --format csv --account "GCash Personal" --account "BPI Savings" --output ~/exports/combined.csv
```

### Natural Language Account Patterns

Skill should recognize these patterns and map to `--account` flag:

```
# Direct account references
"from GCash" → --account "GCash"
"in my BPI account" → --account "BPI"
"GCash spending" → --account "GCash"
"BPI transactions" → --account "BPI"

# Specific account names
"from GCash Personal" → --account "GCash Personal"
"Juan's GCash" → --account "Juan" (fuzzy match)

# Clarification needed
"How much did I spend?" (with 2+ accounts) →
  "I found multiple accounts:
   1. GCash Personal (****5678)
   2. BPI Savings (****1234)

   Which account do you want to see, or 'all' for combined?"
```

### Clarification Prompt Standard

When account is ambiguous:
```
I found multiple accounts in your data:
- GCash Personal (****5678) - 45 transactions
- GCash Business (****9012) - 23 transactions
- BPI Savings (****1234) - 18 transactions

Which account would you like to see?
- Type an account name
- Type 'all' for combined data
```

### Existing Code to Reference

These CLI implementations will exist after Story 5.3:
- `src/analyze_fin/cli/main.py` - query, report, export commands with --account flag
- `src/analyze_fin/queries/spending.py` - SpendingQuery.filter_by_account()
- `src/analyze_fin/database/operations.py` - get_account_display_name()

### Testing Approach

Since skills are documentation, testing is manual:
1. Use each skill with account-related queries
2. Verify Claude uses correct CLI flags
3. Verify response formatting matches patterns
4. Test edge cases (no data, multiple accounts, legacy data)

### Project Structure Notes

- Alignment: Skills are in `.claude/skills/` following project convention
- No code changes: This story is pure documentation updates
- Pattern consistency: All skills use same account format/clarification patterns

### References

- [Source: epics.md#Story 5.5: Skill Updates for Account Context]
- [Source: .claude/skills/*/SKILL.md - existing skill files]
- [Source: project-context.md#CLI Exit Codes]
- [Source: src/analyze_fin/database/operations.py#get_account_display_name]

---

## Dependencies

- **Story 5.1** (Parser Account Identifier Extraction) - COMPLETE
  - ParseResult includes account_number, account_holder fields
- **Story 5.2** (Database Schema & Multi-Account Support) - COMPLETE
  - Account model has account_number, account_holder columns
  - get_account_display_name() function exists
- **Story 5.3** (Account Context in Reports & Queries) - REQUIRED (ready-for-dev)
  - CLI --account flag must be implemented first
  - SpendingQuery account filter must exist
  - Report generator must accept account context
- **Story 5.4** (Account-Scoped Deduplication) - OPTIONAL
  - If complete, can document --cross-account flag in parse-statements skill

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
| 2026-01-06 | Story file created from epics.md by create-story workflow | Create-Story Workflow |
