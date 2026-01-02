---
name: generate-report
description: Generate visual spending reports with charts and breakdowns. Use when user wants to see their spending dashboard, visualize spending patterns, create reports, or get a summary of their finances.
allowed-tools: Bash, Read
---

# Generate Spending Reports

Create comprehensive spending reports with visual charts and detailed breakdowns.

## When to Use This Skill

Trigger when the user asks for:
- "Show me my spending report"
- "Generate a dashboard"
- "Visualize my spending"
- "Give me a summary"
- "Create a monthly report"
- "Show me charts"

## What This Creates

Reports include:
- **Category breakdown** - Pie chart showing spending distribution
- **Spending over time** - Line chart showing trends
- **Top merchants** - Bar chart of where you spend most
- **Summary statistics** - Total spent, transaction count, averages
- **Time period comparisons** - Month-over-month changes

## Basic Workflow

### Step 1: Clarify Report Parameters

Ask about:
- **Time period** - "Which month?" or "All time?"
- **Format** - HTML (visual) or Markdown (text)?
- **Scope** - All categories or specific ones?

### Step 2: Generate the Report

**Full HTML report (default):**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin report --format html
```

**Markdown report:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin report --format markdown
```

**Specific time period:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin report --date-range "November 2024" --format html
```

**Category-specific:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin report --categories "Food & Dining,Transportation" --format html
```

### Step 3: Open and Describe

**For HTML reports:**
1. Report opens automatically in browser
2. Describe what they'll see:

```
✅ Report generated and opened in your browser!

Your November 2024 spending dashboard shows:

📊 Total Spending: ₱42,350.75

Top Categories:
1. Shopping - ₱12,400 (29%)
2. Food & Dining - ₱8,500 (20%)
3. Transportation - ₱5,200 (12%)

Key Insights:
- Spending up 15% from October
- Your biggest merchant: SM Supermalls (₱5,600)
- Average transaction: ₱385.50

The interactive charts let you:
- Click categories to see breakdown
- Hover for exact amounts
- View spending trends over time
```

**For Markdown reports:**
Show a preview:
```
✅ Report generated at: ~/reports/spending_2024_11.md

Here's a preview:

# Spending Report - November 2024

**Total Spent:** ₱42,350.75
**Transactions:** 110
**Average:** ₱385.00/transaction

## Category Breakdown

| Category | Amount | % | Count |
|----------|--------|---|-------|
| Shopping | ₱12,400 | 29% | 18 |
| Food & Dining | ₱8,500 | 20% | 42 |
[...]

Want me to show more details?
```

### Step 4: Offer Insights and Next Steps

After generating, provide observations:

**Spending trends:**
```
📈 Spending Insights:

- You spent 15% more than last month
- Food & Dining increased by ₱1,200
- Transportation decreased by ₱800

This month's biggest change: +₱2,100 in Shopping

Want to drill into what changed?
```

**Patterns noticed:**
```
🔍 Patterns I Notice:

- You spend most on weekends (65% of shopping)
- Food spending peaks mid-month
- Transportation is consistent daily

Curious about any of these?
```

## Report Types

### Monthly Summary Report

**Best for:** Regular monthly review

**Contains:**
- Full month spending breakdown
- Category percentages
- Top 10 merchants
- Day-by-day spending chart
- Comparison with previous month

**Trigger:** "Show me November spending"

### Category Deep-Dive Report

**Best for:** Understanding specific spending area

**Contains:**
- Single category focus (e.g., Food & Dining)
- All merchants in that category
- Sub-category breakdown (restaurants vs groceries)
- Frequency analysis
- Trends over time

**Trigger:** "Analyze my food spending"

### Comparison Report

**Best for:** Tracking changes over time

**Contains:**
- Side-by-side month comparison
- Category changes (+/- amounts and %)
- Merchant additions/removals
- Trend indicators (↑ ↓ →)

**Trigger:** "Compare November to October"

### Annual Summary Report

**Best for:** Year-end review

**Contains:**
- Full year totals
- Monthly spending chart
- Seasonal patterns
- Biggest transactions
- Category distribution

**Trigger:** "Show me my 2025 spending"

## Chart Types Explained

Help users understand the visualizations:

**Pie Chart (Category Breakdown):**
```
Shows how your total spending splits across categories.

Larger slices = more spending in that category.
Hover to see exact amounts and percentages.
```

**Line Chart (Spending Over Time):**
```
Shows spending trends day-by-day or month-by-month.

Going up = spending more
Going down = spending less
Flat = consistent spending
```

**Bar Chart (Top Merchants):**
```
Shows where you spend the most money.

Taller bars = more spent at that merchant.
Compare bars to see relative spending.
```

## Customization Options

Let users customize reports:

**Date ranges:**
- "Last 7 days"
- "November 2024"
- "2024-11-01 to 2024-11-30"
- "Last month"
- "This year"

**Category filtering:**
```
Want to focus on specific categories?

I can generate reports for:
- Single category (just Food & Dining)
- Multiple categories (Food + Shopping)
- Everything except categories (all but Transfers)
```

**Output format:**
- **HTML** - Visual, interactive, opens in browser
- **Markdown** - Text-based, easy to share/read
- **PDF** - Printable (future feature)

## Report Storage

Explain where reports are saved:

```
📁 Your reports are saved at:
~/analyze-fin/reports/

Files:
- spending_2024_11_30.html (today's report)
- spending_2024_10_31.html (last month)

Reports are saved forever unless you delete them.
You can open them anytime by clicking the file.
```

## Error Handling

**No data for time period:**
```
I don't have any transactions for November 2024.

Your data spans: Sep 21 - Oct 21, 2025

Want a report for a different period?
```

**Uncategorized transactions:**
```
⚠️ Notice: 15 transactions (11%) are uncategorized.

I can still generate the report, but:
- Uncategorized will show as a separate category
- Your breakdown might be less accurate

Want to categorize these first? (Recommended)
```

**Report generation failed:**
```
Couldn't generate the report due to: [error]

Let's try:
1. Checking if you have transactions imported
2. Simplifying the date range
3. Using markdown format instead

Which would you like to try?
```

## Integration with Other Skills

After generating reports:

**If spending is high:**
```
Your spending was high this month.

Want to:
- Compare with last month?
- See specific transactions in a category?
- Export data for deeper analysis?
```

**If patterns emerge:**
```
I notice you spend a lot on [category].

Want to:
- Query all [category] transactions?
- See merchant breakdown?
- Set a budget alert? (future feature)
```

**For ongoing tracking:**
```
Great report! For ongoing tracking:
- Generate monthly reports on the 1st
- Compare month-over-month trends
- Export to track in your own spreadsheet
```

## Tips for Better Reports

Share these tips:

1. **Categorize first** - Reports are clearer with categorized data
2. **Regular reports** - Monthly reviews spot trends early
3. **Compare periods** - Month-over-month shows changes
4. **Export raw data** - For custom analysis in Excel
5. **Save reports** - Track progress over time

## Visual Report Preview

When report opens in browser, describe the layout:

```
Your report is organized in sections:

📊 Top Section: Summary Stats
- Total spent, transaction count, averages

🥧 Pie Chart: Category Breakdown
- Visual spending distribution
- Click slices for details

📈 Line Chart: Daily Spending Trend
- Shows spending over time
- Hover for specific days

📊 Bar Chart: Top 10 Merchants
- Where you spend most
- Sorted by amount

📋 Tables: Detailed Breakdowns
- Category table with amounts
- Merchant table with frequency
- Recent transactions list
```
