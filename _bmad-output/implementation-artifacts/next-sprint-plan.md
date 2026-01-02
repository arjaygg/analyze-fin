# Next Sprint Plan: CLI Commands & Module Completion

**Sprint Goal:** Enable all 6 Claude Skills to work functionally through complete CLI commands

**Created:** 2025-01-02
**Sprint Duration:** 5-7 days
**Current Completion:** 68% (15/22 stories done)
**Target Completion:** 95% (21/22 stories done, defer config system)

---

## Sprint Context

### What We Have
- ✅ All 6 Claude Skills created (conversational interface layer)
- ✅ Complete business logic (parsers, categorization, dedup, analysis)
- ✅ Solid database foundation (SQLAlchemy 2.0, migrations)
- ✅ 468 tests validating core functionality
- ✅ BPI parser works with real statement (49 transactions @ 90% quality)

### What's Missing
- ⚠️ CLI commands incomplete (only parse + query partially implemented)
- ❌ Report generation module (charts, templates, generator)
- ❌ Export module (CSV/JSON writers)
- ❌ Database persistence in parse command

### Why This Matters
**Skills won't work without CLI commands.** Users can talk to Claude, but Claude can't execute the operations because CLI endpoints are missing.

---

## Sprint Backlog (6 Work Items)

### 1. Database Persistence for Parse Command
**Story:** 4.3 (CLI Modes - Parse completion)
**Priority:** CRITICAL (Day 1)
**Effort:** 4 hours

**Tasks:**
- [ ] Remove TODO on line 194 of cli.py
- [ ] Add database session management to parse command
- [ ] Save Account records (with bank_type detection)
- [ ] Save Statement records (with file_path and quality_score)
- [ ] Save Transaction records (linked to statement)
- [ ] Test with your BPI statement (verify 49 transactions saved)
- [ ] Verify data queryable after import

**Acceptance:**
- User runs: `uv run analyze-fin parse data/input/SA20251029.pdf`
- 49 transactions saved to database
- Can query afterwards: `uv run analyze-fin query --category "Bills & Utilities"`

**Unblocks:** All Skills (need data in DB to work)

---

### 2. Export Module Implementation
**Story:** 4.1 (Data Export CSV & JSON)
**Priority:** HIGH (Day 2)
**Effort:** 6 hours

**Tasks:**
- [ ] Create `src/analyze_fin/export/exporter.py`
- [ ] Implement `DataExporter` class
- [ ] CSV writer: columns (date, merchant, category, amount, description, account)
- [ ] JSON writer: structured format with metadata
- [ ] Filter support: date_range, category, merchant, amount_min/max
- [ ] Add `export` CLI command in cli.py
- [ ] Write tests: test_exporter.py
- [ ] Test CSV opens correctly in Excel

**Acceptance:**
- User runs: `uv run analyze-fin export --format csv --output ~/test.csv`
- CSV file created with all transactions
- Opens in Excel with proper formatting
- export-data Skill becomes functional

**Dependencies:** Needs parse command completed (data in DB)

---

### 3. Report Generation Module
**Stories:** 3.4 + 3.5 (Visualization + Report Generation)
**Priority:** HIGH (Days 3-4)
**Effort:** 12 hours

**Tasks:**
- [ ] Create `src/analyze_fin/reports/charts.py`
  - [ ] ChartBuilder class with Plotly
  - [ ] build_pie_chart(category_data) → plotly.Figure
  - [ ] build_line_chart(time_series_data) → plotly.Figure
  - [ ] build_bar_chart(merchant_data) → plotly.Figure
- [ ] Create `src/analyze_fin/reports/generator.py`
  - [ ] ReportGenerator class
  - [ ] generate_html_report() using Jinja2 + charts
  - [ ] generate_markdown_report() using Jinja2
- [ ] Create `templates/reports/dashboard.html.j2`
  - [ ] HTML structure with embedded Plotly charts
  - [ ] Summary statistics section
  - [ ] Category/merchant breakdown tables
- [ ] Create `templates/reports/summary.md.j2`
  - [ ] Markdown tables for categories
  - [ ] Text-based summaries
- [ ] Add `report` CLI command in cli.py
- [ ] Write tests: test_charts.py, test_generator.py
- [ ] Test HTML opens in browser with interactive charts

**Acceptance:**
- User runs: `uv run analyze-fin report --format html`
- HTML report opens in browser
- Shows pie chart, line chart, bar chart
- All charts are interactive (hover, click)
- generate-report Skill becomes functional

**Dependencies:** Needs data in database

---

### 4. Deduplicate CLI Command
**Story:** 4.6 (CLI Features - Deduplicate)
**Priority:** MEDIUM (Day 5)
**Effort:** 4 hours

**Tasks:**
- [ ] Add `deduplicate` CLI command in cli.py
- [ ] Connect to existing DuplicateDetector
- [ ] Interactive resolution UI (show side-by-side, ask user choice)
- [ ] Apply resolutions using DuplicateResolver
- [ ] Display summary (duplicates found, resolved, kept)
- [ ] Write tests: test_cli_deduplicate.py

**Acceptance:**
- User runs: `uv run analyze-fin deduplicate`
- Shows potential duplicates with side-by-side comparison
- Prompts for resolution choice
- Marks duplicates in database
- deduplicate-transactions Skill becomes functional

**Dependencies:** Needs data in database

---

### 5. Categorize CLI Command
**Story:** 4.6 (CLI Features - Categorize)
**Priority:** MEDIUM (Day 6)
**Effort:** 4 hours

**Tasks:**
- [ ] Add `categorize` CLI command in cli.py
- [ ] Query uncategorized transactions
- [ ] Display interactive categorization prompt
- [ ] Accept user input for category selection
- [ ] Call CategoryLearner to save rules
- [ ] Apply retroactively to existing transactions
- [ ] Display progress and summary
- [ ] Write tests: test_cli_categorize.py

**Acceptance:**
- User runs: `uv run analyze-fin categorize`
- Shows uncategorized transactions
- Prompts for category
- Saves learning rules
- categorize-transactions Skill becomes functional

**Dependencies:** Needs data in database

---

### 6. Query Command Enhancement
**Story:** 3.6 (Natural Language Query - CLI completion)
**Priority:** LOW (Day 7)
**Effort:** 3 hours

**Tasks:**
- [ ] Remove placeholder code from query command (line 85-105)
- [ ] Connect to database session
- [ ] Implement actual filtering using SpendingQuery
- [ ] Format results properly (pretty, json, csv)
- [ ] Add transaction count and total
- [ ] Write additional tests
- [ ] Verify all filter combinations work

**Acceptance:**
- User runs: `uv run analyze-fin query --category "Food & Dining"`
- Returns actual transactions from database
- Shows totals and summaries
- Works with all filters
- query-spending Skill works fully (currently basic)

**Dependencies:** Needs data in database

---

## Sprint Execution Strategy

### Phase 1: Foundation (Day 1)
**Focus:** Get data into database
- Work Item #1: Database persistence
- **Result:** Can import real data

### Phase 2: Read Operations (Days 2-3)
**Focus:** Get data out of database
- Work Item #2: Export module
- Work Item #6: Query enhancement
- **Result:** Can retrieve and export data

### Phase 3: Visualization (Days 3-4)
**Focus:** Visual output
- Work Item #3: Report generation
- **Result:** Can see spending visually

### Phase 4: Polish (Days 5-7)
**Focus:** Complete the experience
- Work Item #4: Deduplication
- Work Item #5: Categorization
- **Result:** Full workflow operational

---

## Success Criteria

### Sprint Success
- [ ] All 6 Claude Skills trigger and execute successfully
- [ ] User can complete end-to-end workflow conversationally
- [ ] Real BPI statement imports, queries, reports, exports
- [ ] 21 of 22 stories complete (95%)

### MVP Success (What User Can Do)
```
Day 1: "Parse my BPI statement"
       → ✅ 49 transactions imported to database

Day 2: "How much did I spend?"
       → ✅ "You spent ₱X across Y transactions"

Day 3: "Show me a report"
       → ✅ HTML dashboard opens with charts

Day 4: "Export to CSV"
       → ✅ Data exported for Excel analysis

Day 5: "Categorize unknown merchants"
       → ✅ Interactive learning session

Day 6: "Find duplicates"
       → ✅ Duplicate detection and resolution
```

**This achieves the PRD's conversational finance interface!**

---

## Deferred Items (Post-MVP)

**Story 4.2: Configuration System**
- Can use hardcoded defaults for MVP
- Add config file support later
- Not blocking conversational experience

**Story 3.6: Enhanced NL Query**
- Basic query works via CLI
- Advanced NL understanding can improve incrementally
- Skills already provide conversational wrapper

---

## Risk Mitigation

### Risk: CLI Commands Take Longer Than Expected

**Mitigation:**
- Start with simplest (export, deduplicate)
- Use existing modules (don't reinvent)
- Defer polish features if needed

### Risk: Report Generation Complex

**Mitigation:**
- Start with basic Plotly charts
- Simple HTML template first
- Enhance visualizations post-MVP

### Risk: Testing Real Data Uncovers Issues

**Mitigation:**
- Test incrementally after each command
- Fix parser issues as discovered
- Accept <100% accuracy for MVP

---

## Definition of Done (Sprint)

**Code:**
- [ ] All 6 CLI commands implemented
- [ ] All modules complete (export, reports)
- [ ] No TODO comments in critical paths

**Testing:**
- [ ] CLI tests pass (21+ existing tests + new)
- [ ] Integration tests for new commands
- [ ] Manual testing with real BPI statement

**Documentation:**
- [ ] CLI help text complete for all commands
- [ ] Skills tested and working
- [ ] README updated with usage examples

**Tracking:**
- [ ] sprint-status.yaml updated to 95%
- [ ] Stories marked done as completed
- [ ] Retrospective captured (optional)

---

## Next Steps

**Arjay, the sprint plan is ready. You can now:**

**Option A: Start Sprint Immediately**
- Begin with Work Item #1 (Database persistence)
- Work through systematically
- Complete in 5-7 days

**Option B: Review & Refine Plan**
- Adjust priorities
- Change sequencing
- Add/remove items

**Option C: Exit Party Mode & Execute**
- Leave team discussion
- Start implementation with Dev agent
- Use sprint plan as roadmap

**What would you like to do?**