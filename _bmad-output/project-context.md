---
project_name: 'analyze-fin'
user_name: 'arjay'
date: '2025-12-15'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow_rules', 'critical_rules']
status: 'complete'
rule_count: 47
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

**Runtime:** Python 3.11+ (type hints required throughout)

**Package Manager:** uv (NOT pip or Poetry)
- Use `uv add` for dependencies
- Use `uv add --dev` for dev dependencies
- Lock file: `uv.lock`

**Core Stack:**
- SQLAlchemy 2.0 (use `Mapped[]` type annotations, not legacy `Column()`)
- Alembic for migrations (never manual schema changes)
- SQLite with WAL mode enabled
- Typer for CLI (type hints generate help automatically)

**PDF & Visualization:**
- pdfplumber for PDF extraction (not PyPDF2)
- Plotly for charts (not matplotlib)
- Jinja2 for HTML/markdown templates

**Code Quality:**
- ruff for linting AND formatting (not black + flake8)
- pytest for testing (not unittest)

## Python-Specific Rules

**Type Hints (REQUIRED on all public functions):**
- Use modern syntax: `list[str]`, `dict[str, int]`, `str | None`
- NOT legacy: `List[str]`, `Dict[str, int]`, `Optional[str]`
- SQLAlchemy: `Mapped[str]`, `Mapped[int | None]`

**Import Style:**
```python
# CORRECT - absolute imports
from analyze_fin.parsers.base import BaseBankParser
from analyze_fin.database.models import Transaction

# WRONG - relative imports between modules
from ..database.models import Transaction
```

**Exception Hierarchy:**
```python
AnalyzeFinError          # Base - catch-all for CLI
├── ParseError           # PDF parsing failures
├── ValidationError      # Data validation failures
├── DuplicateError       # Duplicate transaction detected
└── ConfigError          # Configuration errors
```

**Error Handling Pattern:**
- Low-level code raises specific exceptions with technical details
- CLI layer catches and formats user-friendly messages
- `--verbose` flag shows full traceback

## Framework-Specific Rules

**Typer CLI:**
```python
# Commands auto-generate help from docstrings and type hints
@app.command()
def parse(
    pdf_path: Path,
    bank: str | None = typer.Option(None, help="Bank type override"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Parse a bank statement PDF and import transactions."""
```

**SQLAlchemy 2.0 Models:**
```python
# CORRECT - SQLAlchemy 2.0 style
class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str | None]  # nullable

# WRONG - legacy style
class Transaction(Base):
    id = Column(Integer, primary_key=True)  # NO!
```

**Parser Strategy Pattern:**
```python
class BaseBankParser(ABC):
    @abstractmethod
    def extract_transactions(self, pdf_path: Path) -> list[RawTransaction]:
        """Must be implemented by each bank parser."""

    def calculate_quality_score(self, transactions: list) -> float:
        """Shared quality scoring logic."""
```

**Bank Parser Naming:** `{BankName}Parser` in `parsers/{bank}.py`
- `GCashParser` in `parsers/gcash.py`
- `BPIParser` in `parsers/bpi.py`
- `MayaParser` in `parsers/maya.py`

## Testing Rules

**Test Organization:**
```
tests/
├── conftest.py              # Shared fixtures (db session, sample data)
├── test_cli.py              # CLI integration tests
├── parsers/
│   ├── test_gcash_parser.py
│   └── test_bpi_parser.py
├── database/
│   └── test_models.py
└── fixtures/
    └── sample_statements/   # Test PDF files
```

**Fixture Patterns:**
```python
# conftest.py - shared fixtures
@pytest.fixture
def db_session():
    """In-memory SQLite for tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def sample_transaction(db_session):
    """Pre-populated transaction for tests."""
```

**Test Naming:**
- Files: `test_{module}.py` (e.g., `test_gcash_parser.py`)
- Functions: `test_{behavior}` (e.g., `test_extracts_date_from_gcash_row`)
- Use descriptive names that explain WHAT is tested

**What to Test:**
- Parser extraction accuracy with real PDF samples
- Categorization rules with known merchant mappings
- Duplicate detection edge cases
- CLI exit codes for success/failure

## Code Quality & Style Rules

**Naming Conventions (PEP 8 - strictly enforced):**
| Element | Convention | Example |
|---------|------------|---------|
| Files | snake_case | `gcash_parser.py` |
| Functions | snake_case | `extract_transactions()` |
| Variables | snake_case | `transaction_count` |
| Classes | PascalCase | `GCashParser` |
| Constants | UPPER_SNAKE | `DEFAULT_CATEGORY` |
| Private | _underscore | `_parse_table()` |

**Database Naming:**
| Element | Convention | Example |
|---------|------------|---------|
| Tables | snake_case plural | `transactions` |
| Columns | snake_case | `created_at` |
| Foreign Keys | `{table}_id` | `account_id` |
| Indexes | `ix_{table}_{col}` | `ix_transactions_date` |

**Currency Formatting (Philippine Peso):**
- Internal: `Decimal` type, no formatting
- Display: `₱{amount:,.2f}` → `₱12,345.67`
- Negative: `(₱1,234.56)` or `-₱1,234.56`

**Date Formatting:**
- Internal/Storage: ISO `2024-11-15`
- JSON Output: ISO `2024-11-15`
- Display/Reports: `Nov 15, 2024`

**JSON Output Keys:** Always `snake_case`
```json
{
  "transaction_id": 123,
  "amount": "1234.56",
  "created_at": "2024-11-15"
}
```

## Development Workflow Rules

**Project Layout:**
```
analyze-fin/
├── src/analyze_fin/     # Source code (src layout)
├── tests/               # Tests (separate folder)
├── templates/           # Jinja2 templates
├── data/                # Static data files
├── alembic/             # Database migrations
└── .claude/commands/    # Claude Skills
```

**Config Location:** `~/.analyze-fin/config.yaml`
- User-specific config in XDG-compliant location
- Override precedence: CLI flags > env vars > config file

**CLI Exit Codes:**
- `0` = Success
- `1` = General error
- `2` = Usage/argument error
- Non-zero for any failure (enables shell scripting)

**Database Migrations:**
```bash
# Create migration after model changes
uv run alembic revision --autogenerate -m "add category column"

# Apply migrations
uv run alembic upgrade head
```

**Running Commands:**
```bash
# Development
uv run analyze-fin parse statement.pdf
uv run pytest
uv run ruff check .
uv run ruff format .
```

## Critical Don't-Miss Rules

**NEVER Do These (Anti-Patterns):**
- Use `float` for currency amounts → Use `Decimal`
- Use SQLAlchemy 1.x `Column()` syntax → Use `Mapped[]`
- Use `pip install` → Use `uv add`
- Transmit data to cloud/external services → Local-only processing
- Store PDF passwords in database → Process and discard
- Use relative imports between modules → Absolute imports only
- Co-locate tests with source → Separate `tests/` folder

**Philippine Bank-Specific Rules:**
- GCash dates: `MMM DD, YYYY` format (e.g., "Nov 15, 2024")
- BPI dates: `MM/DD/YYYY` format
- Maya dates: ISO format typically
- Always parse dates explicitly, never assume format

**Duplicate Detection Rules:**
- Match on: date + amount + description hash
- Same transaction across accounts = NOT duplicate (internal transfer)
- Same transaction in same account = duplicate
- Zero false positives required (prefer missing duplicate over false positive)

**Quality Score Thresholds:**
- `>= 0.95`: High confidence, auto-accept
- `0.80 - 0.95`: Medium confidence, review flagged rows
- `< 0.80`: Low confidence, manual review required

**Graceful Degradation:**
- Partial parse failure: Save successful rows, report failures
- Unknown merchant: Categorize as "Uncategorized", don't fail
- Missing category: Allow null, don't require default

**Security Rules:**
- All data stays local (SQLite file on user's machine)
- No telemetry, no external API calls
- PDF passwords used once for extraction, never stored
- No PII in logs (transaction descriptions OK, but no account numbers)

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge

**For Humans:**
- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time

---

_Last Updated: 2025-12-15_
