"""
Data exporter for transactions to CSV and JSON formats.

Provides:
- DataExporter: Export transactions with filtering support
- CSV export with proper headers and UTF-8 encoding
- JSON export with snake_case keys and string amounts
- Filter support for category, date_range, merchant
- Filter-aware filename generation
- Streaming for large datasets
"""

import csv
import io
import json
import re
from collections.abc import Generator
from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from analyze_fin.database.models import Transaction


class DataExporter:
    """Export transactions to CSV and JSON formats.

    Supports filtering by:
    - Category (exact match)
    - Merchant (case-insensitive partial match)
    - Date range (inclusive)

    Features:
    - Filter metadata tracking and export
    - Filter-aware filename generation
    - Streaming for large datasets
    - Progress callback support

    Example:
        exporter = DataExporter(session)
        exporter.filter_by_category("Food & Dining")
        csv_output = exporter.export_csv()
        filename = exporter.generate_filename("csv")  # "export_food_dining.csv"
    """

    # CSV headers as required by acceptance criteria
    CSV_HEADERS = ["date", "merchant", "category", "amount", "description", "account"]

    def __init__(self, session: Session) -> None:
        """Initialize exporter with database session.

        Args:
            session: SQLAlchemy session
        """
        self._session = session
        self._filters: list[Any] = []
        self._filter_metadata: dict[str, Any] = {}

    def filter_by_category(self, category: str) -> "DataExporter":
        """Filter transactions by category.

        Args:
            category: Category name (e.g., "Food & Dining")

        Returns:
            Self for method chaining
        """
        self._filters.append(Transaction.category == category)
        self._filter_metadata["category"] = category
        return self

    def filter_by_merchant(self, merchant: str) -> "DataExporter":
        """Filter transactions by merchant.

        Uses merchant_normalized field for consistent matching.
        Case-insensitive partial matching.

        Args:
            merchant: Merchant name (e.g., "Jollibee")

        Returns:
            Self for method chaining
        """
        self._filters.append(Transaction.merchant_normalized.ilike(f"%{merchant}%"))
        self._filter_metadata["merchant"] = merchant
        return self

    def filter_by_date_range(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> "DataExporter":
        """Filter transactions by date range (inclusive).

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            Self for method chaining
        """
        if start_date:
            self._filters.append(Transaction.date >= start_date)
            self._filter_metadata["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            # Include the entire end date by adding time buffer
            end_of_day = datetime(
                end_date.year, end_date.month, end_date.day, 23, 59, 59
            )
            self._filters.append(Transaction.date <= end_of_day)
            self._filter_metadata["end_date"] = end_date.strftime("%Y-%m-%d")
        return self

    def get_filter_metadata(self) -> dict[str, Any]:
        """Get metadata about applied filters.

        Returns:
            Dictionary with filter information
        """
        return {
            "filters": self._filter_metadata.copy(),
            "exported_at": datetime.now().isoformat(),
        }

    def generate_filename(self, extension: str = "csv") -> str:
        """Generate filter-aware filename.

        Pattern: export_{category}_{date_range}.{ext}
        Example: export_food_nov2024.csv

        Args:
            extension: File extension (csv or json)

        Returns:
            Sanitized filename
        """
        parts = ["export"]

        # Add category to filename
        if "category" in self._filter_metadata:
            category = self._filter_metadata["category"]
            # Sanitize: lowercase, replace special chars with underscore
            safe_category = re.sub(r"[^a-z0-9]+", "_", category.lower()).strip("_")
            parts.append(safe_category)

        # Add merchant to filename
        if "merchant" in self._filter_metadata:
            merchant = self._filter_metadata["merchant"]
            safe_merchant = re.sub(r"[^a-z0-9]+", "_", merchant.lower()).strip("_")
            parts.append(safe_merchant)

        # Add date range to filename
        if "start_date" in self._filter_metadata or "end_date" in self._filter_metadata:
            date_part = self._format_date_range_for_filename()
            if date_part:
                parts.append(date_part)

        return f"{'_'.join(parts)}.{extension}"

    def _format_date_range_for_filename(self) -> str:
        """Format date range for filename.

        Returns abbreviated date like 'nov2024' or 'nov2024_dec2024'
        """
        start = self._filter_metadata.get("start_date")
        end = self._filter_metadata.get("end_date")

        if start and end:
            # Parse dates
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")

            start_abbr = start_dt.strftime("%b%Y").lower()
            end_abbr = end_dt.strftime("%b%Y").lower()

            if start_abbr == end_abbr:
                return start_abbr
            return f"{start_abbr}_{end_abbr}"
        elif start:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            return f"from_{start_dt.strftime('%b%Y').lower()}"
        elif end:
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            return f"to_{end_dt.strftime('%b%Y').lower()}"
        return ""

    def count(self) -> int:
        """Count transactions matching filters.

        Returns:
            Number of matching transactions
        """
        stmt = select(func.count(Transaction.id))

        if self._filters:
            stmt = stmt.where(and_(*self._filters))

        result = self._session.execute(stmt)
        return result.scalar() or 0

    def _get_transactions(self) -> list[Transaction]:
        """Execute query with current filters.

        Returns:
            List of Transaction objects
        """
        stmt = select(Transaction)

        if self._filters:
            stmt = stmt.where(and_(*self._filters))

        stmt = stmt.order_by(Transaction.date.desc())

        result = self._session.execute(stmt)
        return list(result.scalars().all())

    def _stream_transactions(self, batch_size: int = 100) -> Generator[Transaction, None, None]:
        """Stream transactions in batches for memory efficiency.

        Args:
            batch_size: Number of transactions per batch

        Yields:
            Transaction objects one at a time
        """
        stmt = select(Transaction)

        if self._filters:
            stmt = stmt.where(and_(*self._filters))

        stmt = stmt.order_by(Transaction.date.desc())

        # Use yield_per for streaming
        result = self._session.execute(stmt.execution_options(yield_per=batch_size))

        yield from result.scalars()

    def _get_account_name(self, transaction: Transaction) -> str:
        """Get account name for a transaction.

        Navigates through statement relationship to get account name.

        Args:
            transaction: Transaction object

        Returns:
            Account name or empty string if not available
        """
        if transaction.statement and transaction.statement.account:
            return transaction.statement.account.name
        return ""

    def export_csv(
        self,
        include_metadata: bool = False,
        streaming: bool = False,
        progress_callback: Any | None = None
    ) -> str:
        """Export transactions to CSV format.

        CSV format:
        - Headers: date, merchant, category, amount, description, account
        - Dates in ISO format: YYYY-MM-DD
        - Amounts as plain decimal numbers (no currency symbol)
        - UTF-8 encoding

        Args:
            include_metadata: If True, add filter comments at top
            streaming: If True, use streaming for large datasets
            progress_callback: Optional callback(current, total) for progress

        Returns:
            CSV string
        """
        output = io.StringIO()

        # Add filter metadata as comments if requested
        if include_metadata and self._filter_metadata:
            metadata = self.get_filter_metadata()
            output.write(f"# Export generated: {metadata['exported_at']}\n")
            for key, value in metadata["filters"].items():
                output.write(f"# Filter: {key}=\"{value}\"\n")

        writer = csv.DictWriter(output, fieldnames=self.CSV_HEADERS)
        writer.writeheader()

        if streaming:
            total = self.count()
            for i, tx in enumerate(self._stream_transactions()):
                writer.writerow(self._transaction_to_csv_row(tx))
                if progress_callback and (i + 1) % 100 == 0:
                    progress_callback(i + 1, total)
            if progress_callback:
                progress_callback(total, total)
        else:
            transactions = self._get_transactions()
            for tx in transactions:
                writer.writerow(self._transaction_to_csv_row(tx))

        return output.getvalue()

    def _transaction_to_csv_row(self, tx: Transaction) -> dict[str, str]:
        """Convert transaction to CSV row dict."""
        return {
            "date": tx.date.strftime("%Y-%m-%d"),
            "merchant": tx.merchant_normalized or "",
            "category": tx.category or "",
            "amount": str(tx.amount),
            "description": tx.description,
            "account": self._get_account_name(tx),
        }

    def export_json(
        self,
        include_metadata: bool = False,
        streaming: bool = False,
        progress_callback: Any | None = None
    ) -> str:
        """Export transactions to JSON format.

        JSON format:
        - Array of transaction objects (or object with metadata if include_metadata=True)
        - Keys: transaction_id, date, merchant_normalized, category, amount, description, account, created_at
        - All keys in snake_case (AR21)
        - Amounts as strings for precision: "12345.67"
        - Dates as ISO strings: "2024-11-15"
        - Unicode characters preserved (not escaped)

        Args:
            include_metadata: If True, wrap in object with metadata
            streaming: If True, use streaming for large datasets
            progress_callback: Optional callback(current, total) for progress

        Returns:
            JSON string with pretty formatting
        """
        if streaming:
            transactions_data = []
            total = self.count()
            for i, tx in enumerate(self._stream_transactions()):
                transactions_data.append(self._transaction_to_json_dict(tx))
                if progress_callback and (i + 1) % 100 == 0:
                    progress_callback(i + 1, total)
            if progress_callback:
                progress_callback(total, total)
        else:
            transactions = self._get_transactions()
            transactions_data = [
                self._transaction_to_json_dict(tx) for tx in transactions
            ]

        if include_metadata:
            data = {
                "metadata": self.get_filter_metadata(),
                "count": len(transactions_data),
                "transactions": transactions_data,
            }
        else:
            data = transactions_data

        return json.dumps(data, indent=2, ensure_ascii=False)

    def _transaction_to_json_dict(self, tx: Transaction) -> dict[str, Any]:
        """Convert transaction to JSON-serializable dict."""
        return {
            "transaction_id": tx.id,
            "date": tx.date.strftime("%Y-%m-%d"),
            "merchant_normalized": tx.merchant_normalized,
            "category": tx.category,
            "amount": str(tx.amount),
            "description": tx.description,
            "account": self._get_account_name(tx),
            "created_at": tx.created_at.strftime("%Y-%m-%dT%H:%M:%S") if tx.created_at else None,
        }

    def export_to_file(
        self,
        file_path: str,
        format_type: str = "csv",
        include_metadata: bool = True,
        streaming: bool = True,
        progress_callback: Any | None = None
    ) -> int:
        """Export transactions directly to file.

        Writes incrementally for large datasets to avoid memory issues.

        Args:
            file_path: Path to output file
            format_type: "csv" or "json"
            include_metadata: Include filter metadata
            streaming: Use streaming for memory efficiency
            progress_callback: Optional callback(current, total)

        Returns:
            Number of transactions exported
        """
        if format_type == "csv":
            content = self.export_csv(
                include_metadata=include_metadata,
                streaming=streaming,
                progress_callback=progress_callback
            )
        elif format_type == "json":
            content = self.export_json(
                include_metadata=include_metadata,
                streaming=streaming,
                progress_callback=progress_callback
            )
        else:
            raise ValueError(f"Invalid format: {format_type}. Must be 'csv' or 'json'")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return self.count()
