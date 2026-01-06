"""
Fixtures for file paths and handling.
"""
from pathlib import Path

import pytest


@pytest.fixture
def real_bpi_pdf_path() -> Path:
    """Return path to real sample BPI statement."""
    pdf_path = Path("tests/fixtures/sample_statements/sample_bpi.pdf")
    if not pdf_path.exists():
        pytest.skip("Real BPI sample PDF not found")
    return pdf_path

@pytest.fixture
def real_gcash_pdf_path() -> Path:
    """Return path to real sample GCash statement."""
    pdf_path = Path("tests/fixtures/sample_statements/sample_gcash.pdf")
    if not pdf_path.exists():
        pytest.skip("Real GCash sample PDF not found")
    return pdf_path

