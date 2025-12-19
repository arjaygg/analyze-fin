"""
Duplicate transaction resolution.

Provides:
- DuplicateResolver: Manage duplicate resolutions
- Resolution: Representation of a resolution decision
- Auto-resolve, manual resolve, persistence
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from analyze_fin.dedup.detector import DuplicateMatch


@dataclass
class Resolution:
    """A duplicate resolution decision.

    Attributes:
        transaction_ids: IDs of transactions in this resolution
        resolution_type: 'duplicate' or 'unique'
        keep_id: ID of transaction to keep (None if unique)
        reason: Optional reason for the resolution
        created_at: When the resolution was made
    """

    transaction_ids: list[int]
    resolution_type: str  # 'duplicate' or 'unique'
    keep_id: int | None = None
    reason: str | None = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "transaction_ids": self.transaction_ids,
            "resolution_type": self.resolution_type,
            "keep_id": self.keep_id,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Resolution":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()

        return cls(
            transaction_ids=data["transaction_ids"],
            resolution_type=data["resolution_type"],
            keep_id=data.get("keep_id"),
            reason=data.get("reason"),
            created_at=created_at,
        )


class DuplicateResolver:
    """Manage duplicate transaction resolutions.

    Stores decisions about which duplicates to keep, remove, or treat
    as unique transactions.

    Example:
        resolver = DuplicateResolver()

        # Mark as duplicate (keep first)
        resolver.mark_duplicate([1, 2], keep_id=1)

        # Mark as unique (false positive)
        resolver.mark_unique([3, 4], reason="Different merchants")

        # Filter transactions
        clean = resolver.filter_transactions(all_transactions)

        # Save/load
        resolver.save(Path("resolutions.json"))
        resolver.load(Path("resolutions.json"))
    """

    def __init__(self) -> None:
        """Initialize resolver."""
        self._resolutions: list[Resolution] = []
        self._resolved_ids: dict[int, Resolution] = {}

    def mark_duplicate(
        self,
        transaction_ids: list[int],
        keep_id: int,
        reason: str | None = None,
    ) -> Resolution:
        """Mark transactions as duplicates.

        Args:
            transaction_ids: IDs of duplicate transactions
            keep_id: ID of the transaction to keep
            reason: Optional reason for the resolution

        Returns:
            The created Resolution
        """
        resolution = Resolution(
            transaction_ids=list(transaction_ids),
            resolution_type="duplicate",
            keep_id=keep_id,
            reason=reason,
        )

        self._resolutions.append(resolution)
        for tid in transaction_ids:
            self._resolved_ids[tid] = resolution

        return resolution

    def mark_unique(
        self,
        transaction_ids: list[int],
        reason: str | None = None,
    ) -> Resolution:
        """Mark transactions as unique (not duplicates).

        Args:
            transaction_ids: IDs of transactions
            reason: Optional reason for the resolution

        Returns:
            The created Resolution
        """
        resolution = Resolution(
            transaction_ids=list(transaction_ids),
            resolution_type="unique",
            keep_id=None,
            reason=reason,
        )

        self._resolutions.append(resolution)
        for tid in transaction_ids:
            self._resolved_ids[tid] = resolution

        return resolution

    def get_resolutions(self) -> list[Resolution]:
        """Get all resolutions.

        Returns:
            List of Resolution objects
        """
        return list(self._resolutions)

    def get_duplicate_ids(self) -> set[int]:
        """Get IDs of transactions marked as duplicates (to be removed).

        Returns:
            Set of transaction IDs that should be removed
        """
        duplicate_ids: set[int] = set()

        for resolution in self._resolutions:
            if resolution.resolution_type == "duplicate" and resolution.keep_id is not None:
                for tid in resolution.transaction_ids:
                    if tid != resolution.keep_id:
                        duplicate_ids.add(tid)

        return duplicate_ids

    def is_resolved(self, transaction_id: int) -> bool:
        """Check if a transaction has been resolved.

        Args:
            transaction_id: Transaction ID to check

        Returns:
            True if resolved, False otherwise
        """
        return transaction_id in self._resolved_ids

    def get_resolution_for(self, transaction_id: int) -> Resolution | None:
        """Get the resolution for a specific transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Resolution or None if not resolved
        """
        return self._resolved_ids.get(transaction_id)

    def filter_transactions(
        self, transactions: Sequence[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Filter out duplicate transactions.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Filtered list with duplicates removed
        """
        duplicate_ids = self.get_duplicate_ids()

        return [
            tx for tx in transactions
            if tx.get("id") not in duplicate_ids
        ]

    def auto_resolve(
        self,
        matches: Sequence[DuplicateMatch],
        keep_first: bool = True,
        min_confidence: float = 0.95,
    ) -> int:
        """Automatically resolve duplicate matches.

        Args:
            matches: List of DuplicateMatch objects
            keep_first: If True, keep first transaction; else keep last
            min_confidence: Minimum confidence to auto-resolve

        Returns:
            Number of groups auto-resolved
        """
        resolved_count = 0

        for match in matches:
            if match.confidence < min_confidence:
                continue

            # Get transaction IDs
            id_a = match.transaction_a.get("id")
            id_b = match.transaction_b.get("id")

            if id_a is None or id_b is None:
                continue

            # Already resolved?
            if self.is_resolved(id_a) or self.is_resolved(id_b):
                continue

            # Determine which to keep
            keep_id = id_a if keep_first else id_b

            self.mark_duplicate(
                transaction_ids=[id_a, id_b],
                keep_id=keep_id,
                reason=f"Auto-resolved ({match.match_type}, {match.confidence:.0%} confidence)",
            )
            resolved_count += 1

        return resolved_count

    def save(self, path: Path) -> None:
        """Save resolutions to a JSON file.

        Args:
            path: File path to save to
        """
        data = {
            "version": 1,
            "resolutions": [r.to_dict() for r in self._resolutions],
        }

        path.write_text(json.dumps(data, indent=2))

    def load(self, path: Path) -> int:
        """Load resolutions from a JSON file.

        Args:
            path: File path to load from

        Returns:
            Number of resolutions loaded
        """
        if not path.exists():
            return 0

        data = json.loads(path.read_text())
        resolutions = data.get("resolutions", [])

        count = 0
        for res_data in resolutions:
            resolution = Resolution.from_dict(res_data)
            self._resolutions.append(resolution)
            for tid in resolution.transaction_ids:
                self._resolved_ids[tid] = resolution
            count += 1

        return count

    def get_stats(self) -> dict[str, int]:
        """Get resolution statistics.

        Returns:
            Dictionary with statistics
        """
        duplicate_groups = sum(
            1 for r in self._resolutions if r.resolution_type == "duplicate"
        )
        unique_groups = sum(
            1 for r in self._resolutions if r.resolution_type == "unique"
        )

        total_duplicates_removed = len(self.get_duplicate_ids())

        return {
            "total_resolutions": len(self._resolutions),
            "duplicate_groups": duplicate_groups,
            "unique_groups": unique_groups,
            "total_duplicates_removed": total_duplicates_removed,
        }

    def clear(self) -> None:
        """Clear all resolutions."""
        self._resolutions.clear()
        self._resolved_ids.clear()
