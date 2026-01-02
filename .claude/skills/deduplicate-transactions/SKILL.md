---
name: deduplicate-transactions
description: Find and resolve duplicate transactions from overlapping statement imports. Use when user mentions duplicates, re-importing statements, cleaning up data, or seeing double transactions.
allowed-tools: Bash, Read
---

# Deduplicate Transactions

Detect and resolve duplicate transactions that occur when re-importing statements or importing overlapping periods.

## When to Use This Skill

Trigger when the user mentions:
- "Find duplicates"
- "Remove duplicate transactions"
- "Clean up my data"
- "I imported the same statement twice"
- "Some transactions appear multiple times"
- "Check for duplicates"

## What This Does

The deduplication system uses smart 3-layer detection:

1. **Content Hash** - MD5 of (date + amount + description)
2. **Reference Number** - Bank-provided transaction IDs
3. **Date Bucketing** - Only compares transactions within same/adjacent days

**Performance:** O(n) average case (not slow pairwise comparison)

## Types of Duplicates

### True Duplicates (Same Statement Re-imported)

**Example:**
```
Transaction A: Oct 20, Jollibee, ₱285.00
Transaction B: Oct 20, Jollibee, ₱285.00
(Same statement imported twice)
```

**Action:** Mark one as duplicate, keep the other

### Near Duplicates (Slightly Different Details)

**Example:**
```
Transaction A: Oct 20, JOLLIBEE MANILA, ₱285.00
Transaction B: Oct 20, JOLLIBEE QC, ₱285.00
(Might be same transaction, different descriptions)
```

**Action:** User reviews and decides

### Internal Transfers (NOT Duplicates!)

**Example:**
```
Transaction A: Oct 20, GCash, Transfer OUT, -₱5,000.00
Transaction B: Oct 20, BPI, Transfer IN, +₱5,000.00
(Same money moved between your own accounts)
```

**Action:** Link as internal transfer, keep both

## Basic Workflow

### Step 1: Scan for Duplicates

**Run detection:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin deduplicate --scan
```

**Report findings:**
```
🔍 Duplicate Scan Results:

Found 5 potential duplicate groups affecting 12 transactions:

High Confidence (auto-resolve):
- 3 exact duplicates (same date, amount, description)

Needs Review:
- 2 near-duplicates (similar but not identical)

Want to review and resolve these?
```

### Step 2: Review Duplicates

For each duplicate group, show side-by-side comparison:

```
Duplicate Group #1 (Exact Match)

Transaction A:
- Date: 2025-10-20
- Merchant: Jollibee
- Amount: ₱285.00
- Source: Statement imported on Oct 21
- Description: JOLLIBEE MANILA INC

Transaction B:
- Date: 2025-10-20
- Merchant: Jollibee
- Amount: ₱285.00
- Source: Statement imported on Oct 22
- Description: JOLLIBEE MANILA INC

These appear to be exact duplicates.

Options:
1. Keep A, mark B as duplicate
2. Keep B, mark A as duplicate
3. Keep both (not duplicates)
4. Mark as internal transfer

What should I do?
```

### Step 3: Apply Resolution

Based on user choice:

**Keep first:**
```bash
uv run analyze-fin deduplicate --resolve keep-first --transaction-ids 123,456
```

**Keep second:**
```bash
uv run analyze-fin deduplicate --resolve keep-second --transaction-ids 123,456
```

**Keep both:**
```bash
uv run analyze-fin deduplicate --resolve keep-both --transaction-ids 123,456
```

**Mark as internal transfer:**
```bash
uv run analyze-fin deduplicate --resolve internal-transfer --transaction-ids 123,456
```

**Confirm:**
```
✓ Resolved! Transaction B marked as duplicate of A.

Duplicate transactions are:
- Kept in database for audit trail
- Excluded from reports and totals
- Marked with is_duplicate = true

Your spending totals are now accurate!
```

### Step 4: Summary and Cleanup

After all duplicates resolved:

```
✅ Deduplication complete!

Results:
- 3 duplicates marked (excluded from reports)
- 2 internal transfers linked
- 7 confirmed unique (kept both)

Your data is now clean and accurate!

Next steps:
- Generate fresh report to see corrected totals
- Review spending without duplicate inflation
```

## Auto-Resolution

For exact duplicates, offer auto-resolution:

```
I found 3 exact duplicates (same date, amount, description).

These are clearly the same transactions imported twice.

Auto-resolve? (Keeps first occurrence, marks others as duplicates)

✓ Yes (recommended)
✗ No, let me review each one
```

## Internal Transfer Detection

Explain internal transfers:

```
💡 Internal Transfers

These transactions move money between YOUR OWN accounts:

Example:
- GCash Transfer OUT: -₱5,000
- BPI Transfer IN: +₱5,000

This isn't spending - it's just moving your money!

I'll link these and exclude from spending totals.
Want to review internal transfers?
```

## Preventing Future Duplicates

Educate users:

```
🛡️ Preventing Duplicates:

analyze-fin automatically detects when you try to re-import the same statement:

"Warning: This PDF matches a previously imported statement (imported on Oct 21).
Skip or force re-import?"

Choose "Skip" to avoid duplicates!
```

## Duplicate Statistics

Show duplicate status:

```
📊 Duplicate Status:

Total Transactions: 200
Unique: 185 (92.5%)
Duplicates: 12 (6%)
Internal Transfers: 3 (1.5%)

Last scan: Oct 21, 2025

Your data quality is good!
```

## Bulk Operations

For many duplicates:

```
Found 25 potential duplicates. This might take a while to review individually.

Options:
1. Auto-resolve exact matches (15 found)
2. Review near-matches only (10 found)
3. Review all manually

Recommended: Auto-resolve exact, review near-matches

What would you prefer?
```

## Edge Cases

### Legitimate Identical Transactions

**User says:** "These aren't duplicates, I really bought 2 coffees"

**You respond:**
```
Got it! Marking both as unique.

For future reference:
- Same merchant, same day, same amount = looks like duplicate
- But if they're separate purchases, you can keep both

I'll remember this pattern for similar cases.
```

### Cross-Account Confusion

**User says:** "This transaction is in both GCash and BPI"

**You respond:**
```
This is likely an internal transfer:

GCash: Transfer OUT -₱5,000
BPI: Transfer IN +₱5,000

If you transferred money between accounts, I'll mark this as internal transfer and exclude from spending totals.

If these are actually separate transactions, I'll keep both.

Which is it?
```

## Resolution History

Show audit trail:

```
📋 Resolution History:

Oct 21, 2025:
- Resolved 3 duplicates (kept first occurrence)
- Linked 2 internal transfers

Oct 15, 2025:
- Resolved 5 duplicates (auto-resolved)

All resolutions are reversible if needed.
```

## Error Handling

**No duplicates found:**
```
✅ No duplicates detected!

Your data is clean. All transactions are unique.

This means:
- No overlapping statement imports
- No re-imported PDFs
- Clean spending totals

Good data hygiene!
```

**Database locked:**
```
Can't scan for duplicates right now - database is in use.

Try:
- Close any other analyze-fin processes
- Wait a moment and try again
- Check for background imports
```

**Invalid transaction IDs:**
```
Couldn't find those transactions.

Possible reasons:
- Transactions already resolved
- IDs might be incorrect
- Database was updated

Want to re-scan for current duplicates?
```

## Integration with Other Skills

After deduplication:

**Clean data enables accurate reports:**
```
✓ Duplicates resolved!

Now that your data is clean:
- Generate a fresh report to see accurate totals
- Query spending without duplicate inflation
- Export clean data for analysis

What would you like to do?
```

**Before exporting:**
```
Before exporting, want to check for duplicates?

Clean data ensures:
- Accurate totals in your export
- No duplicate rows confusing your analysis
- Better data quality

Run duplicate scan?
```

## Tips for Users

Share these best practices:

1. **Scan regularly** - After each statement import
2. **Auto-resolve safe matches** - Saves time on obvious duplicates
3. **Review near-matches** - Prevents data loss
4. **Link internal transfers** - Keeps spending totals accurate
5. **Don't delete** - Marking as duplicate preserves audit trail

## Advanced: Duplicate Prevention

Explain how to avoid duplicates:

```
💡 Best Practices:

1. **Check before importing** - analyze-fin warns about duplicate PDFs
2. **Import once per statement** - Don't re-import same file
3. **Use different date ranges** - Avoid overlapping periods
4. **Scan after import** - Catch accidental duplicates immediately

Following these keeps your data clean!
```
