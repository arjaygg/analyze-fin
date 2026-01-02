---
name: query-spending
description: Answer questions about spending patterns, query transactions by category, merchant, date, or amount. Use when user asks "how much", "what did I spend", "show me transactions", or any spending-related questions about their financial data.
allowed-tools: Bash, Read
---

# Query Spending

Answer natural language questions about spending and transactions from the analyze-fin database.

## When to Use This Skill

Trigger when the user asks:
- "How much did I spend on food?"
- "What did I spend at Jollibee?"
- "Show me all transactions over ₱5,000"
- "How much transport last month?"
- "What's my biggest expense?"
- Any question about spending amounts, categories, or merchants

## Available Query Filters

- **Category** - Filter by spending category (Food & Dining, Transportation, Shopping, etc.)
- **Merchant** - Filter by merchant name (Jollibee, SM, Grab, etc.)
- **Date Range** - Filter by time period (last week, November 2024, etc.)
- **Amount** - Filter by minimum/maximum transaction amount

## Basic Workflow

### Step 1: Understand the Question

Parse the user's natural language request to identify:
- What they want to know (total, count, list of transactions)
- Which filters to apply (category, merchant, date, amount)
- How to present results (summary, detailed list, top items)

### Step 2: Build the Query Command

**Simple category query:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin query --category "Food & Dining"
```

**Query by merchant:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin query --merchant "Jollibee"
```

**Query with date range:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin query --date-range "November 2024"
```

**Query by amount threshold:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin query --amount-min 5000
```

**Combined filters:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin query --category "Food & Dining" --date-range "last month" --amount-min 500
```

**JSON output for processing:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin query --category "Food & Dining" --format json
```

### Step 3: Execute and Interpret Results

Run the query command and format results conversationally.

**Example responses:**

✅ **Simple total:**
```
You spent ₱8,456.78 on Food & Dining across 42 transactions.

Your top food merchants:
1. Jollibee - ₱2,345.67 (12 transactions)
2. Grab Food - ₱1,890.00 (8 transactions)
3. McDonald's - ₱1,234.50 (6 transactions)
```

✅ **Transaction list:**
```
Here are your transactions over ₱5,000:

Oct 20 - InstaPay Transfer - ₱50,000.00
Oct 13 - InstaPay Transfer - ₱35,000.00
Oct 10 - Fund Transfer - ₱65,000.00
Oct 07 - Fund Transfer - ₱10,000.00

Total: ₱160,000.00 across 4 large transactions.
```

✅ **Date range summary:**
```
In November 2024, you spent ₱42,350.75 total.

Breakdown:
- Food & Dining: ₱8,500 (20%)
- Transportation: ₱5,200 (12%)
- Shopping: ₱12,400 (29%)
- Bills & Utilities: ₱3,500 (8%)
- Other: ₱12,750.75 (31%)
```

### Step 4: Offer Insights and Follow-ups

After answering, provide context and suggest next questions:

**If spending seems high:**
```
That's 15% more than last month. Want to see what changed?
```

**If merchant query:**
```
You visit Jollibee frequently! Want to see your food spending breakdown?
```

**After showing transactions:**
```
Would you like me to:
- Break this down by category?
- Compare with last month?
- Generate a visual report?
```

## Common Query Patterns

### "How much on [category]?"

**User says:** "How much did I spend on food?"

**You do:**
1. Identify category: "Food & Dining"
2. Query: `--category "Food & Dining"`
3. Format: Show total, count, and top merchants

### "What did I spend at [merchant]?"

**User says:** "Show me Grab transactions"

**You do:**
1. Identify merchant: "Grab"
2. Query: `--merchant "Grab"`
3. Format: List transactions with dates and amounts

### "Show me transactions over [amount]"

**User says:** "What are my big expenses?"

**You do:**
1. Set threshold (e.g., ₱5,000 for "big")
2. Query: `--amount-min 5000`
3. Format: List by date, descending order

### "How much last [time period]?"

**User says:** "How much did I spend last week?"

**You do:**
1. Convert to date range: "last 7 days"
2. Query: `--date-range "last week"`
3. Format: Total with category breakdown

## Handling Edge Cases

**No transactions found:**
```
I didn't find any transactions matching that criteria.

Possible reasons:
- No transactions in that category yet
- Date range might be outside your statement period
- Merchant name might be spelled differently

Want to try a broader search?
```

**Ambiguous merchant name:**
```
I found multiple merchants with "coffee" in the name:
- Starbucks (12 transactions)
- Coffee Bean (5 transactions)
- Bo's Coffee (3 transactions)

Which one are you looking for?
```

**Category not recognized:**
```
I'm not sure which category "snacks" maps to.

Available categories:
- Food & Dining
- Shopping
- Transportation
[list all categories]

Which category fits best?
```

## Available Categories

When users mention spending types, map to these categories:
- **Food & Dining** - restaurants, food delivery, groceries
- **Transportation** - Grab, taxi, gas, parking
- **Shopping** - retail, online purchases, clothing
- **Bills & Utilities** - electricity, water, internet
- **Entertainment** - movies, streaming, hobbies
- **Healthcare** - doctors, medicine, insurance
- And more...

## Tips for Natural Responses

1. **Use the user's language** - If they say "food", you can say "food" (not always "Food & Dining")
2. **Add context** - "That's about ₱280 per day" adds meaning
3. **Be conversational** - "You spent quite a bit on Grab this month!" feels natural
4. **Suggest comparisons** - "Want to compare with last month?"
5. **Acknowledge limitations** - "I only have data from Sept-Oct 2025"

## Integration with Other Skills

After answering queries, suggest:
- **Generate Report** - "Want a visual breakdown?"
- **Categorize** - "Some transactions are uncategorized. Want to fix that?"
- **Export** - "I can export this to CSV if you need it in Excel"
