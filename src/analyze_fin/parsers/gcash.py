"""
GCash PDF statement parser.

GCash statement format:
- Date format: "MMM DD, YYYY" (e.g., "Nov 15, 2024")
- Amount format: "₱1,234.56" or "1234.56"
- Table columns: Date | Description | Reference | Debit | Credit | Balance
"""

import re
import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pdfplumber

from analyze_fin.exceptions import ParseError
from analyze_fin.parsers.base import BaseBankParser, ParseResult, RawTransaction

logger = logging.getLogger(__name__)


class GCashParser(BaseBankParser):
    """Parser for GCash PDF bank statements.

    Extracts transactions from GCash e-wallet statement PDFs.

    Example:
        parser = GCashParser()
        result = parser.parse(Path("gcash_november_2024.pdf"))
        for tx in result.transactions:
            print(f"{tx.date}: {tx.description} - {tx.amount}")
    """

    # Month name to number mapping
    MONTH_MAP = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }

    def extract_transactions(self, pdf_path: Path) -> list[RawTransaction]:
        """Extract transactions from GCash PDF statement.

        Args:
            pdf_path: Path to the GCash PDF file

        Returns:
            List of RawTransaction objects

        Raises:
            ParseError: If PDF cannot be parsed
        """
        return self.parse(pdf_path).transactions

    def parse(self, pdf_path: Path, password: str | None = None) -> ParseResult:
        """Parse GCash PDF and return structured result.

        Args:
            pdf_path: Path to the GCash PDF file
            password: Optional password for protected PDFs

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
        account_number = None
        account_holder = None
        period_start = None
        period_end = None

        try:
            with pdfplumber.open(pdf_path, password=password) as pdf:
                # Extract account info from first page
                if pdf.pages:
                    first_page_text = pdf.pages[0].extract_text() or ""
                    account_number, account_holder, period_start, period_end = (
                        self._extract_account_info(first_page_text)
                    )

                for page_num, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables() or []

                    for table in tables:
                        if not table:
                            continue

                        # Skip header row(s) - look for rows that start with a date
                        for row_idx, row in enumerate(table):
                            if not row or len(row) < 4:
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
                f"Failed to parse GCash PDF: {e}",
                file_path=str(pdf_path),
                reason=str(e),
            ) from e

        quality_score = self.calculate_quality_score(transactions)

        # Adjust quality score for missing account info (Story 5.1 AC#4)
        if account_number is None:
            quality_score = max(0.0, quality_score - 0.05)
            logger.warning("GCash: Could not extract account number from statement")
        if period_start is None or period_end is None:
            quality_score = max(0.0, quality_score - 0.02)
            logger.warning("GCash: Could not extract statement period dates")

        return ParseResult(
            transactions=transactions,
            quality_score=quality_score,
            bank_type="gcash",
            parsing_errors=parsing_errors,
            account_number=account_number,
            account_holder=account_holder,
            period_start=period_start,
            period_end=period_end,
        )

    def _extract_transaction_from_row(self, row: list) -> RawTransaction | None:
        """Extract a single transaction from a table row.

        Expected row format: [Date, Description, Ref#, Debit, Credit, Balance]

        Args:
            row: List of cell values from PDF table

        Returns:
            RawTransaction or None if row is invalid

        Raises:
            ValueError: If date or amount parsing fails
        """
        if len(row) < 4:
            raise ValueError(f"Row too short: {len(row)} columns")

        # Extract fields
        date_str = str(row[0]).strip() if row[0] else ""
        description = str(row[1]).strip() if len(row) > 1 and row[1] else ""
        reference = str(row[2]).strip() if len(row) > 2 and row[2] else None

        # Parse date
        date = self._parse_date(date_str)

        # Determine amount (debit is negative, credit is positive)
        debit_str = str(row[3]).strip() if len(row) > 3 and row[3] else ""
        credit_str = str(row[4]).strip() if len(row) > 4 and row[4] else ""

        if debit_str and debit_str not in ("", "-", "0", "0.00"):
            amount = -abs(self._parse_amount(debit_str))  # Debit = negative
        elif credit_str and credit_str not in ("", "-", "0", "0.00"):
            amount = abs(self._parse_amount(credit_str))  # Credit = positive
        else:
            raise ValueError("No valid amount found in debit or credit columns")

        # Calculate confidence based on field completeness
        confidence = 1.0
        if not reference:
            confidence -= 0.05
        if len(description) < 3:
            confidence -= 0.1

        return RawTransaction(
            date=date,
            description=description,
            amount=amount,
            reference_number=reference if reference else None,
            confidence=max(0.0, confidence),
        )

    def _parse_date(self, date_str: str) -> datetime:
        """Parse GCash date format: 'MMM DD, YYYY'.

        Args:
            date_str: Date string like "Nov 15, 2024"

        Returns:
            datetime object

        Raises:
            ValueError: If date format is invalid
        """
        # Try GCash format: "Nov 15, 2024"
        pattern = r"([A-Za-z]{3})\s+(\d{1,2}),?\s*(\d{4})"
        match = re.match(pattern, date_str.strip())

        if not match:
            raise ValueError(f"Invalid date format: {date_str}")

        month_str, day_str, year_str = match.groups()
        month_num = self.MONTH_MAP.get(month_str.lower())

        if not month_num:
            raise ValueError(f"Unknown month: {month_str}")

        return datetime(int(year_str), month_num, int(day_str))

    def _parse_amount(self, amount_str: str) -> Decimal:
        """Parse GCash amount format.

        Handles:
        - '₱1,234.56'
        - '1,234.56'
        - '(1,234.56)' - negative
        - '-1,234.56' - negative

        Args:
            amount_str: Amount string

        Returns:
            Decimal amount

        Raises:
            ValueError: If amount format is invalid
        """
        if not amount_str:
            raise ValueError("Empty amount string")

        # Check for negative in parentheses
        is_negative = False
        if amount_str.startswith("(") and amount_str.endswith(")"):
            is_negative = True
            amount_str = amount_str[1:-1]
        elif amount_str.startswith("-"):
            is_negative = True
            amount_str = amount_str[1:]

        # Remove currency symbol and whitespace
        cleaned = amount_str.replace("₱", "").replace(",", "").replace(" ", "").strip()

        if not cleaned:
            raise ValueError(f"Invalid amount: {amount_str}")

        try:
            amount = Decimal(cleaned)
            if is_negative:
                amount = -amount
            return amount
        except InvalidOperation as e:
            raise ValueError(f"Cannot parse amount '{amount_str}': {e}") from e

    def _extract_account_info(
        self, text: str
    ) -> tuple[str | None, str | None, date | None, date | None]:
        """Extract account info from PDF header text.

        Args:
            text: Full text from PDF first page

        Returns:
            Tuple of (account_number, account_holder, period_start, period_end)
            Any field may be None if not found.
        """
        account_number = None
        account_holder = None
        period_start = None
        period_end = None

        # Extract mobile number - Philippine format: 09XX XXX XXXX or variations
        # Patterns: "0917 123 4567", "09171234567", "0917-123-4567"
        mobile_pattern = r"09\d{2}[\s\-]?\d{3}[\s\-]?\d{4}"
        mobile_match = re.search(mobile_pattern, text)
        if mobile_match:
            # Normalize to 11 digits without spaces/dashes
            raw_number = mobile_match.group()
            account_number = re.sub(r"[\s\-]", "", raw_number)

        # Extract account holder name - look for "Name:" followed by text
        name_pattern = r"Name:\s*([A-Z][A-Z\s]+?)(?:\n|$)"
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            account_holder = name_match.group(1).strip()

        # Extract statement period - format: "Statement Period: Nov 01 - Nov 30, 2024"
        period_pattern = r"Statement\s*Period:\s*([A-Za-z]{3})\s+(\d{1,2})\s*-\s*([A-Za-z]{3})\s+(\d{1,2}),?\s*(\d{4})"
        period_match = re.search(period_pattern, text, re.IGNORECASE)
        if period_match:
            start_month_str, start_day, end_month_str, end_day, year = (
                period_match.groups()
            )
            start_month = self.MONTH_MAP.get(start_month_str.lower())
            end_month = self.MONTH_MAP.get(end_month_str.lower())

            if start_month and end_month:
                try:
                    period_start = date(int(year), start_month, int(start_day))
                    period_end = date(int(year), end_month, int(end_day))
                except ValueError as e:
                    logger.warning(f"Invalid statement period dates: {e}")

        return account_number, account_holder, period_start, period_end
