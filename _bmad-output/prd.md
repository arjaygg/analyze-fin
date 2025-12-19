---
stepsCompleted: [1, 2, 3, 4, 6, 7, 8, 9, 10]
inputDocuments: []
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 0
  projectDocs: 0
workflowType: 'prd'
lastStep: 11
project_name: 'analyze-fin'
user_name: 'arjay'
date: '2025-12-14'
---

# Product Requirements Document - analyze-fin

**Author:** arjay
**Date:** 2025-12-14

## Executive Summary

**analyze-fin** is a Philippine-specific personal finance tracker that transforms the manual burden of tracking spending across multiple financial accounts into an automated, intelligent system. Filipino consumers typically juggle 2-4 different accounts (BPI for salary, GCash for payments, Maya for savings, Vybe for credit), making it nearly impossible to understand their complete financial picture without hours of manual spreadsheet work.

The product addresses this through statement-based PDF parsing - users simply upload their monthly bank statements and the system automatically extracts, categorizes, deduplicates, and analyzes transactions across all accounts. Unlike traditional finance apps that require manual transaction entry or rely on non-existent bank APIs in the Philippines, analyze-fin works with what users already have access to: PDF statements downloaded from their banking apps.

Built as a local-first application with Claude Skills as the primary interface, all financial data stays on the user's machine in a SQLite database. There are no cloud dependencies, no monthly fees, and complete transparency over personal financial information. The system learns from user corrections, improving merchant categorization accuracy over time.

**Target Users:**
- **Primary:** Filipino professionals and families using multiple accounts who want spending visibility and control
- **Secondary:** Small business owners needing expense tracking for tax filing
- **Tertiary:** Developers/power users wanting batch processing capabilities

### What Makes This Special

**Philippine-Specific Intelligence:** Unlike generic finance trackers, analyze-fin is purpose-built for Philippine banks (GCash, BPI, Maya, Vybe) with 150+ pre-mapped local merchants (Jollibee, SM, Lazada, Meralco, etc.) and understanding of local statement formats.

**Statement-Based Approach:** Solves the fundamental constraint that Philippine banks don't provide personal account APIs. By parsing PDFs, it works within what's actually available while remaining legal and safe (avoiding terms-of-service violations from screen scraping).

**Local-First Architecture:** Complete data privacy and ownership - financial data never leaves the user's machine. Zero monthly costs, no vendor lock-in, full transparency through local SQLite storage.

**Claude Skills Integration:** Natural command-based workflow that fits into Claude Code sessions rather than requiring a separate web application. "Parse my January GCash statement" → done. "How much did I spend on food last week?" → instant answer.

**Intelligent Learning System:** Merchant categorization improves with use. Correct "JOLLIBEE MANILA INC" once, and all similar transactions (JB, JOLLIBEE QC, etc.) automatically normalize to "Jollibee" with proper food category.

## Project Classification

**Technical Type:** CLI Tool / Developer Tool (Claude Skills-driven interface with Python backend)

**Domain:** Fintech (Personal Finance)

**Complexity:** Medium-to-High
- Lighter regulatory burden than typical fintech (personal use, read-only, not a financial service provider)
- Still requires careful handling of sensitive financial data and privacy compliance (RA 10173)

**Project Context:** Greenfield - new project

**Key Compliance Considerations:**
- ✅ No payment processing or KYC/AML requirements (personal tool, not handling transactions)
- ✅ Statement parsing is legal and safe approach
- ⚠️ Must implement data privacy best practices and secure local storage
- ⚠️ Philippine Data Privacy Act (RA 10173) principles apply to personal data handling

## Success Criteria

### User Success

**Primary User (Filipino Professionals & Families):**
- **"Aha!" Moment:** First-time user imports 3 statements (GCash, BPI, Maya) and immediately sees unified spending dashboard showing "You spent ₱42,000 this month: Food ₱8,500 (35%), Shopping ₱5,200..." - complete financial picture in under 5 seconds
- **Immediate Value:** Discovers spending patterns they couldn't see before ("I didn't realize I spent ₱250/day on coffee")
- **Behavioral Change:** After 1 month, user has evidence-based insights to make budgeting decisions ("Food is my top category, I should track this more carefully")
- **Workflow Replacement:** Stops manually tracking in spreadsheets - analyze-fin becomes the single source of truth for financial visibility
- **Query Satisfaction:** Can ask natural questions ("How much transport last week?") and get instant answers without digging through statements

**Secondary User (Small Business Owners):**
- Successfully track business expenses across personal accounts for tax filing
- Generate monthly reports for accountant in 1 click
- Categorize business vs personal transactions with notes

**Tertiary User (Developers/Power Users):**
- Batch process 20+ PDFs in single command for historical analysis
- Export to CSV for custom analysis in Excel/Python
- Pre-validate statement quality before importing

### Business Success

**Personal Project Success (3 Months - MVP):**
- Tool is actively used monthly for personal finance tracking
- Replaced manual spreadsheet workflow completely
- Processing 3-4 statements per month (GCash, BPI, Maya) consistently
- Spending insights lead to at least one concrete budgeting decision

**Adoption Success (12 Months - If Shared):**
- Shared with 5-10 friends/family members who successfully use it
- Word-of-mouth validation: "This actually works for Philippine banks"
- Community contribution: Users share merchant mappings to improve categorization
- Zero cost maintained: Fully local, no cloud infrastructure needed

**Long-term Vision:**
- Becomes go-to solution for Filipino developers wanting to track personal finances
- GitHub repository with active community contributions
- Potential extension to business/tax use cases

### Technical Success

**Parsing Accuracy:**
- >95% transaction extraction accuracy across all supported banks
- Measured by: Manual verification of 100-transaction sample statements
- Quality score system (0-100) accurately reflects statement parse confidence
- Handles edge cases: password-protected PDFs, date format variations, multi-page statements

**Categorization Accuracy:**
- >90% auto-categorization accuracy (only 10% require manual review)
- Merchant normalization works: "JOLLIBEE MANILA INC" → "Jollibee" consistently
- Learning system: User corrections persist and apply to future transactions
- 150+ Philippine merchants pre-mapped and validated

**Deduplication Reliability:**
- Zero false positives: Never marks different transactions as duplicates
- >95% duplicate detection: Catches overlapping statement imports
- Internal transfer detection: Correctly links mirror transactions between own accounts
- 3-layer matching system validated across realistic test cases

**Performance:**
- PDF parsing: 28 transactions extracted in <10 seconds
- Dashboard generation: Complete HTML report in <5 seconds
- Natural language queries: <2 second response time
- Query processing: 500+ transactions analyzed instantly

**Data Integrity:**
- Zero transaction loss during import (100% capture rate)
- SQLite database maintains referential integrity
- Merchant mappings persist correctly across sessions
- Reports accurately reflect underlying transaction data

**Multi-Bank Support:**
- GCash: Full support for transaction tables (MM/DD/YYYY HH:MM:SS AM/PM format)
- BPI: Password-protected PDF handling (SURNAME + last 4 digits)
- Maya: Both Savings and Wallet statement formats supported
- Vybe: Clear user guidance to linked BPI statement

### Measurable Outcomes

**Week 3 (MVP Complete):**
- All 6 Claude Skills functional (parse, categorize, generate-report, query, export, deduplicate)
- Successfully imported 3 real statements with >95% accuracy
- Generated first complete monthly spending report with charts
- Answered 5 natural language queries correctly

**Month 3 (Active Use):**
- Processed 9-12 statements (3-4 months of data)
- Merchant mapping library grown to 200+ entries from corrections
- Spending insights used in at least 2 concrete budgeting decisions
- Zero manual spreadsheet tracking needed

**Month 12 (Established Tool):**
- 12 months of historical financial data in local SQLite
- Trend analysis working: "Spending up 10% from last month"
- If shared: 5-10 active users beyond creator
- System reliability: No data loss incidents, consistent parsing accuracy

## Product Scope

### MVP - Minimum Viable Product (3 Weeks)

**Foundation (Week 1: Days 0-3):**
- ✅ Foundation files: requirements.txt, .gitignore, initialize.sh
- ✅ SQLite database initialization (accounts, statements, transactions, merchant_corrections tables)
- ✅ Core backend modules (models.py, database.py, init_db.py)
- ✅ Initial merchant_mapping.json with 150+ Philippine merchants

**Core Parsing (Week 2: Days 4-11):**
- ✅ PDF statement parser for GCash, BPI, Maya
- ✅ Password handling for BPI statements
- ✅ Quality scoring system (0-100 confidence)
- ✅ Deduplication engine (3-layer: reference #, content hash, user review)
- ✅ Interactive categorization with learning system
- ✅ Merchant normalization logic

**Interface & Reports (Week 3: Days 12-17):**
- ✅ All 6 Claude Skills implemented (parse-statements, categorize-transactions, generate-report, query-spending, export-data, deduplicate)
- ✅ HTML report generation with Plotly charts (pie, line, bar charts)
- ✅ Markdown reports for text viewing
- ✅ Natural language query support via Claude Code context
- ✅ CSV export functionality

**MVP Success Gate:** End-to-end workflow works: Import PDF → Categorize → Generate Report → Query spending

### Growth Features (Post-MVP, Months 2-6)

**Enhanced Analysis:**
- Advanced behavioral insights (spending frequency patterns, anomaly detection)
- Multi-month trend analysis with comparative charts
- Budget tracking and alerts (set spending limits per category)
- Forecasting: "Based on trends, you'll spend ₱45,000 next month"

**Improved Categorization:**
- AI-powered categorization for unknown merchants (optional Claude API integration)
- Category rules engine (regex patterns, merchant patterns)
- Split transactions (single transaction across multiple categories)
- Custom category creation

**Better Reports:**
- Multiple report templates (monthly summary, tax prep, business expenses)
- PDF report export (not just HTML)
- Scheduled report generation
- Email/notification integration for monthly summaries

**Enhanced Deduplication:**
- Visual UI for reviewing potential duplicates
- Bulk duplicate operations
- Merge suggestions with confidence scores
- Historical duplicate review and correction

### Vision (Future, 12+ Months)

**Multi-User Support:**
- Household accounts: Multiple users sharing financial data
- Permission system: Who can see which accounts
- Family spending dashboards
- Shared merchant mappings across users

**Advanced Features:**
- Receipt photo parsing (OCR) to complement statement data
- Mobile app for quick statement uploads on-the-go
- Budget planning tools with goal tracking
- Integration with tax filing tools (BIR Form 1701 prep)

**Community & Ecosystem:**
- Public merchant mapping database (crowd-sourced)
- Plugin system for custom analyzers
- API for third-party integrations
- Template marketplace for custom reports

**Business Evolution:**
- Small business bookkeeping features
- Multi-currency support for OFWs (Overseas Filipino Workers)
- Bank account balance tracking over time
- Financial advisor integration (export for professional review)

## User Journeys

**Journey 1: Marco Villanueva - The End-of-Month Panic**

Marco is a 29-year-old software developer earning ₱85,000 monthly. On paper, he should be comfortable. In reality, every 25th of the month brings the same dread: checking his accounts and finding barely enough for rent. He's not buying luxury items. He doesn't have expensive vices. Yet somehow, between his BPI salary account, GCash for daily transactions, and Maya for online purchases, the money just... evaporates.

The stress compounds. He wants to save for a condo down payment, but after 2 years of "trying to save," he has ₱40,000 in savings - pathetic for someone at his income level. His parents ask when he's getting his own place. He has no answer.

One evening, instead of doom-scrolling through his banking apps, Marco downloads his October statements and drops them into Claude Code: "Parse these and show me where my money went."

Fifteen seconds later, the truth hits. Transportation: ₱12,400. He knew Grab was expensive, but seeing it as 15% of his spending - that's a wake-up call. Subscriptions: ₱4,800. Netflix, Spotify, YouTube Premium, Adobe, gym membership he hasn't used since June. Food delivery: ₱9,200. Not restaurants with friends - solo GrabFood orders because he was "too tired to cook."

Marco doesn't need a budget app lecturing him. He needed evidence. Now he has it. He cancels three subscriptions, commits to cooking twice a week, and takes the MRT when it's not rush hour. Two months later, he's saving ₱15,000/month consistently. The condo fund is actually growing.

---

**Journey 2: The Reyeses - Ending the Money Fights**

Paolo and Jen Reyes have been married three years. They both work - he's in sales (₱70,000 + commissions), she's a nurse (₱55,000 + overtime). Combined income over ₱130,000, yet they fight about money constantly. "You spent how much on gadgets?" "Well, you keep buying clothes!" Neither has visibility into the other's spending, and neither trusts the other's accounting.

The fights follow a pattern: something triggers it (a credit card bill, an unexpected expense), accusations fly, both get defensive, nothing gets resolved. They've tried shared spreadsheets - abandoned after 2 weeks. Budget apps - she downloaded one, he never opened it.

Jen discovers analyze-fin during a Reddit thread about Filipino personal finance. She proposes a deal to Paolo: "Let's both upload our statements. No accusations. Just look at the data together."

Saturday morning, coffee in hand, they import 4 statements: Paolo's BPI and GCash, Jen's BDO and Maya. For the first time, they see their *combined* financial picture. Total household spending: ₱98,000. The breakdown is revealing - and surprisingly, neither is the villain they'd imagined.

Food (combined): ₱28,000. "Wait, we both order GrabFood separately on nights we think the other is eating out?" Transport (Paolo): ₱14,000. "Your Grab is high, but... you do visit clients." Shopping (Jen): ₱8,500. "That's actually less than I thought you spent."

The real culprit? Uncoordinated spending. They're both buying groceries without checking if the other already did. Both paying for streaming services they barely use. Both ordering delivery on nights they could've eaten together.

The conversation shifts. Instead of "you spend too much," it becomes "we should coordinate better." They set up a simple system: Saturday morning statement uploads, 20-minute review over breakfast. The fights stop. Not because they're spending less - because they finally understand where the money goes, together.

---

**Journey 3: Mia Tan - The Claude-Powered Analyst**

Mia is a 34-year-old product manager who lives in spreadsheets and dashboards at work. She's always wanted that same level of insight into her personal finances, but the manual effort never seemed worth it. She has 3 years of statements saved "just in case" - 40+ PDFs across BPI, GCash, and Maya - but they've never been analyzed.

When she discovers analyze-fin works through Claude Code, something clicks. This isn't just a finance tool - it's an AI-powered analysis environment she can *converse* with.

She batch-imports all 40 statements over lunch. By dinner, she has 3,200 transactions in a local database. But unlike typical finance apps, Mia doesn't just look at dashboards. She starts asking questions:

"What's my month-over-month food spending trend for the last 2 years?"

"Which merchants have I spent the most at, ranked by total amount?"

"Show me all transactions over ₱5,000 - I want to see my big purchases."

"Compare my December spending across 2022, 2023, and 2024."

Claude Code becomes her personal financial analyst. She discovers things no dashboard would surface: her spending spikes every quarter (turns out, that's when she stress-shops after performance reviews). Her "coffee" spending dropped 60% when she switched jobs (the new office has free coffee). She's spent ₱47,000 at a single restaurant over 3 years - her go-to client dinner spot.

The power move: Mia exports her data to CSV, builds a simple forecasting model, and asks Claude to help her analyze seasonal patterns. She now predicts her monthly spending within 5% accuracy and adjusts her savings transfers accordingly. Her emergency fund hit 6 months of expenses for the first time ever - not through restriction, but through *understanding*.

### Journey Requirements Summary

These journeys reveal capability requirements for analyze-fin:

**Core Parsing & Import (All Journeys):**
- Multi-statement parsing across banks (GCash, BPI, Maya, BDO)
- Batch processing (40+ PDFs in single session)
- Password handling for protected statements
- Fast processing (<15 seconds for typical statement)
- >95% transaction extraction accuracy

**Categorization & Intelligence (Marco, The Reyeses):**
- Automatic merchant categorization with Philippine merchant database
- Merchant normalization for clean reporting
- Category-level breakdowns (Food, Transport, Subscriptions, etc.)
- Learning system for user corrections

**Household/Multi-Account View (The Reyeses):**
- Combined spending view across multiple people's accounts
- Clear attribution (whose account, whose transaction)
- Side-by-side comparisons

**Conversational Analysis (Mia):**
- Natural language queries via Claude Code
- Trend analysis over time periods
- Merchant ranking and filtering
- Cross-period comparisons (year-over-year, month-over-month)
- Transaction filtering by amount, category, merchant, date

**Data Export & Advanced Use (Mia):**
- CSV export for external analysis
- SQLite database for direct queries
- Clean data format for forecasting/modeling

**Reporting & Insights (All Journeys):**
- Visual HTML dashboard with spending breakdown
- Category percentages and totals
- Time-based aggregations
- Evidence-based insights (not just numbers, but actionable patterns)

## Innovation & Novel Patterns

### Core Innovation: Conversational Finance Interface

**analyze-fin's primary innovation is using Claude as the user interface itself** - not building a dashboard that happens to use AI, but eliminating the traditional UI entirely in favor of natural language interaction.

**Why This Matters:**

Traditional finance tools force users into pre-designed workflows: open app → navigate menus → find report → export → analyze. analyze-fin inverts this: users stay in their environment (Claude Code), ask natural questions, and get immediate answers. No context switching, no learning a new UI, no limitations to pre-built reports.

**The Three-Layer Value:**

1. **Flexibility (Primary)** - Users can ask questions the designer never anticipated. "Show me all transactions over ₱5,000" or "What's my average daily spend on weekdays vs weekends?" are ad-hoc queries that would require Excel skills in traditional tools.

2. **Intelligence (Secondary)** - Claude interprets intent. "How much on food?" doesn't require knowing category names or SQL syntax. Multi-period comparisons and complex aggregations are expressed in plain English.

3. **Integration (Tertiary)** - Users already in Claude Code can query finances without context-switching to another application.

### Supporting Innovation Patterns

**Statement-Based Architecture**
Working around the constraint that Philippine banks don't provide personal account APIs. PDF parsing isn't a limitation - it's a pragmatic solution that works with what users actually have access to, while remaining legal and privacy-respecting.

**Local-First + AI Analysis**
Most AI-powered finance tools require cloud processing. Most privacy-focused tools lack intelligent analysis. analyze-fin bridges both: all data stays local in SQLite, while Claude provides sophisticated analysis capabilities without the data ever leaving the user's machine.

**Philippine-Specific Design**
Not a generic tool localized for the Philippines - built from the ground up for Philippine banks (GCash, BPI, Maya, BDO) with 150+ pre-mapped local merchants and understanding of local statement formats.

### Validation Approach

**Core Innovation Validation (Claude Interface):**
- Test whether natural language queries accurately return expected results
- Measure query interpretation accuracy across diverse phrasing
- Validate that users can accomplish tasks faster than spreadsheet alternatives
- Confirm the "analyst partner" experience - Claude surfaces insights, offers hypotheses, acknowledges limitations

**Supporting Innovation Validation:**
- Statement parsing accuracy across all supported banks (>95% target)
- Local-first architecture: verify zero data transmission to external services
- Philippine merchant recognition accuracy

### Risk Mitigation

**Claude Dependency Risk:**
- Risk: Users must have Claude Code access
- Mitigation: This is intentional scope - the tool targets users already in the Claude ecosystem. Not a bug, a feature.

**Statement Format Changes:**
- Risk: Banks may update PDF layouts, breaking parsers
- Mitigation: Modular parser architecture, quality scoring to detect parsing failures, user feedback loop for format changes

**Query Interpretation Failures:**
- Risk: Claude misunderstands user intent
- Mitigation: Show underlying data with responses so users can verify accuracy; allow follow-up clarification

## CLI Tool Specific Requirements

### Project-Type Overview

analyze-fin is a **CLI tool with Claude Skills as the primary interface**. Unlike traditional CLIs where users memorize commands and flags, the primary interaction model is conversational through Claude Code. However, the underlying system supports both interactive workflows and scriptable batch operations for power users.

### Command Architecture

**Dual-Mode Operation:**

| Mode | Use Case | Example |
|------|----------|---------|
| **Interactive** (Default) | Real-time user decisions, categorization review, duplicate resolution | `parse-statements` prompts for password, asks about unknown merchants |
| **Scriptable** | Automation, batch processing, CI/CD integration | `parse-statements --batch --auto-categorize --format json` |

**Mode Switching:**
- `--batch` or `--non-interactive`: Suppresses prompts, uses defaults
- `--yes` or `-y`: Auto-confirm prompts
- `--quiet` or `-q`: Minimal output for scripting

### Output Formats

**Supported Formats:**

| Format | Flag | Use Case |
|--------|------|----------|
| **Pretty** (default) | `--format pretty` | Human-readable terminal output with colors, tables |
| **JSON** | `--format json` | Machine-readable, piping to jq, programmatic access |
| **CSV** | `--format csv` | Spreadsheet import, data analysis pipelines |
| **HTML** | `--format html` | Visual reports with charts (Plotly) |
| **Markdown** | `--format md` | Documentation, sharing, text-based viewing |

**Output Behavior:**
- Default: Pretty format to terminal
- Reports: HTML by default, opened in browser
- Queries: Pretty format, respects `--format` flag
- Export operations: CSV by default

### Configuration Schema

**Config File Location:**
```
~/.analyze-fin/config.yaml
```

**Config Structure:**
```yaml
# Database location
database_path: ~/.analyze-fin/data.db

# Default account for imports (optional)
default_account: null

# Output preferences
output:
  format: pretty
  color: true
  report_format: html

# Categorization behavior
categorization:
  auto_categorize: true
  confidence_threshold: 0.8
  prompt_for_unknown: true

# Bank-specific settings
banks:
  bpi:
    password_pattern: "{SURNAME}{last4digits}"
```

**Override Hierarchy:**
1. Command-line flags (highest priority)
2. Environment variables (`ANALYZE_FIN_*`)
3. Config file
4. Built-in defaults (lowest priority)

### Claude Skills Integration

**Primary Interface:**
Users interact through Claude Code using natural language. Claude Skills translate intent to underlying CLI operations.

| User Says | Claude Executes |
|-----------|-----------------|
| "Parse my November statements" | `parse-statements ./november/*.pdf` |
| "How much did I spend on food?" | `query-spending --category Food` |
| "Show me my spending report" | `generate-report --format html` |
| "Export everything to CSV" | `export-data --format csv` |

**Skill-to-CLI Mapping:**
- `parse-statements`: PDF parsing with bank detection
- `categorize-transactions`: Interactive or batch categorization
- `generate-report`: Dashboard/report generation
- `query-spending`: Natural language to SQL translation
- `export-data`: Data export in multiple formats
- `deduplicate`: Duplicate detection and resolution

### Scripting Support

**Batch Processing Example:**
```bash
# Process all PDFs in folder, auto-categorize, export to CSV
analyze-fin parse-statements ./statements/*.pdf --batch --auto-categorize
analyze-fin export-data --format csv --output monthly-spending.csv
```

**Pipeline Integration:**
```bash
# Query and pipe to jq for further processing
analyze-fin query-spending --category Food --format json | jq '.transactions[] | .amount'
```

**Exit Codes:**
- `0`: Success
- `1`: General error
- `2`: Parse error (PDF issues)
- `3`: Configuration error
- `4`: Database error

### Implementation Considerations

**For MVP:**
- Focus on Claude Skills as primary interface
- Implement core flags (`--format`, `--batch`, `--quiet`)
- Config file support with sensible defaults
- JSON and CSV export for power users

**Post-MVP:**
- Environment variable overrides
- Advanced scripting flags
- Pipeline-friendly output modes
- Error output to stderr for clean piping

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-Solving MVP
- Solve the core problem (spending visibility across multiple Philippine bank accounts) with minimal features
- Deliver the conversational finance innovation from day one
- Support all three primary user journey types (individual, household, power user)

**Resource Requirements:** Solo developer, 3-week timeline

### MVP Feature Set (Phase 1 - Updated)

**Core User Journeys Supported:**
- ✅ Marco (individual budget stress) - Parse → Categorize → Report → Query
- ✅ The Reyeses (household coordination) - Multi-account import, combined spending view
- ✅ Mia (power user) - Batch processing, CSV export, natural language queries

**Must-Have Capabilities:**

| Category | Features |
|----------|----------|
| **Parsing** | GCash, BPI, Maya PDF parsers; password handling; quality scoring |
| **Data** | SQLite storage; 150+ merchant mappings; deduplication engine |
| **Categorization** | Auto-categorization; merchant normalization; learning from corrections |
| **Interface** | 6 Claude Skills (parse, categorize, report, query, export, deduplicate) |
| **Reports** | HTML dashboard with Plotly charts; markdown reports |
| **CLI Core** | `--format` flag (pretty/JSON/CSV/HTML/md); `--batch` mode; `--quiet` flag |
| **Config** | Config file support (`~/.analyze-fin/config.yaml`); sensible defaults |

**MVP Success Gate:** End-to-end workflow works in both interactive and batch modes

### Post-MVP Features

**Phase 2 - Growth (Months 2-6):**
- Advanced behavioral insights (spending patterns, anomaly detection)
- Multi-month trend analysis with comparative charts
- Budget tracking and alerts
- AI-powered categorization for unknown merchants (optional Claude API)
- Environment variable overrides (`ANALYZE_FIN_*`)
- Advanced scripting flags and pipeline integration
- PDF report export

**Phase 3 - Expansion (12+ Months):**
- Household/multi-user support with permissions
- Receipt photo parsing (OCR)
- Mobile companion for statement uploads
- Community merchant mapping database
- Plugin system for custom analyzers
- Small business bookkeeping features

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Mitigation |
|------|------------|
| Bank PDF format changes | Modular parser architecture; quality scoring detects failures; user feedback loop |
| Claude query interpretation errors | Show underlying data with responses; allow follow-up clarification |
| Parser accuracy below target | Quality score system; fallback to manual review for low-confidence parses |

**Market Risks:**

| Risk | Mitigation |
|------|------------|
| Users don't have Claude Code | Intentional scope - targets Claude ecosystem users; not a mass-market product |
| Statement-based approach feels outdated | Position as privacy feature, not limitation; emphasize "your data stays local" |

**Resource Risks:**

| Risk | Mitigation |
|------|------------|
| Solo developer bottleneck | Lean MVP scope; focus on core value; defer nice-to-haves |
| 3-week timeline too aggressive | Foundation already partially built; familiar tech stack; clear scope boundaries |

## Functional Requirements

### Statement Parsing

- **FR1:** User can import PDF bank statements from supported Philippine banks (GCash, BPI, Maya)
- **FR2:** System can automatically detect which bank a statement belongs to based on PDF content
- **FR3:** User can provide passwords for protected PDF statements (BPI format)
- **FR4:** System can extract transaction data from multi-page statements
- **FR5:** User can import multiple statements in a single batch operation
- **FR6:** System can report parsing quality score (confidence level) for each imported statement
- **FR7:** User can see which transactions were successfully extracted and which failed

### Transaction Management

- **FR8:** System can store transactions in local SQLite database
- **FR9:** System can detect duplicate transactions across overlapping statement imports
- **FR10:** System can detect internal transfers between user's own accounts
- **FR11:** User can review and resolve potential duplicate transactions
- **FR12:** User can associate transactions with specific accounts (GCash, BPI, Maya, etc.)
- **FR13:** System can maintain referential integrity across accounts, statements, and transactions

### Categorization & Merchant Intelligence

- **FR14:** System can automatically categorize transactions based on merchant name
- **FR15:** System can normalize merchant names ("JOLLIBEE MANILA INC" → "Jollibee")
- **FR16:** User can manually categorize or re-categorize transactions
- **FR17:** System can learn from user corrections and apply to future similar transactions
- **FR18:** System can use pre-loaded Philippine merchant mappings (150+ merchants)
- **FR19:** User can add custom merchant mappings
- **FR20:** User can add notes/tags to transactions for custom classification

### Querying & Analysis

- **FR21:** User can query spending by category (e.g., "Food", "Transport")
- **FR22:** User can query spending by merchant
- **FR23:** User can query spending by date range
- **FR24:** User can query spending by amount threshold (e.g., "over ₱5,000")
- **FR25:** User can ask natural language questions about spending via Claude
- **FR26:** User can see aggregated spending totals (daily, weekly, monthly averages)
- **FR27:** User can compare spending across time periods (month-over-month, year-over-year)
- **FR28:** User can see spending patterns by day of week

### Reporting & Visualization

- **FR29:** User can generate spending dashboard with category breakdown
- **FR30:** System can render pie charts showing spending distribution
- **FR31:** System can render line charts showing spending over time
- **FR32:** System can render bar charts for category comparisons
- **FR33:** User can view reports in HTML format (opened in browser)
- **FR34:** User can view reports in markdown format (text-based)

### Data Export

- **FR35:** User can export transactions to CSV format
- **FR36:** User can export transactions to JSON format
- **FR37:** User can filter exports by date range, category, or merchant
- **FR38:** User can export query results in machine-readable format

### Configuration & Settings

- **FR39:** User can configure default settings via config file
- **FR40:** User can specify database location
- **FR41:** User can set default output format preferences
- **FR42:** User can configure auto-categorization behavior (confidence threshold)
- **FR43:** User can override config settings via command-line flags

### CLI Interface

- **FR44:** User can run commands in interactive mode (prompts for input)
- **FR45:** User can run commands in batch mode (no prompts, uses defaults)
- **FR46:** User can specify output format via `--format` flag
- **FR47:** User can suppress output via `--quiet` flag
- **FR48:** System can return appropriate exit codes for success/failure states

## Non-Functional Requirements

### Performance

| Metric | Target | Context |
|--------|--------|---------|
| PDF parsing speed | <10 seconds per statement | For typical 28-transaction statement |
| Batch processing | <1 hour for 40 statements | Historical import scenario |
| Dashboard generation | <5 seconds | Complete HTML report with charts |
| Query response time | <2 seconds | Natural language query processing |
| Transaction analysis | Instant (<500ms) | For datasets up to 500+ transactions |

### Data Accuracy

| Metric | Target | Measurement |
|--------|--------|-------------|
| Transaction extraction | >95% accuracy | Manual verification of 100-transaction samples |
| Auto-categorization | >90% accuracy | Only 10% require manual review |
| Duplicate detection | >95% true positives | Catches overlapping imports |
| False positive duplicates | 0% | Never mark different transactions as duplicates |
| Merchant normalization | Consistent | Same merchant always normalizes to same name |

### Data Integrity & Persistence

- **Zero transaction loss**: 100% capture rate during import
- **Referential integrity**: SQLite foreign keys enforced across accounts, statements, transactions
- **Data retention**: Permanent storage (no automatic deletion)
- **Corruption protection**: SQLite WAL mode for crash recovery
- **Merchant mappings**: User corrections persist across sessions

### Security & Privacy

- **Local-first architecture**: All data stored locally in SQLite; no cloud transmission
- **No external API calls**: Financial data never leaves user's machine
- **Password handling**: BPI statement passwords used only for PDF decryption, never stored
- **File permissions**: Database file readable only by owner (0600)
- **Data Privacy Act compliance**: RA 10173 principles applied to personal data handling

### Backup & Recovery

- **Database portability**: SQLite file can be copied for backup
- **Export capability**: Full transaction export to CSV/JSON for external backup
- **Import recovery**: Ability to re-import from exported data if needed
- **Config backup**: Config file is plain YAML, easily backed up

### Reliability

- **Graceful degradation**: Partial parse failures don't lose successfully extracted transactions
- **Quality scoring**: Low-confidence parses flagged for user review rather than silent failure
- **Error recovery**: Failed operations report clear error messages with recovery suggestions
- **Idempotent imports**: Re-importing same statement doesn't create duplicates

