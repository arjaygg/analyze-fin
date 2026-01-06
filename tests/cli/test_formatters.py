"""Tests for CLI output formatters."""

import json
from decimal import Decimal

import pytest

from analyze_fin.cli.formatters import (
    OutputFormat,
    format_csv,
    format_currency,
    format_json,
    is_quiet_mode,
    set_quiet_mode,
)


@pytest.fixture(autouse=True)
def reset_quiet_mode():
    """Reset quiet mode before and after each test."""
    set_quiet_mode(False)
    yield
    set_quiet_mode(False)


class TestOutputFormat:
    """Test OutputFormat enum."""

    def test_pretty_format_value(self):
        """PRETTY format should have 'pretty' value."""
        assert OutputFormat.PRETTY.value == "pretty"

    def test_json_format_value(self):
        """JSON format should have 'json' value."""
        assert OutputFormat.JSON.value == "json"

    def test_csv_format_value(self):
        """CSV format should have 'csv' value."""
        assert OutputFormat.CSV.value == "csv"

    def test_html_format_value(self):
        """HTML format should have 'html' value."""
        assert OutputFormat.HTML.value == "html"

    def test_markdown_format_value(self):
        """MARKDOWN format should have 'markdown' value."""
        assert OutputFormat.MARKDOWN.value == "markdown"


class TestFormatCurrency:
    """Test currency formatting."""

    def test_format_integer(self):
        """Format integer amount."""
        assert format_currency(1000) == "₱1,000.00"

    def test_format_float(self):
        """Format float amount."""
        assert format_currency(12345.67) == "₱12,345.67"

    def test_format_decimal(self):
        """Format Decimal amount."""
        assert format_currency(Decimal("12345.67")) == "₱12,345.67"

    def test_format_with_thousands(self):
        """Format large amount with thousands separator."""
        assert format_currency(1234567.89) == "₱1,234,567.89"

    def test_format_zero(self):
        """Format zero amount."""
        assert format_currency(0) == "₱0.00"


class TestFormatJson:
    """Test JSON formatting."""

    def test_format_simple_dict(self):
        """Format simple dictionary."""
        data = {"name": "test", "value": 123}
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_format_list_of_dicts(self):
        """Format list of dictionaries."""
        data = [{"id": 1}, {"id": 2}]
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_format_decimal(self):
        """Decimal should be serialized as string."""
        data = {"amount": Decimal("123.45")}
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed["amount"] == "123.45"

    def test_output_is_pretty_printed(self):
        """JSON output should be indented."""
        data = {"key": "value"}
        result = format_json(data)
        assert "\n" in result  # Indented output has newlines


class TestFormatCsv:
    """Test CSV formatting."""

    def test_format_list_of_dicts(self):
        """Format list of dictionaries as CSV."""
        data = [
            {"name": "Alice", "amount": 100},
            {"name": "Bob", "amount": 200},
        ]
        result = format_csv(data)
        lines = result.strip().split("\n")

        # Header row
        assert "name" in lines[0]
        assert "amount" in lines[0]

        # Data rows
        assert "Alice" in lines[1]
        assert "Bob" in lines[2]

    def test_format_with_column_selection(self):
        """Format CSV with specific columns."""
        data = [{"name": "Alice", "amount": 100, "extra": "ignore"}]
        result = format_csv(data, columns=["name", "amount"])

        assert "name" in result
        assert "amount" in result
        assert "extra" not in result

    def test_format_empty_list(self):
        """Format empty list returns empty string."""
        result = format_csv([])
        assert result == ""


class TestQuietMode:
    """Test quiet mode state."""

    def test_quiet_mode_false_by_default(self):
        """Quiet mode should be False by default."""
        assert is_quiet_mode() is False

    def test_set_quiet_mode_true(self):
        """Setting quiet mode to True should work."""
        set_quiet_mode(True)
        assert is_quiet_mode() is True

    def test_set_quiet_mode_false(self):
        """Setting quiet mode to False should work."""
        set_quiet_mode(True)
        set_quiet_mode(False)
        assert is_quiet_mode() is False
