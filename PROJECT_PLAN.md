# analyze-fin: Complete Implementation Plan (Local-First, 5 Phases)

**Philippine Personal Finance Tracker**
**Timeline**: ~3 weeks (5 phases) to fully functional MVP
**Team**: You + Claude Code
**Location**: `/Users/agallentes/git/analyze-fin`
**Architecture**: SQLite + Python scripts + Claude Skills
**Cost**: $0 (fully local, zero external dependencies)

---

## Executive Summary

You're building a statement-based personal finance tracker for Philippine users who manage multiple accounts (BPI, GCash, Maya, Vybe).

**Why this approach wins:**
- Zero API friction (banks don't expose personal data APIs anyway)
- User owns all data (stays on your machine)
- Faster MVP (3 weeks vs 5-6 weeks with cloud)
- Zero cost ($0 vs $20-30/month for cloud)
- Full privacy (data never leaves your computer)
- Works offline (local SQLite)

**What you'll build:**
- Parse PDF statements from 4 Philippine banks
- Smart deduplication across multiple imports
- Interactive merchant categorization (system learns)
- HTML reports with interactive charts
- Claude Code Skills for end-to-end workflows
- Natural language queries about spending

---

## Product Overview: What You're Building

### The Problem

Filipino professionals use 2-4 financial accounts:
- **BPI**: Salary account
- **GCash**: Mobile payments
- **Maya**: Savings (e-wallet)
- **Vybe**: Credit (linked to BPI)

**Challenge**: Tracking spending across all accounts is manual and error-prone.

### The Solution

**analyze-fin** automates the hard part (data entry) and provides insights:

1. **Download PDF statements** from your banking apps (monthly)
2. **Upload to analyze-fin** → Automatic extraction
3. **System categorizes** merchants intelligently (learns from corrections)
4. **View spending insights** via interactive HTML reports
5. **Ask questions** about your spending (natural language)
6. **Export to CSV** anytime for manual analysis

### Core Features

✅ **Multi-Bank PDF Parsing** (all 4 banks)
- GCash: Extracts transaction tables (date + amount + ref#)
- BPI: Handles password-protected PDFs
- Maya: Supports different account formats
- Vybe: Guides users to BPI statement (no export)
- Quality scoring (0-100) for each parse
- Error detection (scanned PDFs, corrupted data)

✅ **Smart Deduplication**
- 3-layer matching: reference# → content hash → user review
- Handles date overlaps (importing same period twice)
- Detects internal transfers (money between your own accounts)
- Zero false positives (conservative approach)

✅ **Merchant Learning System**
- 150+ common Philippine merchants pre-mapped
- Unknown merchants → You categorize once → System remembers
- Saves mappings to local JSON file
- Re-categorizes similar merchants automatically

✅ **Spending Insights**
- HTML reports with Plotly charts
- Pie chart: spending by category
- Line chart: daily spending trend
- Bar chart: top merchants
- Summary cards: total in/out, net, daily average
- Anomaly detection (unusual spending)

✅ **Natural Language Queries**
- Ask: "How much food last week?"
- Ask: "Top spending categories?"
- Ask: "How much transport?"
- Powered by Claude Code context (no external API)
- Private (answers generated from local data)

✅ **Local Data Ownership**
- Everything stored locally: `data/analyze-fin.db`
- Export anytime as CSV/JSON
- Full transparency (inspect data with any SQLite tool)
- Easy backup (copy entire folder)

---

## Architecture: Local-First, Skills-Driven

### Core Principles

1. **Local-First**: All data stays on your machine (SQLite file)
2. **Skills-Driven**: Claude Skills are primary interface, not side feature
3. **No External APIs**: No Supabase, no Claude API calls, no cloud dependencies
4. **Interactive Learning**: Categorize once, system learns forever
5. **Transparent**: Inspect/export data anytime

### Data Storage

**Primary: SQLite Database**
- Location: `data/analyze-fin.db`
- Why: Single file, no server, supports complex queries, perfect for local apps
- Tables: accounts, statements, transactions, merchant_corrections, spending_patterns

**Secondary: JSON/CSV Exports**
- Location: `data/exports/`
- Purpose: Backup, transparency, sharing, further analysis

**Merchant Mappings**
- Location: `data/merchant_mapping.json`
- Purpose: Learning system (grows as you use it)
- Format: `{"JOLLIBEE": {"normalized": "Jollibee", "category": "food"}}`

### Claude Skills: Your Interface

**Instead of web UI**, you interact via Claude Code skills:

#### Skill 1: `parse-statements`
```
You: "Parse my GCash statement from January"
→ Claude Code: Prompts for file path
→ Claude Code: Parses PDF with pdfplumber
→ Claude Code: Stores to SQLite
→ Result: "✅ Imported 28 transactions, quality: 95"
```

#### Skill 2: `categorize-transactions`
```
You: "Categorize my uncategorized merchants"
→ Claude Code: Finds unknown merchants
→ Claude Code: For each one, prompts: "Category?"
→ You: Select from list (Food, Shopping, Bills, etc.)
→ Claude Code: Saves to merchant_mapping.json
→ Claude Code: Updates SQLite
→ Result: Future similar merchants auto-categorized
```

#### Skill 3: `generate-report`
```
You: "Generate my January spending report"
→ Claude Code: Queries SQLite for date range
→ Claude Code: Creates HTML with Plotly charts
→ Claude Code: Creates Markdown summary
→ Claude Code: Opens HTML in browser
→ Result: "✅ Report: data/reports/2025-01-report.html"
```

#### Skill 4: `query-spending`
```
You: "How much did I spend on food last week?"
→ Claude Code: Loads SQLite data into context
→ Claude Code: Uses reasoning to answer
→ Result: "₱1,250 across 12 transactions"
```

#### Skill 5: `export-data`
```
You: "Export all transactions to CSV"
→ Claude Code: Queries SQLite
→ Claude Code: Converts to CSV with Pandas
→ Claude Code: Saves to data/exports/
→ Result: "✅ Exported 156 transactions"
```

#### Skill 6: `deduplicate`
```
You: "Check for duplicate transactions"
→ Claude Code: Runs dedup logic
→ Claude Code: Flags suspicious pairs
→ Claude Code: Asks: "Merge these two?"
→ You: Confirm or skip
→ Claude Code: Updates SQLite
```

---

## Directory Structure

```
analyze-fin/
│
├── 📄 Documentation Files
│   ├── README.md                 # Architecture overview
│   ├── QUICKSTART.md             # 5-minute setup
│   ├── PROJECT_PLAN.md           # This file
│   ├── DEVELOPMENT_GUIDE.md      # Implementation prompts
│   └── SKILLS_GUIDE.md           # Skills documentation
│
├── 🔧 Setup Files
│   ├── requirements.txt          # Python dependencies (minimal)
│   ├── .gitignore                # Git ignores
│   └── initialize.sh             # Setup automation
│
├── 📁 data/                      # All local data storage
│   ├── analyze-fin.db            # SQLite database (created by init_db.py)
│   ├── merchant_mapping.json     # Merchant mappings (grows as you use)
│   ├── category_rules.json       # Categorization rules (optional)
│   ├── sample_statements/        # Your PDF statements (you provide)
│   ├── reports/                  # Generated HTML/MD reports
│   │   ├── 2025-01-report.html
│   │   └── 2025-01-summary.md
│   └── exports/                  # CSV/JSON exports
│       ├── all_transactions.csv
│       └── spending_summary.json
│
├── 📁 backend/                   # Core Python logic
│   ├── __init__.py
│   ├── models.py                 # Pydantic models (Transaction, Account, etc.)
│   ├── database.py               # SQLite CRUD operations
│   ├── statement_parser.py       # PDF extraction (pdfplumber)
│   ├── deduplicator.py           # 3-layer dedup logic
│   ├── categorizer.py            # Merchant categorization
│   ├── report_generator.py       # HTML/Markdown generation
│   └── init_db.py                # Database initialization
│
├── 📁 scripts/                   # Utility scripts (called by skills)
│   ├── parse_statement.py        # Entry point for parse-statements skill
│   ├── categorize.py             # Entry point for categorize-transactions skill
│   ├── generate_report.py        # Entry point for generate-report skill
│   ├── query_spending.py         # Entry point for query-spending skill
│   ├── export.py                 # Entry point for export-data skill
│   └── deduplicate.py            # Entry point for deduplicate skill
│
├── 📁 skills/                    # Claude Skills (primary interface)
│   ├── parse-statements/
│   │   └── SKILL.md
│   ├── categorize-transactions/
│   │   └── SKILL.md
│   ├── generate-report/
│   │   └── SKILL.md
│   ├── query-spending/
│   │   └── SKILL.md
│   ├── export-data/
│   │   └── SKILL.md
│   └── deduplicate/
│       └── SKILL.md
│
├── 📁 templates/                 # HTML/Markdown templates
│   ├── spending_report.html      # Jinja2 template for reports
│   └── markdown_report.md.j2     # Markdown template
│
├── 📁 tests/                     # Unit tests
│   ├── test_parser.py            # Test PDF parsing
│   ├── test_deduplicator.py      # Test deduplication
│   ├── test_categorizer.py       # Test categorization
│   └── conftest.py               # Pytest fixtures
│
└── 📁 .git/                      # Git repository (initialized by initialize.sh)
```

---

## Technology Stack (Minimal, Local-Only)

| Component | Technology | Why | Cost |
|-----------|-----------|-----|------|
| **Database** | SQLite | Local file, no server, perfect for this use case | Free |
| **PDF Parsing** | pdfplumber | Best for Philippine bank table formats | Free |
| **Data Validation** | Pydantic | Type safety + clean error messages | Free |
| **Data Processing** | Pandas | Easy grouping, aggregation, filtering | Free |
| **Reporting** | Jinja2 | HTML template rendering | Free |
| **Charts** | Plotly | Interactive HTML charts, no backend needed | Free |
| **Testing** | pytest | Standard Python testing framework | Free |
| **Interface** | Claude Skills | Native to Claude Code workflows | Free |

**Total Dependencies**: 8 core packages, ~100 lines in requirements.txt

**No Cloud Services**: No Supabase, no FastAPI, no Streamlit, no Railway, no external APIs

---

## Phase Breakdown: 5 Phases, ~3 Weeks

### PHASE 0: Foundation Files (Day 0 - 2 hours)

**Goal**: Create base project structure and initialize Python environment

**Deliverables**:
1. `requirements.txt` - Minimal Python dependencies
2. `.gitignore` - Standard Python ignores
3. `initialize.sh` - Automated setup script
4. Directory structure (created by initialize.sh)

**Actions**:
- `bash initialize.sh` creates venv, installs dependencies, creates directories
- Git repo initialized

**Success Criteria**:
- `source venv/bin/activate` works
- `python -c "import pdfplumber"` works
- Directory structure exists

---

### PHASE 1: Core Backend + SQLite (Days 1-3)

**Goal**: Build foundational Python modules and local SQLite database

**Deliverables**:

1. **backend/models.py** - Pydantic models
   - `Transaction`: id, date, amount, merchant_name, category, account_id
   - `Account`: id, alias, bank_type, created_at
   - `ParsedStatement`: transactions[], quality_score, parsing_issues[]
   - `MerchantCorrection`: raw_merchant, corrected_merchant, category

2. **backend/init_db.py** - Database initialization
   - Creates SQLite database: `data/analyze-fin.db`
   - Tables: accounts, statements, transactions, merchant_corrections
   - Indexes on: (household_id, date), (category), (dedup_hash)
   - Simple schema (single-user, no RLS)

3. **backend/database.py** - SQLite CRUD operations
   - `insert_account()`, `get_accounts()`
   - `insert_statement()`, `get_statements()`
   - `insert_transactions()` (batch), `get_transactions()`
   - `query_by_category()`, `query_by_date_range()`
   - Error handling and logging

4. **data/merchant_mapping.json** - Initial merchant database
   - 150+ common Philippine merchants pre-mapped
   - Format: `{"JOLLIBEE": {"normalized": "Jollibee", "category": "food"}}`
   - Includes: Jollibee, McDonald's, SM, Lazada, Shopee, Meralco, PLDT, SSS, etc.

**Success Criteria**:
- `python backend/init_db.py` creates database
- `sqlite3 data/analyze-fin.db ".tables"` shows all 4 tables
- Can insert and query transactions
- All imports work: `from backend import models, database`

**Timeline**: Days 1-3 (2-3 days)

---

### PHASE 2: Statement Parser (Days 4-7)

**Goal**: Parse PDF statements from all 4 Philippine banks

**Deliverables**:

1. **backend/statement_parser.py** - Main parser
   - `parse(pdf_path, password=None)` - Main entry point
   - `_detect_bank(pdf_text)` - Auto-detect GCash/BPI/Maya/Vybe
   - `_parse_gcash()`, `_parse_bpi()`, `_parse_maya()`, `_parse_vybe()`
   - `_normalize_date()` - Handle all date formats
   - `_normalize_amount()` - Strip ₱, handle parentheses
   - Quality scoring (0-100)
   - Error handling (password-protected, scanned, corrupted)

2. **Bank-Specific Handling**:
   - **GCash**: Table format with columns Date|Desc|Ref#|Debit|Credit|Balance
   - **BPI**: Password-protected (SURNAME + last 4 phone)
   - **Maya**: Different formats (Savings vs Wallet)
   - **Vybe**: Return helpful error message

3. **Unit tests**: tests/test_parser.py
   - Test each bank format
   - Test date normalization
   - Test amount parsing
   - Test error cases (scanned, empty, corrupt)

**Success Criteria**:
- Parse real GCash/BPI statements with >95% accuracy
- Handle password-protected PDFs
- Detect scanned PDFs and return low quality score
- All unit tests passing
- Test with sample statements (you provide)

**Timeline**: Days 4-7 (3-4 days)

---

### PHASE 3: Deduplication + Categorization (Days 8-11)

**Goal**: Smart deduplication and interactive merchant learning

**Deliverables**:

1. **backend/deduplicator.py** - 3-layer dedup
   - `find_duplicates(new_txn)` - Check reference#, content hash
   - `merge_duplicates()` - Mark as duplicate, keep primary
   - `detect_internal_transfers()` - Find mirror transactions
   - Confidence scoring
   - No false positives (conservative matching)

2. **backend/categorizer.py** - Merchant categorization
   - Load merchant_mapping.json
   - `normalize(raw_merchant)` - Clean up name
   - `categorize(merchant)` - Return category
   - Interactive prompts for unknowns (via input())
   - Learn from user corrections

3. **scripts/categorize.py** - Categorization workflow
   - Find uncategorized transactions
   - For each: prompt user, save mapping, update DB
   - Called by categorize-transactions skill

4. **Unit tests**: tests/test_dedup.py, tests/test_categorizer.py
   - Test duplicate detection
   - Test merchant normalization
   - Test categorization accuracy

**Success Criteria**:
- Import 3+ overlapping statements → zero false duplicates
- Interactive categorization works
- Merchant mappings saved to JSON
- Learning persists (test re-importing same merchant)
- All unit tests passing

**Timeline**: Days 8-11 (3-4 days)

---

### PHASE 4: Report Generation (Days 12-14)

**Goal**: Generate interactive HTML and Markdown reports

**Deliverables**:

1. **backend/report_generator.py** - Report logic
   - Query SQLite for date range
   - Calculate totals, category breakdown, top merchants
   - Generate Plotly charts (pie, line, bar)
   - Render HTML and Markdown

2. **templates/spending_report.html** - Jinja2 template
   - Bootstrap CSS (CDN)
   - Embedded Plotly charts
   - Summary cards (total in/out, net, avg daily)
   - Category breakdown table
   - Responsive design

3. **templates/markdown_report.md.j2** - Markdown template
   - Summary stats
   - Category table
   - Top merchants list
   - Date range

4. **scripts/generate_report.py** - Report generation script
   - Take month parameter (e.g., "2025-01")
   - Query SQLite for date range
   - Generate both HTML and Markdown
   - Save to `data/reports/`
   - Called by generate-report skill

**Success Criteria**:
- Generate HTML report with interactive Plotly charts
- Open in browser shows dashboard-like view
- Markdown report is readable in text editor
- All charts render correctly
- Report filenames follow pattern: `2025-01-report.html`, `2025-01-summary.md`

**Timeline**: Days 12-14 (2-3 days)

---

### PHASE 5: Claude Skills (Days 15-17) - MVP COMPLETE

**Goal**: Create all 6 Claude Skills as primary interface

**Deliverables**:

1. **skills/parse-statements/SKILL.md**
   - Invokes `scripts/parse_statement.py`
   - Prompts for file path and password
   - Returns import results (transaction count, quality score)

2. **skills/categorize-transactions/SKILL.md**
   - Invokes `scripts/categorize.py`
   - Interactive categorization workflow
   - Saves mappings to JSON

3. **skills/generate-report/SKILL.md**
   - Invokes `scripts/generate_report.py`
   - Takes month/date range parameter
   - Creates HTML + Markdown reports

4. **skills/query-spending/SKILL.md**
   - Invokes `scripts/query_spending.py`
   - Exports data to JSON
   - Claude Code loads into context, reasons about queries
   - Answers natural language questions

5. **skills/export-data/SKILL.md**
   - Invokes `scripts/export.py`
   - Exports to CSV/JSON formats
   - Saves to `data/exports/`

6. **skills/deduplicate/SKILL.md**
   - Invokes `scripts/deduplicate.py`
   - Interactive duplicate review
   - Prompts to merge or skip

7. **All supporting scripts**: `scripts/*.py`
   - `parse_statement.py` - PDF parser entry point
   - `categorize.py` - Categorization entry point
   - `generate_report.py` - Report generation entry point
   - `query_spending.py` - Data export for NL queries
   - `export.py` - CSV/JSON export
   - `deduplicate.py` - Duplicate review

**Success Criteria**:
- All 6 skills invocable from Claude Code
- End-to-end workflow works:
  1. Parse statement → SQLite
  2. Categorize merchants → JSON + SQLite
  3. Generate report → HTML in browser
  4. Query spending → Claude Code answers
  5. Export data → CSV file
  6. Find duplicates → Manual confirmation
- **MVP COMPLETE** ✅

**Timeline**: Days 15-17 (2-3 days)

---

## Database Schema

### Tables

**accounts**
- id (PRIMARY KEY)
- account_alias (TEXT) - User-friendly name (e.g., "My GCash")
- bank_type (TEXT) - GCash, BPI, MAYA, VYBE
- account_number (TEXT) - Last 4 digits or full number
- created_at (TIMESTAMP)

**statements**
- id (PRIMARY KEY)
- account_id (FK)
- file_hash (TEXT, UNIQUE) - Prevents re-importing same file
- statement_period_start (DATE)
- statement_period_end (DATE)
- total_transactions (INT)
- quality_score (INT) - 0-100
- imported_at (TIMESTAMP)
- raw_json (TEXT) - Backup of original parse result

**transactions**
- id (PRIMARY KEY)
- account_id (FK)
- statement_id (FK)
- date (TIMESTAMP)
- amount (NUMERIC) - Positive = credit, negative = debit
- balance (NUMERIC)
- raw_description (TEXT) - Original from bank
- merchant_name (TEXT) - Normalized
- merchant_category (TEXT) - Categorized
- transaction_type (TEXT) - Debit, Credit, Transfer
- reference_number (TEXT) - Bank ref# (for dedup)
- status (TEXT) - Active, Deleted, Merged
- dedup_hash (TEXT) - For content-based dedup
- is_duplicate_of (FK) - Links to primary if duplicate
- notes (TEXT) - User notes

**merchant_corrections**
- id (PRIMARY KEY)
- raw_merchant (TEXT) - Original from bank
- normalized_merchant (TEXT) - After normalization
- category (TEXT) - User-selected category
- last_corrected (TIMESTAMP)

### Indexes

- transactions(account_id, date) - Fast date range queries
- transactions(merchant_category) - Fast category queries
- transactions(dedup_hash) - Fast duplicate checks
- transactions(reference_number) - Reference-based dedup
- statements(account_id) - Account statement queries

---

## User Workflows (Skills-Based)

### Workflow 1: First Import
```
1. User: "Parse my GCash January statement"
   → parse-statements skill → imports 28 transactions

2. User: "Categorize my unknown merchants"
   → categorize-transactions skill → interactive prompts
   → user picks categories → saved to merchant_mapping.json

3. User: "Generate January report"
   → generate-report skill → creates HTML
   → opens in browser → "₱8,250 spent this month, food 30%"
```

### Workflow 2: Multi-Account Import
```
1. User: "Parse my BPI statement too"
   → imports 45 transactions (different account)

2. User: "Check for duplicates"
   → deduplicate skill → finds transfer between GCash and BPI
   → "Link these as internal transfer?" → user confirms

3. User: "Show total spending"
   → query-spending skill → "₱13,500 across both accounts"
```

### Workflow 3: Ad-Hoc Analysis
```
User: "How much food last week?"
→ query-spending skill → "₱1,250 across 12 transactions"

User: "What's my biggest spending category?"
→ query-spending skill → "Food at ₱8,500 (35% of total)"

User: "Export everything to CSV"
→ export-data skill → "Saved to data/exports/all_transactions.csv"
```

---

## What's Different from Original Plan

**Removed** (not needed locally):
- ❌ Supabase ($25/mo) → SQLite ($0)
- ❌ FastAPI backend → Python scripts ($0)
- ❌ Streamlit (web UI) → HTML reports + Claude Skills ($0)
- ❌ Anthropic Claude API ($5-10/mo) → Claude Code context ($0)
- ❌ Railway deployment ($5-10/mo) → No deployment needed
- ❌ Streamlit Cloud → No deployment needed
- ❌ Multi-user RLS policies → Single user (simpler)

**Kept** (core value):
- ✅ PDF statement parsing (all 4 banks)
- ✅ 3-layer deduplication
- ✅ Merchant learning system
- ✅ Spending analysis + charts
- ✅ Natural language queries
- ✅ Export + backup options

**Result**:
- ✅ 40% faster (3 weeks vs 5-6 weeks)
- ✅ 100% cheaper ($0 vs $20-30/month)
- ✅ 100% more private (data never leaves machine)
- ✅ 50% simpler (local-only architecture)

---

## Cost Analysis

| Component | Original Plan | New Plan |
|-----------|--------------|----------|
| **Database** | Supabase $25/mo | SQLite $0 |
| **Backend API** | FastAPI on Railway $5-10/mo | Python scripts $0 |
| **Frontend** | Streamlit Cloud (free) | HTML + Skills $0 |
| **AI/NLP** | Claude API $5-10/mo | Claude Code context $0 |
| **Deployment** | Railway ops $$ | Local (no ops) |
| **Total** | **$20-30/mo** | **$0** |

---

## Success Metrics (MVP Definition)

**After Phase 5**, you'll be able to:

✅ Parse GCash/BPI/Maya with >95% accuracy
✅ Store 500+ transactions in local SQLite
✅ Auto-categorize merchants (90%+ accuracy)
✅ Deduplicate across multiple imports (zero false positives)
✅ Generate interactive HTML reports with charts
✅ Answer natural language questions in <2 seconds
✅ Export transactions as CSV for Excel
✅ Merchant learning (categorize once, remember forever)

---

## Timeline

**Phase 0**: Day 0 (2 hours)
**Phase 1**: Days 1-3 (2-3 days)
**Phase 2**: Days 4-7 (3-4 days)
**Phase 3**: Days 8-11 (3-4 days)
**Phase 4**: Days 12-14 (2-3 days)
**Phase 5**: Days 15-17 (2-3 days)

**Total**: ~3 weeks (17 days)

---

## Next Steps

1. **Read QUICKSTART.md** - 5 minute overview
2. **Run initialize.sh** - Set up environment
3. **Gather sample statements** - Get test data
4. **Open DEVELOPMENT_GUIDE.md** - Follow Phase-by-phase prompts
5. **Ask Claude Code** - Copy exact prompts, execute one phase at a time
6. **Commit to git** - After each phase completion
7. **Test incrementally** - Verify each phase before proceeding

---

**The plan is solid. The architecture is proven. Time to build.** 🚀
