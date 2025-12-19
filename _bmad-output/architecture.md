---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - _bmad-output/prd.md
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2025-12-15'
project_name: 'analyze-fin'
user_name: 'arjay'
date: '2025-12-15'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (48 total across 8 capability areas):**
- Statement Parsing (FR1-7): PDF import, bank detection, password handling, batch operations, quality scoring
- Transaction Management (FR8-13): SQLite storage, deduplication, internal transfer detection
- Categorization & Merchant Intelligence (FR14-20): Auto-categorize, normalization, learning system
- Querying & Analysis (FR21-28): Category/merchant/date queries, natural language via Claude, aggregations
- Reporting & Visualization (FR29-34): Dashboards, pie/line/bar charts, HTML/markdown formats
- Data Export (FR35-38): CSV, JSON, filtered exports
- Configuration & Settings (FR39-43): Config file, database location, preferences
- CLI Interface (FR44-48): Interactive/batch modes, format flags, exit codes

**Non-Functional Requirements:**
- Performance: <10s PDF parsing, <5s report generation, <2s query response
- Data Accuracy: >95% extraction, >90% categorization, 0% false positive duplicates
- Data Integrity: Zero transaction loss, SQLite with WAL mode, referential integrity
- Security: Local-first architecture, no cloud transmission, passwords not stored
- Backup/Recovery: Portable SQLite file, CSV/JSON export capability
- Reliability: Graceful degradation, quality scoring for confidence levels

### Scale & Complexity

- **Primary domain:** CLI Tool / Data Processing Pipeline
- **Complexity level:** Medium
- **Data volume:** Moderate (hundreds to thousands of transactions per user)
- **User concurrency:** Single user (local-first personal tool)
- **Integration complexity:** Low (Claude Skills interface only)

### Technical Constraints & Dependencies

- Python backend (user's existing tech stack)
- SQLite for local storage (no external database dependencies)
- Claude Skills as primary interface (requires Claude Code environment)
- PDF parsing libraries needed for bank statement extraction
- Plotly for HTML chart generation
- Local-first: all processing on user's machine, zero cloud dependencies

### Cross-Cutting Concerns Identified

1. **Error Handling**: Graceful degradation - partial failures don't lose successful data
2. **Quality Scoring**: Confidence levels for parsing accuracy across all operations
3. **Output Format Flexibility**: 5 formats (pretty, JSON, CSV, HTML, markdown) throughout
4. **Config Management**: File-based config with command-line flag overrides
5. **Mode Switching**: Batch vs interactive mode affects prompting and defaults
6. **Merchant Learning**: Corrections persist and apply to future similar transactions

## Starter Template Evaluation

### Primary Technology Domain

**Python CLI Tool / Data Processing Pipeline** - No traditional "starter template" applies. We're establishing project structure and tooling conventions from scratch.

### Technical Stack Decisions

| Category | Decision | Rationale |
|----------|----------|-----------|
| **Package Manager** | **uv** | Fast Rust-based tooling, modern, handles venv + deps |
| **Project Structure** | **src layout** | `src/analyze_fin/` - cleaner imports |
| **CLI Framework** | **Typer** | Type-hint based, auto-help generation |
| **Testing** | **pytest** | Industry standard, excellent fixtures |
| **Code Quality** | **ruff** | Fast linter + formatter, replaces multiple tools |
| **Database** | **SQLite** | Local-first, zero dependencies |
| **PDF Parsing** | **pdfplumber** or **pypdf** | Bank statement extraction |
| **Charts** | **Plotly** | Interactive HTML visualizations |

### Project Initialization

```bash
# Create project with uv
uv init analyze-fin
cd analyze-fin

# Add dependencies
uv add typer rich pdfplumber plotly sqlalchemy

# Add dev dependencies
uv add --dev pytest ruff

# Create src layout
mkdir -p src/analyze_fin
touch src/analyze_fin/__init__.py
```

### Project Structure

```
analyze-fin/
├── pyproject.toml          # uv/project config
├── uv.lock                  # lockfile
├── README.md
├── src/
│   └── analyze_fin/
│       ├── __init__.py
│       ├── cli.py           # Typer CLI commands
│       ├── parsers/         # Bank-specific PDF parsers
│       ├── database/        # SQLite models & queries
│       ├── categorization/  # Merchant mapping & learning
│       ├── reports/         # HTML/chart generation
│       └── skills/          # Claude Skills definitions
├── tests/
├── data/
│   └── merchant_mapping.json
└── .claude/
    └── commands/            # Claude Skills
```

### Architectural Decisions Provided by Stack

- **Language & Runtime:** Python 3.11+, type hints throughout
- **Dependency Management:** uv with lockfile for reproducible builds
- **CLI Structure:** Typer commands map 1:1 to Claude Skills
- **Code Organization:** Domain-driven folders (parsers, database, categorization, reports)
- **Development Experience:** ruff for fast linting, pytest for testing

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Database ORM: SQLAlchemy
- Parser Architecture: Strategy pattern
- Report Templating: Jinja2

**Important Decisions (Shape Architecture):**
- Migration Strategy: Alembic
- Config Format: YAML

**Deferred Decisions (Post-MVP):**
- Caching strategy (not needed for local tool initially)
- Plugin architecture (future extensibility)

### Data Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **ORM** | SQLAlchemy 2.0 | Type-safe, Pythonic, mature ecosystem |
| **Migrations** | Alembic | Version-controlled schema changes, rollback capability |
| **Connection** | SQLite with WAL mode | Crash recovery, concurrent reads |

**Schema Design Approach:**
```python
# SQLAlchemy declarative models
class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    bank_type: Mapped[str]  # gcash, bpi, maya
    statements: Mapped[list["Statement"]] = relationship(back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    statement_id: Mapped[int] = mapped_column(ForeignKey("statements.id"))
    date: Mapped[datetime]
    description: Mapped[str]
    amount: Mapped[Decimal]
    category: Mapped[str | None]
    merchant_normalized: Mapped[str | None]
```

### Parser Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Pattern** | Strategy pattern | Extensible, clean separation per bank |
| **Base Class** | `BaseBankParser` | Shared validation, quality scoring |
| **Bank Parsers** | `GCashParser`, `BPIParser`, `MayaParser` | Bank-specific extraction logic |

**Parser Structure:**
```python
class BaseBankParser(ABC):
    @abstractmethod
    def extract_transactions(self, pdf_path: Path) -> list[RawTransaction]: ...

    def calculate_quality_score(self, transactions: list) -> float: ...
    def detect_bank_type(self, pdf_path: Path) -> str | None: ...

class GCashParser(BaseBankParser):
    def extract_transactions(self, pdf_path: Path) -> list[RawTransaction]:
        # GCash-specific table extraction
```

### Report Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Templating** | Jinja2 | Clean separation, maintainable templates |
| **HTML Reports** | Jinja2 + Plotly | Interactive charts embedded in template |
| **Markdown Reports** | Jinja2 | Same data, different template |

**Template Structure:**
```
templates/
├── reports/
│   ├── dashboard.html.j2
│   ├── monthly_summary.html.j2
│   └── export.md.j2
└── components/
    ├── chart_pie.html.j2
    └── transaction_table.html.j2
```

### Configuration Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Format** | YAML | Human-readable, standard for config |
| **Location** | `~/.analyze-fin/config.yaml` | XDG-compliant user config |
| **Override** | CLI flags > env vars > config file | Standard precedence |

### Decision Impact Analysis

**Implementation Sequence:**
1. SQLAlchemy models + Alembic setup (foundation)
2. Base parser + first bank parser (GCash)
3. Jinja2 templates + report generation
4. Additional parsers (BPI, Maya)
5. Claude Skills integration

**Cross-Component Dependencies:**
- Parsers depend on SQLAlchemy models for transaction structure
- Reports depend on SQLAlchemy queries for data
- All components share config loading

## Implementation Patterns & Consistency Rules

### Naming Patterns

**Python Code (PEP 8):**

| Element | Convention | Example |
|---------|------------|---------|
| Files/Modules | snake_case | `gcash_parser.py`, `merchant_mapping.py` |
| Functions | snake_case | `extract_transactions()`, `calculate_quality_score()` |
| Variables | snake_case | `transaction_count`, `raw_description` |
| Classes | PascalCase | `GCashParser`, `Transaction`, `MerchantMapping` |
| Constants | UPPER_SNAKE | `DEFAULT_CATEGORY`, `SUPPORTED_BANKS` |
| Private | leading underscore | `_parse_table()`, `_validate_row()` |

**Database (SQLAlchemy):**

| Element | Convention | Example |
|---------|------------|---------|
| Tables | snake_case plural | `transactions`, `accounts`, `statements` |
| Columns | snake_case | `created_at`, `merchant_name`, `quality_score` |
| Foreign Keys | `{singular_table}_id` | `account_id`, `statement_id` |
| Indexes | `ix_{table}_{column}` | `ix_transactions_date` |

### Structure Patterns

**Test Organization:** Separate `tests/` folder mirroring `src/` structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_cli.py              # CLI command tests
├── parsers/
│   ├── test_gcash_parser.py
│   ├── test_bpi_parser.py
│   └── test_maya_parser.py
├── database/
│   └── test_models.py
└── fixtures/
    └── sample_statements/   # Test PDF files
```

**Fixture Naming:** `test_*.py` files, `test_*` functions, fixtures in `conftest.py`

### Error Handling Patterns

**Exception Hierarchy:**
```python
# src/analyze_fin/exceptions.py
class AnalyzeFinError(Exception):
    """Base exception for all analyze-fin errors."""

class ParseError(AnalyzeFinError):
    """PDF parsing failed."""

class ValidationError(AnalyzeFinError):
    """Data validation failed."""

class DuplicateError(AnalyzeFinError):
    """Duplicate transaction detected."""

class ConfigError(AnalyzeFinError):
    """Configuration error."""
```

**Error Flow:**
1. Low-level code raises specific exceptions with technical details
2. Exceptions bubble up to CLI layer
3. CLI catches and formats user-friendly messages
4. `--verbose` flag shows full traceback

### Format Patterns

**Currency:**
- Internal: `Decimal` type, no formatting
- Display: `₱{amount:,.2f}` (e.g., `₱12,345.67`)
- Negative: `(₱1,234.56)` or `-₱1,234.56`

**Dates:**
- Internal/Storage: ISO format `2024-11-15`
- JSON Output: ISO format `2024-11-15`
- Reports/Display: `Nov 15, 2024`
- With time: `2024-11-15T14:30:00`

**JSON Output:**
- Keys: snake_case (Python convention)
- Decimals: String representation for precision
- Dates: ISO string format
- Nulls: Explicit `null`, not omitted

**Example JSON:**
```json
{
  "transaction_id": 123,
  "date": "2024-11-15",
  "amount": "1234.56",
  "category": "Food & Dining",
  "merchant_normalized": "Jollibee"
}
```

### Logging Patterns

**Log Levels:**
- `DEBUG`: Detailed parsing info, SQL queries
- `INFO`: Import started/completed, report generated
- `WARNING`: Low quality score, unknown merchant
- `ERROR`: Parse failures, validation errors

**Log Format:**
```python
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### Enforcement Guidelines

**All AI Agents MUST:**
1. Follow PEP 8 naming conventions exactly as documented
2. Use the exception hierarchy for all errors
3. Format currency and dates as specified
4. Place tests in `tests/` folder, not co-located
5. Use type hints on all public functions

**Verification:**
- `ruff check` catches naming violations
- `pytest` validates test organization
- PR review checks pattern compliance

## Project Structure & Boundaries

### Complete Project Directory Structure

```
analyze-fin/
├── pyproject.toml                    # uv project config, dependencies
├── uv.lock                           # Dependency lockfile
├── README.md
├── .gitignore
├── .python-version                   # Python 3.11+
├── ruff.toml                         # Linter/formatter config
├── alembic.ini                       # Migration config
│
├── src/
│   └── analyze_fin/
│       ├── __init__.py
│       ├── cli.py                    # Typer CLI entry point (FR44-48)
│       ├── exceptions.py             # Custom exception hierarchy
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py           # Config loading (FR39-43)
│       │   └── defaults.py           # Default values
│       │
│       ├── database/
│       │   ├── __init__.py
│       │   ├── models.py             # SQLAlchemy models (FR8-13)
│       │   ├── session.py            # Database connection
│       │   └── queries.py            # Common queries
│       │
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── base.py               # BaseBankParser (FR1-7)
│       │   ├── gcash.py              # GCashParser
│       │   ├── bpi.py                # BPIParser
│       │   ├── maya.py               # MayaParser
│       │   └── detector.py           # Bank type detection (FR2)
│       │
│       ├── categorization/
│       │   ├── __init__.py
│       │   ├── categorizer.py        # Auto-categorization (FR14-17)
│       │   ├── normalizer.py         # Merchant normalization (FR15)
│       │   └── learning.py           # Learning from corrections (FR17)
│       │
│       ├── deduplication/
│       │   ├── __init__.py
│       │   ├── detector.py           # Duplicate detection (FR9-11)
│       │   └── resolver.py           # Interactive resolution
│       │
│       ├── queries/
│       │   ├── __init__.py
│       │   ├── spending.py           # Spending queries (FR21-28)
│       │   └── aggregations.py       # Aggregations & comparisons
│       │
│       ├── reports/
│       │   ├── __init__.py
│       │   ├── generator.py          # Report generation (FR29-34)
│       │   ├── charts.py             # Plotly chart builders
│       │   └── formatters.py         # Output formatters (pretty/json/csv/md)
│       │
│       ├── export/
│       │   ├── __init__.py
│       │   └── exporter.py           # CSV/JSON export (FR35-38)
│       │
│       └── skills/
│           ├── __init__.py
│           └── definitions.py        # Claude Skills metadata
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                     # Migration files
│
├── templates/
│   ├── reports/
│   │   ├── dashboard.html.j2
│   │   ├── monthly_summary.html.j2
│   │   └── export.md.j2
│   └── components/
│       ├── chart_pie.html.j2
│       └── transaction_table.html.j2
│
├── data/
│   └── merchant_mapping.json         # 150+ Philippine merchants
│
├── tests/
│   ├── conftest.py                   # Shared fixtures
│   ├── test_cli.py
│   ├── parsers/
│   │   ├── test_gcash_parser.py
│   │   ├── test_bpi_parser.py
│   │   └── test_maya_parser.py
│   ├── database/
│   │   └── test_models.py
│   ├── categorization/
│   │   └── test_categorizer.py
│   └── fixtures/
│       └── sample_statements/        # Test PDFs
│
└── .claude/
    └── commands/
        ├── parse.md                  # Claude Skill: parse statements
        ├── categorize.md             # Claude Skill: categorize
        ├── report.md                 # Claude Skill: generate report
        ├── query.md                  # Claude Skill: query spending
        ├── export.md                 # Claude Skill: export data
        └── deduplicate.md            # Claude Skill: resolve duplicates
```

### FR Category to Directory Mapping

| FR Category | Directory | Key Files |
|-------------|-----------|-----------|
| Statement Parsing (FR1-7) | `src/analyze_fin/parsers/` | `base.py`, `gcash.py`, `bpi.py`, `maya.py` |
| Transaction Management (FR8-13) | `src/analyze_fin/database/` | `models.py`, `queries.py` |
| Categorization (FR14-20) | `src/analyze_fin/categorization/` | `categorizer.py`, `normalizer.py` |
| Querying & Analysis (FR21-28) | `src/analyze_fin/queries/` | `spending.py`, `aggregations.py` |
| Reporting (FR29-34) | `src/analyze_fin/reports/` | `generator.py`, `charts.py` |
| Data Export (FR35-38) | `src/analyze_fin/export/` | `exporter.py` |
| Configuration (FR39-43) | `src/analyze_fin/config/` | `settings.py` |
| CLI Interface (FR44-48) | `src/analyze_fin/` | `cli.py` |

### Data Flow

```
PDF Statement
     ↓
[Parser] (bank-specific extraction)
     ↓
[Deduplication] (detect duplicates)
     ↓
[Categorization] (auto-categorize, normalize)
     ↓
[Database] (SQLite storage)
     ↓
[Queries] ←→ [Reports/Export]
     ↓
User Output (HTML/JSON/CSV/Terminal)
```

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**

| Stack Component | Version/Choice | Compatible With |
|-----------------|----------------|-----------------|
| uv | Latest | All Python packages |
| SQLAlchemy | 2.0 | Alembic, SQLite |
| Alembic | Latest | SQLAlchemy 2.0 |
| Typer | Latest | Python 3.11+ |
| pdfplumber | Latest | Python 3.11+ |
| Plotly | Latest | Jinja2 templates |
| Jinja2 | Latest | Python 3.11+ |
| pytest | Latest | src layout |
| ruff | Latest | Python 3.11+ |

**No conflicts detected.** All libraries work together in Python 3.11+ ecosystem.

**Pattern Consistency:** All patterns align with Python/PEP 8 conventions.

**Structure Alignment:** Project structure supports all architectural decisions.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**

| FR Category | FRs | Architecture Support |
|-------------|-----|---------------------|
| Statement Parsing | FR1-7 | `parsers/` with strategy pattern |
| Transaction Management | FR8-13 | `database/` with SQLAlchemy |
| Categorization | FR14-20 | `categorization/` module |
| Querying | FR21-28 | `queries/` module |
| Reporting | FR29-34 | `reports/` + Jinja2 templates |
| Export | FR35-38 | `export/` module |
| Configuration | FR39-43 | `config/` + YAML |
| CLI | FR44-48 | Typer in `cli.py` |

**All 48 FRs architecturally supported.**

**Non-Functional Requirements Coverage:**

| NFR | Architecture Support |
|-----|---------------------|
| Performance (<10s parse) | pdfplumber efficient extraction |
| Data Accuracy (>95%) | Quality scoring in base parser |
| Data Integrity | SQLite WAL + foreign keys |
| Security (local-first) | No cloud dependencies |
| Backup/Recovery | SQLite portable + CSV export |

### Implementation Readiness ✅

**Architecture Completeness Checklist:**

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Requirements to structure mapping complete

### Gap Analysis

**Critical Gaps:** None

**Minor Gaps (addressed during implementation):**
- Claude Skills `.md` files content (implementation task)
- `merchant_mapping.json` initial data (data entry task)

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** HIGH

**Key Strengths:**
1. Clean separation of concerns (parsers, database, categorization, reports)
2. Strategy pattern enables easy bank addition
3. Consistent patterns prevent AI agent conflicts
4. All 48 requirements traceable to specific code locations

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2025-12-15
**Document Location:** `_bmad-output/architecture.md`

### Final Architecture Deliverables

**Complete Architecture Document:**
- All architectural decisions documented with specific versions
- Implementation patterns ensuring AI agent consistency
- Complete project structure with all files and directories
- Requirements to architecture mapping
- Validation confirming coherence and completeness

**Implementation Ready Foundation:**
- 12+ architectural decisions made
- 5 implementation pattern categories defined
- 8 architectural components specified
- 48 functional requirements fully supported

### Implementation Handoff

**For AI Agents:**
This architecture document is your complete guide for implementing analyze-fin. Follow all decisions, patterns, and structures exactly as documented.

**First Implementation Priority:**
```bash
uv init analyze-fin
cd analyze-fin
uv add typer rich pdfplumber plotly sqlalchemy jinja2 pyyaml
uv add --dev pytest ruff alembic
```

**Development Sequence:**
1. Initialize project using uv
2. Create src layout directory structure
3. Set up SQLAlchemy models + Alembic migrations
4. Implement base parser + GCash parser first
5. Build categorization and report modules
6. Create Claude Skills definitions

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

