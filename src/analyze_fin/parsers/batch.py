"""
Batch import functionality for multiple PDF statements.

Provides:
- BatchImporter: Process multiple PDF files
- BatchImportResult: Aggregated import results
- Progress callbacks for CLI feedback
- Quality score aggregation
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from analyze_fin.exceptions import ParseError
from analyze_fin.parsers.base import BaseBankParser, ParseResult


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
    """

    total_files: int
    successful: int
    failed: int
    average_quality_score: float
    results: list[ParseResult] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)


# Progress callback type: (current, total, file_path, status)
ProgressCallback = Callable[[int, int, Path, str], None]


class BatchImporter:
    """Batch importer for processing multiple PDF statements.

    Automatically detects bank type and uses the appropriate parser.

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

        # Import from directory
        result = importer.import_directory(Path("statements/"))
    """

    def __init__(self) -> None:
        """Initialize BatchImporter with available parsers."""
        # Lazy import to avoid circular dependencies
        self._parsers: dict[str, BaseBankParser] | None = None

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

    def import_all(
        self,
        pdf_paths: list[Path],
        progress_callback: ProgressCallback | None = None,
        passwords: dict[str, str] | None = None,
    ) -> BatchImportResult:
        """Import multiple PDF files.

        Args:
            pdf_paths: List of PDF file paths to import
            progress_callback: Optional callback for progress updates
            passwords: Optional dict mapping file paths to passwords

        Returns:
            BatchImportResult with aggregated statistics
        """
        results: list[ParseResult] = []
        errors: list[tuple[str, str]] = []
        total = len(pdf_paths)

        for idx, pdf_path in enumerate(pdf_paths, start=1):
            status = "processing"

            try:
                password = passwords.get(str(pdf_path)) if passwords else None
                result = self._parse_file(pdf_path, password)
                results.append(result)
                status = "success"
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
            for parser_type, parser in self.parsers.items():
                try:
                    return parser.parse(pdf_path, password)
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

        return parser.parse(pdf_path, password)
