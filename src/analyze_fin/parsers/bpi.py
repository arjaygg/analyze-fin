"""
BPI PDF statement parser.

BPI (Bank of the Philippine Islands) statement format:
- Date format: "MM/DD/YYYY" (e.g., "11/15/2024")
- Password-protected PDFs (password: SURNAME + last 4 digits)
- Table columns: Date | Description | Debit | Credit | Balance
"""

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pdfplumber

from analyze_fin.exceptions import ParseError
from analyze_fin.parsers.base import BaseBankParser, ParseResult, RawTransaction


class BPIParser(BaseBankParser):
    """Parser for BPI PDF bank statements.

    Handles password-protected PDFs common with BPI statements.
    Password format: SURNAME + last 4 phone digits (e.g., "GARCIA1234")

    Example:
        parser = BPIParser()
        result = parser.parse(Path("bpi_statement.pdf"), password="GARCIA1234")
        for tx in result.transactions:
            print(f"{tx.date}: {tx.description} - {tx.amount}")

    Security Note:
        Password is used only for PDF decryption and is never stored.
    """

    def extract_transactions(self, pdf_path: Path) -> list[RawTransaction]:
        """Extract transactions from BPI PDF statement.

        Args:
            pdf_path: Path to the BPI PDF file

        Returns:
            List of RawTransaction objects

        Raises:
            ParseError: If PDF cannot be parsed
        """
        return self.parse(pdf_path).transactions

    def parse(self, pdf_path: Path, password: str | None = None) -> ParseResult:
        """Parse BPI PDF and return structured result.

        Args:
            pdf_path: Path to the BPI PDF file
            password: Password for protected PDFs (SURNAME + last 4 digits)

        Returns:
            ParseResult with transactions, quality score, and metadata

        Raises:
            ParseError: If PDF cannot be parsed or password is incorrect
        """
        transactions: list[RawTransaction] = []
        parsing_errors: list[str] = []

        try:
            with pdfplumber.open(pdf_path, password=password) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables() or []

                    for table in tables:
                        if not table:
                            continue

                        for row_idx, row in enumerate(table):
                            if not row or len(row) < 4:
                                continue

                            # Skip header rows
                            first_cell = str(row[0]).strip().lower() if row[0] else ""
                            if first_cell in ("date", "transaction date", "posting date", ""):
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
            error_msg = str(e).lower()
            if "password" in error_msg or "encrypted" in error_msg:
                raise ParseError(
                    "PDF is password-protected. Provide password parameter.",
                    file_path=str(pdf_path),
                    reason="Password required",
                )
            raise ParseError(
                f"Failed to parse BPI PDF: {e}",
                file_path=str(pdf_path),
                reason=str(e),
            )

        quality_score = self.calculate_quality_score(transactions)

        return ParseResult(
            transactions=transactions,
            quality_score=quality_score,
            bank_type="bpi",
            parsing_errors=parsing_errors,
        )

    def _extract_transaction_from_row(self, row: list) -> RawTransaction | None:
        """Extract a single transaction from a BPI table row.

        Expected row format: [Date, Description, Debit, Credit, Balance]

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

        # Parse date
        date = self._parse_date(date_str)

        # Determine amount (debit is negative, credit is positive)
        debit_str = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        credit_str = str(row[3]).strip() if len(row) > 3 and row[3] else ""

        if debit_str and debit_str not in ("", "-", "0", "0.00"):
            amount = -abs(self._parse_amount(debit_str))  # Debit = negative
        elif credit_str and credit_str not in ("", "-", "0", "0.00"):
            amount = abs(self._parse_amount(credit_str))  # Credit = positive
        else:
            raise ValueError("No valid amount found in debit or credit columns")

        # Calculate confidence based on field completeness
        confidence = 1.0
        if len(description) < 3:
            confidence -= 0.1

        return RawTransaction(
            date=date,
            description=description,
            amount=amount,
            reference_number=None,  # BPI doesn't typically show ref# in statements
            confidence=max(0.0, confidence),
        )

    def _parse_date(self, date_str: str) -> datetime:
        """Parse BPI date format: 'MM/DD/YYYY'.

        Args:
            date_str: Date string like "11/15/2024"

        Returns:
            datetime object

        Raises:
            ValueError: If date format is invalid
        """
        # Try BPI format: "MM/DD/YYYY"
        pattern = r"(\d{1,2})/(\d{1,2})/(\d{4})"
        match = re.match(pattern, date_str.strip())

        if not match:
            raise ValueError(f"Invalid date format: {date_str}")

        month_str, day_str, year_str = match.groups()

        return datetime(int(year_str), int(month_str), int(day_str))

    def _parse_amount(self, amount_str: str) -> Decimal:
        """Parse BPI amount format.

        Handles:
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

        # Remove commas and whitespace
        cleaned = amount_str.replace(",", "").replace(" ", "").strip()

        if not cleaned:
            raise ValueError(f"Invalid amount: {amount_str}")

        try:
            amount = Decimal(cleaned)
            if is_negative:
                amount = -amount
            return amount
        except InvalidOperation as e:
            raise ValueError(f"Cannot parse amount '{amount_str}': {e}")
