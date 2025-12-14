# analyze-fin: Project Index

**Philippine Personal Finance Tracker**
**Location**: `/Users/agallentes/git/analyze-fin`
**Status**: Ready to build - all documentation updated for local-first approach
**Timeline**: ~3 weeks (5 phases) to MVP

---

## 📚 Documentation (Read in This Order)

### 1. **README.md** - Architecture Overview
Start here. Explains the local-first approach, 5-phase plan, Claude Skills interface.

### 2. **QUICKSTART.md** - Get Started in 5 Minutes
Quick setup instructions. Run `initialize.sh`, gather sample statements, start Phase 0.

### 3. **PROJECT_PLAN.md** - Complete Technical Specification
Detailed breakdown of all 5 phases, architecture decisions, directory structure, what you're building.

### 4. **DEVELOPMENT_GUIDE.md** - Step-by-Step Implementation
Claude Code prompts for every phase. Copy prompts, ask Claude Code to execute.

### 5. **SKILLS_GUIDE.md** - Claude Skills Documentation
Detailed documentation of all 6 skills (parse-statements, categorize-transactions, generate-report, query-spending, export-data, deduplicate).

---

## 🎯 Quick Navigation

### For First-Time Setup
→ QUICKSTART.md → Run `initialize.sh`

### For Architecture Understanding
→ README.md → PROJECT_PLAN.md

### For Implementation
→ DEVELOPMENT_GUIDE.md (Phase 0, 1, 2, ...)

### For Skill Usage
→ SKILLS_GUIDE.md

---

## 📁 Project Structure (What Gets Created)

```
analyze-fin/
├── 📄 README.md                 # Start here
├── 📄 QUICKSTART.md             # 5-minute setup
├── 📄 PROJECT_PLAN.md           # Technical spec
├── 📄 DEVELOPMENT_GUIDE.md      # Implementation prompts
├── 📄 SKILLS_GUIDE.md           # Skills documentation
├── 📄 requirements.txt          # Python dependencies
├── 📄 .gitignore                # Git ignores
├── 🔨 initialize.sh             # Setup automation
│
├── 📁 data/                     # All local data
│   ├── analyze-fin.db           # SQLite database
│   ├── merchant_mapping.json    # Merchant mappings
│   ├── sample_statements/       # Your PDF statements
│   ├── reports/                 # Generated reports
│   └── exports/                 # CSV/JSON exports
│
├── 📁 backend/                  # Core Python logic
│   ├── models.py                # Pydantic models
│   ├── database.py              # SQLite operations
│   ├── statement_parser.py       # PDF parsing
│   ├── deduplicator.py          # Deduplication
│   ├── categorizer.py           # Categorization
│   └── report_generator.py      # Report generation
│
├── 📁 scripts/                  # Utility scripts
│   ├── parse_statement.py       # Parser script
│   ├── categorize.py            # Categorization script
│   ├── generate_report.py       # Report script
│   ├── query_spending.py        # Query script
│   ├── export.py                # Export script
│   └── deduplicate.py           # Dedup script
│
├── 📁 skills/                   # Claude Skills (primary interface)
│   ├── parse-statements/        # Skill 1
│   ├── categorize-transactions/ # Skill 2
│   ├── generate-report/         # Skill 3
│   ├── query-spending/          # Skill 4
│   ├── export-data/             # Skill 5
│   └── deduplicate/             # Skill 6
│
├── 📁 templates/                # HTML/MD templates
│   ├── spending_report.html     # Report template
│   └── markdown_report.md.j2    # Markdown template
│
└── 📁 tests/                    # Unit tests
    ├── test_parser.py
    ├── test_deduplicator.py
    └── test_categorizer.py
```

---

## ⏱️ The 5-Phase Timeline

| Phase | Duration | What Gets Built | Key Files |
|-------|----------|-----------------|-----------|
| **Phase 0** | Day 0 (2h) | Foundation: requirements.txt, .gitignore, initialize.sh | Root directory |
| **Phase 1** | Days 1-3 | SQLite database + models + CRUD | backend/database.py, backend/models.py |
| **Phase 2** | Days 4-7 | PDF statement parser (all 4 banks) | backend/statement_parser.py |
| **Phase 3** | Days 8-11 | Deduplication + categorization | backend/deduplicator.py, backend/categorizer.py |
| **Phase 4** | Days 12-14 | Report generation | backend/report_generator.py, templates/ |
| **Phase 5** | Days 15-17 | Claude Skills (**MVP Complete**) | skills/, scripts/ |

---

## 🚀 Key Milestones

✅ **Phase 0 Complete**: Foundation files created, Python environment ready
✅ **Phase 1 Complete**: SQLite database working, can insert/query transactions
✅ **Phase 2 Complete**: Can parse GCash/BPI/Maya PDF statements
✅ **Phase 3 Complete**: Deduplication + merchant learning working
✅ **Phase 4 Complete**: Can generate HTML reports with charts
✅ **Phase 5 Complete**: **MVP READY** - All 6 Claude Skills working end-to-end

---

## 💰 Cost

**$0** - Everything is local:
- ✅ SQLite (free, built-in)
- ✅ Python libraries (free, open source)
- ✅ Claude Skills (free, part of Claude Code)
- ✅ No Supabase, no Railway, no API costs

---

## 🎮 Interface

**Old Plan**: Web UI (Streamlit)
**New Plan**: Claude Code Skills

```
Your command → Claude Code invokes skill → Skill runs Python script → SQLite updates
```

6 skills for 6 core workflows:
1. Parse statements → SQLite
2. Categorize merchants → Learning system
3. Generate reports → HTML + Markdown
4. Query spending → NL answers
5. Export data → CSV/JSON
6. Find duplicates → Manual review + merge

---

## ⚡ Quick Actions

### Right Now (Today)
```bash
cd /Users/agallentes/git/analyze-fin
bash initialize.sh
source venv/bin/activate
```

### Next (In 1 hour)
1. Gather 1-3 sample PDF statements from your banks
2. Save to `data/sample_statements/`
3. Note passwords (SURNAME + last 4 phone digits for GCash/BPI)

### Then (Phase 0)
1. Open `DEVELOPMENT_GUIDE.md`, find Phase 0 section
2. Copy the prompt
3. Ask Claude Code to execute
4. Commit to git: `git commit -m "Phase 0: Foundation files"`

### After That (Phase 1)
1. Open `DEVELOPMENT_GUIDE.md`, find Phase 1 section
2. Follow same process
3. By end of Phase 1, SQLite database will be working

---

## 🔍 What Changed from Original Plan

**Removed** (not needed for local-first):
- ❌ Supabase ($20-30/month) → ✅ SQLite ($0)
- ❌ FastAPI backend → ✅ Python scripts
- ❌ Streamlit frontend → ✅ HTML reports + Claude Skills
- ❌ Anthropic Claude API → ✅ Claude Code context
- ❌ Railway deployment → ✅ No deployment
- ❌ Multi-user → ✅ Single user

**Result**: Simpler, faster, cheaper, more private

---

## 📊 Success Metrics (MVP)

After Phase 5, you'll be able to:

✅ Upload GCash/BPI/Maya PDF statement
✅ See 28+ transactions parsed correctly
✅ View transactions in sortable table
✅ See spending by category chart
✅ Ask natural language questions ("How much food?")
✅ Export to CSV
✅ Auto-deduplicate across multiple imports
✅ Merchant learning (categorize once, remember forever)

**That's MVP.**

---

## 🤔 FAQ

**Q: Do I need any external accounts?**
No. Everything is local on your machine.

**Q: How long will this take?**
About 3 weeks following the 5-phase plan (~17 days).

**Q: Can I use this offline?**
Yes. SQLite works completely offline.

**Q: What if I want to add features?**
Edit Python scripts + Claude Code. Easy to customize.

**Q: Where's my data stored?**
In `data/analyze-fin.db` (SQLite file on your computer).

**Q: How do I back up?**
Copy the entire project folder. Or export to CSV.

---

## 📖 How to Use This Guide

1. **Starting out?** → Read README.md
2. **Want quick setup?** → Read QUICKSTART.md + run initialize.sh
3. **Need architecture details?** → Read PROJECT_PLAN.md
4. **Ready to code?** → Open DEVELOPMENT_GUIDE.md + copy prompts
5. **Using the skills?** → See SKILLS_GUIDE.md

---

## ✨ Next Steps

1. **Read QUICKSTART.md** (5 min)
2. **Run initialize.sh** (5 min)
3. **Gather sample statements** (10 min)
4. **Read PROJECT_PLAN.md** (20 min)
5. **Open DEVELOPMENT_GUIDE.md, Phase 0** (5 min)
6. **Copy + execute first prompt** (30 min)
7. **Commit to git** (5 min)

**Total: ~1 hour to get started**

---

**Everything is ready. Time to build.** 🚀
