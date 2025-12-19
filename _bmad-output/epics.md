---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - _bmad-output/prd.md
  - _bmad-output/architecture.md
  - _bmad-output/project-context.md
project_name: 'analyze-fin'
user_name: 'arjay'
date: '2025-12-15'
completedAt: '2025-12-15'
status: 'complete'
totalEpics: 4
totalStories: 22
validationStatus: 'passed'
---

# analyze-fin - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for analyze-fin, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

**Statement Parsing (FR1-7):**
- FR1: User can import PDF bank statements from supported Philippine banks (GCash, BPI, Maya)
- FR2: System can automatically detect which bank a statement belongs to based on PDF content
- FR3: User can provide passwords for protected PDF statements (BPI format)
- FR4: System can extract transaction data from multi-page statements
- FR5: User can import multiple statements in a single batch operation
- FR6: System can report parsing quality score (confidence level) for each imported statement
- FR7: User can see which transactions were successfully extracted and which failed

**Transaction Management (FR8-13):**
- FR8: System can store transactions in local SQLite database
- FR9: System can detect duplicate transactions across overlapping statement imports
- FR10: System can detect internal transfers between user's own accounts
- FR11: User can review and resolve potential duplicate transactions
- FR12: User can associate transactions with specific accounts (GCash, BPI, Maya, etc.)
- FR13: System can maintain referential integrity across accounts, statements, and transactions

**Categorization & Merchant Intelligence (FR14-20):**
- FR14: System can automatically categorize transactions based on merchant name
- FR15: System can normalize merchant names ("JOLLIBEE MANILA INC" → "Jollibee")
- FR16: User can manually categorize or re-categorize transactions
- FR17: System can learn from user corrections and apply to future similar transactions
- FR18: System can use pre-loaded Philippine merchant mappings (150+ merchants)
- FR19: User can add custom merchant mappings
- FR20: User can add notes/tags to transactions for custom classification

**Querying & Analysis (FR21-28):**
- FR21: User can query spending by category (e.g., "Food", "Transport")
- FR22: User can query spending by merchant
- FR23: User can query spending by date range
- FR24: User can query spending by amount threshold (e.g., "over ₱5,000")
- FR25: User can ask natural language questions about spending via Claude
- FR26: User can see aggregated spending totals (daily, weekly, monthly averages)
- FR27: User can compare spending across time periods (month-over-month, year-over-year)
- FR28: User can see spending patterns by day of week

**Reporting & Visualization (FR29-34):**
- FR29: User can generate spending dashboard with category breakdown
- FR30: System can render pie charts showing spending distribution
- FR31: System can render line charts showing spending over time
- FR32: System can render bar charts for category comparisons
- FR33: User can view reports in HTML format (opened in browser)
- FR34: User can view reports in markdown format (text-based)

**Data Export (FR35-38):**
- FR35: User can export transactions to CSV format
- FR36: User can export transactions to JSON format
- FR37: User can filter exports by date range, category, or merchant
- FR38: User can export query results in machine-readable format

**Configuration & Settings (FR39-43):**
- FR39: User can configure default settings via config file
- FR40: User can specify database location
- FR41: User can set default output format preferences
- FR42: User can configure auto-categorization behavior (confidence threshold)
- FR43: User can override config settings via command-line flags

**CLI Interface (FR44-48):**
- FR44: User can run commands in interactive mode (prompts for input)
- FR45: User can run commands in batch mode (no prompts, uses defaults)
- FR46: User can specify output format via `--format` flag
- FR47: User can suppress output via `--quiet` flag
- FR48: System can return appropriate exit codes for success/failure states

### Non-Functional Requirements

**Performance:**
- NFR1: PDF parsing speed <10 seconds per statement (typical 28-transaction statement)
- NFR2: Batch processing <1 hour for 40 statements (historical import)
- NFR3: Dashboard generation <5 seconds (complete HTML report with charts)
- NFR4: Query response time <2 seconds (natural language query processing)
- NFR5: Transaction analysis instant (<500ms) for datasets up to 500+ transactions

**Data Accuracy:**
- NFR6: Transaction extraction >95% accuracy (manual verification of 100-transaction samples)
- NFR7: Auto-categorization >90% accuracy (only 10% require manual review)
- NFR8: Duplicate detection >95% true positives (catches overlapping imports)
- NFR9: False positive duplicates 0% (never mark different transactions as duplicates)
- NFR10: Merchant normalization consistent (same merchant always normalizes to same name)

**Data Integrity & Persistence:**
- NFR11: Zero transaction loss - 100% capture rate during import
- NFR12: Referential integrity - SQLite foreign keys enforced
- NFR13: Data retention - permanent storage (no automatic deletion)
- NFR14: Corruption protection - SQLite WAL mode for crash recovery
- NFR15: Merchant mappings persist across sessions

**Security & Privacy:**
- NFR16: Local-first architecture - all data stored locally, no cloud transmission
- NFR17: No external API calls - financial data never leaves user's machine
- NFR18: Password handling - BPI passwords used only for decryption, never stored
- NFR19: File permissions - database file readable only by owner (0600)
- NFR20: Data Privacy Act compliance - RA 10173 principles applied

**Backup & Recovery:**
- NFR21: Database portability - SQLite file can be copied for backup
- NFR22: Export capability - full transaction export to CSV/JSON
- NFR23: Import recovery - ability to re-import from exported data
- NFR24: Config backup - plain YAML, easily backed up

**Reliability:**
- NFR25: Graceful degradation - partial failures don't lose successful transactions
- NFR26: Quality scoring - low-confidence parses flagged for review
- NFR27: Error recovery - clear error messages with recovery suggestions
- NFR28: Idempotent imports - re-importing same statement doesn't create duplicates

### Additional Requirements

**From Architecture - Foundation Setup:**
- AR1: Initialize project with uv (Rust-based package manager)
- AR2: Use src layout with `src/analyze_fin/` structure
- AR3: SQLAlchemy 2.0 with Mapped[] type annotations
- AR4: Alembic for database migrations
- AR5: Typer CLI framework with type-hint based commands
- AR6: pdfplumber for PDF extraction
- AR7: Plotly for interactive charts
- AR8: Jinja2 for report templates
- AR9: ruff for linting and formatting
- AR10: pytest for testing

**From Architecture - Parser Pattern:**
- AR11: Strategy pattern for bank parsers (BaseBankParser abstract class)
- AR12: Bank-specific parsers: GCashParser, BPIParser, MayaParser
- AR13: Quality scoring in base parser class

**From Architecture - Exception Handling:**
- AR14: Custom exception hierarchy (AnalyzeFinError base)
- AR15: ParseError, ValidationError, DuplicateError, ConfigError subclasses
- AR16: CLI layer catches and formats user-friendly messages

**From Architecture - Claude Skills:**
- AR17: Claude Skills in `.claude/commands/` directory
- AR18: Skills map 1:1 to CLI commands (parse, categorize, report, query, export, deduplicate)

**From Project Context - Critical Rules:**
- AR19: Currency as Decimal type, display as ₱{amount:,.2f}
- AR20: Dates as ISO internal, localized display (Nov 15, 2024)
- AR21: JSON keys always snake_case
- AR22: Type hints required on all public functions
- AR23: Absolute imports only (no relative imports between modules)
- AR24: Separate tests/ folder (not co-located)

### FR Coverage Map

**Epic 1 - Import Bank Statements:**
- FR1: Import PDF bank statements
- FR2: Automatic bank detection
- FR3: Password handling for BPI
- FR4: Multi-page statement extraction
- FR5: Batch import operations
- FR6: Quality scoring system
- FR7: View extraction results
- FR8: SQLite storage
- FR12: Associate transactions with accounts
- FR13: Referential integrity

**Epic 2 - Transaction Intelligence:**
- FR9: Detect duplicate transactions
- FR10: Detect internal transfers
- FR11: Review and resolve duplicates
- FR14: Auto-categorize transactions
- FR15: Normalize merchant names
- FR16: Manual categorization
- FR17: Learn from user corrections
- FR18: Philippine merchant mappings
- FR19: Custom merchant mappings
- FR20: Add notes/tags

**Epic 3 - Insights & Reporting:**
- FR21: Query by category
- FR22: Query by merchant
- FR23: Query by date range
- FR24: Query by amount threshold
- FR25: Natural language queries via Claude
- FR26: Aggregated spending totals
- FR27: Time period comparisons
- FR28: Day of week patterns
- FR29: Spending dashboard generation
- FR30: Pie charts
- FR31: Line charts
- FR32: Bar charts
- FR33: HTML reports
- FR34: Markdown reports

**Epic 4 - Advanced Features:**
- FR35: CSV export
- FR36: JSON export
- FR37: Filtered exports
- FR38: Export query results
- FR39: Config file support
- FR40: Database location config
- FR41: Output format preferences
- FR42: Auto-categorization config
- FR43: Command-line flag overrides
- FR44: Interactive mode
- FR45: Batch mode
- FR46: Format flag
- FR47: Quiet flag
- FR48: Exit codes

## Epic List

### Epic 1: Import Bank Statements
Users can import PDF statements from Philippine banks (GCash, BPI, Maya) and see their transactions stored locally in a database.

**User Capabilities:**
- Upload PDF bank statements (single or batch)
- Handle password-protected BPI statements
- See which transactions were successfully extracted
- View quality scores for parsing confidence
- Store transactions in local SQLite database

**FRs Covered:** FR1-8, FR12-13
**Additional Requirements:** AR1-AR10 (foundation setup), AR11-AR13 (parser architecture), AR14-AR16 (exception handling)

### Epic 2: Transaction Intelligence
Users get automatically categorized transactions with clean merchant names and no duplicates.

**User Capabilities:**
- Auto-categorize transactions using Philippine merchant database (150+ merchants)
- See normalized merchant names ("JOLLIBEE MANILA INC" → "Jollibee")
- Detect and resolve duplicate transactions
- Identify internal transfers between own accounts
- Manually categorize and teach the system
- Add notes/tags to transactions

**FRs Covered:** FR9-11, FR14-20
**Additional Requirements:** AR19 (currency formatting), AR20 (date formatting)

### Epic 3: Insights & Reporting
Users can query their spending, generate visual reports with charts, and understand their financial patterns through natural language.

**User Capabilities:**
- Ask natural language questions via Claude ("How much on food?")
- Query by category, merchant, date range, amount
- See aggregated spending (daily, weekly, monthly)
- Compare time periods (month-over-month, year-over-year)
- Generate HTML dashboards with pie/line/bar charts
- View markdown reports for text-based viewing

**FRs Covered:** FR21-34
**Additional Requirements:** AR21 (JSON keys snake_case)

### Epic 4: Advanced Features
Users can export data for external analysis, customize tool settings, and use batch processing for power user workflows.

**User Capabilities:**
- Export transactions to CSV/JSON
- Filter exports by date, category, merchant
- Configure settings via config file
- Run commands in interactive or batch mode
- Specify output formats (pretty, JSON, CSV, HTML, markdown)
- Use Claude Skills for conversational interface
- Customize auto-categorization behavior

**FRs Covered:** FR35-48
**Additional Requirements:** AR17-AR18 (Claude Skills), AR22-AR24 (implementation rules)

---

## Epic 1: Import Bank Statements

Users can import PDF statements from Philippine banks (GCash, BPI, Maya) and see their transactions stored locally in a database.

### Story 1.1: Project Foundation & Database Setup

As a developer,
I want to initialize the project with proper foundation and database structure,
So that I have a working base to build the import functionality.

**Acceptance Criteria:**

**Given** a new project directory
**When** I initialize the project with uv
**Then** the project has src layout with `src/analyze_fin/` structure
**And** pyproject.toml is configured with uv dependencies (SQLAlchemy 2.0, Alembic, pdfplumber, Typer)
**And** .python-version specifies Python 3.11+

**Given** the project structure is created
**When** I run database initialization
**Then** SQLite database is created with WAL mode enabled
**And** Alembic migrations folder is initialized
**And** Initial migration creates accounts table (id, name, bank_type, created_at)
**And** Initial migration creates statements table (id, account_id FK, file_path, imported_at, quality_score)
**And** Initial migration creates transactions table (id, statement_id FK, date, description, amount as Decimal, created_at)
**And** Foreign key constraints are enforced (referential integrity)

**Given** the codebase structure
**When** I review the exception hierarchy
**Then** src/analyze_fin/exceptions.py exists with AnalyzeFinError base class
**And** ParseError, ValidationError, DuplicateError, ConfigError subclasses are defined
**And** All exceptions include descriptive error messages

**Given** the foundation is complete
**When** I run `uv run pytest`
**Then** test infrastructure works with conftest.py providing db_session fixture
**And** tests/ folder mirrors src/ structure
**And** ruff check passes with no violations

**Requirements:** FR8, FR13, AR1-AR10, AR14-AR16, AR22-AR24

---

### Story 1.2: GCash Statement Parser

As a user,
I want to import a GCash PDF statement,
So that I can see my GCash transactions stored in the database.

**Acceptance Criteria:**

**Given** the foundation is complete
**When** I create the parser architecture
**Then** src/analyze_fin/parsers/base.py contains BaseBankParser abstract class
**And** BaseBankParser has abstract method `extract_transactions(pdf_path: Path) -> list[RawTransaction]`
**And** BaseBankParser has `calculate_quality_score(transactions: list) -> float` method
**And** BaseBankParser has `detect_bank_type(pdf_path: Path) -> str | None` method

**Given** the base parser exists
**When** I implement GCashParser in src/analyze_fin/parsers/gcash.py
**Then** GCashParser inherits from BaseBankParser
**And** GCashParser extracts date in "MMM DD, YYYY" format (e.g., "Nov 15, 2024")
**And** GCashParser extracts description from transaction rows
**And** GCashParser extracts amount as Decimal (handles ₱12,345.67 format)
**And** GCashParser handles multi-page statements correctly

**Given** a valid GCash PDF statement
**When** I run the parser
**Then** transactions are extracted with >95% accuracy
**And** quality score is calculated (0.0-1.0 range)
**And** quality score considers: complete dates, valid amounts, non-empty descriptions
**And** quality score >= 0.95 indicates high confidence

**Given** a GCash statement with 28 transactions
**When** I import the statement
**Then** parsing completes in <10 seconds (NFR1)
**And** Account record is created with bank_type="gcash"
**And** Statement record is created with quality_score and file_path
**And** 28 Transaction records are created linked to the statement
**And** All amounts are stored as Decimal type (not float)
**And** All dates are stored in ISO format internally

**Given** a corrupted or invalid PDF
**When** I attempt to parse
**Then** ParseError is raised with descriptive message
**And** No partial data is saved to database
**And** Error message suggests recovery steps

**Requirements:** FR1, FR2, FR4, FR6, FR7, FR8, AR11-AR13, AR19-AR20, NFR1, NFR6, NFR11

---

### Story 1.3: BPI Statement Parser with Password Handling

As a user,
I want to import a password-protected BPI PDF statement,
So that I can see my BPI salary account transactions.

**Acceptance Criteria:**

**Given** the parser architecture exists
**When** I implement BPIParser in src/analyze_fin/parsers/bpi.py
**Then** BPIParser inherits from BaseBankParser
**And** BPIParser accepts optional password parameter
**And** BPIParser uses password format: SURNAME + last 4 digits (e.g., "GARCIA1234")

**Given** a password-protected BPI PDF
**When** I provide the correct password
**Then** PDF is decrypted successfully
**And** Password is used only for decryption, never stored (NFR18)
**And** Transactions are extracted from unlocked PDF

**Given** a BPI statement with MM/DD/YYYY date format
**When** I parse the statement
**Then** Dates are correctly converted to ISO format for storage
**And** Amount formatting handles both positive and negative values
**And** Account debits and credits are correctly signed

**Given** an incorrect password is provided
**When** I attempt to decrypt
**Then** ParseError is raised: "Invalid password for BPI statement"
**And** User is prompted to retry with correct password
**And** No data is saved to database

**Given** a valid BPI statement is imported
**When** I verify the results
**Then** Account record has bank_type="bpi"
**And** Quality score accurately reflects parsing confidence
**And** All transactions maintain referential integrity with statement

**Given** BPI parsing implementation
**When** I run security review
**Then** Password is never logged or stored in database
**And** Password variables are cleared from memory after use
**And** No PII (account numbers) appears in logs

**Requirements:** FR1, FR2, FR3, FR4, FR8, AR11-AR13, AR19-AR20, NFR6, NFR18

---

### Story 1.4: Maya Statement Parser

As a user,
I want to import Maya PDF statements (both Savings and Wallet),
So that I can track my Maya transactions alongside other accounts.

**Acceptance Criteria:**

**Given** the parser architecture exists
**When** I implement MayaParser in src/analyze_fin/parsers/maya.py
**Then** MayaParser inherits from BaseBankParser
**And** MayaParser detects Maya Savings vs Maya Wallet format
**And** Both formats are parsed correctly

**Given** a Maya Savings statement
**When** I parse the statement
**Then** Dates are extracted in ISO format (typical for Maya)
**And** Transaction descriptions are cleaned and normalized
**And** Amounts handle decimal precision correctly

**Given** a Maya Wallet statement
**When** I parse the statement
**Then** QR payment transactions are captured
**And** Load/cash-in transactions are identified
**And** All transaction types are stored consistently

**Given** Maya statements are imported
**When** I verify the results
**Then** Account records have bank_type="maya_savings" or "maya_wallet"
**And** Transactions from both account types are distinguishable
**And** Quality scoring works for both formats

**Given** edge cases in Maya statements
**When** I parse statements with special characters or multi-line descriptions
**Then** Parser handles them gracefully without data loss
**And** Quality score reflects any parsing ambiguities

**Requirements:** FR1, FR2, FR4, FR8, AR11-AR13, AR19-AR20, NFR6

---

### Story 1.5: Batch Import & Quality Reporting

As a user,
I want to import multiple bank statements at once and see quality reports,
So that I can quickly build my transaction history and know parsing confidence.

**Acceptance Criteria:**

**Given** multiple PDF files in a folder (GCash, BPI, Maya mixed)
**When** I run batch import command
**Then** Bank type is auto-detected for each PDF (FR2)
**And** Appropriate parser is selected automatically
**And** All statements are processed sequentially

**Given** batch import with 40 statements
**When** I run the import
**Then** Processing completes in <1 hour (NFR2)
**And** Progress is displayed for each file processed
**And** Partial failures don't stop the entire batch

**Given** statements are imported
**When** I view the quality report
**Then** Each statement shows quality score (0.0-1.0)
**And** Quality score >= 0.95 is marked "High Confidence"
**And** Quality score 0.80-0.95 is marked "Medium - Review Recommended"
**And** Quality score < 0.80 is marked "Low - Manual Review Required"

**Given** a quality report is displayed
**When** I review low-confidence parses
**Then** I can see which rows failed extraction
**And** I can see what data was successfully extracted
**And** I receive suggestions for manual review

**Given** the same statement is re-imported
**When** I attempt to import again
**Then** System detects it as potential duplicate (idempotent)
**And** User is warned: "This statement may already be imported"
**And** User can choose to skip or force re-import

**Given** batch import encounters errors
**When** some PDFs fail to parse
**Then** Successfully parsed statements are still saved (graceful degradation, NFR25)
**And** Error summary lists failed files with reasons
**And** User can retry failed imports individually

**Given** all parsers are implemented
**When** I verify data integrity
**Then** Zero transaction loss during import (NFR11)
**And** All foreign key relationships are maintained (NFR12)
**And** SQLite database uses WAL mode for crash recovery (NFR14)

**Requirements:** FR1, FR2, FR5, FR6, FR7, FR12, NFR1, NFR2, NFR11, NFR12, NFR14, NFR25, NFR28

---

## Epic 2: Transaction Intelligence

Users get automatically categorized transactions with clean merchant names and no duplicates.

### Story 2.1: Philippine Merchant Database & Categories

As a user,
I want my transactions to be automatically categorized using Philippine merchant knowledge,
So that I don't have to manually categorize every transaction.

**Acceptance Criteria:**

**Given** the project structure exists
**When** I create the merchant mapping system
**Then** data/merchant_mapping.json contains 150+ Philippine merchants
**And** Merchant mappings include: Jollibee, SM, Lazada, Meralco, Globe, Smart, Grab, Foodpanda, etc.
**And** Each mapping includes: merchant_pattern (regex), normalized_name, default_category

**Given** merchant mappings are loaded
**When** I review the category structure
**Then** Categories include: Food & Dining, Transportation, Shopping, Utilities, Telecommunications, Healthcare, Entertainment, Other
**And** Categories are stored as enum or validated strings
**And** Categories align with Philippine spending patterns

**Given** the merchant database schema
**When** I create the database tables
**Then** merchant_corrections table is created (id, original_merchant, normalized_merchant, category, created_at)
**And** transactions table is extended with: category (nullable), merchant_normalized (nullable), notes (nullable)
**And** Alembic migration handles schema changes properly

**Given** merchant data is loaded
**When** I access the merchant mappings
**Then** Merchant patterns support fuzzy matching (e.g., "JOLLIBEE MANILA INC" matches "Jollibee")
**And** Case-insensitive matching works correctly
**And** Partial matches are ranked by confidence

**Given** the categorization module structure
**When** I create src/analyze_fin/categorization/
**Then** categorizer.py exists with categorization logic
**And** normalizer.py exists with merchant normalization
**And** learning.py exists for correction persistence
**And** All files follow project conventions (type hints, absolute imports)

**Requirements:** FR14, FR18, AR19-AR20

---

### Story 2.2: Auto-Categorization Engine

As a user,
I want transactions automatically categorized when imported,
So that I immediately see organized spending data.

**Acceptance Criteria:**

**Given** merchant mappings are loaded
**When** I implement the categorization engine
**Then** src/analyze_fin/categorization/categorizer.py contains Categorizer class
**And** Categorizer.categorize(transaction) returns (category, confidence_score)
**And** Confidence score is 0.0-1.0 range

**Given** a transaction with merchant "JOLLIBEE MANILA INC"
**When** I categorize the transaction
**Then** Category is set to "Food & Dining"
**And** Confidence score is high (>0.9)
**And** Normalized merchant name is "Jollibee"

**Given** a transaction with unknown merchant
**When** I categorize the transaction
**Then** Category is set to "Uncategorized"
**And** Confidence score is low (<0.5)
**And** Transaction is flagged for manual review
**And** No exception is raised (graceful degradation)

**Given** auto-categorization is configured
**When** I set confidence_threshold in config (default 0.8)
**Then** Transactions with confidence >= threshold are auto-categorized
**And** Transactions below threshold are marked for review
**And** User can adjust threshold in config.yaml

**Given** transactions are imported
**When** Auto-categorization runs
**Then** >90% of transactions are correctly categorized (NFR7)
**And** Categorization happens during import process
**And** Already-categorized transactions are not re-categorized

**Given** edge cases in merchant names
**When** I test categorization
**Then** Special characters are handled (& / - etc.)
**And** Multi-word merchants match correctly
**And** Typos within edit-distance threshold still match
**And** Ambiguous merchants default to "Uncategorized"

**Requirements:** FR14, FR16, FR42, NFR7

---

### Story 2.3: Merchant Normalization

As a user,
I want messy merchant names cleaned to consistent values,
So that my reports show "Jollibee" instead of "JOLLIBEE MANILA INC".

**Acceptance Criteria:**

**Given** the normalizer module exists
**When** I implement merchant normalization
**Then** src/analyze_fin/categorization/normalizer.py contains MerchantNormalizer class
**And** MerchantNormalizer.normalize(raw_merchant) returns normalized_name

**Given** a transaction with "JOLLIBEE MANILA INC"
**When** I normalize the merchant
**Then** Normalized name is "Jollibee"
**And** Normalization is consistent across all "JOLLIBEE*" variants

**Given** merchant normalization patterns
**When** I test Philippine merchants
**Then** "SM CITY MANILA" → "SM Supermalls"
**And** "GRAB TRANSPORT" → "Grab"
**And** "MERALCO PAYMENT" → "Meralco"
**And** "LAZADA PHILIPPINES" → "Lazada"
**And** Same merchant always normalizes to same name (NFR10)

**Given** transactions are imported
**When** Normalization is applied
**Then** merchant_normalized field is populated
**And** Original description is preserved unchanged
**And** Normalization happens before categorization

**Given** an unknown merchant with no mapping
**When** I normalize
**Then** Raw merchant name is cleaned (trimmed, title-cased)
**And** No normalization mapping is created automatically
**And** merchant_normalized is set to cleaned version

**Given** normalized merchants in database
**When** I query transactions by merchant
**Then** Queries use merchant_normalized field
**And** Variants of same merchant are grouped correctly
**And** Reports show consistent merchant names

**Requirements:** FR15, NFR10

---

### Story 2.4: Duplicate Detection & Internal Transfers

As a user,
I want duplicate transactions automatically detected,
So that re-importing statements doesn't create duplicate data.

**Acceptance Criteria:**

**Given** the deduplication module exists
**When** I implement duplicate detection
**Then** src/analyze_fin/deduplication/detector.py contains DuplicateDetector class
**And** DuplicateDetector uses 3-layer matching: reference#, content hash, user review

**Given** transactions are imported
**When** I run duplicate detection
**Then** Layer 1: Transactions with same reference number are marked as potential duplicates
**And** Layer 2: Transactions with same (date, amount, description hash) are marked as potential duplicates
**And** Layer 3: User can review and confirm/reject duplicates

**Given** the same statement is imported twice
**When** Duplicate detection runs
**Then** Second import transactions are flagged as duplicates
**And** >95% of actual duplicates are detected (NFR8)
**And** Zero false positives occur (NFR9)

**Given** an internal transfer (GCash → BPI)
**When** Transactions appear in both accounts
**Then** System detects matching amount and opposite signs
**And** Both transactions are flagged as "potential internal transfer"
**And** They are NOT marked as duplicates to delete
**And** User can confirm/reject internal transfer link

**Given** potential duplicates are detected
**When** I review duplicates
**Then** Side-by-side comparison shows: date, amount, description, source statement
**And** User can: Keep both, Keep first, Keep second, Mark as internal transfer
**And** Decision is persisted in database

**Given** a duplicate transaction is confirmed
**When** User chooses to keep only one
**Then** The other transaction is marked as duplicate (not deleted)
**And** Duplicate transactions are excluded from reports
**And** Audit trail shows which transaction was marked as duplicate

**Given** idempotent import requirement (NFR28)
**When** Same statement is re-imported
**Then** System warns user before creating duplicates
**And** User can choose: Skip (default), Force re-import
**And** No silent duplicate creation occurs

**Requirements:** FR9, FR10, FR11, NFR8, NFR9, NFR28

---

### Story 2.5: Learning System & Manual Corrections

As a user,
I want my categorization corrections to persist and apply automatically,
So that the system learns from my input and improves over time.

**Acceptance Criteria:**

**Given** a transaction is manually categorized
**When** I correct "SM CITY MANILA" from "Uncategorized" to "Shopping"
**Then** Correction is saved to merchant_corrections table
**And** merchant_corrections includes: original_merchant, normalized_merchant, category, user_id (optional), created_at

**Given** a correction exists
**When** Future transactions have the same merchant pattern
**Then** Correction is automatically applied
**And** System learns: all "SM*" variants categorized as "Shopping"
**And** User corrections take precedence over default mappings

**Given** multiple corrections for similar merchants
**When** I build the learning logic
**Then** Most recent correction takes precedence
**And** User can see correction history
**And** Corrections persist across sessions (NFR15)

**Given** I want to add custom merchant mappings
**When** I use the add custom mapping command
**Then** New mapping is added to merchant_corrections table
**And** New mapping immediately applies to existing uncategorized transactions
**And** Future transactions use the new mapping

**Given** I want to add notes/tags to transactions
**When** I add a note to a transaction
**Then** notes field is populated in transactions table
**And** Notes are searchable and filterable
**And** Notes display in reports and queries

**Given** transactions are manually re-categorized
**When** I change category from "Food & Dining" to "Entertainment"
**Then** Category is updated in database
**And** If pattern is recognizable, system asks: "Apply to all similar merchants?"
**And** User can choose: Just this transaction, All matching future, All matching (past + future)

**Given** the learning system is working
**When** I verify accuracy over time
**Then** Categorization accuracy improves with more corrections
**And** System tracks: total corrections, auto-categorization success rate
**And** User can export merchant mappings for backup

**Requirements:** FR16, FR17, FR19, FR20, NFR15

---

## Epic 3: Insights & Reporting

Users can query their spending, generate visual reports with charts, and understand their financial patterns through natural language.

### Story 3.1: Query Engine & Basic Filters

As a user,
I want to query my transactions by category, merchant, date, and amount,
So that I can find specific transactions and analyze targeted spending.

**Acceptance Criteria:**

**Given** transactions exist in the database
**When** I implement the query module
**Then** src/analyze_fin/queries/spending.py contains SpendingQuery class
**And** SpendingQuery supports filtering by: category, merchant, date_range, amount_min, amount_max

**Given** I want to query by category
**When** I query for category="Food & Dining"
**Then** All transactions with that category are returned
**And** Results include: date, merchant, amount, description
**And** Query response time is <2 seconds for 500+ transactions (NFR4, NFR5)

**Given** I want to query by merchant
**When** I query for merchant="Jollibee"
**Then** All transactions with merchant_normalized="Jollibee" are returned
**And** Original merchant variations are shown alongside normalized name
**And** Results are sorted by date descending (most recent first)

**Given** I want to query by date range
**When** I query for date_range="2024-11-01 to 2024-11-30"
**Then** Only transactions within that range are returned
**And** Range is inclusive on both ends
**And** Partial dates are supported (e.g., "November 2024" expands to full month)

**Given** I want to query by amount threshold
**When** I query for amount > ₱5,000
**Then** Only transactions above that amount are returned
**And** Amount comparison works with Decimal precision
**And** Both positive and negative amounts are handled correctly

**Given** I want to combine multiple filters
**When** I query for category="Food & Dining" AND date_range="Last 7 days" AND amount > ₱500
**Then** All filters are applied with AND logic
**And** Results match all criteria
**And** Empty result set returns gracefully with message "No transactions found matching filters"

**Given** query results exist
**When** I view the output
**Then** Results display: date, merchant_normalized, category, amount formatted as ₱{amount:,.2f}
**And** Total count is shown: "Found 42 transactions"
**And** Total amount is shown: "Total: ₱24,567.89"

**Requirements:** FR21, FR22, FR23, FR24, NFR4, NFR5

---

### Story 3.2: Aggregations & Spending Analytics

As a user,
I want to see aggregated spending totals and patterns,
So that I understand my overall spending behavior.

**Acceptance Criteria:**

**Given** transactions exist in the database
**When** I implement aggregation logic
**Then** src/analyze_fin/queries/aggregations.py contains AggregationEngine class
**And** AggregationEngine supports: sum, average, count, min, max by time period

**Given** I want daily spending totals
**When** I query for daily aggregation
**Then** Results show spending grouped by day
**And** Each day shows: date, total_amount, transaction_count
**And** Days with no transactions show ₱0.00

**Given** I want weekly spending totals
**When** I query for weekly aggregation
**Then** Results show spending grouped by week
**And** Week definition: Sunday-Saturday or configurable
**And** Each week shows: week_start_date, total_amount, transaction_count

**Given** I want monthly spending totals
**When** I query for monthly aggregation
**Then** Results show spending grouped by month
**And** Each month shows: month (e.g., "November 2024"), total_amount, transaction_count, average_per_day

**Given** I want category breakdown
**When** I query for spending by category
**Then** Results show: category, total_amount, transaction_count, percentage_of_total
**And** Categories are sorted by total_amount descending
**And** Percentages sum to 100%

**Given** I want merchant ranking
**When** I query for top merchants
**Then** Results show top 10 merchants by spending
**And** Each merchant shows: merchant_normalized, total_amount, transaction_count, average_transaction

**Given** I want day-of-week patterns
**When** I query for spending by day of week
**Then** Results show: day_name (Monday, Tuesday, etc.), total_amount, transaction_count, average_amount
**And** Reveals patterns like "You spend more on weekends"

**Given** I want spending averages
**When** I query for average calculations
**Then** System calculates: average_per_day, average_per_transaction, average_per_category
**And** Averages exclude days with zero transactions
**And** Averages are displayed with 2 decimal places

**Given** aggregations are complete
**When** I verify performance
**Then** Aggregation queries complete in <500ms for 500+ transactions (NFR5)
**And** Results are cached for repeated queries
**And** Cache is invalidated when new transactions are imported

**Requirements:** FR26, FR28, NFR5

---

### Story 3.3: Time Period Comparisons

As a user,
I want to compare my spending across different time periods,
So that I can track trends and see if spending is increasing or decreasing.

**Acceptance Criteria:**

**Given** transactions span multiple months
**When** I implement comparison logic
**Then** src/analyze_fin/queries/aggregations.py includes ComparisonEngine
**And** ComparisonEngine supports: month-over-month, year-over-year, custom period comparisons

**Given** I want month-over-month comparison
**When** I compare November 2024 vs October 2024
**Then** Results show both months side-by-side
**And** Difference is calculated: amount, percentage change
**And** Change indicators show: ↑ increase, ↓ decrease, → no change

**Given** I want year-over-year comparison
**When** I compare November 2024 vs November 2023
**Then** Results show both years side-by-side for the same month
**And** Annual growth/decline percentage is calculated
**And** Category-by-category comparison is available

**Given** I want to compare multiple months
**When** I query "Compare last 3 months"
**Then** Results show all 3 months in a table
**And** Trend line indicates: increasing, decreasing, stable
**And** Highest and lowest spending months are highlighted

**Given** comparison results exist
**When** I view the output
**Then** Current period shows actual amounts
**And** Previous period shows actual amounts
**And** Difference shows: absolute (₱X,XXX) and relative (X%)
**And** Positive change (spending increased) is highlighted in red
**And** Negative change (spending decreased) is highlighted in green

**Given** I want category-specific comparisons
**When** I compare "Food & Dining" November vs October
**Then** Results focus on that single category
**And** Merchant breakdown shows which merchants contributed to change
**And** Insights like "Spent ₱1,200 more on Grab vs last month" are surfaced

**Given** insufficient data for comparison
**When** I try to compare periods with missing data
**Then** System shows available data clearly
**And** Missing periods are marked: "No data for October 2023"
**And** Comparison is still shown for available periods

**Requirements:** FR27

---

### Story 3.4: Visualization with Plotly Charts

As a user,
I want visual charts showing my spending distribution,
So that I can quickly understand patterns without reading tables.

**Acceptance Criteria:**

**Given** transaction data exists
**When** I implement chart generation
**Then** src/analyze_fin/reports/charts.py contains ChartBuilder class
**And** ChartBuilder uses Plotly for interactive HTML charts
**And** Charts support: pie, line, bar formats

**Given** I want a category breakdown pie chart
**When** I generate a pie chart
**Then** Pie chart shows spending by category
**And** Each slice shows: category name, amount, percentage
**And** Colors are distinct and visually appealing
**And** Chart is interactive (hover shows details)
**And** Largest slice is highlighted or labeled prominently

**Given** I want spending over time line chart
**When** I generate a line chart
**Then** X-axis shows dates (daily, weekly, or monthly)
**And** Y-axis shows spending amount in ₱
**And** Line shows trend clearly
**And** Hover displays exact date and amount
**And** Multiple lines can be shown for category comparison

**Given** I want category comparison bar chart
**When** I generate a bar chart
**Then** X-axis shows categories
**And** Y-axis shows total spending
**And** Bars are sorted by amount descending
**And** Colors match category theme
**And** Hover shows exact amounts and transaction counts

**Given** I want time period comparison bar chart
**When** I generate a comparison bar chart
**Then** Grouped bars show current vs previous period side-by-side
**And** Legend clearly identifies which bar is which period
**And** Visual difference is easy to spot

**Given** charts are generated
**When** I verify the output
**Then** Charts are fully interactive (zoom, pan, hover)
**And** Charts are responsive (work on different screen sizes)
**And** Chart generation completes in <5 seconds (NFR3)
**And** Charts are embedded in HTML reports seamlessly

**Given** empty or insufficient data
**When** I try to generate a chart
**Then** Placeholder message: "Not enough data to generate chart"
**And** Minimum data requirements are communicated
**And** No error is thrown

**Requirements:** FR30, FR31, FR32, NFR3

---

### Story 3.5: Report Generation (HTML & Markdown)

As a user,
I want to generate comprehensive spending reports with charts,
So that I have a complete view of my finances ready to review.

**Acceptance Criteria:**

**Given** the report generation module exists
**When** I implement report builder
**Then** src/analyze_fin/reports/generator.py contains ReportGenerator class
**And** ReportGenerator uses Jinja2 templates for rendering
**And** Templates exist in templates/reports/ folder

**Given** I want to generate an HTML dashboard
**When** I run generate-report command
**Then** HTML report is created with embedded Plotly charts
**And** Report includes: title, date range, summary statistics
**And** Report sections: Category Breakdown, Top Merchants, Spending Over Time, Comparisons
**And** Report generation completes in <5 seconds (NFR3)

**Given** HTML report is generated
**When** I open the report in browser
**Then** Report displays beautifully with proper styling
**And** All charts are interactive
**And** Report includes: spending summary table, pie chart, line chart, bar chart
**And** Color scheme is consistent and professional

**Given** I want to generate a markdown report
**When** I run generate-report --format markdown
**Then** Markdown report is created with tables and text
**And** Report uses markdown tables for data
**And** Charts are represented as ASCII art or text summaries
**And** Report is readable in text editors and renders well on GitHub

**Given** report sections exist
**When** I review the dashboard structure
**Then** Summary section shows: Total Spending, Transaction Count, Average per Day, Date Range
**And** Category section shows: Pie chart + table of categories
**And** Merchants section shows: Top 10 merchants by spending
**And** Trends section shows: Line chart of spending over time
**And** Comparisons section shows: Month-over-month changes

**Given** I want customizable reports
**When** I configure report options
**Then** User can specify: date_range, included_categories, format (HTML/markdown)
**And** User can choose which sections to include
**And** User can set title and add custom notes

**Given** reports are generated
**When** I verify the output location
**Then** HTML reports open automatically in default browser
**And** Markdown reports are saved to specified location
**And** Report filename includes date: "spending_report_2024_11_30.html"
**And** Previous reports are preserved (not overwritten unless specified)

**Given** report generation with insufficient data
**When** User has < 10 transactions
**Then** Report is generated but includes warning: "Limited data - insights may not be representative"
**And** Charts show available data
**And** No errors are thrown

**Given** templates for reports
**When** I review template structure
**Then** templates/reports/dashboard.html.j2 exists for HTML reports
**And** templates/reports/summary.md.j2 exists for markdown reports
**And** Templates use Jinja2 variables and loops correctly
**And** Templates follow project conventions

**Requirements:** FR29, FR33, FR34, AR7, AR8, NFR3

---

### Story 3.6: Natural Language Query Interface

As a user,
I want to ask questions in natural language via Claude,
So that I can get insights without memorizing commands or SQL.

**Acceptance Criteria:**

**Given** the query engine exists
**When** I implement natural language interface
**Then** Claude Code can interpret queries and call appropriate functions
**And** Natural language parser understands common spending questions

**Given** I ask "How much did I spend on food?"
**When** Claude processes the query
**Then** Category="Food & Dining" filter is applied
**And** Total spending is calculated
**And** Response: "You spent ₱8,456.78 on Food & Dining across 42 transactions"

**Given** I ask "What's my top merchant?"
**When** Claude processes the query
**Then** Merchant ranking is calculated
**And** Response: "Your top merchant is Jollibee with ₱2,345.67 spent in 12 transactions"

**Given** I ask "Show me spending last week"
**When** Claude processes the query
**Then** Date range is calculated (last 7 days from today)
**And** Transactions are filtered
**And** Summary is provided with total and breakdown

**Given** I ask "Compare November to October"
**When** Claude processes the query
**Then** Month-over-month comparison is generated
**And** Response includes: both months' totals, difference, percentage change
**And** Notable changes are highlighted

**Given** I ask complex queries
**When** I say "How much did I spend on transport via Grab last month?"
**Then** Multiple filters are combined: category=Transport, merchant=Grab, date=last month
**And** Accurate results are returned
**And** Response is conversational and contextual

**Given** I ask ambiguous questions
**When** I say "How much did I spend?"
**Then** Claude asks for clarification: "For which time period? Last week, last month, or all time?"
**And** User can provide more context
**And** Query is refined and re-executed

**Given** query results are returned
**When** I view Claude's response
**Then** Response is conversational, not just raw data
**And** Response includes context: "In November 2024, you spent..."
**And** Response suggests follow-ups: "Would you like to see the category breakdown?"

**Given** natural language query performance
**When** I verify response time
**Then** Query interpretation + execution + formatting completes in <2 seconds (NFR4)
**And** Claude's response is immediate and helpful

**Requirements:** FR25, NFR4

---

## Epic 4: Advanced Features

Users can export data for external analysis, customize tool settings, and use batch processing for power user workflows.

### Story 4.1: Data Export (CSV & JSON)

As a user,
I want to export my transaction data to CSV and JSON formats,
So that I can analyze data in Excel, Python, or other tools.

**Acceptance Criteria:**

**Given** transactions exist in the database
**When** I implement the export module
**Then** src/analyze_fin/export/exporter.py contains DataExporter class
**And** DataExporter supports: CSV, JSON output formats
**And** DataExporter accepts filter parameters: date_range, category, merchant

**Given** I want to export all transactions to CSV
**When** I run export command with --format csv
**Then** CSV file is created with headers: date, merchant, category, amount, description, account
**And** Dates are in ISO format: 2024-11-15
**And** Amounts are formatted as: 12345.67 (no currency symbol in CSV)
**And** All transactions are included

**Given** I want to export all transactions to JSON
**When** I run export command with --format json
**Then** JSON file is created as array of transaction objects
**And** Each object has keys: transaction_id, date, merchant_normalized, category, amount, description, account, created_at
**And** JSON keys use snake_case (AR21)
**And** Amounts are strings for precision: "12345.67"
**And** Dates are ISO strings: "2024-11-15"

**Given** I want filtered exports
**When** I export with date_range="November 2024" AND category="Food & Dining"
**Then** Only matching transactions are exported
**And** Export filename indicates filters: "export_food_nov2024.csv"
**And** Filter summary is included as comment/metadata

**Given** I want to export query results
**When** I run a query and choose to export results
**Then** Current query filters are applied to export
**And** User can choose format: CSV or JSON
**And** Export preserves query context

**Given** CSV export is complete
**When** I open the file in Excel
**Then** Data loads correctly with proper column types
**And** Currency amounts display correctly
**And** Dates are recognized as dates
**And** UTF-8 encoding preserves Philippine characters (₱, Ñ, etc.)

**Given** JSON export is complete
**When** I load the file in Python/JavaScript
**Then** JSON parses correctly
**And** Data structure is consistent and predictable
**And** Amounts can be converted to Decimal without precision loss

**Given** large dataset export
**When** I export 3,000+ transactions
**Then** Export completes successfully without memory issues
**And** File is created incrementally (streaming)
**And** Progress is shown for large exports

**Given** export with no matching data
**When** Filters result in zero transactions
**Then** Empty file is created with headers only (CSV) or empty array (JSON)
**And** User is informed: "No transactions match filters. Empty export created."

**Requirements:** FR35, FR36, FR37, FR38, AR21, NFR22

---

### Story 4.2: Configuration System

As a user,
I want to configure default settings via a config file,
So that I don't have to specify the same options repeatedly.

**Acceptance Criteria:**

**Given** the project is initialized
**When** I create the config system
**Then** src/analyze_fin/config/settings.py contains ConfigManager class
**And** src/analyze_fin/config/defaults.py contains default values
**And** Config file location is: ~/.analyze-fin/config.yaml

**Given** I run the tool for the first time
**When** No config file exists
**Then** Default config is created automatically at ~/.analyze-fin/config.yaml
**And** Config includes: database_path, output format, categorization settings
**And** Config file has comments explaining each setting

**Given** config.yaml exists
**When** I review the structure
**Then** Config includes section: database (database_path)
**And** Config includes section: output (format, color, report_format)
**And** Config includes section: categorization (auto_categorize, confidence_threshold, prompt_for_unknown)
**And** Config includes section: banks (bpi.password_pattern)

**Given** I want to set database location
**When** I configure database_path: ~/Documents/analyze-fin/data.db
**Then** Database is created at specified location
**And** Path is expanded correctly (~/ to full path)
**And** Directory is created if it doesn't exist

**Given** I want to set default output format
**When** I configure output.format: json
**Then** All commands default to JSON output
**And** Can be overridden with --format flag per command

**Given** I want to configure auto-categorization
**When** I set categorization.auto_categorize: false
**Then** Transactions are not auto-categorized on import
**And** User must manually categorize each transaction

**Given** I set confidence threshold
**When** I configure categorization.confidence_threshold: 0.9
**Then** Only transactions with confidence >= 0.9 are auto-categorized
**And** Lower confidence transactions require manual review

**Given** I want command-line overrides
**When** I run command with --database /tmp/test.db
**Then** CLI flag takes precedence over config file
**And** Override precedence: CLI flags > env vars > config file > defaults

**Given** invalid config values
**When** Config file has syntax errors or invalid values
**Then** ConfigError is raised with descriptive message
**And** Error indicates which setting is invalid
**And** Suggests correct format or valid values

**Given** config backup needed
**When** I want to backup my settings
**Then** Config file is plain YAML, easily copied (NFR24)
**And** User can version control config file
**And** Config can be restored by copying file back

**Requirements:** FR39, FR40, FR41, FR42, FR43, NFR24

---

### Story 4.3: CLI Modes (Interactive vs Batch)

As a user,
I want to run commands in interactive or batch mode,
So that I can choose between guided prompts or automated scripting.

**Acceptance Criteria:**

**Given** the CLI framework exists
**When** I implement mode handling
**Then** src/analyze_fin/cli.py uses Typer for command definition
**And** All commands support --batch and --yes flags
**And** Interactive mode is default

**Given** I run in interactive mode (default)
**When** I import a BPI statement
**Then** System prompts for password: "Enter BPI statement password:"
**And** System asks about unknown merchants: "Category for 'UNKNOWN MERCHANT'?"
**And** User input is required for decisions

**Given** I run in batch mode
**When** I use --batch flag
**Then** No prompts are shown
**And** Default values are used for all decisions
**And** Unknown merchants are categorized as "Uncategorized"
**And** Processing continues without user interaction

**Given** I want to auto-confirm prompts
**When** I use --yes or -y flag
**Then** All yes/no prompts are automatically confirmed
**And** Useful for: re-import confirmations, overwrite warnings
**And** Still prompts for required input (like passwords in interactive)

**Given** batch mode for automation
**When** I script: `analyze-fin parse *.pdf --batch --auto-categorize`
**Then** All PDFs are processed automatically
**And** Script can run unattended (e.g., cron job)
**And** Exit code indicates success/failure for scripting

**Given** interactive mode with duplicate detection
**When** Duplicate is found
**Then** User is prompted: "Duplicate found. [K]eep both, Keep [F]irst, Keep [S]econd?"
**And** User input is awaited
**And** Decision is applied immediately

**Given** batch mode with duplicate detection
**When** Duplicate is found
**Then** Default action is taken: Keep first (skip duplicate)
**And** Summary reports duplicates skipped
**And** No user interaction required

**Given** mode affects output verbosity
**When** I compare interactive vs batch output
**Then** Interactive: Detailed progress, friendly messages, colors
**And** Batch: Minimal output, machine-readable format available
**And** Both: Same functionality, different UX

**Requirements:** FR44, FR45

---

### Story 4.4: Output Format Flags & Exit Codes

As a user,
I want to control output format and get proper exit codes,
So that I can integrate the tool into scripts and pipelines.

**Acceptance Criteria:**

**Given** the CLI supports multiple formats
**When** I implement format handling
**Then** All commands accept --format flag
**And** Valid formats: pretty, json, csv, html, markdown
**And** Default format is "pretty" (human-readable)

**Given** I want pretty output (default)
**When** I run command without --format flag
**Then** Output uses colors and formatting
**And** Tables are aligned and readable
**And** Amounts show ₱ symbol: ₱12,345.67

**Given** I want JSON output
**When** I use --format json
**Then** Output is valid JSON
**And** Can be piped to jq for further processing
**And** All data is included in structured format

**Given** I want CSV output
**When** I use --format csv
**Then** Output is CSV format
**And** Can be redirected to file or piped
**And** Headers are included in first row

**Given** I want to suppress output
**When** I use --quiet or -q flag
**Then** No output is shown except errors
**And** Exit code still indicates success/failure
**And** Useful for scripting where output is ignored

**Given** command succeeds
**When** I check exit code
**Then** Exit code is 0
**And** Shell scripts can use: `if analyze-fin parse statement.pdf; then ...`

**Given** command fails (general error)
**When** I check exit code
**Then** Exit code is 1
**And** Error message is printed to stderr

**Given** parse fails (PDF issue)
**When** Invalid or corrupted PDF is provided
**Then** Exit code is 2 (parse-specific)
**And** Error message explains PDF issue

**Given** configuration error
**When** Config file is invalid or missing required settings
**Then** Exit code is 3 (config-specific)
**And** Error message points to config issue

**Given** database error
**When** Database cannot be accessed or is corrupted
**Then** Exit code is 4 (database-specific)
**And** Error message suggests recovery steps

**Given** output is piped or redirected
**When** I run: `analyze-fin query --format json | jq '.[] | .amount'`
**Then** JSON output goes to stdout
**And** Progress/info messages go to stderr (not polluting pipe)
**And** Pipeline works correctly

**Requirements:** FR46, FR47, FR48

---

### Story 4.5: Claude Skills Integration

As a user,
I want to use Claude Skills to interact conversationally with my data,
So that I can use natural language instead of memorizing commands.

**Acceptance Criteria:**

**Given** the CLI commands exist
**When** I create Claude Skills
**Then** .claude/commands/ directory contains skill definition files
**And** Each skill maps to a CLI command
**And** Skills: parse.md, categorize.md, report.md, query.md, export.md, deduplicate.md

**Given** parse.md skill exists
**When** User says "Parse my November statements"
**Then** Claude executes: parse-statements with appropriate files
**And** Claude handles password prompts for BPI
**And** Claude reports quality scores and results

**Given** categorize.md skill exists
**When** User says "Categorize my uncategorized transactions"
**Then** Claude executes: categorize-transactions --interactive
**And** Claude guides user through categorization
**And** Claude applies learning to future transactions

**Given** report.md skill exists
**When** User says "Show me my spending report"
**Then** Claude executes: generate-report --format html
**And** HTML report opens in browser
**And** Claude summarizes key insights

**Given** query.md skill exists
**When** User says "How much did I spend on food?"
**Then** Claude executes: query-spending --category "Food & Dining"
**And** Claude formats response conversationally
**And** Claude offers follow-up questions

**Given** export.md skill exists
**When** User says "Export my November data to CSV"
**Then** Claude executes: export-data --date-range November --format csv
**And** Claude confirms export location
**And** Claude provides file path for user

**Given** deduplicate.md skill exists
**When** User says "Find and remove duplicates"
**Then** Claude executes: deduplicate --interactive
**And** Claude guides through duplicate review
**And** Claude confirms decisions before applying

**Given** Skills have help text
**When** User asks "What can analyze-fin do?"
**Then** Claude lists all available skills
**And** Each skill has clear description
**And** Examples are provided for common use cases

**Given** Skills handle errors gracefully
**When** Command fails (e.g., file not found)
**Then** Claude explains error in user-friendly terms
**And** Claude suggests corrections
**And** Claude doesn't expose raw error traces unless --verbose

**Given** Skills support context
**When** User has multi-turn conversation
**Then** Claude remembers previous queries/commands
**And** User can reference: "Export those results" after a query
**And** Context makes workflow more natural

**Requirements:** FR25, AR17-AR18

---

### Story 4.6: Advanced CLI Features & Polish

As a developer,
I want the CLI to follow best practices and provide excellent UX,
So that users have a professional, polished experience.

**Acceptance Criteria:**

**Given** the Typer CLI is implemented
**When** I review command structure
**Then** All commands have clear help text
**And** Type hints auto-generate parameter documentation
**And** Command examples are provided in help

**Given** I want to see help
**When** I run analyze-fin --help
**Then** Main help shows all available commands
**And** Each command has one-line description
**And** Usage examples are included

**Given** I want command-specific help
**When** I run analyze-fin parse --help
**Then** Detailed help for parse command is shown
**And** All flags and options are documented
**And** Examples show common use cases

**Given** I want to check version
**When** I run analyze-fin --version
**Then** Version number is displayed
**And** Format: "analyze-fin version 0.1.0"

**Given** invalid arguments are provided
**When** I run command with wrong flag or missing required argument
**Then** Clear error message explains the issue
**And** Help text is shown automatically
**And** Exit code is 2 (usage error)

**Given** file path arguments
**When** I provide paths with spaces
**Then** Paths are handled correctly (quoted or escaped)
**And** Shell expansion works (e.g., *.pdf)
**And** Relative and absolute paths both work

**Given** output formatting
**When** I view pretty output
**Then** Rich library is used for colors and tables
**And** Currency amounts are right-aligned in tables
**And** Colors enhance readability (not just decoration)

**Given** progress indicators
**When** Long operations run (batch import, large export)
**Then** Progress bar or spinner is shown
**And** Current item being processed is indicated
**And** Estimated time remaining is shown when possible

**Given** testing infrastructure
**When** I review tests/test_cli.py
**Then** CLI commands are tested with Typer's test runner
**And** Exit codes are verified
**And** Output format validation exists
**And** Mocked filesystem and database for tests

**Given** error handling
**When** Exceptions occur
**Then** User-friendly error messages are shown (not tracebacks)
**And** --verbose flag enables full traceback for debugging
**And** Logs include timestamp and context for troubleshooting

**Given** the tool is production-ready
**When** I verify completeness
**Then** All NFRs are met (performance, accuracy, integrity, security)
**And** All FRs are implemented and tested
**And** Documentation exists (README, help text)
**And** Project follows architecture and context rules exactly

**Requirements:** FR44-FR48, AR5, AR22-AR24, All NFRs

