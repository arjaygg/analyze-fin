"""
Batch import functionality for multiple PDF statements.

Provides:
- BatchImporter: Process multiple PDF files
- BatchImportResult: Aggregated import results
- Progress callbacks for CLI feedback
- Quality score aggregation
- Duplicate detection within batch
"""

import hashlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from analyze_fin.exceptions import ParseError
from analyze_fin.parsers.base import BaseBankParser, ParseResult

logger = logging.getLogger(__name__)


@dataclass
class BatchImportResult:
    """Result of batch importing multiple PDF files.

    Attributes:
        total_files: Total number of files processed
        successful: Number of successfully imported files
        failed: Number of failed imports
        average_quality_score: Average quality score across successful imports
        results: List of ParseResult for successful imports
        errors: List of (file_path, error_message) tuples for failures
        duplicates: List of (file_path, reason) tuples for skipped duplicates
    """

    total_files: int
    successful: int
    failed: int
    average_quality_score: float
    results: list[ParseResult] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)
    duplicates: list[tuple[str, str]] = field(default_factory=list)

    def get_confidence_label(self) -> str:
        """Get human-readable confidence label for average quality score.

        Returns:
            Confidence label string:
            - '>= 0.95': "High Confidence"
            - '0.80-0.95': "Medium - Review Recommended"
            - '< 0.80': "Low - Manual Review Required"
        """
        if self.average_quality_score >= 0.95:
            return "High Confidence"
        elif self.average_quality_score >= 0.80:
            return "Medium - Review Recommended"
        return "Low - Manual Review Required"

    def get_quality_report(self) -> str:
        """Generate formatted quality report.

        Returns:
            Multi-line string with import summary and quality breakdown.
        """
        lines = [
            f"Import Summary: {self.successful}/{self.total_files} files imported successfully",
            f"Average Quality Score: {self.average_quality_score:.1%} ({self.get_confidence_label()})",
            "",
        ]

        # Categorize results by confidence
        high_conf = []
        medium_conf = []
        low_conf = []

        for result in self.results:
            if result.quality_score >= 0.95:
                high_conf.append(result)
            elif result.quality_score >= 0.80:
                medium_conf.append(result)
            else:
                low_conf.append(result)

        if high_conf:
            lines.append(f"✓ High Confidence ({len(high_conf)} files): Auto-accept")
        if medium_conf:
            lines.append(f"⚠ Medium Confidence ({len(medium_conf)} files): Review recommended")
        if low_conf:
            lines.append(f"✗ Low Confidence ({len(low_conf)} files): Manual review required")
            for result in low_conf:
                if result.parsing_errors:
                    lines.append(f"  - {result.bank_type}: {len(result.parsing_errors)} parsing errors")

        if self.duplicates:
            lines.append(f"\n⊘ Duplicates Skipped ({len(self.duplicates)} files):")
            for file_path, reason in self.duplicates:
                lines.append(f"  - {file_path}: {reason}")

        if self.errors:
            lines.append(f"\n✗ Failed ({len(self.errors)} files):")
            for file_path, error in self.errors:
                lines.append(f"  - {file_path}: {error}")

        return "\n".join(lines)


# Progress callback type: (current, total, file_path, status)
ProgressCallback = Callable[[int, int, Path, str], None]


class BatchImporter:
    """Batch importer for processing multiple PDF statements.

    Automatically detects bank type and uses the appropriate parser.
    Includes duplicate detection within batch and optional historical check.

    Example:
        importer = BatchImporter()

        # Import multiple files
        result = importer.import_all([
            Path("gcash_jan.pdf"),
            Path("bpi_jan.pdf"),
            Path("maya_jan.pdf"),
        ])

        print(f"Imported {result.successful}/{result.total_files} files")
        print(f"Average quality: {result.average_quality_score:.1%}")
        print(result.get_quality_report())

        # Import from directory
        result = importer.import_directory(Path("statements/"))
    """

    def __init__(self, imported_hashes: set[str] | None = None) -> None:
        """Initialize BatchImporter with available parsers.

        Args:
            imported_hashes: Optional set of previously imported file hashes
                for duplicate detection across sessions.
        """
        # Lazy import to avoid circular dependencies
        self._parsers: dict[str, BaseBankParser] | None = None
        # Track imported file hashes for duplicate detection
        self._imported_hashes: set[str] = imported_hashes or set()
        # Track file paths processed in current batch
        self._processed_paths: set[str] = set()

    @property
    def parsers(self) -> dict[str, BaseBankParser]:
        """Get parser instances, lazily initialized."""
        if self._parsers is None:
            from analyze_fin.parsers.bpi import BPIParser
            from analyze_fin.parsers.gcash import GCashParser
            from analyze_fin.parsers.maya import MayaParser

            self._parsers = {
                "gcash": GCashParser(),
                "bpi": BPIParser(),
                "maya_savings": MayaParser(),
                "maya_wallet": MayaParser(),
            }
        return self._parsers

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file contents for duplicate detection.

        Args:
            file_path: Path to the file

        Returns:
            Hex string of SHA-256 hash
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _check_duplicate(self, pdf_path: Path) -> tuple[str | None, str | None]:
        """Check if file is a duplicate.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Tuple of (reason_string, file_hash):
            - reason_string: Reason if duplicate, None if not a duplicate
            - file_hash: Computed hash for tracking after successful parse
        """
        path_str = str(pdf_path.resolve())

        # Check if same path already processed in this batch
        if path_str in self._processed_paths:
            return ("Same file path already processed in this batch", None)

        # Check file hash for content-based duplicate detection
        file_hash: str | None = None
        try:
            file_hash = self._compute_file_hash(pdf_path)
            if file_hash in self._imported_hashes:
                return ("File content matches previously imported statement", None)
            # NOTE: Hash is NOT added here - caller adds after successful parse
        except OSError as e:
            logger.warning(f"Could not compute hash for {pdf_path}: {e}")

        # Mark path as processed
        self._processed_paths.add(path_str)
        return (None, file_hash)

    def import_all(
        self,
        pdf_paths: list[Path],
        progress_callback: ProgressCallback | None = None,
        passwords: dict[str, str] | None = None,
        skip_duplicates: bool = True,
    ) -> BatchImportResult:
        """Import multiple PDF files.

        Args:
            pdf_paths: List of PDF file paths to import
            progress_callback: Optional callback for progress updates
            passwords: Optional dict mapping file paths to passwords
            skip_duplicates: If True, skip duplicate files (default True)

        Returns:
            BatchImportResult with aggregated statistics
        """
        results: list[ParseResult] = []
        errors: list[tuple[str, str]] = []
        duplicates: list[tuple[str, str]] = []
        total = len(pdf_paths)

        for idx, pdf_path in enumerate(pdf_paths, start=1):
            status = "processing"
            file_hash: str | None = None

            # Check for duplicates
            if skip_duplicates:
                dup_reason, file_hash = self._check_duplicate(pdf_path)
                if dup_reason:
                    duplicates.append((str(pdf_path), dup_reason))
                    status = "skipped"
                    if progress_callback:
                        progress_callback(idx, total, pdf_path, status)
                    continue

            try:
                password = passwords.get(str(pdf_path)) if passwords else None
                result = self._parse_file(pdf_path, password)
                results.append(result)
                status = "success"

                # Only add hash after successful parse (prevents false "already imported" on retry)
                if file_hash:
                    self._imported_hashes.add(file_hash)

            except ParseError as e:
                errors.append((str(pdf_path), str(e)))
                status = "failed"
            except Exception as e:
                errors.append((str(pdf_path), f"Unexpected error: {e}"))
                status = "failed"

            if progress_callback:
                progress_callback(idx, total, pdf_path, status)

        # Calculate average quality score
        if results:
            avg_quality = sum(r.quality_score for r in results) / len(results)
        else:
            avg_quality = 0.0

        return BatchImportResult(
            total_files=total,
            successful=len(results),
            failed=len(errors),
            average_quality_score=avg_quality,
            results=results,
            errors=errors,
            duplicates=duplicates,
        )

    def import_directory(
        self,
        directory: Path,
        progress_callback: ProgressCallback | None = None,
        passwords: dict[str, str] | None = None,
        recursive: bool = False,
    ) -> BatchImportResult:
        """Import all PDF files from a directory.

        Args:
            directory: Directory containing PDF files
            progress_callback: Optional callback for progress updates
            passwords: Optional dict mapping file paths to passwords
            recursive: If True, search subdirectories recursively

        Returns:
            BatchImportResult with aggregated statistics
        """
        if recursive:
            pdf_files = list(directory.rglob("*.pdf"))
        else:
            pdf_files = list(directory.glob("*.pdf"))

        return self.import_all(pdf_files, progress_callback, passwords)

    def _parse_file(self, pdf_path: Path, password: str | None = None) -> ParseResult:
        """Parse a single PDF file.

        Automatically detects bank type and uses appropriate parser.

        Args:
            pdf_path: Path to PDF file
            password: Optional password for protected PDFs

        Returns:
            ParseResult from the appropriate parser

        Raises:
            ParseError: If parsing fails
        """
        # Detect bank type
        bank_type = BaseBankParser.detect_bank_type(pdf_path)

        if bank_type is None:
            # Try each parser until one works
            for _parser_type, parser in self.parsers.items():
                try:
                    result = parser.parse(pdf_path, password)
                    result.file_path = pdf_path  # Track source file
                    return result
                except ParseError:
                    continue

            raise ParseError(
                f"Could not determine bank type for {pdf_path}",
                file_path=str(pdf_path),
                reason="Bank type detection failed",
            )

        # Use detected parser
        parser = self.parsers.get(bank_type)
        if parser is None:
            raise ParseError(
                f"No parser available for bank type: {bank_type}",
                file_path=str(pdf_path),
                reason=f"Unsupported bank type: {bank_type}",
            )

        result = parser.parse(pdf_path, password)
        result.file_path = pdf_path  # Track source file
        return result
