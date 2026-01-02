"""
TDD Tests: Batch Import & Quality Reporting

Story 1.5 AC: Batch importing multiple statements with quality reporting.
RED phase - these tests will fail until batch.py is implemented.
"""

from pathlib import Path
from unittest.mock import patch


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
        from analyze_fin.exceptions import ParseError
        from analyze_fin.parsers.batch import BatchImporter

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
        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

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
        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

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
        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

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
        import tempfile

        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

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

    def test_import_directory_recursive_finds_nested_pdfs(self):
        """import_directory with recursive=True finds PDFs in subdirectories."""
        import tempfile

        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

        importer = BatchImporter()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = Path(tmpdir, "subdir")
            subdir.mkdir()
            Path(tmpdir, "test1.pdf").touch()
            Path(subdir, "test2.pdf").touch()

            with patch.object(importer, "_parse_file") as mock_parse:
                mock_parse.return_value = ParseResult(
                    transactions=[], quality_score=0.95, bank_type="gcash"
                )

                # Non-recursive should only find 1
                result_nonrec = importer.import_directory(Path(tmpdir), recursive=False)
                assert result_nonrec.total_files == 1

            # Reset importer to clear state
            importer = BatchImporter()

            with patch.object(importer, "_parse_file") as mock_parse:
                mock_parse.return_value = ParseResult(
                    transactions=[], quality_score=0.95, bank_type="gcash"
                )

                # Recursive should find 2
                result_rec = importer.import_directory(Path(tmpdir), recursive=True)
                assert result_rec.total_files == 2


class TestBatchImportDuplicateDetection:
    """Test duplicate detection functionality."""

    def test_skip_duplicates_true_skips_same_content(self):
        """skip_duplicates=True skips files with same content hash."""
        import tempfile

        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two files with same content
            file1 = Path(tmpdir, "test1.pdf")
            file2 = Path(tmpdir, "test2.pdf")
            file1.write_bytes(b"same content")
            file2.write_bytes(b"same content")

            importer = BatchImporter()

            with patch.object(importer, "_parse_file") as mock_parse:
                mock_parse.return_value = ParseResult(
                    transactions=[], quality_score=0.95, bank_type="gcash"
                )

                result = importer.import_all([file1, file2], skip_duplicates=True)

            # First file should succeed, second should be skipped as duplicate
            assert result.successful == 1
            assert len(result.duplicates) == 1
            assert "previously imported" in result.duplicates[0][1].lower()

    def test_skip_duplicates_false_processes_duplicates(self):
        """skip_duplicates=False processes files with same content hash."""
        import tempfile

        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two files with same content
            file1 = Path(tmpdir, "test1.pdf")
            file2 = Path(tmpdir, "test2.pdf")
            file1.write_bytes(b"same content")
            file2.write_bytes(b"same content")

            importer = BatchImporter()

            with patch.object(importer, "_parse_file") as mock_parse:
                mock_parse.return_value = ParseResult(
                    transactions=[], quality_score=0.95, bank_type="gcash"
                )

                result = importer.import_all([file1, file2], skip_duplicates=False)

            # Both files should be processed
            assert result.successful == 2
            assert len(result.duplicates) == 0

    def test_duplicate_hash_not_added_on_failure(self):
        """Failed parses don't mark file as 'previously imported'."""
        import tempfile

        from analyze_fin.exceptions import ParseError
        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file
            file1 = Path(tmpdir, "test.pdf")
            file1.write_bytes(b"test content")

            importer = BatchImporter()

            # First attempt fails
            with patch.object(importer, "_parse_file") as mock_parse:
                mock_parse.side_effect = ParseError("Parse failed")
                result1 = importer.import_all([file1], skip_duplicates=True)

            assert result1.failed == 1
            assert len(result1.duplicates) == 0

            # Reset processed paths for retry
            importer._processed_paths.clear()

            # Second attempt should succeed (not marked as duplicate)
            with patch.object(importer, "_parse_file") as mock_parse:
                mock_parse.return_value = ParseResult(
                    transactions=[], quality_score=0.95, bank_type="gcash"
                )
                result2 = importer.import_all([file1], skip_duplicates=True)

            assert result2.successful == 1
            assert len(result2.duplicates) == 0  # Not marked as duplicate

    def test_imported_hashes_parameter_enables_cross_session_detection(self):
        """imported_hashes parameter enables detection across sessions."""
        import hashlib
        import tempfile

        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir, "test.pdf")
            file1.write_bytes(b"test content")

            # Compute hash manually
            content_hash = hashlib.sha256(b"test content").hexdigest()

            # Create importer with pre-existing hash
            importer = BatchImporter(imported_hashes={content_hash})

            with patch.object(importer, "_parse_file") as mock_parse:
                mock_parse.return_value = ParseResult(
                    transactions=[], quality_score=0.95, bank_type="gcash"
                )

                result = importer.import_all([file1], skip_duplicates=True)

            # Should be marked as duplicate from cross-session
            assert result.successful == 0
            assert len(result.duplicates) == 1


class TestBatchImportPasswordHandling:
    """Test password handling for protected PDFs."""

    def test_password_passed_to_parser(self):
        """Passwords are passed to the parser correctly."""
        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

        importer = BatchImporter()

        with patch.object(importer, "_parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                transactions=[], quality_score=0.95, bank_type="bpi"
            )

            passwords = {"test.pdf": "secret123"}
            importer.import_all([Path("test.pdf")], passwords=passwords)

            # Verify password was passed
            mock_parse.assert_called_once()
            call_args = mock_parse.call_args
            assert call_args[0][1] == "secret123" or call_args[1].get("password") == "secret123"

    def test_password_error_added_to_errors_list(self):
        """Password errors are captured in errors list."""
        from analyze_fin.exceptions import ParseError
        from analyze_fin.parsers.batch import BatchImporter

        importer = BatchImporter()

        with patch.object(importer, "_parse_file") as mock_parse:
            mock_parse.side_effect = ParseError("Incorrect password")

            result = importer.import_all(
                [Path("protected.pdf")],
                passwords={"protected.pdf": "wrong_password"}
            )

        assert result.failed == 1
        assert len(result.errors) == 1
        assert "protected.pdf" in result.errors[0][0]

    def test_mixed_batch_with_and_without_passwords(self):
        """Batch with some password-protected and some unprotected files."""
        from analyze_fin.parsers.base import ParseResult
        from analyze_fin.parsers.batch import BatchImporter

        importer = BatchImporter()

        passwords_received = []

        def side_effect(path, password=None):
            passwords_received.append((str(path), password))
            return ParseResult(transactions=[], quality_score=0.95, bank_type="gcash")

        with patch.object(importer, "_parse_file", side_effect=side_effect):
            passwords = {"protected.pdf": "secret"}
            importer.import_all(
                [Path("protected.pdf"), Path("unprotected.pdf")],
                passwords=passwords
            )

        # First file should have password, second should not
        assert passwords_received[0][1] == "secret"
        assert passwords_received[1][1] is None


class TestBatchImportQualityLabels:
    """Test quality score labeling."""

    def test_get_confidence_label_high(self):
        """get_confidence_label returns 'High Confidence' for >= 0.95."""
        from analyze_fin.parsers.batch import BatchImportResult

        result = BatchImportResult(
            total_files=1,
            successful=1,
            failed=0,
            average_quality_score=0.98,
            results=[],
            errors=[],
        )

        assert result.get_confidence_label() == "High Confidence"

    def test_get_confidence_label_medium(self):
        """get_confidence_label returns 'Medium - Review Recommended' for 0.80-0.95."""
        from analyze_fin.parsers.batch import BatchImportResult

        result = BatchImportResult(
            total_files=1,
            successful=1,
            failed=0,
            average_quality_score=0.87,
            results=[],
            errors=[],
        )

        assert result.get_confidence_label() == "Medium - Review Recommended"

    def test_get_confidence_label_low(self):
        """get_confidence_label returns 'Low - Manual Review Required' for < 0.80."""
        from analyze_fin.parsers.batch import BatchImportResult

        result = BatchImportResult(
            total_files=1,
            successful=1,
            failed=0,
            average_quality_score=0.65,
            results=[],
            errors=[],
        )

        assert result.get_confidence_label() == "Low - Manual Review Required"


class TestBatchImportQualityReport:
    """Test quality report generation."""

    def test_get_quality_report_contains_summary(self):
        """get_quality_report contains import summary."""
        from analyze_fin.parsers.batch import BatchImportResult

        result = BatchImportResult(
            total_files=10,
            successful=8,
            failed=2,
            average_quality_score=0.92,
            results=[],
            errors=[("bad.pdf", "Parse error")],
        )

        report = result.get_quality_report()

        assert "8/10" in report
        assert "92.0%" in report
        assert "Medium - Review Recommended" in report

    def test_get_quality_report_shows_errors(self):
        """get_quality_report shows failed files."""
        from analyze_fin.parsers.batch import BatchImportResult

        result = BatchImportResult(
            total_files=2,
            successful=1,
            failed=1,
            average_quality_score=0.95,
            results=[],
            errors=[("corrupt.pdf", "PDF cannot be read")],
        )

        report = result.get_quality_report()

        assert "Failed" in report
        assert "corrupt.pdf" in report
        assert "PDF cannot be read" in report

    def test_get_quality_report_shows_duplicates(self):
        """get_quality_report shows skipped duplicates."""
        from analyze_fin.parsers.batch import BatchImportResult

        result = BatchImportResult(
            total_files=2,
            successful=1,
            failed=0,
            average_quality_score=0.95,
            results=[],
            errors=[],
            duplicates=[("dup.pdf", "File content matches previously imported statement")],
        )

        report = result.get_quality_report()

        assert "Duplicates" in report
        assert "dup.pdf" in report
