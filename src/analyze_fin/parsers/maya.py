"""
Maya PDF statement parser.

Maya (formerly PayMaya) statement format:
- Two account types: maya_savings and maya_wallet
- Date format varies: "YYYY-MM-DD", "DD/MM/YYYY", or "MM/DD/YYYY"
- Table columns typically: Date | Description | Amount | Balance
"""

import logging
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pdfplumber

from analyze_fin.exceptions import ParseError
from analyze_fin.parsers.base import BaseBankParser, ParseResult, RawTransaction

logger = logging.getLogger(__name__)


class MayaParser(BaseBankParser):
    """Parser for Maya PDF statements.

    Handles both Maya Savings and Maya Wallet account statements.

    Example:
        parser = MayaParser()
        result = parser.parse(Path("maya_statement.pdf"))
        print(f"Account type: {result.bank_type}")  # maya_savings or maya_wallet
        for tx in result.transactions:
            print(f"{tx.date}: {tx.description} - {tx.amount}")
    """

    def extract_transactions(self, pdf_path: Path) -> list[RawTransaction]:
        """Extract transactions from Maya PDF statement.

        Args:
            pdf_path: Path to the Maya PDF file

        Returns:
            List of RawTransaction objects

        Raises:
            ParseError: If PDF cannot be parsed
        """
        return self.parse(pdf_path).transactions

    def parse(self, pdf_path: Path, password: str | None = None) -> ParseResult:
        """Parse Maya PDF and return structured result.

        Args:
            pdf_path: Path to the Maya PDF file
            password: Optional password (Maya PDFs typically not protected)

        Returns:
            ParseResult with transactions, quality score, and metadata

        Raises:
            ParseError: If PDF cannot be parsed or file doesn't exist
        """
        # Validate file exists
        if not pdf_path.exists():
            raise ParseError(
                f"File not found: {pdf_path}",
                file_path=str(pdf_path),
                reason="File does not exist",
            )

        transactions: list[RawTransaction] = []
        parsing_errors: list[str] = []
        bank_type = "maya_wallet"  # Default

        try:
            with pdfplumber.open(pdf_path, password=password) as pdf:
                # Detect account type from first page
                if pdf.pages:
                    first_page_text = pdf.pages[0].extract_text() or ""
                    bank_type = self._detect_account_type(first_page_text)

                for page_num, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables() or []

                    for table in tables:
                        if not table:
                            continue

                        for row_idx, row in enumerate(table):
                            if not row or len(row) < 3:
                                continue

                            # Skip header rows
                            first_cell = str(row[0]).strip().lower() if row[0] else ""
                            if first_cell in ("date", "transaction date", ""):
                                continue

                            try:
                                tx = self._extract_transaction_from_row(row)
                                if tx:
                                    transactions.append(tx)
                            except (ValueError, InvalidOperation) as e:
                                parsing_errors.append(
                                    f"Page {page_num}, row {row_idx}: {e}"
                                )

        except Exception as e:
            raise ParseError(
                f"Failed to parse Maya PDF: {e}",
                file_path=str(pdf_path),
                reason=str(e),
            ) from e

        quality_score = self.calculate_quality_score(transactions)

        return ParseResult(
            transactions=transactions,
            quality_score=quality_score,
            bank_type=bank_type,
            parsing_errors=parsing_errors,
        )

    def _detect_account_type(self, text: str) -> str:
        """Detect Maya account type from PDF text.

        Args:
            text: Extracted text from first PDF page

        Returns:
            'maya_savings' or 'maya_wallet'
        """
        text_lower = text.lower()

        if "savings" in text_lower:
            return "maya_savings"
        elif "wallet" in text_lower:
            return "maya_wallet"

        # Default to wallet for generic Maya statements
        return "maya_wallet"

    def _extract_transaction_from_row(self, row: list) -> RawTransaction | None:
        """Extract a single transaction from a Maya table row.

        Expected row format: [Date, Description, Amount, Balance] or similar

        Args:
            row: List of cell values from PDF table

        Returns:
            RawTransaction or None if row is invalid

        Raises:
            ValueError: If date or amount parsing fails
        """
        if len(row) < 3:
            raise ValueError(f"Row too short: {len(row)} columns")

        # Extract fields - Maya format varies
        date_str = str(row[0]).strip() if row[0] else ""
        description = str(row[1]).strip() if len(row) > 1 and row[1] else ""
        amount_str = str(row[2]).strip() if len(row) > 2 and row[2] else ""

        # Parse date
        date = self._parse_date(date_str)

        # Parse amount
        amount = self._parse_amount(amount_str)

        # Calculate confidence based on field completeness
        confidence = 1.0
        if len(description) < 3:
            confidence -= 0.1

        return RawTransaction(
            date=date,
            description=description,
            amount=amount,
            reference_number=None,
            confidence=max(0.0, confidence),
        )

    def _parse_date(self, date_str: str) -> datetime:
        """Parse Maya date format.

        Handles multiple formats:
        - 'YYYY-MM-DD' (ISO format) - Unambiguous
        - 'DD/MM/YYYY' (European format) - Detected when day > 12
        - 'MM/DD/YYYY' (US format) - Default assumption

        Note: Dates like "05/12/2024" are ambiguous and default to MM/DD/YYYY
        (May 12, 2024). A warning is logged for ambiguous dates.

        Args:
            date_str: Date string

        Returns:
            datetime object

        Raises:
            ValueError: If date format is invalid
        """
        date_str = date_str.strip()

        # Try ISO format: YYYY-MM-DD (unambiguous)
        iso_pattern = r"(\d{4})-(\d{1,2})-(\d{1,2})"
        match = re.match(iso_pattern, date_str)
        if match:
            year, month, day = match.groups()
            return datetime(int(year), int(month), int(day))

        # Try slash format: DD/MM/YYYY or MM/DD/YYYY
        slash_pattern = r"(\d{1,2})/(\d{1,2})/(\d{4})"
        match = re.match(slash_pattern, date_str)
        if match:
            first, second, year = match.groups()
            first_int = int(first)
            second_int = int(second)
            year_int = int(year)

            # Heuristic: if first > 12, it must be DD/MM/YYYY
            if first_int > 12:
                # DD/MM/YYYY - unambiguous
                return datetime(year_int, second_int, first_int)
            elif second_int > 12:
                # Second > 12 means first must be month (MM/DD/YYYY)
                return datetime(year_int, first_int, second_int)
            else:
                # Ambiguous: both values could be month or day
                # Default to MM/DD/YYYY but log warning
                logger.debug(
                    f"Ambiguous date format '{date_str}': interpreting as MM/DD/YYYY "
                    f"({first_int}/{second_int}/{year_int} = month {first_int}, day {second_int}). "
                    f"If this is incorrect, dates may be wrong."
                )
                return datetime(year_int, first_int, second_int)

        raise ValueError(f"Invalid date format: {date_str}")

    def _parse_amount(self, amount_str: str) -> Decimal:
        """Parse Maya amount format.

        Handles:
        - 'PHP 1,234.56'
        - '₱1,234.56'
        - '1,234.56'
        - '-1,234.56' (negative)

        Args:
            amount_str: Amount string

        Returns:
            Decimal amount

        Raises:
            ValueError: If amount format is invalid
        """
        if not amount_str:
            raise ValueError("Empty amount string")

        # Check for negative
        is_negative = False
        if amount_str.startswith("-"):
            is_negative = True
            amount_str = amount_str[1:]
        elif amount_str.startswith("(") and amount_str.endswith(")"):
            is_negative = True
            amount_str = amount_str[1:-1]

        # Remove currency symbols and whitespace
        cleaned = (
            amount_str
            .replace("PHP", "")
            .replace("₱", "")
            .replace(",", "")
            .replace(" ", "")
            .strip()
        )

        if not cleaned:
            raise ValueError(f"Invalid amount: {amount_str}")

        try:
            amount = Decimal(cleaned)
            if is_negative:
                amount = -amount
            return amount
        except InvalidOperation as e:
            raise ValueError(f"Cannot parse amount '{amount_str}': {e}") from e
