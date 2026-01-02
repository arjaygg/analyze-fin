---
name: categorize-transactions
description: Interactively categorize unknown merchants and teach the system to recognize them. Use when user wants to categorize, organize, or tag transactions, fix merchant names, or improve auto-categorization accuracy.
allowed-tools: Bash, Read
---

# Categorize Transactions

Interactive merchant categorization with learning system. Teach analyze-fin to recognize merchants and improve auto-categorization.

## When to Use This Skill

Trigger when the user wants to:
- "Categorize my transactions"
- "Fix unknown merchants"
- "Teach you about this merchant"
- "Why is this categorized wrong?"
- "Review uncategorized transactions"
- "Update merchant categories"

## What This Does

The categorization system:
1. **Auto-categorizes** - 100+ Philippine merchants pre-mapped (Jollibee, SM, Grab, etc.)
2. **Learns from you** - Your corrections persist and apply to future transactions
3. **Normalizes names** - "JOLLIBEE MANILA INC" → "Jollibee"
4. **Improves over time** - Accuracy increases with your input

## Basic Workflow

### Step 1: Check for Uncategorized Transactions

**Query uncategorized:**
```bash
cd /Users/agallentes/git/analyze-fin && uv run analyze-fin query --category "Uncategorized" --format json
```

If many uncategorized transactions exist, suggest batch categorization.

### Step 2: Interactive Categorization

**For each unknown merchant, ask user:**

```
I found "MANILA ELECTRIC COMPANY" - what category?

Available categories:
1. Bills & Utilities (recommended for electric company)
2. Food & Dining
3. Transportation
4. Shopping
5. Healthcare
[... list all categories ...]

Choose a number or type the category name.
```

### Step 3: Apply and Learn

Once user provides category:

```bash
# This would be a Python call to the categorization module
cd /Users/agallentes/git/analyze-fin && uv run python -m analyze_fin.categorization.learning add-rule "MANILA ELECTRIC" "Bills & Utilities" "Meralco"
```

**Confirm to user:**
```
✓ Saved! "MANILA ELECTRIC COMPANY" → Meralco (Bills & Utilities)

This will automatically apply to:
- All future "MANILA ELECTRIC" transactions
- Similar merchant names (fuzzy matching)

Found 3 existing transactions with this merchant. Applied category retroactively.
```

### Step 4: Build Learning Database

As users categorize, the system builds a personal merchant database:
- Stores merchant patterns
- Maps to normalized names
- Associates with categories
- Persists across sessions

## Available Categories

Present these options during categorization:

1. **Food & Dining** - Restaurants, food delivery, groceries
2. **Transportation** - Grab, taxi, gas, parking, tolls
3. **Shopping** - Retail stores, online purchases, clothing
4. **Bills & Utilities** - Electricity, water, internet, phone
5. **Entertainment** - Movies, streaming services, hobbies
6. **Healthcare** - Doctors, pharmacies, hospitals, insurance
7. **Personal Care** - Salon, spa, beauty products
8. **Education** - Tuition, books, courses
9. **Travel** - Hotels, flights, tours
10. **Groceries** - Supermarkets, wet markets
11. **Financial Services** - Bank fees, insurance, investments
12. **Government** - Taxes, licenses, permits
13. **Transfers** - Money transfers between accounts
14. **Cash** - ATM withdrawals, cash deposits
15. **Uncategorized** - When truly unknown

## Smart Suggestions

Help users by suggesting likely categories:

**Pattern matching:**
```
"JOLLIBEE" → Likely "Food & Dining"
"GRAB" → Likely "Transportation"
"SM DEPT" → Likely "Shopping"
"MERALCO" → Likely "Bills & Utilities"
```

**Keywords in description:**
```
"PAYMENT TO MERCHANT" + "COFFEE" → Suggest "Food & Dining"
"BILLS PAYMENT" + "ELECTRIC" → Suggest "Bills & Utilities"
"FUND TRANSFER" → Suggest "Transfers"
```

## Handling Special Cases

### Internal Transfers

**User categorizing:** "Fund Transfer FROM:ARJAY"

**You suggest:**
```
This looks like a transfer between your own accounts.

Suggested category: "Transfers"

This won't count as spending since it's moving your own money.
```

### Interest and Fees

**Interest Earned:**
```
Category: "Financial Services" (as income)
Note: This is income, not spending.
```

**Bank Fees:**
```
Category: "Financial Services" (as expense)
Examples: "InstaPay Transfer Fee", "ATM Fee"
```

### Split Transactions

If user mentions a transaction should be split:
```
Currently, analyze-fin categorizes entire transactions.

Split transaction support is planned for future updates.

For now, you can:
1. Categorize to the primary category
2. Add a note explaining the split
3. Track split amounts manually
```

## Review and Correction Workflow

**User says:** "This transaction shouldn't be Food"

**You do:**
1. Ask which transaction (show recent Food transactions)
2. Ask for correct category
3. Update categorization
4. Ask if this should apply to all similar transactions

**Example:**
```
Which transaction needs correction?

Recent Food & Dining:
1. Oct 20 - Starbucks - ₱150.00
2. Oct 18 - SM Supermarket - ₱1,245.00
3. Oct 15 - Jollibee - ₱285.00

(User selects #2)

What's the correct category for "SM Supermarket"?

(User says "Groceries")

✓ Updated! SM Supermarket → Groceries

Apply to all SM Supermarket transactions? (5 found)
```

## Merchant Normalization

Explain how normalization works:

```
**Merchant normalization** cleans up messy names:

Raw: "JOLLIBEE MANILA INC"
Normalized: "Jollibee"

Raw: "GRAB TRANSPORT SERVICES"
Normalized: "Grab"

This makes your reports cleaner and groups similar transactions together.
```

## Progress Tracking

Show categorization progress:

```
📊 Categorization Status:

✓ Categorized: 156 transactions (89%)
⚠ Uncategorized: 19 transactions (11%)

Top uncategorized merchants:
1. "XYZ MERCHANT" - 5 transactions
2. "ABC STORE" - 3 transactions
3. "UNKNOWN VENDOR" - 2 transactions

Want to categorize these now?
```

## Tips for Users

Share these tips during categorization:

1. **Be consistent** - Use the same category for similar merchants
2. **Use Groceries vs Food & Dining** - Groceries for supermarkets, Food & Dining for restaurants
3. **Bills are predictable** - Utilities, subscriptions belong in Bills & Utilities
4. **Transportation is broad** - Includes Grab, gas, parking, tolls
5. **When in doubt, ask** - I can suggest based on the merchant name

## Integration with Other Skills

After categorizing, suggest:
- **Query** - "Want to see your Food spending now?"
- **Report** - "Ready to generate a categorized report?"
- **Parse** - "Import more statements to categorize?"

## Error Handling

**No uncategorized transactions:**
```
Great news! All your transactions are already categorized.

Your auto-categorization accuracy: 94%

Want to review any categories for accuracy?
```

**Category doesn't exist:**
```
"Snacks" isn't a standard category.

Did you mean:
- Food & Dining
- Groceries
- Shopping

Or should I add "Snacks" as a custom category?
```

**Merchant not found:**
```
I couldn't find that merchant in your transactions.

Want to:
1. Search by partial name
2. Show all uncategorized merchants
3. Query by date range
```
