---
stepsCompleted: [1, 2, 3]
inputDocuments: []
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 0
  projectDocs: 0
workflowType: 'prd'
lastStep: 3
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
