"""
Duplicate transaction detection.

Provides:
- DuplicateDetector: Find duplicate transactions
- DuplicateMatch: Representation of a duplicate pair
- Exact and near-duplicate detection
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Sequence


@dataclass
class DuplicateMatch:
    """Represents a potential duplicate match.

    Attributes:
        transaction_a: First transaction in the pair
        transaction_b: Second transaction in the pair
        confidence: Confidence score (0.0 to 1.0)
        match_type: Type of match ('exact', 'near', 'cross_source')
        reasons: List of reasons for the match
    """

    transaction_a: dict[str, Any]
    transaction_b: dict[str, Any]
    confidence: float
    match_type: str
    reasons: list[str] = field(default_factory=list)


class DuplicateDetector:
    """Detect duplicate transactions.

    Supports exact duplicates, near-duplicates, and cross-source duplicates.

    Example:
        detector = DuplicateDetector()

        # Find all duplicates in a list
        duplicates = detector.find_duplicates(transactions)
        for dup in duplicates:
            print(f"Potential duplicate: {dup.confidence:.0%}")

        # Compare two specific transactions
        match = detector.is_duplicate(tx_a, tx_b)
        if match:
            print(f"Duplicate found: {match.match_type}")
    """

    def __init__(
        self,
        time_threshold_hours: float = 24,  # Same day by default
        amount_threshold_percent: float = 1.0,  # 1% difference allowed
    ) -> None:
        """Initialize detector with thresholds.

        Args:
            time_threshold_hours: Maximum time difference to consider duplicates
            amount_threshold_percent: Maximum percentage difference in amounts
        """
        self.time_threshold = timedelta(hours=time_threshold_hours)
        self.amount_threshold_percent = amount_threshold_percent

    def find_duplicates(
        self, transactions: Sequence[dict[str, Any]]
    ) -> list[DuplicateMatch]:
        """Find all duplicate pairs in a list of transactions.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            List of DuplicateMatch objects
        """
        duplicates: list[DuplicateMatch] = []

        # Compare each pair
        for i, tx_a in enumerate(transactions):
            for tx_b in transactions[i + 1:]:
                match = self.is_duplicate(tx_a, tx_b)
                if match:
                    duplicates.append(match)

        return duplicates

    def is_duplicate(
        self, tx_a: dict[str, Any], tx_b: dict[str, Any]
    ) -> DuplicateMatch | None:
        """Check if two transactions are duplicates.

        Args:
            tx_a: First transaction
            tx_b: Second transaction

        Returns:
            DuplicateMatch if duplicates, None otherwise
        """
        reasons: list[str] = []
        confidence = 0.0

        # Compare dates
        date_a = tx_a.get("date")
        date_b = tx_b.get("date")
        if date_a and date_b:
            date_match, date_reason = self._compare_dates(date_a, date_b)
            if not date_match:
                return None
            reasons.append(date_reason)
            confidence += 0.35 if "Same date" in date_reason else 0.25

        # Compare amounts
        amount_a = tx_a.get("amount")
        amount_b = tx_b.get("amount")
        if amount_a and amount_b:
            amount_match, amount_reason = self._compare_amounts(amount_a, amount_b)
            if not amount_match:
                return None
            reasons.append(amount_reason)
            confidence += 0.35 if "Same amount" in amount_reason else 0.25

        # Compare descriptions
        desc_a = tx_a.get("description", "")
        desc_b = tx_b.get("description", "")
        desc_match, desc_reason, desc_confidence = self._compare_descriptions(
            desc_a, desc_b
        )
        if not desc_match:
            return None
        reasons.append(desc_reason)
        confidence += desc_confidence

        # Check for cross-source
        source_a = tx_a.get("source")
        source_b = tx_b.get("source")
        is_cross_source = source_a and source_b and source_a != source_b
        if is_cross_source:
            reasons.append("Cross-source duplicate")

        # Determine match type
        match_type = self._determine_match_type(reasons, confidence, is_cross_source)

        # Normalize confidence
        confidence = min(1.0, confidence)

        return DuplicateMatch(
            transaction_a=tx_a,
            transaction_b=tx_b,
            confidence=confidence,
            match_type=match_type,
            reasons=reasons,
        )

    def _compare_dates(
        self, date_a: datetime, date_b: datetime
    ) -> tuple[bool, str]:
        """Compare two dates.

        Returns:
            Tuple of (is_match, reason)
        """
        if date_a == date_b:
            return True, "Same date and time"

        diff = abs(date_a - date_b)

        # Must be same calendar day (or within configured threshold if smaller)
        same_day = date_a.date() == date_b.date()

        if same_day and diff <= self.time_threshold:
            if diff <= timedelta(minutes=5):
                return True, "Same date (within 5 minutes)"
            elif diff <= timedelta(hours=1):
                return True, "Same date (within 1 hour)"
            else:
                return True, "Same date"
        elif diff < self.time_threshold and diff < timedelta(hours=12):
            # Allow near-duplicates within threshold but different days only if very close
            return True, f"Near date (within {diff})"

        return False, ""

    def _compare_amounts(
        self, amount_a: Decimal, amount_b: Decimal
    ) -> tuple[bool, str]:
        """Compare two amounts.

        Returns:
            Tuple of (is_match, reason)
        """
        if amount_a == amount_b:
            return True, "Same amount"

        # Calculate percentage difference
        avg = (amount_a + amount_b) / 2
        if avg == 0:
            return amount_a == amount_b, "Same amount (zero)"

        diff_percent = abs(float(amount_a - amount_b) / float(avg)) * 100

        if diff_percent <= self.amount_threshold_percent:
            return True, f"Similar amount ({diff_percent:.1f}% difference)"

        return False, ""

    def _compare_descriptions(
        self, desc_a: str, desc_b: str
    ) -> tuple[bool, str, float]:
        """Compare two descriptions.

        Returns:
            Tuple of (is_match, reason, confidence_contribution)
        """
        if not desc_a or not desc_b:
            return False, "", 0.0

        # Normalize for comparison
        norm_a = desc_a.upper().strip()
        norm_b = desc_b.upper().strip()

        if norm_a == norm_b:
            return True, "Same description", 0.35

        # Check if one contains the other
        if norm_a in norm_b or norm_b in norm_a:
            return True, "Similar description", 0.25

        # Check common prefix
        common_prefix = self._common_prefix_length(norm_a, norm_b)
        min_len = min(len(norm_a), len(norm_b))

        if common_prefix >= min_len * 0.7:  # 70% common prefix
            return True, "Similar description (common prefix)", 0.2

        return False, "", 0.0

    def _common_prefix_length(self, a: str, b: str) -> int:
        """Get length of common prefix between two strings."""
        length = 0
        for char_a, char_b in zip(a, b):
            if char_a == char_b:
                length += 1
            else:
                break
        return length

    def _determine_match_type(
        self, reasons: list[str], confidence: float, is_cross_source: bool
    ) -> str:
        """Determine the type of match.

        Returns:
            'exact', 'near', or 'cross_source'
        """
        if is_cross_source:
            return "cross_source"

        # Check if all comparisons are exact
        if any("Same date and time" in r for r in reasons) and \
           any("Same amount" in r for r in reasons) and \
           any("Same description" in r for r in reasons):
            return "exact"

        return "near"

    def group_duplicates(
        self, transactions: Sequence[dict[str, Any]]
    ) -> list[list[dict[str, Any]]]:
        """Group transactions that are duplicates of each other.

        Args:
            transactions: List of transactions

        Returns:
            List of groups (each group is a list of duplicate transactions)
        """
        # Find all duplicate pairs
        duplicates = self.find_duplicates(transactions)

        if not duplicates:
            return []

        # Build adjacency list
        tx_ids = {id(tx): tx for tx in transactions}
        adjacency: dict[int, set[int]] = {id(tx): set() for tx in transactions}

        for dup in duplicates:
            id_a = id(dup.transaction_a)
            id_b = id(dup.transaction_b)
            adjacency[id_a].add(id_b)
            adjacency[id_b].add(id_a)

        # Find connected components using BFS
        visited: set[int] = set()
        groups: list[list[dict[str, Any]]] = []

        for tx_id in adjacency:
            if tx_id in visited or not adjacency[tx_id]:
                continue

            # BFS to find all connected transactions
            group: list[dict[str, Any]] = []
            queue = [tx_id]

            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                group.append(tx_ids[current])

                for neighbor in adjacency[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)

            if len(group) > 1:  # Only include groups with actual duplicates
                groups.append(group)

        return groups
