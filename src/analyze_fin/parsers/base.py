"""
Base classes for bank statement parsers.

Strategy pattern: Each bank parser inherits from BaseBankParser
and implements the extract_transactions() method.

Supported banks:
- GCash (gcash)
- BPI (bpi)
- Maya Savings (maya_savings)
- Maya Wallet (maya_wallet)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RawTransaction:
    """Raw transaction data extracted from PDF.

    This is the intermediate format before storing to database.
    """

    date: datetime
    description: str
    amount: Decimal
    reference_number: str | None = None
    confidence: float = 1.0  # 0.0 to 1.0, how confident the extraction is


@dataclass
class ParseResult:
    """Result of parsing a bank statement PDF.

    Contains extracted transactions, quality score, and metadata.
    """

    transactions: list[RawTransaction]
    quality_score: float  # 0.0 to 1.0
    bank_type: str  # gcash, bpi, maya_savings, maya_wallet
    file_path: Path | None = None  # Source file path for database persistence

    # Optional metadata
    opening_balance: Decimal | None = None
    closing_balance: Decimal | None = None
    statement_date: datetime | None = None
    parsing_errors: list[str] = field(default_factory=list)


class BaseBankParser(ABC):
    """Abstract base class for bank statement parsers.

    Strategy pattern: Each bank implements its own parser
    that inherits from this class.

    Example:
        class GCashParser(BaseBankParser):
            def extract_transactions(self, pdf_path: Path) -> list[RawTransaction]:
                # GCash-specific extraction logic
                ...
    """

    @abstractmethod
    def extract_transactions(self, pdf_path: Path) -> list[RawTransaction]:
        """Extract transactions from a PDF bank statement.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of RawTransaction objects

        Raises:
            ParseError: If PDF cannot be parsed
        """
        pass

    def calculate_quality_score(self, transactions: list[RawTransaction]) -> float:
        """Calculate quality score based on extraction confidence.

        The quality score is the average confidence across all transactions.

        Args:
            transactions: List of extracted transactions

        Returns:
            Quality score between 0.0 and 1.0
            - >= 0.95: High confidence, auto-accept
            - 0.80 - 0.95: Medium confidence, review flagged rows
            - < 0.80: Low confidence, manual review required
        """
        if not transactions:
            return 0.0

        total_confidence = sum(tx.confidence for tx in transactions)
        return total_confidence / len(transactions)

    @staticmethod
    def detect_bank_type(pdf_path: Path) -> str | None:
        """Detect bank type from PDF content.

        Examines PDF text for bank-specific identifiers.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Bank type string (gcash, bpi, maya_savings, maya_wallet)
            or None if bank cannot be identified
        """
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                # Read first page for identification
                if not pdf.pages:
                    logger.debug(f"No pages found in PDF: {pdf_path}")
                    return None

                text = pdf.pages[0].extract_text() or ""
                text_lower = text.lower()

                # Check for bank identifiers
                if "gcash" in text_lower or "g-xchange" in text_lower:
                    return "gcash"
                elif "bank of the philippine islands" in text_lower or "bpi" in text_lower:
                    return "bpi"
                elif "maya" in text_lower:
                    if "savings" in text_lower:
                        return "maya_savings"
                    return "maya_wallet"

                logger.debug(f"Could not identify bank type from PDF content: {pdf_path}")
                return None

        except Exception as e:
            logger.warning(f"Error detecting bank type for {pdf_path}: {e}")
            return None
