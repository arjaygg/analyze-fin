# analyze-fin: Quick Start (5 Minutes)

**Philippine Personal Finance Tracker** - Fully local, zero-cost alternative to cloud-based finance apps.

---

## What You Have

Complete project structure in `/Users/agallentes/git/analyze-fin` ready to build with Claude Code.

**Key Files**:
- `README.md` - Architecture overview
- `PROJECT_PLAN.md` - Complete 5-phase technical specification
- `DEVELOPMENT_GUIDE.md` - Step-by-step Claude Code prompts
- `initialize.sh` - Automated setup script

---

## 3-Minute Setup

### Step 1: Initialize Project
```bash
cd /Users/agallentes/git/analyze-fin
bash initialize.sh
source venv/bin/activate
```

This:
- Creates Python virtual environment
- Installs dependencies (pdfplumber, pandas, plotly, etc.)
- Creates directory structure
- Initializes SQLite database
- Sets up git repo

**No external credentials needed.** Everything is local.

### Step 2: Gather Sample Statements
```bash
# Download 1-3 PDF statements from your banks:
# - GCash (last month statement)
# - BPI (optional)
# - Maya (optional)
#
# Save to: data/sample_statements/
#
# Note the password for GCash/BPI:
# Format: SURNAME + last 4 phone digits (e.g., "reyes4356")
```

### Step 3: Verify Setup
```bash
# Check Python imports work
python -c "import pdfplumber, pandas, plotly; print('✅ Ready')"

# Check SQLite database created
sqlite3 data/analyze-fin.db ".tables"
```

### Step 4: Start Phase 1
Open `DEVELOPMENT_GUIDE.md`, find Phase 0 and Phase 1 prompts.
Copy each prompt and ask Claude Code to execute.

---

## The 5-Phase Plan (~3 Weeks)

| Phase | Timeline | What Gets Built | Your Job |
|-------|----------|-----------------|----------|
| **Phase 0** | Day 0 (2h) | Foundation files | Follow initialize.sh |
| **Phase 1** | Days 1-3 | SQLite + models | Copy prompt, review |
| **Phase 2** | Days 4-7 | PDF parser | Copy prompt, test |
| **Phase 3** | Days 8-11 | Dedup + categorization | Copy prompt, test |
| **Phase 4** | Days 12-14 | Reports | Copy prompt, test |
| **Phase 5** | Days 15-17 | Claude Skills (MVP) | Copy prompt, test |

**🎯 MVP Complete After Phase 5** (~3 weeks)

---

## Your Interface: Claude Skills

After Phase 5, you'll use these 6 skills:

```
"Parse my GCash statement"
  → Claude Code imports transactions to SQLite

"Categorize unknown merchants"
  → You pick categories, system learns

"Generate January report"
  → Creates interactive HTML dashboard

"How much food last week?"
  → Claude Code answers from local data

"Export transactions to CSV"
  → Downloads for Excel analysis

"Check for duplicates"
  → Reviews and merges duplicates
```

No web UI. Pure Claude Code workflows.

---

## Cost Reality

| Service | Cost |
|---------|------|
| Everything | **$0** |

- ✅ SQLite (free, local file)
- ✅ Python libraries (free, open source)
- ✅ Claude Skills (free, part of Claude Code)
- ✅ No Supabase, no Railway, no API costs

---

## What Makes This Different

**vs Old Plan**:
- ❌ Removed Supabase (was $25/mo) → ✅ Local SQLite ($0)
- ❌ Removed FastAPI backend → ✅ Python scripts only
- ❌ Removed Streamlit (web app) → ✅ HTML reports + Claude Skills
- ❌ Removed deployment → ✅ Everything local
- ✅ 40% faster (3 weeks vs 5-6 weeks)
- ✅ $0 cost (vs $20-30/month)
- ✅ Full privacy (data never leaves machine)

---

## FAQ

**Q: Do I need a Supabase account?**
No. Everything runs locally on your machine.

**Q: Will this work offline?**
Yes. SQLite queries run completely offline.

**Q: What about Claude API costs?**
Zero. Uses Claude Code's built-in reasoning, not separate API calls.

**Q: How do I back up my data?**
Copy the entire project folder to backup. Or export to CSV anytime.

**Q: Can I share this with family?**
Not yet (single user for MVP). Could add multi-user later.

**Q: What if I want the web UI back?**
Possible in future, but not in MVP. Focus on core features first.

---

## Next Steps

1. **Right now** (5 min):
   ```bash
   bash initialize.sh
   source venv/bin/activate
   ```

2. **In 5 min**:
   - Read PROJECT_PLAN.md
   - Gather sample statements

3. **In 10 min**:
   - Open DEVELOPMENT_GUIDE.md, Phase 0
   - Copy Claude Code prompt
   - Ask Claude Code to execute

4. **In 2 hours**:
   - Phase 0 complete
   - Foundation files created
   - Ready for Phase 1

5. **In 1-2 days**:
   - Phase 1 complete
   - SQLite database working
   - Ready for Phase 2 (PDF parsing)

---

## Phase 0 Immediate Action

Find this in DEVELOPMENT_GUIDE.md:

```
"Create these files for /Users/agallentes/git/analyze-fin:

1. requirements.txt
2. .gitignore
3. initialize.sh
..."
```

Copy it, ask Claude Code, review, commit to git.

That's Phase 0. ✅

---

## Phase 1 Next

```
"Create /Users/agallentes/git/analyze-fin/backend/init_db.py

This should initialize SQLite database with tables:
- accounts
- statements
- transactions
- merchant_corrections
..."
```

Copy, ask Claude Code, test, commit.

That's Phase 1 starting. ✅

---

## Success Looks Like

After Phase 5 (3 weeks):

✅ Can parse GCash statement → See 28 transactions in SQLite
✅ Can categorize merchants (learning system)
✅ Can generate HTML report with charts
✅ Can ask "How much food last week?" → Get answer
✅ Can export all transactions to CSV
✅ Can deduplicate across multiple imports

**That's your MVP.** Fully functional, locally owned, zero cost.

---

## Ready?

```bash
cd /Users/agallentes/git/analyze-fin
bash initialize.sh
```

Then:
```
Read PROJECT_PLAN.md (20 min)
Read DEVELOPMENT_GUIDE.md, Phase 0 (5 min)
Ask Claude Code to execute Phase 0 prompt (30 min)
Commit to git (5 min)
```

**You'll have foundation files ready in ~1 hour.**

---

**Questions? See README.md or PROJECT_PLAN.md.**

**Let's build.** 🚀
