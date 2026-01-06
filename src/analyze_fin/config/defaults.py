"""
Default configuration values for analyze-fin.

These defaults are used when:
- No config file exists
- Config file doesn't specify a value
- Override precedence: CLI flags > env vars > config file > defaults
"""

from pathlib import Path

# Config file location
DEFAULT_CONFIG_DIR = Path.home() / ".analyze-fin"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.yaml"

# Default configuration values
DEFAULT_CONFIG: dict = {
    "database": {
        "path": str(DEFAULT_CONFIG_DIR / "data.db"),
    },
    "output": {
        "format": "pretty",  # pretty, json, csv
        "color": True,
        "report_format": "html",  # html, markdown
    },
    "categorization": {
        "auto_categorize": True,
        "confidence_threshold": 0.8,
        "prompt_for_unknown": True,
    },
    "banks": {
        "bpi": {
            "password_pattern": None,  # Regex pattern for auto-detecting password
        },
    },
}

# Default config template with comments (for auto-generated config file)
DEFAULT_CONFIG_TEMPLATE = """\
# analyze-fin configuration
# Location: ~/.analyze-fin/config.yaml
#
# Override precedence: CLI flags > environment variables > this file > defaults
# Environment variables use ANALYZE_FIN_ prefix (e.g., ANALYZE_FIN_DATABASE_PATH)

# Database settings
database:
  # Path to SQLite database file
  # Supports ~ for home directory and environment variables
  path: ~/.analyze-fin/data.db

# Output settings
output:
  # Default output format: pretty, json, csv
  format: pretty
  # Enable colors in terminal output
  color: true
  # Default report format: html, markdown
  report_format: html

# Categorization settings
categorization:
  # Automatically categorize transactions on import
  auto_categorize: true
  # Minimum confidence score for auto-categorization (0.0 to 1.0)
  confidence_threshold: 0.8
  # Prompt for unknown merchant categories in interactive mode
  prompt_for_unknown: true

# Bank-specific settings
banks:
  bpi:
    # Regex pattern to auto-detect BPI statement password
    # Example: "^\\\\d{6}$" for 6-digit numeric passwords
    password_pattern: null
"""
