# Story 4.2: Configuration System

Status: done

---

## Story

As a user,
I want to configure default settings via a config file,
So that I don't have to specify the same options repeatedly.

---

## Acceptance Criteria

### AC1: Config System Infrastructure
**Given** the project is initialized
**When** I create the config system
**Then** `src/analyze_fin/config/settings.py` contains `ConfigManager` class
**And** `src/analyze_fin/config/defaults.py` contains default values
**And** Config file location is: `~/.analyze-fin/config.yaml`

### AC2: Auto-Generate Default Config
**Given** I run the tool for the first time
**When** No config file exists
**Then** Default config is created automatically at `~/.analyze-fin/config.yaml`
**And** Config includes: database_path, output format, categorization settings
**And** Config file has comments explaining each setting

### AC3: Config Structure
**Given** config.yaml exists
**When** I review the structure
**Then** Config includes section: `database` (database_path)
**And** Config includes section: `output` (format, color, report_format)
**And** Config includes section: `categorization` (auto_categorize, confidence_threshold, prompt_for_unknown)
**And** Config includes section: `banks` (bpi.password_pattern)

### AC4: Database Location Config
**Given** I want to set database location
**When** I configure `database_path: ~/Documents/analyze-fin/data.db`
**Then** Database is created at specified location
**And** Path is expanded correctly (`~/` to full path)
**And** Directory is created if it doesn't exist

### AC5: Output Format Config
**Given** I want to set default output format
**When** I configure `output.format: json`
**Then** All commands default to JSON output
**And** Can be overridden with `--format` flag per command

### AC6: Auto-Categorization Config
**Given** I want to configure auto-categorization
**When** I set `categorization.auto_categorize: false`
**Then** Transactions are not auto-categorized on import
**And** User must manually categorize each transaction

### AC7: Confidence Threshold Config
**Given** I set confidence threshold
**When** I configure `categorization.confidence_threshold: 0.9`
**Then** Only transactions with confidence >= 0.9 are auto-categorized
**And** Lower confidence transactions require manual review

### AC8: CLI Override Precedence
**Given** I want command-line overrides
**When** I run command with `--database /tmp/test.db`
**Then** CLI flag takes precedence over config file
**And** Override precedence: CLI flags > env vars > config file > defaults

### AC9: Config Validation
**Given** invalid config values
**When** Config file has syntax errors or invalid values
**Then** `ConfigError` is raised with descriptive message
**And** Error indicates which setting is invalid
**And** Suggests correct format or valid values

### AC10: Config Backup
**Given** config backup needed
**When** I want to backup my settings
**Then** Config file is plain YAML, easily copied (NFR24)
**And** User can version control config file
**And** Config can be restored by copying file back

**Requirements:** FR39, FR40, FR41, FR42, FR43, NFR24

---

## Tasks / Subtasks

### Task 1: Create Config Module Structure (AC: 1)
- [x] 1.1: Create `src/analyze_fin/config/__init__.py`
- [x] 1.2: Create `src/analyze_fin/config/defaults.py` with DEFAULT_CONFIG dict
- [x] 1.3: Create `src/analyze_fin/config/settings.py` with ConfigManager class
- [x] 1.4: Add ConfigError to exceptions.py if not exists (already existed)

### Task 2: Implement ConfigManager Class (AC: 1, 2, 3, 4)
- [x] 2.1: Implement `ConfigManager.__init__()` to locate config file
- [x] 2.2: Implement `ConfigManager.load()` to read YAML config
- [x] 2.3: Implement `ConfigManager.create_default()` to generate initial config
- [x] 2.4: Implement path expansion for `~` and environment variables
- [x] 2.5: Auto-create parent directories if needed

### Task 3: Implement Config Sections (AC: 3, 4, 5, 6, 7)
- [x] 3.1: Implement `database` section handling (database_path)
- [x] 3.2: Implement `output` section handling (format, color, report_format)
- [x] 3.3: Implement `categorization` section handling (auto_categorize, confidence_threshold)
- [x] 3.4: Implement `banks` section handling (bpi.password_pattern)

### Task 4: Implement Override Precedence (AC: 8)
- [x] 4.1: Implement environment variable reading (ANALYZE_FIN_* prefix)
- [x] 4.2: Create `get_config_value(key, cli_override=None)` method
- [x] 4.3: Implement precedence: CLI > env > config > defaults
- [x] 4.4: Update CLI commands to use ConfigManager

### Task 5: Implement Validation (AC: 9)
- [x] 5.1: Implement YAML syntax error handling
- [x] 5.2: Implement value type validation (str, int, bool, float)
- [x] 5.3: Implement path validation (exists, writable)
- [x] 5.4: Provide helpful error messages with suggestions

### Task 6: Write Tests (AC: 1-10)
- [x] 6.1: Test config file creation on first run
- [x] 6.2: Test config loading and parsing
- [x] 6.3: Test override precedence
- [x] 6.4: Test validation error handling
- [x] 6.5: Test path expansion

### Task 7: Documentation (AC: 2)
- [x] 7.1: Add comments to default config template
- [x] 7.2: Update CLI help text to mention config file
- [ ] 7.3: Document config options in README or help (deferred)

---

## Dev Notes

### Architecture Decisions

1. **XDG-Compliant Location**: Use `~/.analyze-fin/config.yaml` as per project context
2. **YAML Format**: Human-readable, supports comments, widely understood
3. **Lazy Loading**: Config loaded on first access, not at module import
4. **Singleton Pattern**: Single ConfigManager instance per process

### Implementation Pattern

```python
# src/analyze_fin/config/settings.py
from pathlib import Path
from typing import Any
import yaml

DEFAULT_CONFIG_PATH = Path.home() / ".analyze-fin" / "config.yaml"

class ConfigManager:
    _instance: "ConfigManager | None" = None

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self._config: dict[str, Any] = {}
        self._loaded = False

    def load(self) -> dict[str, Any]:
        if not self._loaded:
            if not self.config_path.exists():
                self.create_default()
            with open(self.config_path) as f:
                self._config = yaml.safe_load(f)
            self._loaded = True
        return self._config

    def get(self, key: str, default: Any = None, cli_override: Any = None) -> Any:
        if cli_override is not None:
            return cli_override
        env_key = f"ANALYZE_FIN_{key.upper().replace('.', '_')}"
        if env_key in os.environ:
            return os.environ[env_key]
        config = self.load()
        # Navigate nested keys like "output.format"
        ...
```

### Existing Code to Leverage

- `src/analyze_fin/exceptions.py` - Add ConfigError
- `src/analyze_fin/database/session.py` - DEFAULT_DB_PATH to migrate
- `src/analyze_fin/cli.py` - Commands to integrate config

### Testing Standards

- Use `tmp_path` fixture for isolated config files
- Test with missing/invalid/corrupt YAML
- Mock `Path.home()` for XDG path testing
- Verify CLI flag override works correctly

---

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References
- Initial implementation: 2026-01-04
- All tests pass: 695 passed, 3 skipped, 54 xfailed

### Completion Notes List
1. Created ConfigManager class with singleton pattern
2. Implemented lazy loading with auto-creation of default config
3. Added override precedence: CLI flags > env vars > config file > defaults
4. Added typed convenience methods for common config values
5. Integrated with CLI via callback with --database and --config options
6. Updated database/session.py to use config system
7. Fixed test fixtures to properly isolate config state
8. Added pyyaml dependency

### File List
**Created:**
- src/analyze_fin/config/defaults.py - Default config values and template
- src/analyze_fin/config/settings.py - ConfigManager class
- tests/config/test_config.py - 24 tests for config system

**Modified:**
- src/analyze_fin/config/__init__.py - Export ConfigManager and helpers
- src/analyze_fin/cli.py - Added CLI callback with --database and --config
- src/analyze_fin/database/session.py - Added config integration
- tests/cli/conftest.py - Updated temp_db fixture for config isolation
- tests/database/test_session.py - Fixed test for config awareness
- tests/e2e/test_parse_workflow.py - Fixed tests for config isolation
- pyproject.toml - Added pyyaml dependency

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-04 | Story file created from epics.md | Dev Agent |
