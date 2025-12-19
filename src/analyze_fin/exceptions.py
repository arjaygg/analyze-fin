"""
Exception hierarchy for analyze-fin.

All application-specific exceptions inherit from AnalyzeFinError,
allowing CLI layer to catch-all with a single handler.

Hierarchy:
    AnalyzeFinError          # Base - catch-all for CLI
    ├── ParseError           # PDF parsing failures
    ├── ValidationError      # Data validation failures
    ├── DuplicateError       # Duplicate transaction detected
    └── ConfigError          # Configuration errors
"""


class AnalyzeFinError(Exception):
    """Base exception for all analyze-fin errors.

    CLI layer catches this to format user-friendly messages.
    Use --verbose flag to show full traceback.
    """

    pass


class ParseError(AnalyzeFinError):
    """PDF parsing failures.

    Raised when:
    - PDF file is corrupted or invalid
    - PDF is password-protected and no password provided
    - Bank type cannot be detected
    - Table extraction fails
    """

    def __init__(
        self,
        message: str,
        *,
        file_path: str | None = None,
        reason: str | None = None,
    ) -> None:
        super().__init__(message)
        self.file_path = file_path
        self.reason = reason


class ValidationError(AnalyzeFinError):
    """Data validation failures.

    Raised when:
    - Transaction data is invalid (negative amounts where not expected)
    - Date parsing fails
    - Required fields are missing
    - Data type conversion fails
    """

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: str | None = None,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.value = value


class DuplicateError(AnalyzeFinError):
    """Duplicate transaction detected.

    Raised when:
    - Same transaction is imported twice
    - Content hash matches existing transaction
    - Reference number matches existing transaction
    """

    def __init__(
        self,
        message: str,
        *,
        original_id: int | None = None,
        duplicate_id: int | None = None,
    ) -> None:
        super().__init__(message)
        self.original_id = original_id
        self.duplicate_id = duplicate_id


class ConfigError(AnalyzeFinError):
    """Configuration errors.

    Raised when:
    - Config file has invalid syntax
    - Required setting is missing
    - Setting value is invalid
    - Database path is inaccessible
    """

    def __init__(
        self,
        message: str,
        *,
        setting: str | None = None,
    ) -> None:
        super().__init__(message)
        self.setting = setting
