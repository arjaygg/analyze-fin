# analyze-fin: Claude Skills Guide

**Comprehensive documentation for all 6 Claude Skills**

After Phase 5, you'll have 6 skills that form the primary interface to analyze-fin. This guide explains each skill in detail.

---

## Quick Reference

| Skill | Purpose | Command | Output |
|-------|---------|---------|--------|
| **parse-statements** | Import PDF statements | "Parse my GCash statement" | ✅ Imported 28 transactions |
| **categorize-transactions** | Interactive merchant learning | "Categorize unknown merchants" | ✅ Categorized 5 merchants |
| **generate-report** | Create spending reports | "Generate January report" | ✅ Report saved: report.html |
| **query-spending** | Natural language questions | "How much food?" | ₱1,250 across 12 transactions |
| **export-data** | Export to CSV/JSON | "Export all to CSV" | ✅ Exported to data/exports/ |
| **deduplicate** | Find duplicate transactions | "Check for duplicates" | Found 2 potential duplicates |

---

## Skill 1: parse-statements

**Purpose**: Parse PDF bank statements and import transactions to local SQLite database

**When to use**:
- Monthly statement imports
- Multi-account tracking (GCash, BPI, Maya)
- Batch imports (multiple PDFs at once)

### Usage Examples

**Example 1: Single statement**
```
You: "Parse my GCash statement from January"
Claude Code: Prompts for file path
You: data/sample_statements/gcash_jan.pdf
Claude Code: Prompts for password
You: reyes4356
Claude Code: Parses → Stores to SQLite
Result: "✅ Imported 28 transactions, quality score: 95"
```

**Example 2: Password-protected PDF**
```
You: "Parse my BPI December statement"
Claude Code: Prompts for file path
You: data/sample_statements/bpi_dec.pdf
Claude Code: Prompts for password
You: santos1234
Result: "✅ Imported 45 transactions"
```

**Example 3: Multiple accounts**
```
You: "Parse all my statements"
Claude Code: Asks which statements
You: GCash and BPI for January
Claude Code: Imports both
Result: "✅ Imported 73 transactions total (28 GCash + 45 BPI)"
```

### What Happens Behind the Scenes

1. **File validation**: Checks if PDF exists and is readable
2. **Bank detection**: Analyzes PDF content to determine bank (GCash/BPI/Maya/Vybe)
3. **Password handling**: If password-protected, uses provided password
4. **Table extraction**: Uses pdfplumber to extract transaction table from PDF
5. **Date normalization**: Converts bank date formats to ISO 8601
6. **Amount normalization**: Removes ₱, commas, handles debits as negative
7. **Duplicate check**: Compares against existing transactions (file_hash prevents re-imports)
8. **Quality scoring**: Rates extraction quality (100 = perfect, <60 = error)
9. **Database insert**: Stores account, statement, and transactions to SQLite
10. **Return result**: Shows transaction count, quality score, date range

### Success Criteria

✅ Imported transactions have correct dates
✅ Amounts are accurate (including correct sign for debits/credits)
✅ Merchant names preserved (normalization happens in categorize-transactions)
✅ Quality score >80 (indicates good extraction)
✅ No duplicate transactions from same statement

### Error Handling

**Password required**: "PDF is password-protected. Please provide password."
**Scanned PDF**: "This appears to be a scanned PDF (quality: 45). Please re-export as text PDF."
**Invalid PDF**: "File is not a valid PDF or is corrupted."
**Unknown bank**: "Cannot detect bank format. Check if statement is from GCash, BPI, Maya, or Vybe."

---

## Skill 2: categorize-transactions

**Purpose**: Interactive merchant categorization with learning system

**When to use**:
- After first statement import (categorizes unknown merchants)
- Monthly before generating report (ensures all merchants are categorized)
- When adding new merchants you haven't seen before

### Usage Examples

**Example 1: Basic categorization**
```
You: "Categorize my uncategorized merchants"
Claude Code: Found 5 unknown merchants

Merchant: "ABC STORE MANILA"
Options: 1) Food 2) Shopping 3) Utilities 4) Transport 5) Transfer 6) Bills 7) Entertainment 8) Financial 9) Government 10) Other
You: 2
Claude Code: ✅ Saved: ABC STORE → Shopping

Merchant: "UNKNOWN PHARMACY"
You: (Pharmacy not in list) 10
Claude Code: ✅ Saved: UNKNOWN PHARMACY → Other

(continues for each unknown merchant...)

Result: "✅ Categorized 5 merchants"
```

**Example 2: Auto-categorization from mapping**
```
You: "Categorize my new transactions"
Claude Code: Checking 12 new transactions
- JOLLIBEE: ✅ food (in mapping)
- MCDO: ✅ food (in mapping)
- SM MALL: ✅ shopping (in mapping)
- UNKNOWN STORE: ❓ needs input

(prompts only for unknown merchants)

Result: "✅ 11 auto-categorized, 1 needs your input"
```

### Categories Available

**Food & Dining**
- FOOD_DELIVERY: Grab, UberEats, FoodPanda, Jollibee, McDonald's
- GROCERIES: Puregold, SM, Robinsons, Savemore
- COFFEE: Starbucks, Coffee Bean, Cbtl

**Shopping**
- SHOPPING: Lazada, Shopee, SM, Uniqlo
- CLOTHING: Forever 21, H&M, Zara
- ELECTRONICS: Best Buy, Lazada Electronics

**Utilities & Bills**
- UTILITIES: Meralco, Manila Water, PLDT, Smart, Globe
- GAS: Petron, Shell, Total

**Transport**
- TRANSPORT: Grab, Uber, Angkas, MRT, Bus
- RIDE_SHARE: Grab, Uber, Angkas

**Financial**
- TRANSFER: Bank transfers between own accounts
- PAYMENT: Credit card payments, loan payments
- FINANCIAL: BPI, GCash, Maya, insurance, stocks

**Government**
- GOVERNMENT: SSS, PhilHealth, Pag-IBIG, BIR, DTI

**Entertainment**
- ENTERTAINMENT: Netflix, Spotify, Cineplex, KTV
- GAMES: Steam, PlayStation Store

**Other**
- PHARMACY: Drugstore, pharmacy, hospital
- PERSONAL_CARE: Salon, SPA, gym
- SCHOOL: Tuition, books
- MISCELLANEOUS: Everything else

### Learning System

**First time you see "JOLLIBEE":**
- System asks: "Category?"
- You answer: "Food"
- System saves: `{"JOLLIBEE": {"normalized": "Jollibee", "category": "food"}}`

**Second time you see "JOLLIBEE QC":**
- System normalizes: "JOLLIBEE QC" → "Jollibee"
- Looks up in mapping → finds "food"
- **Auto-categorizes** without asking

**You correct a merchant:**
- You: "This should be shopping, not food"
- System updates mapping
- Future transactions auto-corrected

### Success Criteria

✅ All merchants have a category
✅ Mapping file updated with new merchants
✅ Future imports auto-categorize known merchants
✅ No merchant appears as "other" unless truly unknown

---

## Skill 3: generate-report

**Purpose**: Generate interactive HTML and Markdown spending reports

**When to use**:
- End-of-month analysis
- Before reviewing spending with family
- For sharing spending summary
- Archiving monthly reports

### Usage Examples

**Example 1: Monthly report**
```
You: "Generate my January spending report"
Claude Code: Querying SQLite for January data
- Found 156 transactions
- Generating HTML with charts
- Generating Markdown summary
- Opening report in browser

Result: "✅ Report saved: data/reports/2025-01-report.html
✅ Summary saved: data/reports/2025-01-summary.md"

HTML opens in browser showing:
- Summary cards: Total In ₱145,000 | Out ₱98,500 | Net ₱46,500
- Pie chart: Food 35%, Shopping 25%, Utilities 20%, Other 20%
- Line chart: Daily spending trend over 31 days
- Bar chart: Top 10 merchants
```

**Example 2: Date range report**
```
You: "Generate spending report for 2025-01-01 to 2025-01-31"
Claude Code: Querying 2025-01-01 to 2025-01-31
Result: "✅ Generated report for 31 days"
```

**Example 3: Year-to-date report**
```
You: "Generate YTD report"
Claude Code: Queries from Jan 1 to today
Result: "✅ YTD spending report generated"
```

### Report Contents

**HTML Report** (interactive, opens in browser)
- Header with period (e.g., "January 2025")
- Summary cards:
  * **Total In**: ₱145,000 (income/deposits)
  * **Total Out**: ₱98,500 (expenses)
  * **Net**: ₱46,500 (savings)
  * **Daily Average**: ₱3,177
- Pie chart: Spending by category
  * Food 35%
  * Shopping 25%
  * Utilities 20%
  * Entertainment 12%
  * Other 8%
- Line chart: Daily spending trend
  * Shows daily net spending over month
  * Identifies high-spending days
- Bar chart: Top 10 merchants
  * Lists biggest individual merchant expenditures
- Footer: Generated timestamp

**Markdown Report** (text-based, editable)
```markdown
# Spending Report - 2025-01

## Summary
- Period: 2025-01-01 to 2025-01-31
- Total In: ₱145,000
- Total Out: ₱98,500
- Net: ₱46,500
- Daily Average: ₱3,177

## Category Breakdown
| Category | Amount | % |
|----------|--------|---|
| Food | ₱34,475 | 35% |
| Shopping | ₱24,625 | 25% |
| Utilities | ₱19,700 | 20% |
| Entertainment | ₱11,810 | 12% |
| Other | ₱7,890 | 8% |

## Top Merchants
- Jollibee: ₱8,500
- Lazada: ₱7,200
- Meralco: ₱5,800
...
```

### Success Criteria

✅ HTML report opens in browser
✅ Charts render correctly (pie, line, bar)
✅ All spending categories included
✅ Report dates are accurate
✅ Currency formatted with ₱ symbol

---

## Skill 4: query-spending

**Purpose**: Answer natural language questions about spending using Claude Code reasoning

**When to use**:
- Ad-hoc analysis (no need to generate full report)
- Quick budget checks
- Comparative analysis ("more than last month?")
- Category deep-dives

### Usage Examples

**Example 1: Category spending**
```
You: "How much did I spend on food last week?"
Claude Code: Loads SQLite data to context
- Queries transactions from 7 days ago to today
- Filters for food category
- Calculates total and transaction count
Result: "You spent ₱1,250 on food last week across 12 transactions.
Average ₱104/transaction. Top merchant: Jollibee (₱450)"
```

**Example 2: Top categories**
```
You: "What are my top 5 spending categories?"
Claude Code: Queries all transactions (or this month)
- Calculates totals per category
- Ranks by amount
Result: "1. Food: ₱34,500 (35%)
2. Shopping: ₱24,600 (25%)
3. Utilities: ₱19,700 (20%)
4. Entertainment: ₱11,800 (12%)
5. Other: ₱7,900 (8%)"
```

**Example 3: Budget tracking**
```
You: "Am I on track for budget?"
Claude Code: Loads spending data
- Calculates daily average
- Projects to month-end
Result: "Current daily average: ₱3,177
At this rate, you'll spend ₱95,310 this month.
Your July spending was ₱89,500 (6% higher)"
```

**Example 4: Merchant analysis**
```
You: "How much do I spend at Jollibee?"
Claude Code: Filters for Jollibee transactions
- Calculates total and frequency
Result: "You've spent ₱8,500 at Jollibee across 42 transactions
Average ₱202/visit. Last visit: 2 days ago"
```

**Example 5: Comparative**
```
You: "Compared to last month, am I spending more on food?"
Claude Code: Compares two months
- This month food: ₱34,500
- Last month food: ₱29,200
Result: "Yes, +18% more on food this month (₱5,300 extra)
This is above your 35% average allocation"
```

### Query Types Supported

**Direct Amount**
- "How much food this month?"
- "Total shopping last week?"

**Ranking**
- "Top 5 merchants?"
- "Most expensive category?"

**Trends**
- "More than last month?"
- "Spending increasing or decreasing?"

**Frequency**
- "How often do I eat out?"
- "Average per transaction for groceries?"

**Comparative**
- "vs last week?"
- "vs same period last year?"

**Budget**
- "On track for budget?"
- "Projection if I keep spending at this rate?"

### Success Criteria

✅ Answers are accurate (matches SQLite data)
✅ Answers include numbers with ₱ symbol
✅ Includes relevant context (transaction count, average, trends)
✅ Response time <2 seconds
✅ Natural language phrasing (not just raw numbers)

---

## Skill 5: export-data

**Purpose**: Export transactions to CSV or JSON for external analysis

**When to use**:
- Tax filing preparation
- Sharing data with accountant
- Excel analysis
- Backup/portability
- API integration with other tools

### Usage Examples

**Example 1: Export all to CSV**
```
You: "Export all transactions to CSV"
Claude Code: Queries entire transactions table
- Exports all 156 transactions
- Saves to: data/exports/all_transactions.csv
Result: "✅ Exported 156 transactions to data/exports/all_transactions.csv"

CSV format:
date,merchant,category,amount,account,status
2025-01-01,Jollibee,food,-250.00,GCash,active
2025-01-02,Meralco,utilities,-5800.00,BPI,active
...
```

**Example 2: Export month to JSON**
```
You: "Export January to JSON"
Claude Code: Filters for January 2025
Result: "✅ Exported 156 transactions to data/exports/2025-01_transactions.json"

JSON format:
{
  "period": "2025-01",
  "transactions": [
    {
      "date": "2025-01-01",
      "merchant": "Jollibee",
      "category": "food",
      "amount": -250.00,
      "account": "GCash"
    },
    ...
  ]
}
```

**Example 3: Export category**
```
You: "Export food transactions to CSV"
Claude Code: Filters for food category only
Result: "✅ Exported 42 food transactions"
```

**Example 4: Export account**
```
You: "Export all GCash transactions"
Claude Code: Filters for GCash account
Result: "✅ Exported 98 GCash transactions"
```

### Export Formats

**CSV** (Excel-compatible)
- Columns: date, merchant, category, amount, balance, account, reference, status, notes
- Encoding: UTF-8 with BOM (for Windows Excel)
- Format: ₱ symbol included, negative for debits

**JSON** (structured data)
- Metadata: period, total_transactions, totals, by_category
- Nested transactions array
- ISO 8601 dates
- All fields preserved

### File Locations

Exports saved to: `data/exports/`

Naming pattern:
- `all_transactions.csv` (all data)
- `{YYYY-MM}_transactions.csv` (monthly export)
- `{YYYY-MM-DD}_transactions.csv` (date-specific)
- `{category}_transactions.csv` (category export)
- `{account}_transactions.csv` (account export)

### Success Criteria

✅ File created at expected location
✅ All data included in export
✅ No data corruption (amounts, dates correct)
✅ File can be opened in Excel/CSV viewer
✅ JSON is valid and parseable

---

## Skill 6: deduplicate

**Purpose**: Find and merge duplicate transactions (smart deduplication with user review)

**When to use**:
- After importing overlapping statements
- Monthly deduplication sweep
- Linking internal transfers
- Cleanup before analysis

### Usage Examples

**Example 1: Check for duplicates**
```
You: "Check for duplicates"
Claude Code: Runs 3-layer dedup algorithm
- Reference number matching
- Content hash matching (date + amount + merchant[:30])
- Temporal proximity (same day ±3 days)

Result:
"Found 2 potential duplicates:

Candidate 1:
  Transaction A: 2025-01-15 Jollibee -250.00 (Ref: GC1001234567890)
  Transaction B: 2025-01-15 Jollibee -250.00 (Ref: GC1001234567890)
  Reason: Same reference number (100% match)
  Confidence: HIGH
  Merge? [y/n]: "

You: y
Claude Code: ✅ Merged (Transaction B marked as duplicate of A)

(continues with next potential duplicate...)

Result: "✅ Processed 2 potential duplicates, merged 2"
```

**Example 2: Internal transfer detection**
```
Claude Code: Found potential internal transfer:
  GCash: 2025-01-20 Transfer out -5000.00
  BPI: 2025-01-21 Deposit +5000.00
  Reason: Same amount, opposite signs, 1 day apart
  Confidence: HIGH
  Link as transfer? [y/n]: "

You: y
Claude Code: ✅ Linked as internal transfer (won't count as duplicate spending)"
```

### Deduplication Logic

**Layer 1: Reference Number** (100% confidence)
- If two transactions have identical reference numbers → Duplicate
- Used only if reference# field is populated
- Strongest indicator (banks issue unique ref#s)

**Layer 2: Content Hash** (95% confidence)
- Hash = SHA256(date + amount + merchant[:30])
- Matches same date, same amount, same merchant (first 30 chars)
- Catches manual entry errors, formatting differences

**Layer 3: User Review** (manual)
- Flag candidates that don't match L1 or L2
- Show both transactions to user
- User confirms merge or skips
- Conservative approach (avoids false positives)

### Duplicate Scenarios

**Same statement imported twice**:
- File hash check prevents (system skips reimport)

**Overlapping statements** (e.g., GCash Jan 15-31 + Jan 1-31):
- Layer 2 catches identical transactions
- User confirms dedup

**Internal transfers** (money between own accounts):
- Appears in both accounts (one debit, one credit)
- Layer 3 detects (same amount, opposite signs, 1-3 days)
- User links as transfer (doesn't count as duplicate spending)

### Success Criteria

✅ No duplicate transactions in final database
✅ Internal transfers properly linked
✅ Zero false positives (conservative matching)
✅ User confirms all merges

---

## Workflow Examples

### Monthly Routine

**Step 1: Parse statements**
```
You: "Parse my GCash and BPI statements for January"
Claude Code: Imports both
Result: ✅ 28 GCash + 45 BPI = 73 total transactions
```

**Step 2: Check for duplicates**
```
You: "Check for duplicates between accounts"
Claude Code: Finds internal transfer (GCash to BPI)
You: Confirm merge
Result: ✅ Merged 1, final count: 72 unique transactions
```

**Step 3: Categorize unknowns**
```
You: "Categorize any unknown merchants"
Claude Code: Found 2 unknown, 70 known
You: Categorize the 2 new merchants
Result: ✅ All 72 transactions categorized
```

**Step 4: Generate report**
```
You: "Generate January report"
Claude Code: Creates HTML + Markdown
Result: ✅ Open in browser, view charts
```

**Step 5: Export for archiving**
```
You: "Export January to CSV"
Claude Code: Saves to data/exports/2025-01_transactions.csv
Result: ✅ Backed up for future reference
```

### Ad-Hoc Analysis

```
You: "How much food and shopping combined last week?"
Claude Code: Queries food + shopping for past 7 days
Result: "Food ₱1,250 + Shopping ₱850 = ₱2,100 total"

You: "I think I'm overspending. Compare to last month"
Claude Code: Compares current vs previous month
Result: "This month: ₱98,500. Last month: ₱89,300. +10% increase"

You: "Where's that extra ₱9,200 coming from?"
Claude Code: Analyzes by category
Result: "Extra ₱5,200 on shopping (+25%)
Extra ₱3,000 on food (+12%)
Utilities actually down ₱200"
```

---

## Tips & Tricks

### Batch Processing
```
You: "Parse all PDFs in my sample_statements folder"
Claude Code: Processes each PDF automatically
```

### Batch Categorization
```
You: "Show me all uncategorized transactions"
Claude Code: Displays list, then prompts to categorize
```

### Custom Reports
```
You: "Generate Q1 report (Jan-Mar)"
Claude Code: Aggregates all three months
```

### Data Integrity
```
You: "Backup my data"
Claude Code: Exports everything to data/exports/
You: Copy data/exports/ to backup location
```

---

## Troubleshooting

**Skill not invoking correctly:**
- Verify Claude Code recognizes the skill name
- Check skill syntax matches SKILL.md

**Script not executing:**
- Test script manually: `python scripts/script_name.py`
- Check imports: All dependencies in venv?

**Data not showing up:**
- Verify transactions were imported: Check SQLite directly
- Check date range in query

**Reports look wrong:**
- Verify merchant_mapping.json is valid JSON
- Check template files exist in templates/

---

**Master these 6 skills and you've got the complete analyze-fin system.** 🚀
