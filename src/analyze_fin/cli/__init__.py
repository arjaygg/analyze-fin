"""CLI package for analyze-fin."""

from analyze_fin.cli.exit_codes import (
    CONFIG_ERROR,
    DB_ERROR,
    ERROR,
    PARSE_ERROR,
    SUCCESS,
    exit_success,
    exit_with_error,
    exit_with_exception,
    get_exit_code_for_exception,
)
from analyze_fin.cli.formatters import (
    OutputFormat,
    debug,
    error,
    format_csv,
    format_currency,
    format_json,
    format_pretty_table,
    info,
    is_quiet_mode,
    is_verbose_mode,
    output,
    progress,
    set_quiet_mode,
    set_verbose_mode,
    success,
)
from analyze_fin.cli.main import app, main
from analyze_fin.cli.prompts import (
    is_auto_confirm,
    is_batch_mode,
    prompt_choice,
    prompt_for_input,
    prompt_yes_no,
    set_mode_state,
)

__all__ = [
    # Main app
    "app",
    "main",
    # Exit codes
    "SUCCESS",
    "ERROR",
    "PARSE_ERROR",
    "CONFIG_ERROR",
    "DB_ERROR",
    "exit_with_error",
    "exit_with_exception",
    "exit_success",
    "get_exit_code_for_exception",
    # Formatters
    "OutputFormat",
    "output",
    "format_json",
    "format_csv",
    "format_pretty_table",
    "format_currency",
    "debug",
    "info",
    "progress",
    "error",
    "success",
    "is_quiet_mode",
    "is_verbose_mode",
    "set_quiet_mode",
    "set_verbose_mode",
    # Prompts/modes
    "is_batch_mode",
    "is_auto_confirm",
    "set_mode_state",
    "prompt_for_input",
    "prompt_yes_no",
    "prompt_choice",
]
