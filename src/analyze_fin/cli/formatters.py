"""Output formatters for CLI commands.

This module provides consistent output formatting across all CLI commands.
Supports: pretty (default), json, csv, html, markdown formats.

Data flows:
- Data output goes to stdout (for pipes)
- Progress/info messages go to stderr (not polluting pipes)
"""

from __future__ import annotations

import csv
import io
import json
from decimal import Decimal
from enum import Enum
from typing import Any

from rich.console import Console
from rich.table import Table

# Console for data output (stdout)
stdout_console = Console()

# Console for info/progress output (stderr)
stderr_console = Console(stderr=True)


class OutputFormat(str, Enum):
    """Supported output formats."""

    PRETTY = "pretty"
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    MARKDOWN = "markdown"


# Module-level state
_quiet_mode = False
_verbose_mode = False


def set_quiet_mode(quiet: bool) -> None:
    """Set quiet mode state.

    Args:
        quiet: Whether to suppress non-error output
    """
    global _quiet_mode
    _quiet_mode = quiet


def is_quiet_mode() -> bool:
    """Check if quiet mode is enabled.

    Returns:
        True if --quiet flag was specified
    """
    return _quiet_mode


def set_verbose_mode(verbose: bool) -> None:
    """Set verbose mode state.

    Args:
        verbose: Whether to show debug output
    """
    global _verbose_mode
    _verbose_mode = verbose


def is_verbose_mode() -> bool:
    """Check if verbose mode is enabled.

    Returns:
        True if --verbose flag was specified
    """
    return _verbose_mode


def debug(message: str) -> None:
    """Print debug message to stderr (only in verbose mode).

    Args:
        message: Debug message to display
    """
    if _verbose_mode and not _quiet_mode:
        stderr_console.print(f"[dim]DEBUG: {message}[/dim]")


def info(message: str) -> None:
    """Print info message to stderr (unless quiet mode).

    Args:
        message: Message to display
    """
    if not _quiet_mode:
        stderr_console.print(message)


def progress(message: str) -> None:
    """Print progress message to stderr (unless quiet mode).

    Args:
        message: Progress message to display
    """
    if not _quiet_mode:
        stderr_console.print(f"[dim]{message}[/dim]")


def error(message: str, *, show_traceback: bool = False) -> None:
    """Print error message to stderr (always, even in quiet mode).

    Args:
        message: Error message to display
        show_traceback: If True, print full traceback (auto-enabled in verbose mode)
    """
    stderr_console.print(f"[red]Error:[/red] {message}")

    # Show traceback if verbose mode is enabled or explicitly requested
    if show_traceback or _verbose_mode:
        import traceback

        stderr_console.print("[dim]" + traceback.format_exc() + "[/dim]")


def success(message: str) -> None:
    """Print success message to stderr (unless quiet mode).

    Args:
        message: Success message to display
    """
    if not _quiet_mode:
        stderr_console.print(f"[green]{message}[/green]")


def format_currency(amount: Decimal | float | int) -> str:
    """Format amount as Philippine Peso.

    Args:
        amount: Amount to format

    Returns:
        Formatted string like "₱12,345.67"
    """
    if isinstance(amount, Decimal):
        amount = float(amount)
    return f"₱{amount:,.2f}"


def format_pretty_table(
    data: list[dict[str, Any]],
    title: str | None = None,
    columns: list[str] | None = None,
) -> None:
    """Format data as a Rich table (stdout).

    Args:
        data: List of dictionaries to display
        title: Optional table title
        columns: Optional list of columns to show (default: all)
    """
    if not data:
        return

    if columns is None:
        columns = list(data[0].keys())

    table = Table(title=title)

    for col in columns:
        # Right-align amount columns
        justify = "right" if "amount" in col.lower() else "left"
        table.add_column(col.replace("_", " ").title(), justify=justify)

    for row in data:
        values = []
        for col in columns:
            val = row.get(col, "")
            # Format amounts with peso sign
            if "amount" in col.lower() and isinstance(val, (int, float, Decimal)):
                val = format_currency(val)
            values.append(str(val) if val is not None else "")
        table.add_row(*values)

    stdout_console.print(table)


def format_json(data: Any) -> str:
    """Format data as JSON string.

    Args:
        data: Data to format (must be JSON-serializable)

    Returns:
        Pretty-printed JSON string
    """

    def default_serializer(obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return str(obj)
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    return json.dumps(data, indent=2, default=default_serializer)


def format_csv(data: list[dict[str, Any]], columns: list[str] | None = None) -> str:
    """Format data as CSV string.

    Args:
        data: List of dictionaries to format
        columns: Optional list of columns (default: all keys from first row)

    Returns:
        CSV string with headers
    """
    if not data:
        return ""

    if columns is None:
        columns = list(data[0].keys())

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def output(
    data: Any,
    fmt: OutputFormat = OutputFormat.PRETTY,
    title: str | None = None,
    columns: list[str] | None = None,
) -> None:
    """Output data in specified format to stdout.

    Args:
        data: Data to output (list of dicts for table formats)
        fmt: Output format
        title: Optional title (for pretty format)
        columns: Optional column list (for table formats)
    """
    if _quiet_mode:
        return

    if fmt == OutputFormat.PRETTY:
        if isinstance(data, list) and data and isinstance(data[0], dict):
            format_pretty_table(data, title=title, columns=columns)
        else:
            stdout_console.print(data)

    elif fmt == OutputFormat.JSON:
        print(format_json(data))

    elif fmt == OutputFormat.CSV:
        if isinstance(data, list):
            print(format_csv(data, columns=columns))
        else:
            print(format_csv([data] if isinstance(data, dict) else data, columns=columns))

    elif fmt == OutputFormat.MARKDOWN:
        # Basic markdown table format
        if isinstance(data, list) and data and isinstance(data[0], dict):
            cols = columns or list(data[0].keys())
            header = "| " + " | ".join(cols) + " |"
            separator = "|" + "|".join(["---"] * len(cols)) + "|"
            rows = [
                "| " + " | ".join(str(row.get(c, "")) for c in cols) + " |" for row in data
            ]
            print(f"{header}\n{separator}")
            print("\n".join(rows))
        else:
            print(str(data))

    elif fmt == OutputFormat.HTML:
        # Basic HTML table format
        if isinstance(data, list) and data and isinstance(data[0], dict):
            cols = columns or list(data[0].keys())
            print("<table>")
            print("  <thead><tr>")
            for col in cols:
                print(f"    <th>{col}</th>")
            print("  </tr></thead>")
            print("  <tbody>")
            for row in data:
                print("    <tr>")
                for col in cols:
                    val = row.get(col, "")
                    print(f"      <td>{val}</td>")
                print("    </tr>")
            print("  </tbody>")
            print("</table>")
        else:
            print(f"<pre>{data}</pre>")
