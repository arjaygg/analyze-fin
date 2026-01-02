"""
Pytest fixtures for parser tests.

Provides common fixtures for mocking PDF file operations.
"""

from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_pdf_exists():
    """Mock Path.exists() to return True for PDF paths in tests.

    This allows tests that mock pdfplumber to work without needing
    actual PDF files on disk.

    Usage:
        def test_my_parser(mock_pdf_exists):
            parser = MyParser()
            with patch("pdfplumber.open", return_value=mock_pdf):
                result = parser.parse(Path("test.pdf"))
    """
    original_exists = Path.exists

    def mock_exists(self):
        # Return True for .pdf files (they're mocked in tests)
        if str(self).endswith('.pdf'):
            return True
        return original_exists(self)

    with patch.object(Path, 'exists', mock_exists):
        yield


@pytest.fixture(autouse=True)
def auto_mock_pdf_exists():
    """Auto-apply PDF exists mock to all parser tests.

    This fixture automatically mocks Path.exists() for all tests
    in the parsers test module, allowing mock-based tests to work
    without real PDF files.
    """
    original_exists = Path.exists

    def mock_exists(self):
        # Return True for .pdf files (they're mocked in tests)
        if str(self).endswith('.pdf'):
            return True
        return original_exists(self)

    with patch.object(Path, 'exists', mock_exists):
        yield
