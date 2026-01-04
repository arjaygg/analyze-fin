"""
BPI PDF statement parser.

BPI (Bank of the Philippine Islands) statement format:
- Date format: "MM/DD/YYYY" (e.g., "11/15/2024")
- Password-protected PDFs (password provided by user)
- Table columns: Date | Description | Debit | Credit | Balance
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

# Month name to number mapping
MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


class BPIParser(BaseBankParser):
    """Parser for BPI PDF bank statements.

    Handles password-protected PDFs common with BPI statements.
    Password should be provided by the user when calling parse().

    Example:
        parser = BPIParser()
        result = parser.parse(Path("bpi_statement.pdf"), password="your_password")
        for tx in result.transactions:
            print(f"{tx.date}: {tx.description} - {tx.amount}")

    Security Note:
        Password is used only for PDF decryption and is never stored or logged.
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
            password: Password for protected PDFs (if required)

        Returns:
            ParseResult with transactions, quality score, and metadata

        Raises:
            ParseError: If PDF cannot be parsed, password is incorrect, or file doesn't exist
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

                # Try table extraction first (standard format)
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

                # If no transactions found or quality too low, try text-based parsing (Savings Account format)
                if len(transactions) == 0 or (transactions and all(tx.confidence < 0.5 for tx in transactions)):
                    transactions = []
                    parsing_errors = []
                    for page_num, page in enumerate(pdf.pages, start=1):
                        text = page.extract_text() or ""
                        page_txs, page_errors = self._parse_text_format(text, page_num)
                        transactions.extend(page_txs)
                        parsing_errors.extend(page_errors)

        except Exception as e:
            error_msg = str(e).lower()
            if "password" in error_msg or "encrypted" in error_msg:
                raise ParseError(
                    "PDF is password-protected. Provide password parameter.",
                    file_path=str(pdf_path),
                    reason="Password required",
                ) from e
            raise ParseError(
                f"Failed to parse BPI PDF: {e}",
                file_path=str(pdf_path),
                reason=str(e),
            ) from e

        quality_score = self.calculate_quality_score(transactions)

        # Adjust quality score for missing account info (Story 5.1 AC#4)
        if account_number is None:
            quality_score = max(0.0, quality_score - 0.05)
            logger.warning("BPI: Could not extract account number from statement")
        if period_start is None or period_end is None:
            quality_score = max(0.0, quality_score - 0.02)
            logger.warning("BPI: Could not extract statement period dates")

        return ParseResult(
            transactions=transactions,
            quality_score=quality_score,
            bank_type="bpi",
            parsing_errors=parsing_errors,
            account_number=account_number,
            account_holder=account_holder,
            period_start=period_start,
            period_end=period_end,
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

    def _parse_text_format(self, text: str, page_num: int) -> tuple[list[RawTransaction], list[str]]:
        """Parse BPI Savings Account text format (MMM DD date style).

        This handles BPI statements where dates are "MMM DD" (e.g., "Sep 29", "Oct 02")
        and transactions are line-by-line text rather than table format.

        Args:
            text: Raw text from PDF page
            page_num: Page number for error reporting

        Returns:
            Tuple of (transactions list, errors list)
        """
        transactions: list[RawTransaction] = []
        errors: list[str] = []

        # Extract year from "PERIOD COVERED" line
        year_match = re.search(r'PERIOD COVERED.*?(\d{4})', text)
        year = int(year_match.group(1)) if year_match else datetime.now().year

        # Pattern for transaction lines: "MMM DD Description [REF] [DETAILS] Amount(s) Balance"
        # Amount can be in DEBIT or CREDIT column (before balance)
        lines = text.split('\n')

        for line_num, line in enumerate(lines, start=1):
            # Match lines starting with month abbreviation + day
            tx_pattern = r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})\s+(.+)'
            match = re.match(tx_pattern, line.strip())

            if not match:
                continue

            month_abbr, day, rest = match.groups()

            try:
                # Parse date
                date_str = f"{month_abbr} {day} {year}"
                date = datetime.strptime(date_str, "%b %d %Y")

                # Extract description and amounts from rest of line
                # Pattern: Description [Numbers] [Numbers] Balance
                # Need to find the last number (balance) and work backwards

                # Split by whitespace and find numeric values
                parts = rest.split()
                numbers = []
                desc_parts = []

                for part in parts:
                    # Check if this looks like a number (with comma separators)
                    if re.match(r'^\d{1,3}(,\d{3})*(\.\d{2})?$', part):
                        numbers.append(part)
                    elif not numbers:  # Before we find numbers, it's description
                        desc_parts.append(part)

                if len(numbers) < 2:  # Need at least amount + balance
                    continue

                description = ' '.join(desc_parts)
                if not description:
                    description = "Transaction"

                # Last number is balance, second-to-last is the amount
                balance_str = numbers[-1]
                amount_str = numbers[-2]

                # Parse amount
                amount = self._parse_amount(amount_str)

                # Determine if debit or credit by checking if there are 3+ numbers
                # If 3 numbers: [debit, credit, balance] or [amount, amount, balance]
                # We'll determine sign by comparing with balance direction
                # For now, assume withdrawals are more common and mark as negative
                # This is a heuristic - better would be to track balance changes

                # Simple heuristic: If description contains transfer OUT keywords, it's debit
                debit_keywords = ['transfer fee', 'payment', 'bills payment', 'tax withheld']
                credit_keywords = ['from:', 'interest earned', 'cash in']

                desc_lower = description.lower()
                if any(kw in desc_lower for kw in debit_keywords):
                    amount = -abs(amount)
                elif any(kw in desc_lower for kw in credit_keywords):
                    amount = abs(amount)
                elif 'instapay transfer' in desc_lower and 'from:' not in desc_lower:
                    amount = -abs(amount)  # Outgoing transfer
                # If ambiguous, leave as-is (positive)

                tx = RawTransaction(
                    date=date,
                    description=description[:200],  # Limit description length
                    amount=amount,
                    reference_number=None,
                    confidence=0.9,  # High confidence for text parsing
                )
                transactions.append(tx)

            except (ValueError, InvalidOperation) as e:
                errors.append(f"Page {page_num}, line {line_num}: {e}")

        return transactions, errors

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
            Account number is masked to show only last 4 digits.
        """
        account_number = None
        account_holder = None
        period_start = None
        period_end = None

        # Extract account number - various BPI formats
        # Patterns: "Account Number: 1234-5678-9012", "Account No: 123456789012", "Acct No.: 1234 5678 9012"
        acct_pattern = r"(?:Account\s*(?:Number|No\.?)|Acct\s*No\.?)[\s:]*(\d[\d\s\-]+\d)"
        acct_match = re.search(acct_pattern, text, re.IGNORECASE)
        if acct_match:
            # Extract digits only and mask all but last 4
            raw_number = re.sub(r"[\s\-]", "", acct_match.group(1))
            if len(raw_number) >= 4:
                account_number = f"****{raw_number[-4:]}"

        # Extract account holder name - look for "Account Name:" followed by text
        name_pattern = r"Account\s*Name:\s*([A-Z][A-Z\s]+?)(?:\n|$)"
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            account_holder = name_match.group(1).strip()

        # Extract statement period - format: "Statement Period: November 01, 2024 - November 30, 2024"
        # or "PERIOD COVERED: ..."
        period_pattern = r"(?:Statement\s*Period|PERIOD\s*COVERED)[\s:]*([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})\s*[-–]\s*([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})"
        period_match = re.search(period_pattern, text, re.IGNORECASE)
        if period_match:
            start_month_str, start_day, start_year, end_month_str, end_day, end_year = (
                period_match.groups()
            )
            start_month = MONTH_MAP.get(start_month_str.lower())
            end_month = MONTH_MAP.get(end_month_str.lower())

            if start_month and end_month:
                try:
                    period_start = date(int(start_year), start_month, int(start_day))
                    period_end = date(int(end_year), end_month, int(end_day))
                except ValueError as e:
                    logger.warning(f"Invalid statement period dates: {e}")

        return account_number, account_holder, period_start, period_end
