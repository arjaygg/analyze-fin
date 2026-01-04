---
name: parse-statements
description: Parse and import bank statement PDFs from Philippine banks (GCash, BPI, Maya). Automatically categorizes transactions and checks for duplicates. Use when user mentions parsing, importing, uploading, adding, or processing bank statements, PDFs, or transactions from files.
allowed-tools: Bash, Read, Glob
---

# Parse Bank Statements

Import transactions from PDF bank statements into the local analyze-fin database with automatic categorization and duplicate detection.

## When to Use This Skill

Trigger this skill when the user wants to:
- Parse, import, or upload bank statement PDFs
- Add new transactions from statements
- Process PDF files from GCash, BPI, or Maya
- Import multiple statements at once

## Supported Banks

- **GCash** - E-wallet transactions
- **BPI** - Bank of the Philippine Islands (password-protected)
- **Maya** - Maya Wallet and Maya Savings accounts

Bank type is auto-detected from PDF content.

## Unified Workflow (Default)

The parse command now automatically:
1. **Parses** - Extracts transactions from PDF
2. **Saves** - Stores in SQLite database
3. **Categorizes** - Auto-categorizes using merchant database
4. **Checks duplicates** - Warns about potential duplicates (non-destructive)

This is the recommended workflow for most users.

## Basic Workflow

### Step 1: Get File Path(s)

Ask the user for the PDF file path(s). Be helpful:
- If they mention "my November statement", ask: "Where is the PDF file located?"
- Accept single files or multiple files
- Support glob patterns like `statements/*.pdf`

### Step 2: Check for Password (BPI only)

If the file might be from BPI, ask: "Is this a password-protected BPI statement? If so, what's the password?"

BPI passwords are user-provided and typically known to the account holder.

### Step 3: Execute Parse Command

Run the parse command:

**Single file (full workflow - recommended):**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin parse path/to/statement.pdf
```

**With password (BPI):**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin parse path/to/bpi_statement.pdf --password PASSWORD
```

**Multiple files:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin parse file1.pdf file2.pdf file3.pdf
```

**Skip auto-categorization (power user):**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin parse statement.pdf --no-auto-categorize
```

**Skip duplicate checking (power user):**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin parse statement.pdf --no-check-duplicates
```

**Preview without saving:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin parse statement.pdf --dry-run
```

### Step 4: Interpret and Report Results

The command now outputs a unified summary:
- Total files processed
- Successful imports
- Failed imports
- Quality score (High Confidence, Medium, or Low)
- Total transactions extracted
- **Categorization results** (count and percentage)
- **Duplicate warnings** (if any found)

**Format the response conversationally:**

✅ **Success example (full workflow):**
```
Great! I've parsed your November GCash statement.

📊 Import Summary:
- Imported: 28 transactions
- Quality: High Confidence (95%)
- Categorized: 24 (86%)
- No duplicates found

Your transactions are ready! What would you like to know about your spending?
```

✅ **Success with low categorization:**
```
Parsed your statement.

📊 Import Summary:
- Imported: 45 transactions
- Categorized: 15 (33%)
- Uncategorized: 30

Tip: Run `analyze-fin categorize` to manually review uncategorized transactions.
```

✅ **Success with duplicates:**
```
Parsed your statement.

📊 Import Summary:
- Imported: 35 transactions
- Categorized: 28 (80%)
- Duplicate warnings: 3

⚠️ Found 3 potential duplicates. Run `analyze-fin deduplicate` to review.
```

❌ **Error example:**
```
I had trouble parsing that file:
- Error: PDF is password-protected

This looks like a BPI statement. BPI statements require a password.

What's the password for this statement?
```

⚠️ **Low quality example:**
```
I parsed the statement, but the quality score is low (65%).

This might be a scanned PDF rather than a text PDF. The data might not be fully accurate.

Extracted: 22 transactions (some may be incomplete)

Would you like me to show you what was extracted so you can verify?
```

## Handling Multiple Files

When importing multiple statements:
1. Report progress as files are processed
2. Summarize total results at the end
3. List any failures separately

**Example:**
```
I've processed all 3 statements:

✅ gcash_nov.pdf: 28 transactions (High Confidence)
✅ bpi_nov.pdf: 45 transactions (High Confidence)
✅ maya_nov.pdf: 19 transactions (Medium - Review Recommended)

📊 Import Summary:
- Total: 92 transactions imported
- Categorized: 78 (85%)
- Duplicate warnings: 2
```

## Error Handling

Common errors and responses:

**File not found:**
```
I couldn't find that file. Could you provide the full path?

You can also drag and drop the PDF into this chat, and I'll use that path.
```

**Wrong password:**
```
The password didn't work.

Want to try again?
```

**Unsupported bank:**
```
I couldn't detect the bank type from this PDF.

analyze-fin currently supports:
- GCash
- BPI
- Maya

Is this statement from one of these banks? If so, it might be in an unsupported format.
```

## After Successful Import

Since categorization and duplicate checking are now automatic, suggest:
- "Want to see a breakdown by category?" (run report)
- "How much did I spend on food?" (run query)
- "Show me my spending trends" (generate report)

If duplicates were found:
- "Let me review those duplicates for you" (run deduplicate)

If categorization was low:
- "Let me help categorize those remaining transactions" (run categorize)

## CLI Command Reference

**Full workflow (default):**
```bash
analyze-fin parse <files...> [--password PASSWORD]
```

**Options:**
- `--password, -p` - Password for encrypted PDFs (BPI)
- `--dry-run` - Preview without saving to database
- `--no-auto-categorize` - Skip automatic categorization
- `--no-check-duplicates` - Skip duplicate detection

**Related commands (for follow-up):**
- `analyze-fin categorize` - Manual categorization review
- `analyze-fin deduplicate` - Duplicate resolution
- `analyze-fin report` - Generate spending report
- `analyze-fin query` - Query transactions

## Tips for Success

1. **Be conversational** - Don't just show raw command output
2. **Ask clarifying questions** - Better to ask than assume
3. **Explain quality scores** - Help user understand confidence levels
4. **Interpret the summary** - Explain categorization rate and duplicates
5. **Handle errors gracefully** - Turn technical errors into helpful guidance

## Database Note

Transactions are stored in the local SQLite database at:
`/Users/agallentes/git/analyze-fin/data/analyze-fin.db`

All data stays on the user's machine - no cloud upload.
