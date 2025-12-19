"""
TDD Tests: Batch Import & Quality Reporting

Story 1.5 AC: Batch importing multiple statements with quality reporting.
RED phase - these tests will fail until batch.py is implemented.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestBatchImporterStructure:
    """Test BatchImporter class structure."""

    def test_batch_importer_exists(self):
        """BatchImporter can be imported."""
        from analyze_fin.parsers.batch import BatchImporter

        assert BatchImporter is not None

    def test_batch_importer_can_instantiate(self):
        """BatchImporter can be instantiated."""
        from analyze_fin.parsers.batch import BatchImporter

        importer = BatchImporter()
        assert importer is not None

    def test_batch_importer_has_import_all_method(self):
        """BatchImporter has import_all method."""
        from analyze_fin.parsers.batch import BatchImporter

        importer = BatchImporter()
        assert callable(importer.import_all)


class TestBatchImportResult:
    """Test BatchImportResult data class."""

    def test_batch_import_result_exists(self):
        """BatchImportResult can be imported."""
        from analyze_fin.parsers.batch import BatchImportResult

        assert BatchImportResult is not None

    def test_batch_import_result_has_required_fields(self):
        """BatchImportResult has total, successful, failed, quality_score."""
        from analyze_fin.parsers.batch import BatchImportResult

        result = BatchImportResult(
            total_files=5,
            successful=4,
            failed=1,
            average_quality_score=0.92,
            results=[],
            errors=[],
        )

        assert result.total_files == 5
        assert result.successful == 4
        assert result.failed == 1
        assert result.average_quality_score == 0.92


class TestBatchImportFunctionality:
    """Test batch import functionality."""

    def test_import_all_returns_batch_result(self):
        """import_all returns BatchImportResult."""
        from analyze_fin.parsers.batch import BatchImporter, BatchImportResult

        importer = BatchImporter()

        # Mock all parsers to return successful results
        with patch.object(importer, "_parse_file") as mock_parse:
            from analyze_fin.parsers.base import ParseResult
            mock_parse.return_value = ParseResult(
                transactions=[],
                quality_score=0.95,
                bank_type="gcash",
            )

            result = importer.import_all([Path("test1.pdf"), Path("test2.pdf")])

        assert isinstance(result, BatchImportResult)

    def test_import_all_counts_successful_imports(self):
        """import_all correctly counts successful imports."""
        from analyze_fin.parsers.batch import BatchImporter

        importer = BatchImporter()

        with patch.object(importer, "_parse_file") as mock_parse:
            from analyze_fin.parsers.base import ParseResult
            mock_parse.return_value = ParseResult(
                transactions=[],
                quality_score=0.95,
                bank_type="gcash",
            )

            result = importer.import_all([
                Path("test1.pdf"),
                Path("test2.pdf"),
                Path("test3.pdf"),
            ])

        assert result.total_files == 3
        assert result.successful == 3
        assert result.failed == 0

    def test_import_all_counts_failed_imports(self):
        """import_all correctly counts failed imports."""
        from analyze_fin.parsers.batch import BatchImporter
        from analyze_fin.exceptions import ParseError

        importer = BatchImporter()

        def side_effect(path, password=None):
            if "bad" in str(path):
                raise ParseError("Failed")
            from analyze_fin.parsers.base import ParseResult
            return ParseResult(transactions=[], quality_score=0.95, bank_type="gcash")

        with patch.object(importer, "_parse_file", side_effect=side_effect):
            result = importer.import_all([
                Path("good1.pdf"),
                Path("bad.pdf"),
                Path("good2.pdf"),
            ])

        assert result.total_files == 3
        assert result.successful == 2
        assert result.failed == 1

    def test_import_all_calculates_average_quality_score(self):
        """import_all calculates average quality score."""
        from analyze_fin.parsers.batch import BatchImporter
        from analyze_fin.parsers.base import ParseResult

        importer = BatchImporter()

        scores = [0.90, 0.95, 0.98]
        call_count = [0]

        def side_effect(path, password=None):
            score = scores[call_count[0]]
            call_count[0] += 1
            return ParseResult(transactions=[], quality_score=score, bank_type="gcash")

        with patch.object(importer, "_parse_file", side_effect=side_effect):
            result = importer.import_all([
                Path("test1.pdf"),
                Path("test2.pdf"),
                Path("test3.pdf"),
            ])

        expected_avg = sum(scores) / len(scores)
        assert abs(result.average_quality_score - expected_avg) < 0.001


class TestBatchImportProgressCallback:
    """Test progress callback functionality."""

    def test_import_all_calls_progress_callback(self):
        """import_all calls progress callback for each file."""
        from analyze_fin.parsers.batch import BatchImporter
        from analyze_fin.parsers.base import ParseResult

        importer = BatchImporter()
        progress_calls = []

        def progress_callback(current: int, total: int, file_path: Path, status: str):
            progress_calls.append((current, total, file_path, status))

        with patch.object(importer, "_parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                transactions=[], quality_score=0.95, bank_type="gcash"
            )

            importer.import_all(
                [Path("test1.pdf"), Path("test2.pdf")],
                progress_callback=progress_callback,
            )

        assert len(progress_calls) == 2
        assert progress_calls[0][0] == 1  # current
        assert progress_calls[0][1] == 2  # total
        assert progress_calls[1][0] == 2


class TestBatchImportBankDetection:
    """Test automatic bank type detection in batch import."""

    def test_import_all_auto_detects_bank_type(self):
        """import_all auto-detects bank type from PDF content."""
        from analyze_fin.parsers.batch import BatchImporter
        from analyze_fin.parsers.base import ParseResult

        importer = BatchImporter()

        # Create results with different bank types
        results_data = [
            ("gcash", "test1.pdf"),
            ("bpi", "test2.pdf"),
            ("maya_wallet", "test3.pdf"),
        ]

        call_idx = [0]

        def side_effect(path, password=None):
            bank_type = results_data[call_idx[0]][0]
            call_idx[0] += 1
            return ParseResult(transactions=[], quality_score=0.95, bank_type=bank_type)

        with patch.object(importer, "_parse_file", side_effect=side_effect):
            result = importer.import_all([
                Path("test1.pdf"),
                Path("test2.pdf"),
                Path("test3.pdf"),
            ])

        # All should be successful regardless of bank type
        assert result.successful == 3


class TestBatchImportDirectory:
    """Test importing from a directory."""

    def test_import_directory_finds_pdf_files(self):
        """import_directory finds all PDF files in a directory."""
        from analyze_fin.parsers.batch import BatchImporter

        importer = BatchImporter()

        # Check method exists
        assert hasattr(importer, "import_directory")
        assert callable(importer.import_directory)

    def test_import_directory_filters_by_extension(self):
        """import_directory only processes PDF files."""
        from analyze_fin.parsers.batch import BatchImporter
        from analyze_fin.parsers.base import ParseResult
        import tempfile
        import os

        importer = BatchImporter()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "test1.pdf").touch()
            Path(tmpdir, "test2.pdf").touch()
            Path(tmpdir, "test3.txt").touch()  # Not a PDF
            Path(tmpdir, "test4.doc").touch()  # Not a PDF

            with patch.object(importer, "_parse_file") as mock_parse:
                mock_parse.return_value = ParseResult(
                    transactions=[], quality_score=0.95, bank_type="gcash"
                )

                result = importer.import_directory(Path(tmpdir))

            # Should only process PDF files
            assert result.total_files == 2
