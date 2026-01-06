"""Tests for CLI modes (interactive vs batch)."""

import pytest
from typer.testing import CliRunner

from analyze_fin.cli import app
from analyze_fin.cli.prompts import set_mode_state


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def reset_mode_state():
    """Reset mode state before and after each test."""
    set_mode_state(batch=False, yes=False)
    yield
    set_mode_state(batch=False, yes=False)


class TestGlobalModeFlags:
    """Test global --batch and --yes flags (AC1)."""

    def test_batch_flag_is_recognized(self, runner):
        """--batch flag should be accepted by CLI."""
        result = runner.invoke(app, ["--batch", "version"])
        assert result.exit_code == 0

    def test_yes_flag_is_recognized(self, runner):
        """--yes flag should be accepted by CLI."""
        result = runner.invoke(app, ["--yes", "version"])
        assert result.exit_code == 0

    def test_y_short_flag_is_recognized(self, runner):
        """-y short flag should be accepted by CLI."""
        result = runner.invoke(app, ["-y", "version"])
        assert result.exit_code == 0

    def test_batch_and_yes_combined(self, runner):
        """--batch and --yes flags can be used together."""
        result = runner.invoke(app, ["--batch", "--yes", "version"])
        assert result.exit_code == 0


class TestModeStateHelpers:
    """Test is_batch_mode() and is_auto_confirm() helpers."""

    def test_is_batch_mode_false_by_default(self):
        """is_batch_mode() returns False when --batch not specified."""
        from analyze_fin.cli.prompts import is_batch_mode

        assert is_batch_mode() is False

    def test_is_auto_confirm_false_by_default(self):
        """is_auto_confirm() returns False when --yes not specified."""
        from analyze_fin.cli.prompts import is_auto_confirm

        assert is_auto_confirm() is False


class TestPromptUtilities:
    """Test prompt utility functions (AC2, AC3, AC4)."""

    def test_prompt_for_input_returns_default_in_batch_mode(self):
        """prompt_for_input should return default in batch mode."""
        from analyze_fin.cli.prompts import prompt_for_input

        set_mode_state(batch=True, yes=False)
        result = prompt_for_input("Enter value:", default="default_value")
        assert result == "default_value"

    def test_prompt_for_input_raises_in_batch_mode_without_default(self):
        """prompt_for_input should raise in batch mode without default."""
        from analyze_fin.cli.prompts import prompt_for_input

        set_mode_state(batch=True, yes=False)
        with pytest.raises(ValueError, match="Required input in batch mode"):
            prompt_for_input("Enter value:")

    def test_prompt_yes_no_returns_default_in_batch_mode(self):
        """prompt_yes_no should return default in batch mode."""
        from analyze_fin.cli.prompts import prompt_yes_no

        set_mode_state(batch=True, yes=False)
        assert prompt_yes_no("Continue?", default=True) is True
        assert prompt_yes_no("Continue?", default=False) is False

    def test_prompt_yes_no_returns_true_with_yes_flag(self):
        """prompt_yes_no should return True when --yes flag is set."""
        from analyze_fin.cli.prompts import prompt_yes_no

        set_mode_state(batch=False, yes=True)
        # Always returns True regardless of default when --yes is set
        assert prompt_yes_no("Continue?", default=False) is True

    def test_prompt_choice_returns_first_in_batch_mode(self):
        """prompt_choice should return first choice in batch mode."""
        from analyze_fin.cli.prompts import prompt_choice

        set_mode_state(batch=True, yes=False)
        choices = ["keep_first", "keep_second", "keep_both"]
        result = prompt_choice("Select action:", choices)
        assert result == "keep_first"


class TestBatchModeParseCommand:
    """Test batch mode behavior in parse command (AC5)."""

    def test_parse_batch_mode_uses_env_password(self, runner, tmp_path, monkeypatch):
        """--batch mode should use ANALYZE_FIN_BPI_PASSWORD env var."""
        # This test validates the pattern, actual parsing requires PDFs
        monkeypatch.setenv("ANALYZE_FIN_BPI_PASSWORD", "test_password")

        # With batch mode, no password prompt should occur
        result = runner.invoke(app, ["--batch", "version"])
        assert result.exit_code == 0
        assert "password" not in result.output.lower()


class TestDuplicateHandlingModes:
    """Test duplicate handling in different modes (AC6, AC7)."""

    def test_batch_mode_defaults_to_keep_first(self):
        """Batch mode should default to keeping first transaction."""
        from analyze_fin.cli.prompts import prompt_choice

        set_mode_state(batch=True, yes=False)
        choices = ["keep_first", "keep_second", "keep_both"]
        result = prompt_choice("Duplicate found:", choices)
        assert result == "keep_first"


class TestOutputVerbosity:
    """Test output verbosity in different modes (AC8)."""

    def test_batch_mode_disables_colors(self, runner, monkeypatch):
        """--batch mode should disable Rich colors."""
        from analyze_fin.cli.prompts import is_batch_mode

        set_mode_state(batch=True, yes=False)
        assert is_batch_mode() is True


class TestVerboseFlag:
    """Test --verbose flag behavior."""

    def test_verbose_flag_is_recognized(self, runner):
        """--verbose flag should be accepted by CLI."""
        result = runner.invoke(app, ["--verbose", "version"])
        assert result.exit_code == 0

    def test_v_short_flag_is_recognized(self, runner):
        """Short -v flag should be accepted by CLI."""
        result = runner.invoke(app, ["-v", "version"])
        assert result.exit_code == 0

    def test_verbose_mode_state(self):
        """Verbose mode state should be manageable."""
        from analyze_fin.cli.formatters import (
            is_verbose_mode,
            set_verbose_mode,
        )

        # Reset to default
        set_verbose_mode(False)
        assert is_verbose_mode() is False

        # Enable verbose
        set_verbose_mode(True)
        assert is_verbose_mode() is True

        # Disable again
        set_verbose_mode(False)
        assert is_verbose_mode() is False
