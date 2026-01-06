"""Exit codes for analyze-fin CLI.

Exit codes follow common conventions for shell scripting:
- 0: Success
- 1: General error
- 2: Parse/input error
- 3: Configuration error
- 4: Database error

Scripts can check exit codes:
    if analyze-fin parse statement.pdf; then
        echo "Success"
    else
        case $? in
            2) echo "Parse error - check PDF file" ;;
            3) echo "Config error - check settings" ;;
            4) echo "Database error - check DB path" ;;
            *) echo "Unknown error" ;;
        esac
    fi
"""

from __future__ import annotations

from typing import NoReturn

import typer
from rich.console import Console

# Exit code constants
SUCCESS = 0
ERROR = 1
PARSE_ERROR = 2
CONFIG_ERROR = 3
DB_ERROR = 4

# Console for error output (stderr)
stderr_console = Console(stderr=True)


def get_exit_code_for_exception(exc: Exception) -> int:
    """Map exception types to exit codes.

    Args:
        exc: The exception to map

    Returns:
        Appropriate exit code for the exception type
    """
    from analyze_fin.exceptions import (
        ConfigError,
        ParseError,
        ValidationError,
    )

    exception_map = {
        ParseError: PARSE_ERROR,
        ValidationError: PARSE_ERROR,
        ConfigError: CONFIG_ERROR,
    }

    for exc_type, code in exception_map.items():
        if isinstance(exc, exc_type):
            return code

    # Check for SQLAlchemy/database errors by name pattern
    exc_name = type(exc).__name__.lower()
    if "database" in exc_name or "sql" in exc_name or "sqlite" in exc_name:
        return DB_ERROR

    # Also check for common SQLAlchemy exception types
    try:
        from sqlalchemy.exc import SQLAlchemyError

        if isinstance(exc, SQLAlchemyError):
            return DB_ERROR
    except ImportError:
        pass  # SQLAlchemy not installed

    return ERROR


def exit_with_error(message: str, code: int = ERROR) -> NoReturn:
    """Print error message to stderr and exit with code.

    Args:
        message: Error message to display
        code: Exit code (default: 1 for general error)
    """
    from analyze_fin.cli.prompts import is_batch_mode

    if is_batch_mode():
        stderr_console.print(f"ERROR: {message}")
    else:
        stderr_console.print(f"[red]Error:[/red] {message}")

    raise typer.Exit(code=code)


def exit_with_exception(exc: Exception) -> NoReturn:
    """Print exception message to stderr and exit with appropriate code.

    Args:
        exc: The exception that caused the error
    """
    code = get_exit_code_for_exception(exc)
    exit_with_error(str(exc), code)


def exit_success() -> NoReturn:
    """Exit with success code."""
    raise typer.Exit(code=SUCCESS)
