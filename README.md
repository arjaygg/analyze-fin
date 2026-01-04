# analyze-fin: Philippine Finance Tracker (Local-First)

**Location**: `/Users/agallentes/git/analyze-fin`
**Status**: Ready to build with Claude Code
**Timeline**: ~3 weeks (5 phases) to fully functional MVP
**Cost**: $0 (fully local, zero external dependencies)
**Architecture**: SQLite + Claude Skills + HTML Reports

---

## What You're Building

A **statement-based personal finance tracker** for Philippine users who use multiple accounts (BPI, GCash, Maya, Vybe).

**Problem**: Tracking spending across 2-4 financial accounts is manual and error-prone.

**Solution**: Upload PDF statements → Automatic parsing → Smart categorization → Unified spending insights.

### Core Features

✅ **Multi-bank PDF parsing** - GCash, BPI, Maya statements (95%+ accuracy)
✅ **Smart deduplication** - Handle overlapping statements, detect internal transfers
✅ **Merchant learning** - Unknown merchants → You categorize → System remembers
✅ **Spending dashboard** - HTML reports with interactive Plotly charts
✅ **Natural language queries** - "How much food last week?" (via Claude Code context)
✅ **Local data** - SQLite database stays on your computer, never cloud-synced
✅ **Export options** - Download transactions as CSV/JSON anytime

---

## Why Local-First?

**Privacy**: Your financial data never leaves your machine
**Cost**: Zero external services ($0/month vs $20-30/month for cloud)
**Speed**: Local SQLite queries are instant
**Ownership**: Full control over your data
**Simplicity**: No Supabase, no FastAPI, no Streamlit Cloud account needed

---

## The 5-Phase Plan

| Phase | Timeline | What Gets Built | Status |
|-------|----------|-----------------|--------|
| **Phase 0** | Day 0 (2h) | Foundation files (requirements.txt, .gitignore, initialize.sh) | Setup & config |
| **Phase 1** | Days 1-3 | Core backend: SQLite database, Pydantic models, CRUD operations | Ready to code |
| **Phase 2** | Days 4-7 | Statement parser: PDF extraction for all 4 banks | Ready to code |
| **Phase 3** | Days 8-11 | Dedup + categorization: Smart merchant learning + deduplication | Ready to code |
| **Phase 4** | Days 12-14 | Report generation: HTML + Markdown reports with Plotly charts | Ready to code |
| **Phase 5** | Days 15-17 | **MVP Complete**: 6 Claude Skills for end-to-end workflows | Ready to code |

**🎯 MVP Ready After Phase 5** (~3 weeks)

---

## Your Interface: Claude Skills

Instead of clicking a web UI, you interact with the app via Claude Code skills:

### Skill 1: `parse-statements` (Unified Workflow)
```
You: "Parse my GCash statement from January"
Claude Code: Prompts for file path → Parses PDF → Auto-categorizes → Checks duplicates
Result: "✅ Imported 28 transactions, categorized 24 (86%), no duplicates"
```

The parse workflow now automatically:
- **Parses** - Extracts transactions from PDF
- **Saves** - Stores to SQLite database
- **Categorizes** - Auto-categorizes using merchant database
- **Checks duplicates** - Warns about potential duplicates (non-destructive)

Power users can skip steps with `--no-auto-categorize` or `--no-check-duplicates`.

### Skill 2: `generate-report`
```
You: "Generate my January spending report"
Claude Code: Queries SQLite → Creates HTML + Markdown
Result: "✅ Report saved to data/reports/2025-01-report.html"
```

### Skill 3: `query-spending`
```
You: "How much did I spend on food last week?"
Claude Code: Loads SQLite data into context → Uses reasoning
Result: "₱1,250 across 12 transactions"
```

### Skill 4: `export-data`
```
You: "Export all transactions to CSV"
Claude Code: Queries SQLite → Writes to CSV
Result: "✅ Exported 156 transactions"
```

### CLI Commands (for power users)
```bash
# Manual categorization review
analyze-fin categorize

# Manual duplicate review
analyze-fin deduplicate
```

---

## Project Structure

```
analyze-fin/
├── data/                         # All local data
│   ├── analyze-fin.db            # SQLite database (created on init)
│   ├── merchant_mapping.json     # Local merchant mappings
│   ├── sample_statements/        # Test PDFs (you provide)
│   ├── reports/                  # Generated HTML/MD reports
│   └── exports/                  # CSV/JSON exports
│
├── backend/                      # Python core logic
│   ├── models.py                 # Pydantic models
│   ├── database.py               # SQLite operations
│   ├── statement_parser.py       # PDF parsing (Phase 2)
│   ├── deduplicator.py           # Dedup logic (Phase 3)
│   ├── categorizer.py            # Merchant categorization (Phase 3)
│   └── report_generator.py       # HTML/MD generation (Phase 4)
│
├── scripts/                      # Scripts called by skills
│   ├── parse_statement.py
│   ├── categorize.py
│   ├── generate_report.py
│   ├── query_spending.py
│   ├── export.py
│   └── deduplicate.py
│
├── skills/                       # Claude Skills (primary interface)
│   ├── parse-statements/         # Unified: parse + categorize + dedup
│   ├── generate-report/
│   ├── query-spending/
│   └── export-data/
│
├── templates/                    # HTML/Markdown templates
│   ├── spending_report.html      # Jinja2 template for reports
│   └── markdown_report.md.j2
│
├── tests/                        # Unit tests
├── requirements.txt              # Python dependencies (minimal, local-only)
├── .gitignore                    # Git ignores
└── initialize.sh                 # Setup script
```

---

## Quick Start (5 minutes)

### 1. Initialize Project
```bash
cd /Users/agallentes/git/analyze-fin
bash initialize.sh
source venv/bin/activate
```

This:
- Creates Python virtual environment
- Installs minimal dependencies (pdfplumber, pandas, plotly, jinja2, sqlite3)
- Sets up directory structure
- Initializes git repo
- Creates empty SQLite database

### 2. Gather Sample Statements
Place 1-3 sample PDF statements in `data/sample_statements/`:
- GCash statement (password: SURNAME + last 4 phone digits)
- BPI statement (optional)
- Maya statement (optional)

### 3. Start Phase 1
Read DEVELOPMENT_GUIDE.md, Phase 1:
- Copy Claude Code prompt
- Ask Claude Code to implement
- Review generated code
- Commit to git

---

## Key Technologies

| Component | Technology | Why |
|-----------|-----------|-----|
| PDF Parsing | pdfplumber | Best for Philippine bank formats |
| Database | SQLite | Local file-based, no server needed |
| Data Models | Pydantic | Type safety + validation |
| Reports | Jinja2 + Plotly | Interactive HTML charts |
| Testing | pytest | Standard Python testing |
| Interface | Claude Skills | Native to Claude Code workflow |

---

## What's NOT Included (Intentionally Removed)

❌ **Supabase** - Replaced with local SQLite
❌ **FastAPI** - No REST API needed (data stays local)
❌ **Streamlit** - Replaced with HTML reports + Claude Skills
❌ **Anthropic Claude API** - Using Claude Code's built-in reasoning instead
❌ **Railway deployment** - No deployment needed (fully local)
❌ **Multi-user support** - Single-user local app (easier, faster)

**Result**: Simpler, faster, cheaper, more private.

---

## Success Metrics (MVP)

After Phase 5, you'll have:

✅ Parse GCash/BPI/Maya statements with >95% accuracy
✅ Store 500+ transactions in local SQLite
✅ Auto-categorize merchants with 90%+ accuracy
✅ Deduplicate across multiple statement imports (zero false positives)
✅ Generate interactive HTML reports with spending charts
✅ Answer natural language questions via Claude Code context
✅ Export transactions as CSV for Excel analysis

---

## Documentation Files

**Start here:**
1. **QUICKSTART.md** - 5-min overview + immediate next steps
2. **PROJECT_PLAN.md** - Complete technical specification (5 phases)
3. **DEVELOPMENT_GUIDE.md** - Step-by-step Claude Code prompts per phase

**Reference:**
4. **This README** - Architecture overview

---

## Dependencies (Minimal)

All in `requirements.txt`:
- **pdfplumber** - PDF table extraction
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **plotly** - Interactive charts
- **jinja2** - HTML template rendering
- **pydantic** - Data validation
- **pytest** - Testing
- **python-dotenv** - Config management

**That's it.** No cloud SDKs, no API clients, no heavy frameworks.

Install with: `pip install -r requirements.txt`

---

## Git Workflow

```bash
# After Phase 0 foundation:
git add .
git commit -m "Phase 0: Foundation files"

# After each phase:
git commit -m "Phase X: [Description]"

# By end of Phase 5:
git log --oneline  # Should show 5-6 commits
```

---

## Claude Code Workflow

For each task:

1. **Read prompt** in DEVELOPMENT_GUIDE.md
2. **Ask Claude Code** the exact prompt
3. **Review code** (usually 90%+ correct)
4. **Test locally** with sample data
5. **Commit** to git
6. **Move to next task**

Most tasks take 1-2 hours this way.

---

## Cost Reality

| Service | Cost | Notes |
|---------|------|-------|
| **TOTAL** | **$0** | Everything local, zero external services |

No Supabase, no Claude API calls, no Railway, no Streamlit Cloud.

---

## Advantages vs Original Plan

| Aspect | Old Plan | New Plan |
|--------|----------|----------|
| **Cost** | $20-30/month | **$0** |
| **Timeline** | 5-6 weeks | **~3 weeks** |
| **Complexity** | High (cloud + web) | **Low (local only)** |
| **Privacy** | Data in Supabase | **Data on your machine** |
| **Interface** | Web UI (browser) | **Claude Skills (CLI)** |
| **Users** | Multi-user | **Single user** |
| **Deployment** | Railway + Streamlit Cloud | **None (local)** |

---

## Ready to Start?

```bash
# Step 1: Initialize
cd /Users/agallentes/git/analyze-fin
bash initialize.sh
source venv/bin/activate

# Step 2: Gather sample statements
# Place 1-3 PDFs in data/sample_statements/

# Step 3: Read quick start
cat QUICKSTART.md

# Step 4: Start Phase 1
# Open DEVELOPMENT_GUIDE.md, Phase 1
# Copy Claude Code prompt
# Ask Claude Code to execute
```

**You'll have your first working statement parser in 1-2 days.**

---

## Questions?

1. **How do I...?** → See QUICKSTART.md
2. **Technical details** → See PROJECT_PLAN.md
3. **Step-by-step prompts** → See DEVELOPMENT_GUIDE.md
4. **Stuck?** → Ask Claude Code, it's your development partner

---

**Status**: All documentation aligned with approved plan.
**Ready to build**: Start Phase 0 (initialize.sh).
**Expected MVP**: ~3 weeks from now.

Let's go. 🚀
