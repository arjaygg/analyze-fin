---
name: export-data
description: Export transaction data to CSV or JSON for external analysis. Use when user wants to export, download, save data to a file, or analyze in Excel, Google Sheets, or other tools.
allowed-tools: Bash, Read
---

# Export Transaction Data

Export your financial data to CSV or JSON for analysis in Excel, Google Sheets, Python, or other tools.

## When to Use This Skill

Trigger when the user wants to:
- "Export my data"
- "Save to CSV"
- "Download transactions"
- "Export to Excel"
- "Get my data in JSON"
- "Backup my transactions"

## What This Does

Exports transaction data with:
- All transaction details (date, merchant, amount, category)
- Filtered by your criteria (date, category, merchant)
- Multiple formats (CSV for Excel, JSON for programming)
- Clean, structured data ready for analysis

## Basic Workflow

### Step 1: Understand Export Requirements

Ask:
- **Format:** CSV (Excel/Sheets) or JSON (programming)?
- **Scope:** All transactions or filtered?
- **Time period:** Specific dates or all-time?

### Step 2: Build Export Command

**Export everything to CSV:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin export --format csv --output ~/exports/transactions.csv
```

**Export to JSON:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin export --format json --output ~/exports/transactions.json
```

**Filtered export (date range):**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin export --date-range "November 2024" --format csv --output ~/exports/nov_2024.csv
```

**Category-specific export:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin export --category "Food & Dining" --format csv --output ~/exports/food_spending.csv
```

**Merchant-specific export:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin export --merchant "Jollibee" --format csv --output ~/exports/jollibee.csv
```

### Step 3: Confirm and Provide File Location

**Success response:**
```
✅ Exported 156 transactions to CSV!

File: ~/exports/transactions.csv
Size: 24 KB

You can now:
- Open in Excel or Google Sheets
- Create pivot tables
- Build custom charts
- Analyze in Python/R
- Archive for records
```

### Step 4: Explain How to Use

Help users get started with exported data:

**For Excel/Sheets:**
```
📊 Using in Excel:

1. Open Excel
2. File → Open → Select transactions.csv
3. Data will load with columns:
   - Date, Merchant, Category, Amount, Description

Ready to create pivot tables!
```

**For Python analysis:**
```
🐍 Using in Python:

import pandas as pd
df = pd.read_csv('~/exports/transactions.csv')
print(df.groupby('category')['amount'].sum())

Your data is ready for pandas analysis!
```

## Export Formats

### CSV Format

**Best for:** Excel, Google Sheets, general use

**Columns:**
- `date` - Transaction date (YYYY-MM-DD)
- `merchant` - Merchant name (normalized)
- `category` - Spending category
- `amount` - Transaction amount (positive = income, negative = expense)
- `description` - Original transaction description
- `account` - Source account (GCash, BPI, Maya)
- `reference_number` - Bank reference (if available)

**Example:**
```csv
date,merchant,category,amount,description,account
2025-10-20,Jollibee,Food & Dining,-285.00,JOLLIBEE MANILA,GCash
2025-10-19,Grab,Transportation,-350.00,GRAB TRANSPORT,GCash
```

### JSON Format

**Best for:** Programming, APIs, data pipelines

**Structure:**
```json
{
  "transactions": [
    {
      "transaction_id": 123,
      "date": "2025-10-20",
      "merchant_normalized": "Jollibee",
      "category": "Food & Dining",
      "amount": "-285.00",
      "description": "JOLLIBEE MANILA INC",
      "account": "gcash",
      "reference_number": null,
      "created_at": "2025-10-21T08:30:00Z"
    }
  ],
  "metadata": {
    "total_transactions": 156,
    "date_range": "2025-09-21 to 2025-10-21",
    "exported_at": "2025-10-21T10:15:00Z"
  }
}
```

## Filter Options

### By Date Range

**Last 30 days:**
```bash
--date-range "last 30 days"
```

**Specific month:**
```bash
--date-range "November 2024"
```

**Custom range:**
```bash
--date-range "2024-11-01 to 2024-11-30"
```

### By Category

**Single category:**
```bash
--category "Food & Dining"
```

**Multiple categories:**
```bash
--categories "Food & Dining,Shopping,Transportation"
```

### By Merchant

**Specific merchant:**
```bash
--merchant "Jollibee"
```

**Partial matching:**
```bash
--merchant-contains "coffee"  # Matches Starbucks, Coffee Bean, etc.
```

### By Amount

**Large transactions only:**
```bash
--amount-min 5000
```

**Small transactions only:**
```bash
--amount-max 500
```

**Amount range:**
```bash
--amount-min 1000 --amount-max 10000
```

## Common Export Scenarios

### Tax Preparation

**User says:** "Export for my accountant"

**You do:**
```bash
# Export full year with categories
uv run analyze-fin export --date-range "2025" --format csv --output ~/exports/2025_taxes.csv
```

**Explain:**
```
✅ Exported full 2025 transactions for tax filing!

File: ~/exports/2025_taxes.csv

Your accountant can use this to:
- Identify deductible expenses
- Calculate business vs personal
- Verify income sources

All categories and amounts are included.
```

### Budget Analysis

**User says:** "Export so I can analyze in Excel"

**You do:**
```bash
uv run analyze-fin export --format csv --output ~/exports/budget_analysis.csv
```

**Suggest:**
```
✅ Exported all transactions!

In Excel, try:
1. Insert → PivotTable
2. Rows: Category
3. Values: Sum of Amount
4. See spending by category instantly!

Want me to show example formulas?
```

### Power User Deep Dive

**User says:** "Export to JSON for Python"

**You do:**
```bash
uv run analyze-fin export --format json --output ~/exports/transactions.json
```

**Provide starter code:**
```
✅ Exported to JSON!

Quick Python starter:

```python
import json
import pandas as pd

with open('transactions.json') as f:
    data = json.load(f)

df = pd.DataFrame(data['transactions'])
print(df.groupby('category')['amount'].sum())
```

Your data is ready for analysis!
```

### Monthly Archive

**User says:** "Backup November data"

**You do:**
```bash
uv run analyze-fin export --date-range "November 2024" --format csv --output ~/backups/2024_11_backup.csv
```

**Confirm:**
```
✅ November 2024 archived!

File: ~/backups/2024_11_backup.csv
Transactions: 110
Total: ₱42,350.75

Your data is safely backed up.
```

## Data Privacy Note

Remind users about data handling:

```
🔒 Privacy Note:

Your exported file contains:
- Transaction amounts and descriptions
- Merchant names
- Spending patterns

This is sensitive financial data. Store securely:
- Don't email unencrypted
- Don't upload to public cloud
- Keep in password-protected folders
- Delete when no longer needed
```

## Error Handling

**No transactions match filters:**
```
No transactions found matching your criteria.

Filters applied:
- Category: "Entertainment"
- Date: November 2024

Try:
- Broader date range
- Different category
- Remove filters to see all data
```

**Output file exists:**
```
File ~/exports/transactions.csv already exists.

Options:
1. Overwrite (replace old file)
2. Create new with timestamp (transactions_2025_10_21.csv)
3. Choose different filename

What would you prefer?
```

**Export failed:**
```
Couldn't export data due to: [error]

Let's try:
1. Different output location
2. Different format (CSV vs JSON)
3. Smaller date range

Which should we try?
```

## Integration with Other Skills

After exporting:

**For further analysis:**
```
You've exported your data!

Want to:
- Generate a visual report first?
- Query specific transactions before exporting?
- Export different time periods?
```

**For archival:**
```
Data exported and backed up!

Regular exports recommended:
- Monthly: End of each month
- Quarterly: For trend analysis
- Yearly: Tax preparation

Set a reminder?
```

## Tips for Users

Share these tips:

1. **Regular exports** - Monthly backups protect your data
2. **Descriptive filenames** - Use dates: `2024_11_transactions.csv`
3. **Organize exports** - Create folders by year/month
4. **CSV for Excel** - Easier than JSON for spreadsheets
5. **Test with small sample** - Export last week first to test

## Advanced Use Cases

### Creating Custom Dashboards

```
With your exported CSV, you can:
- Build Power BI dashboards
- Create Google Data Studio reports
- Make custom Excel charts
- Analyze trends in Tableau
```

### Combining with Other Data

```
You can merge this with:
- Credit card statements
- Investment account data
- Budget spreadsheets
- Financial planning tools
```

### Forecasting

```
Use historical exports to:
- Predict next month's spending
- Identify seasonal patterns
- Build budget models
- Track spending changes
```
