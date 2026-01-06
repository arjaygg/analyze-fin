"""Prompt utilities for CLI modes (interactive vs batch).

This module provides mode-aware prompt functions that respect
--batch and --yes flags for automation support.
"""

from __future__ import annotations

from rich.console import Console
from rich.prompt import Confirm, Prompt

# Module-level state for CLI mode
_mode_state: dict[str, bool] = {
    "batch": False,
    "yes": False,
}

console = Console()


def set_mode_state(*, batch: bool = False, yes: bool = False) -> None:
    """Set the current CLI mode state.

    Called by the main CLI callback when --batch or --yes flags are used.

    Args:
        batch: Whether batch mode is enabled (no prompts)
        yes: Whether auto-confirm is enabled (yes to confirmations)
    """
    _mode_state["batch"] = batch
    _mode_state["yes"] = yes


def is_batch_mode() -> bool:
    """Check if running in batch mode (no prompts).

    Returns:
        True if --batch flag was specified
    """
    return _mode_state["batch"]


def is_auto_confirm() -> bool:
    """Check if auto-confirm mode is enabled.

    Returns:
        True if --yes flag was specified
    """
    return _mode_state["yes"]


def prompt_for_input(
    message: str,
    default: str | None = None,
    password: bool = False,
) -> str:
    """Prompt for text input, respecting batch mode.

    In batch mode:
    - If default is provided, returns default immediately
    - If no default, raises ValueError (required input missing)

    In interactive mode:
    - Shows prompt and waits for user input

    Args:
        message: The prompt message to display
        default: Default value to use if no input (and in batch mode)
        password: If True, hide input (for sensitive data)

    Returns:
        User input or default value

    Raises:
        ValueError: In batch mode without a default value
    """
    if _mode_state["batch"]:
        if default is not None:
            return default
        raise ValueError(f"Required input in batch mode: {message}")

    return Prompt.ask(message, default=default, password=password)


def prompt_yes_no(
    message: str,
    default: bool = True,
) -> bool:
    """Prompt for yes/no confirmation, respecting batch and yes flags.

    In batch mode: Returns the default value
    With --yes flag: Returns True (always confirms)
    In interactive mode: Shows prompt and waits for response

    Args:
        message: The confirmation message to display
        default: Default value when no input or in batch mode

    Returns:
        True for yes, False for no
    """
    if _mode_state["yes"]:
        return True

    if _mode_state["batch"]:
        return default

    return Confirm.ask(message, default=default)


def prompt_choice(
    message: str,
    choices: list[str],
    default_index: int = 0,
) -> str:
    """Prompt for selection from choices, respecting batch mode.

    In batch mode: Returns the choice at default_index (first by default)
    In interactive mode: Shows choices and waits for selection

    Args:
        message: The prompt message to display
        choices: List of valid choices
        default_index: Index of default choice (0 = first)

    Returns:
        Selected choice string

    Raises:
        ValueError: If choices is empty or default_index is out of bounds
    """
    if not choices:
        raise ValueError("prompt_choice() requires at least one choice")
    if default_index < 0 or default_index >= len(choices):
        raise ValueError(
            f"default_index {default_index} out of bounds for {len(choices)} choices"
        )

    if _mode_state["batch"]:
        return choices[default_index]

    # Build choice display
    choice_str = "/".join(f"[{c[0]}]{c[1:]}" if c else c for c in choices)
    response = Prompt.ask(f"{message} ({choice_str})")

    # Match response to choices (case-insensitive, first letter match)
    response_lower = response.lower()
    for choice in choices:
        if choice.lower().startswith(response_lower) or response_lower == choice[0].lower():
            return choice

    # Default if no match
    return choices[default_index]
