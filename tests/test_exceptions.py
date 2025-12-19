"""
TDD Tests: Exception Hierarchy

Story 1.1 AC: Exception hierarchy exists with descriptive error messages.
RED phase - these tests will fail until exceptions.py is implemented.
"""

import pytest


class TestExceptionHierarchy:
    """Test the exception class hierarchy."""

    def test_analyze_fin_error_is_base_exception(self):
        """AnalyzeFinError is the base class for all app exceptions."""
        from analyze_fin.exceptions import AnalyzeFinError

        error = AnalyzeFinError("base error")
        assert isinstance(error, Exception)
        assert str(error) == "base error"

    def test_parse_error_inherits_from_base(self):
        """ParseError inherits from AnalyzeFinError."""
        from analyze_fin.exceptions import AnalyzeFinError, ParseError

        error = ParseError("PDF parsing failed")
        assert isinstance(error, AnalyzeFinError)
        assert isinstance(error, Exception)

    def test_validation_error_inherits_from_base(self):
        """ValidationError inherits from AnalyzeFinError."""
        from analyze_fin.exceptions import AnalyzeFinError, ValidationError

        error = ValidationError("Invalid data")
        assert isinstance(error, AnalyzeFinError)

    def test_duplicate_error_inherits_from_base(self):
        """DuplicateError inherits from AnalyzeFinError."""
        from analyze_fin.exceptions import AnalyzeFinError, DuplicateError

        error = DuplicateError("Duplicate transaction detected")
        assert isinstance(error, AnalyzeFinError)

    def test_config_error_inherits_from_base(self):
        """ConfigError inherits from AnalyzeFinError."""
        from analyze_fin.exceptions import AnalyzeFinError, ConfigError

        error = ConfigError("Invalid configuration")
        assert isinstance(error, AnalyzeFinError)


class TestExceptionMessages:
    """Test that exceptions include descriptive messages."""

    def test_parse_error_with_file_path(self):
        """ParseError can include file path context."""
        from analyze_fin.exceptions import ParseError

        error = ParseError("Failed to parse PDF", file_path="/path/to/file.pdf")
        assert "Failed to parse PDF" in str(error)
        assert error.file_path == "/path/to/file.pdf"

    def test_parse_error_with_reason(self):
        """ParseError can include specific reason."""
        from analyze_fin.exceptions import ParseError

        error = ParseError("Corrupted PDF", reason="Invalid PDF structure")
        assert error.reason == "Invalid PDF structure"

    def test_validation_error_with_field(self):
        """ValidationError can include field context."""
        from analyze_fin.exceptions import ValidationError

        error = ValidationError("Invalid amount", field="amount", value="-100")
        assert error.field == "amount"
        assert error.value == "-100"

    def test_duplicate_error_with_transaction_ids(self):
        """DuplicateError can include transaction IDs."""
        from analyze_fin.exceptions import DuplicateError

        error = DuplicateError(
            "Duplicate detected",
            original_id=1,
            duplicate_id=2,
        )
        assert error.original_id == 1
        assert error.duplicate_id == 2

    def test_config_error_with_setting(self):
        """ConfigError can include setting context."""
        from analyze_fin.exceptions import ConfigError

        error = ConfigError("Invalid setting", setting="database_path")
        assert error.setting == "database_path"


class TestExceptionCatching:
    """Test that exceptions can be caught properly."""

    def test_catch_all_app_errors_with_base(self):
        """All app errors can be caught with AnalyzeFinError."""
        from analyze_fin.exceptions import (
            AnalyzeFinError,
            ConfigError,
            DuplicateError,
            ParseError,
            ValidationError,
        )

        errors = [
            ParseError("parse"),
            ValidationError("validation"),
            DuplicateError("duplicate"),
            ConfigError("config"),
        ]

        for error in errors:
            try:
                raise error
            except AnalyzeFinError as e:
                assert e is error  # Should be caught by base class

    def test_specific_error_not_caught_by_sibling(self):
        """ParseError is not caught by ConfigError handler."""
        from analyze_fin.exceptions import ConfigError, ParseError

        with pytest.raises(ParseError):
            try:
                raise ParseError("parse error")
            except ConfigError:
                pytest.fail("ParseError should not be caught by ConfigError")
