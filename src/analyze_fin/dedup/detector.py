"""
Duplicate transaction detection.

Provides:
- DuplicateDetector: Find duplicate transactions
- DuplicateMatch: Representation of a duplicate pair
- Exact and near-duplicate detection

Performance:
- Uses date-based indexing to avoid O(n²) comparisons
- Content hash index for exact duplicate detection
- Reference number index for bank-provided dedup
"""

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from hashlib import md5
from typing import Any


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

        Uses indexed approach for O(n) average case instead of O(n²):
        1. Exact matches via content hash (O(n) build, O(1) lookup)
        2. Reference number matches (O(n) build, O(1) lookup)
        3. Near-duplicate detection via date bucketing (compare within same day only)

        Args:
            transactions: List of transaction dictionaries

        Returns:
            List of DuplicateMatch objects
        """
        if len(transactions) <= 1:
            return []

        duplicates: list[DuplicateMatch] = []
        seen_pairs: set[tuple[int, int]] = set()  # Track compared pairs by index

        # Build indexes for efficient lookup
        content_hash_index = self._build_content_hash_index(transactions)
        reference_index = self._build_reference_index(transactions)
        date_index = self._build_date_index(transactions)

        # Step 1: Find exact duplicates via content hash (highest confidence)
        for tx_hash, indices in content_hash_index.items():
            if len(indices) > 1:
                for i in range(len(indices)):
                    for j in range(i + 1, len(indices)):
                        idx_a, idx_b = indices[i], indices[j]
                        pair_key = (min(idx_a, idx_b), max(idx_a, idx_b))
                        if pair_key not in seen_pairs:
                            match = self.is_duplicate(
                                transactions[idx_a], transactions[idx_b]
                            )
                            if match:
                                duplicates.append(match)
                            seen_pairs.add(pair_key)

        # Step 2: Find duplicates via reference number
        for ref_num, indices in reference_index.items():
            if len(indices) > 1:
                for i in range(len(indices)):
                    for j in range(i + 1, len(indices)):
                        idx_a, idx_b = indices[i], indices[j]
                        pair_key = (min(idx_a, idx_b), max(idx_a, idx_b))
                        if pair_key not in seen_pairs:
                            match = self.is_duplicate(
                                transactions[idx_a], transactions[idx_b]
                            )
                            if match:
                                duplicates.append(match)
                            seen_pairs.add(pair_key)

        # Step 3: Find near-duplicates via date bucketing
        # Only compare transactions on the same date or adjacent dates
        sorted_dates = sorted(date_index.keys())
        for i, current_date in enumerate(sorted_dates):
            # Get indices for current date
            current_indices = date_index[current_date]

            # Compare within same date
            self._compare_indices(
                transactions, current_indices, current_indices,
                duplicates, seen_pairs
            )

            # Compare with next date (for cross-midnight near-duplicates)
            if i + 1 < len(sorted_dates):
                next_date = sorted_dates[i + 1]
                if (next_date - current_date).days <= 1:
                    next_indices = date_index[next_date]
                    self._compare_indices(
                        transactions, current_indices, next_indices,
                        duplicates, seen_pairs
                    )

        return duplicates

    def _build_content_hash_index(
        self, transactions: Sequence[dict[str, Any]]
    ) -> dict[str, list[int]]:
        """Build index mapping content hash to transaction indices.

        Content hash is computed from date + amount + normalized description.
        """
        index: dict[str, list[int]] = defaultdict(list)

        for idx, tx in enumerate(transactions):
            tx_hash = self._compute_content_hash(tx)
            if tx_hash:
                index[tx_hash].append(idx)

        return dict(index)

    def _build_reference_index(
        self, transactions: Sequence[dict[str, Any]]
    ) -> dict[str, list[int]]:
        """Build index mapping reference numbers to transaction indices."""
        index: dict[str, list[int]] = defaultdict(list)

        for idx, tx in enumerate(transactions):
            ref = tx.get("reference_number")
            if ref:
                index[str(ref).strip().upper()].append(idx)

        return dict(index)

    def _build_date_index(
        self, transactions: Sequence[dict[str, Any]]
    ) -> dict[datetime, list[int]]:
        """Build index mapping dates (day only) to transaction indices."""
        index: dict[datetime, list[int]] = defaultdict(list)

        for idx, tx in enumerate(transactions):
            date = tx.get("date")
            if isinstance(date, datetime):
                # Use date only (not time) for bucketing
                day_key = datetime(date.year, date.month, date.day)
                index[day_key].append(idx)

        return dict(index)

    def _compute_content_hash(self, tx: dict[str, Any]) -> str | None:
        """Compute content hash for a transaction.

        Hash is based on: date (day only) + amount + normalized description.
        Returns None if required fields are missing.
        """
        date = tx.get("date")
        amount = tx.get("amount")
        description = tx.get("description", "")

        if not date or amount is None:
            return None

        # Normalize components
        date_str = date.strftime("%Y-%m-%d") if isinstance(date, datetime) else str(date)
        amount_str = f"{float(amount):.2f}"
        desc_normalized = description.upper().strip()[:50]  # First 50 chars

        content = f"{date_str}|{amount_str}|{desc_normalized}"
        return md5(content.encode()).hexdigest()

    def _compare_indices(
        self,
        transactions: Sequence[dict[str, Any]],
        indices_a: list[int],
        indices_b: list[int],
        duplicates: list[DuplicateMatch],
        seen_pairs: set[tuple[int, int]],
    ) -> None:
        """Compare transactions between two index lists.

        If indices_a == indices_b, compares within the list (avoiding self-comparison).
        """
        same_list = indices_a is indices_b

        for i, idx_a in enumerate(indices_a):
            start_j = i + 1 if same_list else 0
            for idx_b in (indices_b[start_j:] if same_list else indices_b):
                if idx_a == idx_b:
                    continue

                pair_key = (min(idx_a, idx_b), max(idx_a, idx_b))
                if pair_key in seen_pairs:
                    continue

                match = self.is_duplicate(transactions[idx_a], transactions[idx_b])
                if match:
                    duplicates.append(match)
                seen_pairs.add(pair_key)

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

        Uses transaction indices (not object IDs) for stable grouping
        that works across sessions.

        Args:
            transactions: List of transactions

        Returns:
            List of groups (each group is a list of duplicate transactions)
        """
        # Find all duplicate pairs
        duplicates = self.find_duplicates(transactions)

        if not duplicates:
            return []

        # Build transaction index lookup
        tx_list = list(transactions)
        tx_to_idx: dict[int, int] = {id(tx): idx for idx, tx in enumerate(tx_list)}

        # Build adjacency list using indices (not object IDs)
        adjacency: dict[int, set[int]] = defaultdict(set)

        for dup in duplicates:
            idx_a = tx_to_idx.get(id(dup.transaction_a))
            idx_b = tx_to_idx.get(id(dup.transaction_b))
            if idx_a is not None and idx_b is not None:
                adjacency[idx_a].add(idx_b)
                adjacency[idx_b].add(idx_a)

        # Find connected components using BFS
        visited: set[int] = set()
        groups: list[list[dict[str, Any]]] = []

        for tx_idx in adjacency:
            if tx_idx in visited:
                continue

            # BFS to find all connected transactions
            group_indices: list[int] = []
            queue = [tx_idx]

            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                group_indices.append(current)

                for neighbor in adjacency[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)

            if len(group_indices) > 1:  # Only include groups with actual duplicates
                # Convert indices back to transactions
                group = [tx_list[idx] for idx in sorted(group_indices)]
                groups.append(group)

        return groups
