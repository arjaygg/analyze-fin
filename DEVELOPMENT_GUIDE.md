# analyze-fin: Development Guide (Claude Code Edition)

Step-by-step instructions for building with Claude Code. **Copy each prompt exactly and ask Claude Code to execute.**

---

## How to Use This Guide

1. **Read** the phase description
2. **Copy** the Claude Code prompt (exact text in code block)
3. **Paste** into Claude Code and ask
4. **Review** generated code
5. **Test** with sample data if needed
6. **Commit** to git
7. **Move to next phase**

**Each phase should take 1-4 hours with Claude Code.**

---

## Getting Started (5 Minutes)

### 1. Initialize Project
```bash
cd /Users/agallentes/git/analyze-fin
bash initialize.sh
source venv/bin/activate
```

### 2. Verify Setup
```bash
python -c "import pdfplumber, pandas, plotly, jinja2; print('✅ All imports work')"
sqlite3 data/analyze-fin.db ".tables"  # Should be empty (no tables yet)
```

### 3. Gather Sample Statements
- Download 1-3 PDF statements from GCash, BPI, or Maya
- Save to `data/sample_statements/`
- Note password format: SURNAME + last 4 phone digits (e.g., "reyes4356")

### 4. Ready to Build
Follow phases below. Copy exact prompt, ask Claude Code.

---

## PHASE 0: Foundation Files (Day 0, 2 Hours)

**Goal**: Create requirements.txt, .gitignore, initialize.sh

**Ask Claude Code:**

```
Create foundation files for /Users/agallentes/git/analyze-fin:

1. requirements.txt with these exact packages:
pdfplumber==0.11.0
pandas==2.2.0
numpy==1.26.4
plotly==5.18.0
jinja2==3.1.2
pydantic==2.7.1
pytest==7.4.4
python-dotenv==1.0.1

2. .gitignore with:
venv/
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
data/*.db
data/sample_statements/*.pdf
data/reports/
data/exports/

3. initialize.sh that:
   - Checks for Python 3.10+
   - Creates venv with: python3 -m venv venv
   - Installs with: pip install -r requirements.txt
   - Creates directories: data/sample_statements data/reports data/exports backend scripts skills templates tests
   - Initializes git if needed
   - Prints success message and next steps

Make all files executable where needed.
```

**After Claude Code runs:**
- Review the files
- Commit: `git add . && git commit -m "Phase 0: Foundation files"`

**Verify:**
```bash
bash initialize.sh  # Should complete without errors
source venv/bin/activate
python -c "import pdfplumber; print('✅ Ready')"
```

---

## PHASE 1: Core Backend + SQLite (Days 1-3)

### Task 1.1: Create Pydantic Models

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/backend/models.py with Pydantic models:

1. Transaction model:
   - id: str (UUID)
   - account_id: str
   - date: datetime
   - amount: float
   - balance: float
   - raw_description: str
   - merchant_name: str (normalized)
   - merchant_category: str
   - reference_number: str (for dedup)
   - dedup_hash: str
   - status: str
   - notes: str (optional)

2. Account model:
   - id: str
   - account_alias: str
   - bank_type: str (GCash, BPI, MAYA, VYBE)
   - account_number: str
   - created_at: datetime

3. ParsedStatement model:
   - bank_type: str
   - transactions: List[Transaction]
   - quality_score: int (0-100)
   - parsing_issues: List[str]

4. MerchantCorrection model:
   - id: str
   - raw_merchant: str
   - normalized_merchant: str
   - category: str
   - last_corrected: datetime

5. MerchantMapping model (simple):
   - normalized: str
   - category: str

Use Pydantic v2 with Field() for descriptions. Include JSON schema examples.
```

**Verify:** `python -c "from backend.models import Transaction; print('✅ Models work')"`

### Task 1.2: Create Database Initialization

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/backend/init_db.py that:

1. Uses sqlite3 module (no ORM)
2. Creates database at: data/analyze-fin.db
3. Creates these tables (with CREATE TABLE IF NOT EXISTS):

   accounts (id TEXT PRIMARY KEY, account_alias TEXT, bank_type TEXT, account_number TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

   statements (id TEXT PRIMARY KEY, account_id TEXT, file_hash TEXT UNIQUE, statement_period_start DATE, statement_period_end DATE, total_transactions INT, quality_score INT, imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, raw_json TEXT, FOREIGN KEY(account_id) REFERENCES accounts(id))

   transactions (id TEXT PRIMARY KEY, account_id TEXT, statement_id TEXT, date TIMESTAMP, amount NUMERIC, balance NUMERIC, raw_description TEXT, merchant_name TEXT, merchant_category TEXT, reference_number TEXT, dedup_hash TEXT, status TEXT DEFAULT 'active', notes TEXT, is_duplicate_of TEXT, FOREIGN KEY(account_id) REFERENCES accounts(id), FOREIGN KEY(statement_id) REFERENCES statements(id))

   merchant_corrections (id TEXT PRIMARY KEY, raw_merchant TEXT, normalized_merchant TEXT, category TEXT, last_corrected TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

4. Create indexes on: (account_id, date), (merchant_category), (dedup_hash), (reference_number)

5. When run directly, should:
   - Create database
   - Create all tables
   - Print "Database initialized: data/analyze-fin.db"

Use proper error handling and logging.
```

**Verify:** `python backend/init_db.py && sqlite3 data/analyze-fin.db ".tables"`

### Task 1.3: Create Database CRUD Operations

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/backend/database.py with DatabaseManager class:

1. Constructor: __init__(db_path='data/analyze-fin.db')
   - Store connection
   - Enable row factory for dict-like access

2. Methods:

   insert_account(account_alias, bank_type, account_number) -> str
     Returns: account_id

   get_accounts() -> List[dict]

   insert_statement(account_id, file_hash, period_start, period_end, total_txns, quality_score, raw_json) -> str
     Returns: statement_id

   insert_transactions(statement_id, account_id, transactions: List[dict]) -> int
     transactions is list of dicts with: date, amount, balance, raw_description, merchant_name, merchant_category, reference_number
     Returns: count inserted
     Do batch insert for efficiency

   get_transactions(date_from=None, date_to=None, category=None, account_id=None) -> List[dict]

   get_transaction_by_id(txn_id) -> dict

   query_by_category(category) -> List[dict]

   update_merchant_category(txn_id, new_merchant, new_category) -> bool

   mark_as_duplicate(txn_id, duplicate_of_id) -> bool

   save_merchant_correction(raw_merchant, normalized, category) -> bool

3. Error handling:
   - Catch sqlite3 exceptions
   - Log operations
   - Return None or False on error

4. Close connection properly with __del__()

Use type hints throughout.
```

**Verify:** `python -c "from backend.database import DatabaseManager; db = DatabaseManager(); print('✅ Database works')"`

### Task 1.4: Create Merchant Mapping JSON

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/data/merchant_mapping.json with 150+ Philippine merchants:

Format:
{
  "JOLLIBEE": {"normalized": "Jollibee", "category": "food_delivery"},
  "MCDO": {"normalized": "McDonald's", "category": "food_delivery"},
  "GRAB": {"normalized": "Grab", "category": "transport"},
  ...
}

Include these merchants (grouped by category):

Food & Dining:
- JOLLIBEE, MCDO, CHOWKING, KFC, POPEYES, BONCHON, DICOS
- PIZZA HUT, MANG INASAL, NANDOS
- STARBUCKS, COFFEE BEAN, CBTL
- SHAKEYS, MAX'S, CONTI'S
- SEAFOOD MARKET, LUTONG BAHAY

Shopping:
- SM (malls), LAZADA, SHOPEE
- PUREGOLD, SAVEMORE, ROBINSONS
- HAND M, UNIQLO, FOREVER 21
- WATSON'S, WATSONS, CENTURY SQUARE

Utilities & Bills:
- MERALCO, MANILA WATER, MAYNILAD, PAGIBIG, PCHC
- PLDT, SMART, GLOBE, SUN
- GAS STATION names, TOTAL, SHELL, PETRON

Transport:
- GRAB, UBER, ANGKAS, LALAMOVE
- MRT, BUS TERMINALS, INFINITY

Financial Services:
- BPI, GCASH, MAYA, PAYPAL, WISE
- INSURANCE, STOCKS

Government:
- SSS, PHILHEALTH, PAGIBIG, BUREAU OF INTERNAL REVENUE
- VEHICLE REGISTRATION, PASSPORT

Entertainment:
- NETFLIX, SPOTIFY, STEAM, CINEPLEX, AYALA MALLS CINEMA
- KARAOKE, BARS, RESTAURANTS

Other categories:
- PHARMACY, DRUGSTORE
- HAIRCUT, SPA, GYM
- BOOKSTORE, SCHOOL

Total: 150+ merchants with proper formatting.
```

**Verify:** `python -c "import json; m = json.load(open('data/merchant_mapping.json')); print(f'✅ {len(m)} merchants loaded')"`

### Task 1.5: Commit Phase 1

```bash
git add backend/ data/merchant_mapping.json
git commit -m "Phase 1: Core backend + SQLite database + models"
```

---

## PHASE 2: Statement Parser (Days 4-7)

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/backend/statement_parser.py with StatementParser class:

1. __init__():
   - Import pdfplumber
   - Load merchant_mapping.json
   - Load category_rules.json if exists

2. parse(pdf_path: str, password: str = None) -> ParsedStatement
   - Main entry point
   - Call _detect_bank()
   - Call appropriate _parse_* method
   - Return ParsedStatement with transactions

3. _detect_bank(pdf_text: str) -> str
   - Search for 'GCash', 'Bank of Philippine', 'Maya', 'Vybe' in text
   - Return: 'GCASH', 'BPI', 'MAYA', 'VYBE', or 'UNKNOWN'

4. _parse_gcash(pdf, password) -> ParsedStatement
   - Table columns: Date and Time | Description | Reference No. | Debit | Credit | Balance
   - Date format: MM/DD/YYYY HH:MM:SS AM/PM
   - Extract tables with pdfplumber
   - Parse each row, normalize amounts/dates
   - Extract closing balance from last row
   - Return ParsedStatement

5. _parse_bpi(pdf, password) -> ParsedStatement
   - Handle password-protected PDFs (use password param)
   - Table columns: Date | Description | Reference # | Debit | Credit | Balance
   - Date format: MMM DD, YYYY (e.g., 'Dec 10, 2021')
   - Extract and parse similar to GCash
   - Return ParsedStatement

6. _parse_maya(pdf, password) -> ParsedStatement
   - Similar structure to BPI
   - Handle both Savings and Wallet formats
   - Detect format from PDF content
   - Return ParsedStatement

7. _parse_vybe(pdf) -> ParsedStatement
   - Return error: "Vybe does not provide statement exports. Please use your linked BPI statement instead."

8. Helper methods:

   _extract_table(pdf, bank_type) -> List[dict]
     - Use pdfplumber.extract_tables()
     - Handle different table layouts
     - Return list of row dicts

   _normalize_date(date_str: str, bank_type: str) -> datetime
     - GCash: MM/DD/YYYY HH:MM:SS AM/PM
     - BPI: MMM DD, YYYY
     - Maya: various formats
     - Return UTC datetime

   _normalize_amount(amount_str: str) -> float
     - Remove ₱, PHP, commas
     - Handle parentheses for debits: (1000) -> -1000
     - Return float

9. Error handling:
   - InvalidPDFError if not valid PDF
   - PasswordRequiredError if protected and no password
   - ExtractionFailedError if table extraction fails
   - Include helpful error messages

10. Quality scoring:
    - 100: Clean extraction, no issues
    - 80-99: Minor issues (truncated merchant, etc)
    - 60-79: OCR-extracted (poor quality)
    - <60: Severe issues (return error)

Use type hints, include docstrings, add logging.
```

**After Claude Code runs:**
- Review the parser
- Test with a sample statement: `python -c "from backend.statement_parser import StatementParser; p = StatementParser(); print(p._detect_bank('GCash'))"`

**Commit:**
```bash
git add backend/statement_parser.py
git commit -m "Phase 2: PDF statement parser for all 4 banks"
```

---

## PHASE 3: Deduplication + Categorization (Days 8-11)

### Task 3.1: Deduplicator

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/backend/deduplicator.py with Deduplicator class:

1. __init__(db_path='data/analyze-fin.db')
   - Connect to database
   - Load existing transactions for building index

2. _compute_hash(txn: dict) -> str
   - Hash = SHA256(date.isoformat() + str(amount) + description[:30].upper())
   - Used for content-based dedup

3. find_duplicates(new_txn: dict) -> List[tuple]
   - Check reference_number first (if exists)
   - Check dedup_hash next
   - Return list of (matching_txn_id, confidence, reason)
   - Return empty list if no matches

4. detect_internal_transfers(account_pairs: List[tuple]) -> List[dict]
   - Find mirror transactions:
     * Same amount, opposite signs
     * Between different accounts
     * Within 1-3 days apart
   - Return: [{'txn1_id': '...', 'txn2_id': '...', 'confidence': 0.95}]

5. merge_duplicates(primary_id: str, duplicate_id: str) -> bool
   - Mark duplicate_id as duplicate of primary_id
   - Update database
   - Return success

6. validate_transaction(txn: dict) -> tuple (is_valid, errors)
   - Check amount != 0
   - Check date is valid
   - Check description not empty
   - Return (bool, list of error messages)

Include error handling and logging.
```

**Verify:**
```python
from backend.deduplicator import Deduplicator
d = Deduplicator()
print('✅ Deduplicator works')
```

### Task 3.2: Categorizer

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/backend/categorizer.py with MerchantCategorizer class:

1. __init__(db_path='data/analyze-fin.db')
   - Load merchant_mapping.json
   - Load category_rules.json if exists
   - Connect to database for saving corrections

2. normalize(raw_merchant: str) -> str
   - Remove suffixes: INC, CORP, LTD, PH, MANILA, PHILIPPINES
   - Lookup in merchant_mapping
   - Return normalized name (or original if not found)
   - Do case-insensitive matching

3. categorize(merchant: str, description: str = '') -> str
   - Category options: 'food_delivery', 'groceries', 'utilities', 'transport', 'transfer', 'bills', 'shopping', 'entertainment', 'government', 'financial', 'fee', 'other'
   - Use merchant_mapping for merchant -> category lookup
   - Use regex patterns for unknowns
   - Default to 'other' if no match
   - Return category string

4. apply_user_correction(raw_merchant: str, normalized: str, category: str) -> bool
   - Save to merchant_corrections table
   - Update merchant_mapping.json
   - Return success

5. get_uncategorized_count() -> int
   - Query database for transactions with category = 'other'
   - Return count

Include error handling and logging.
```

**Verify:**
```python
from backend.categorizer import MerchantCategorizer
c = MerchantCategorizer()
print(f'Category: {c.categorize("Jollibee")}')
print('✅ Categorizer works')
```

### Task 3.3: Interactive Categorization Script

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/scripts/categorize.py that:

1. Imports from backend: database, categorizer
2. Connects to SQLite
3. Finds all uncategorized transactions (category = 'other')
4. For each transaction:
   - Display: date, amount, raw_description, normalized merchant
   - Show options: 1) Food 2) Shopping 3) Utilities 4) Transport 5) Transfer 6) Bills 7) Entertainment 8) Financial 9) Government 10) Other
   - Prompt: "Enter number: "
   - User picks category
   - Save correction to database
   - Update transaction
5. After all processed, show: "✅ Categorized X transactions"

Make it user-friendly with clear prompts and confirmations.
```

**Commit:**
```bash
git add backend/deduplicator.py backend/categorizer.py scripts/categorize.py
git commit -m "Phase 3: Deduplication + merchant categorization + interactive categorization"
```

---

## PHASE 4: Report Generation (Days 12-14)

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/backend/report_generator.py with ReportGenerator class:

1. __init__(db_path='data/analyze-fin.db')
   - Connect to database
   - Load Jinja2 environment for templates

2. query_data(date_from, date_to) -> dict
   - Query transactions for date range
   - Calculate:
     * total_in (sum of positive amounts)
     * total_out (sum of negative amounts)
     * net (in - out)
     * by_category (dict of category -> total)
     * top_merchants (list of (merchant, total) sorted by amount)
     * daily_average (net / days in range)
   - Return dict with all metrics

3. generate_html(month: str) -> str
   - Parse month (e.g., '2025-01' or '2025-01-15') to get date range
   - Query data
   - Load template: templates/spending_report.html
   - Render with Jinja2:
     * Pass: totals, by_category, top_merchants, charts (as Plotly JSON)
     * Generate Plotly charts: pie (categories), line (daily trend), bar (top merchants)
   - Save to: data/reports/{month}-report.html
   - Return filepath

4. generate_markdown(month: str) -> str
   - Query data for month
   - Format as Markdown:
     * # Spending Report {month}
     * Summary table: total in/out, net, daily avg
     * Category breakdown table
     * Top merchants list
   - Save to: data/reports/{month}-summary.md
   - Return filepath

Include error handling and logging.
```

**Create HTML Template:**

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/templates/spending_report.html as Jinja2 template:

1. HTML5 structure
2. Bootstrap 5 CSS (from CDN)
3. Head:
   - Title: "Spending Report - {{ month }}"
   - Meta tags for responsive design

4. Body:
   - Header: "Spending Report for {{ period_start }} to {{ period_end }}"
   - Summary section with 4 cards:
     * Total In: {{ total_in | currency }}
     * Total Out: {{ total_out | currency }}
     * Net: {{ net | currency }}
     * Daily Avg: {{ daily_average | currency }}

5. Charts section (use Plotly):
   - Pie chart: Spending by category
   - Line chart: Daily spending trend
   - Bar chart: Top 10 merchants

6. Footer with generated timestamp

Use Plotly CDN, embed charts as JSON.
Make responsive with Bootstrap grid.
Use Philippine peso (₱) symbol.
```

**Create Markdown Template:**

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/templates/markdown_report.md.j2 as Markdown template:

# Spending Report - {{ month }}

## Summary
- Period: {{ period_start }} to {{ period_end }}
- Total In: ₱{{ total_in }}
- Total Out: ₱{{ total_out }}
- Net: ₱{{ net }}
- Daily Average: ₱{{ daily_average }}

## Category Breakdown
| Category | Amount | % of Total |
|----------|--------|-----------|
{% for cat, amount in by_category.items() %}
| {{ cat }} | ₱{{ amount }} | {{ (amount / total_out * 100) | round(1) }}% |
{% endfor %}

## Top Merchants
{% for merchant, amount in top_merchants %}
- {{ merchant }}: ₱{{ amount }}
{% endfor %}

Generated: {{ generated_at }}
```

**Create Report Generation Script:**

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/scripts/generate_report.py that:

1. Parse command line argument: month (e.g., '2025-01')
2. Import ReportGenerator from backend
3. Create generator instance
4. Call: generate_html(month) and generate_markdown(month)
5. Get returned file paths
6. Print: "✅ Report generated: {html_path}"
7. Print: "✅ Summary generated: {md_path}"
8. Try to open HTML in browser (optional)

Make it simple and user-friendly.
```

**Commit:**
```bash
git add backend/report_generator.py templates/ scripts/generate_report.py
git commit -m "Phase 4: Report generation with HTML and Markdown templates"
```

---

## PHASE 5: Claude Skills (Days 15-17) - MVP COMPLETE

### Task 5.1: Create All 6 Skills

**For each skill, create a SKILL.md file.**

**Skill 1: parse-statements**

**Ask Claude Code:**

```
Create /Users/agallentes/git/analyze-fin/skills/parse-statements/SKILL.md

Content:
# parse-statements

## Description
Parse a PDF bank statement and import transactions to SQLite

## How to use
"Parse my GCash statement from January"

## What happens
- Prompts for file path
- Prompts for password (if needed)
- Parses PDF with pdfplumber
- Imports transactions to SQLite
- Returns import results

## Implementation
Call: scripts/parse_statement.py <file_path> [password]
```

**Skill 2: categorize-transactions**

```
Create /Users/agallentes/git/analyze-fin/skills/categorize-transactions/SKILL.md

Content:
# categorize-transactions

## Description
Interactive merchant categorization with learning

## How to use
"Categorize my uncategorized merchants"

## What happens
- Finds unknown merchants
- For each: prompts for category
- Saves to merchant_mapping.json
- Updates SQLite
- Shows results

## Implementation
Call: scripts/categorize.py
```

**Skill 3: generate-report**

```
Create /Users/agallentes/git/analyze-fin/skills/generate-report/SKILL.md

Content:
# generate-report

## Description
Generate spending report (HTML + Markdown)

## How to use
"Generate my January spending report"

## What happens
- Queries SQLite for date range
- Creates interactive HTML dashboard
- Creates Markdown summary
- Opens HTML in browser

## Implementation
Call: scripts/generate_report.py 2025-01
```

**Skill 4: query-spending**

```
Create /Users/agallentes/git/analyze-fin/skills/query-spending/SKILL.md

Content:
# query-spending

## Description
Answer natural language questions about spending

## How to use
"How much food last week?"
"Top spending categories?"
"How much transport?"

## What happens
- Loads transaction data into context
- Uses Claude Code reasoning
- Answers in natural language

## Implementation
Call: scripts/query_spending.py
Loads data into JSON, Claude Code analyzes
```

**Skill 5: export-data**

```
Create /Users/agallentes/git/analyze-fin/skills/export-data/SKILL.md

Content:
# export-data

## Description
Export transactions to CSV or JSON

## How to use
"Export all transactions to CSV"
"Export January to JSON"

## What happens
- Queries SQLite
- Converts to requested format
- Saves to data/exports/

## Implementation
Call: scripts/export.py [format] [month]
```

**Skill 6: deduplicate**

```
Create /Users/agallentes/git/analyze-fin/skills/deduplicate/SKILL.md

Content:
# deduplicate

## Description
Find and merge duplicate transactions

## How to use
"Check for duplicates"

## What happens
- Runs deduplication logic
- Flags suspicious pairs
- Prompts to merge or skip

## Implementation
Call: scripts/deduplicate.py
```

### Task 5.2: Create Supporting Scripts

**Ask Claude Code:**

```
Create all 6 scripts in /Users/agallentes/git/analyze-fin/scripts/:

1. parse_statement.py
   - Arguments: <file_path> [password]
   - Calls: backend.statement_parser.parse()
   - Calls: database.insert_statement() and insert_transactions()
   - Returns: "✅ Imported {N} transactions, quality: {score}"

2. categorize.py
   - No arguments
   - Calls: scripts/categorize.py logic (already created)
   - Interactive prompts

3. generate_report.py
   - Arguments: <month> (e.g., 2025-01)
   - Calls: backend.report_generator.generate_html() and generate_markdown()
   - Returns file paths

4. query_spending.py
   - Arguments: <question>
   - Exports SQLite data to JSON
   - Passes to Claude Code context
   - Returns answer

5. export.py
   - Arguments: <format> [month]
   - format: csv or json
   - month: optional (2025-01)
   - Saves to data/exports/

6. deduplicate.py
   - No arguments
   - Queries database for potential duplicates
   - Prompts user: "Merge these transactions?"
   - Updates database

All scripts should:
- Have error handling
- Print success/error messages
- Be called from skills
```

**Commit:**
```bash
git add skills/ scripts/
git commit -m "Phase 5: Claude Skills + all supporting scripts - MVP COMPLETE"
```

---

## Phase Completion Checklist

### Phase 0
- [ ] requirements.txt created
- [ ] .gitignore created
- [ ] initialize.sh works
- [ ] Committed to git

### Phase 1
- [ ] Models created (Transaction, Account, etc.)
- [ ] Database initialized (data/analyze-fin.db)
- [ ] Database CRUD operations work
- [ ] Merchant mapping JSON loaded
- [ ] Committed to git

### Phase 2
- [ ] Statement parser works for GCash
- [ ] Statement parser works for BPI
- [ ] Statement parser works for Maya
- [ ] Parser handles password-protected PDFs
- [ ] Parser handles error cases
- [ ] Tested with real sample statement
- [ ] Committed to git

### Phase 3
- [ ] Deduplicator detects duplicates
- [ ] Categorizer normalizes merchants
- [ ] Categorizer categorizes merchants
- [ ] Interactive categorization script works
- [ ] Merchant mappings saved to JSON
- [ ] Committed to git

### Phase 4
- [ ] Report generator queries data
- [ ] HTML report generates
- [ ] Markdown report generates
- [ ] Reports open in browser
- [ ] Plotly charts render
- [ ] Committed to git

### Phase 5
- [ ] All 6 skills created
- [ ] All 6 scripts created and working
- [ ] End-to-end workflow:
  1. Parse statement → SQLite ✅
  2. Categorize merchants ✅
  3. Generate report → browser ✅
  4. Query spending ✅
  5. Export to CSV ✅
  6. Find duplicates ✅
- [ ] **MVP COMPLETE** ✅
- [ ] Committed to git

---

## Testing Workflow

After each phase:

```bash
# Test imports
python -c "from backend import models, database; print('✅ OK')"

# Run sample parser test (Phase 2+)
python -c "from backend.statement_parser import StatementParser; print('✅ OK')"

# Test with real sample
python scripts/parse_statement.py data/sample_statements/gcash_jan.pdf reyes4356

# Generate report
python scripts/generate_report.py 2025-01

# Check git status
git status
git log --oneline -3
```

---

## Troubleshooting

**Python import errors:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**SQLite database errors:**
```bash
python backend/init_db.py  # Reinitialize
```

**PDF parsing issues:**
- Check PDF is not scanned (is it text-based?)
- Verify password format: SURNAME + last 4 phone digits
- Check bank format matches GCash/BPI/Maya

**Skill not working:**
- Verify script is executable: `chmod +x scripts/*.py`
- Check imports: `python scripts/script_name.py`
- Verify Claude Code can invoke the skill

---

## Success Indicators

✅ Phase 0: `python -c "import pdfplumber"` works
✅ Phase 1: `sqlite3 data/analyze-fin.db ".tables"` shows 4 tables
✅ Phase 2: Parser extracts 28+ transactions from real statement
✅ Phase 3: Categorization saves to JSON and updates DB
✅ Phase 4: Report opens in browser with charts
✅ Phase 5: Can use all 6 skills from Claude Code

---

**All set. Time to build.** 🚀
